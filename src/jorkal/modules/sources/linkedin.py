from jorkal.types.source import Source
from jorkal.types.jobs import Job
import asyncio
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import re


LINKEDIN_AUTHENTICATION_URL = "https://www.linkedin.com/login"
LINKEDIN_FEED_PAGE_URL = "https://www.linkedin.com/feed"


class Linkedin(Source):
    def __init__(self, logger, configuration, database):
        super().__init__(logger, configuration, database)
        self.name = "Linkedin"
        self.browser = None
        self.database = database
        self.__is_healthy = True

    async def __is_wanted_job(self, title):
        regular_expressions = "(?:% s)" % "|".join(
            self.configuration.job_title_expressions
        )
        if re.match(regular_expressions, title, re.IGNORECASE):
            return True
        else:
            return False

    async def __gather_jobs(self, query):
        try:
            query = urllib.parse.quote(query)
            self.browser.get(  # pyright: ignore
                f"https://www.linkedin.com/jobs/search/?f_TPR=r86400&f_WT=2&geoId=103644278&keywords={query}&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true&sortBy=DD"
            )
            await asyncio.sleep(10)
            elements = self.browser.find_elements(
                By.XPATH, "//div/ul/li[@data-occludable-job-id]"
            )
            await asyncio.sleep(4)
            actions = ActionChains(self.browser)  # pyright: ignore
            actions.move_to_element(elements[0])
            count = 0
            for element in elements:
                self.browser.execute_script("arguments[0].scrollIntoView();", element)
                await asyncio.sleep(0.1)
            await asyncio.sleep(5)
            postings = self.browser.find_elements(
                By.XPATH,
                '//li[contains(@class, "ember-view")]//div[contains(@class, "flex-grow-1")]',
            )
            print(f"number of postings: {len(postings)}")
            self.logger.debug(f"number of job postings: {len(postings)}")
            for posting in postings:
                title = posting.find_element(By.XPATH, ".//a/span/strong").text
                if not await self.__is_wanted_job(title):
                    continue
                company = posting.find_element(
                    By.XPATH,
                    './/div[contains(@class, "artdeco-entity-lockup__subtitle")]/span',
                ).text
                link = posting.find_element(
                    By.XPATH,
                    './/div/a[contains(@class, "job-card-container__link")]',
                ).get_attribute("href")
                if link is None:
                    continue
                link = link.split("?")[0]
                self.jobs.add_posting(Job(title, company, "Remote, US", link))
            return True
        except Exception as E:
            self.logger.error(f"Error gathering jobs for query '{query}' ({E})")
            return False

    async def __start_browser(self, retry_count=0):
        try:
            if self.browser is None:
                options = webdriver.ChromeOptions()
                options.add_argument(
                    f"--user-data-dir={self.configuration.chrome_data_dir}"
                )
                options.add_argument("--profile-directory=Default")
                self.browser = webdriver.Chrome(options=options)
                return True
        except Exception as E:
            while retry_count < 3:
                retry_successful = await self.__start_browser(retry_count + 1)
                if retry_successful is True:
                    return True
                else:
                    retry_count += 1
                    continue
            self.logger.error(
                f"Error starting chrome browser. Marking '{self.name}' module as unhealthy ({E}"
            )
            self.__is_healthy = False
            self.browser = None
            return False

    async def __authenticate(self, retry_count=0):
        user_is_authenticating = True
        if self.browser is None:
            await self.__start_browser()
        else:
            try:
                self.browser.get(LINKEDIN_AUTHENTICATION_URL)
                time_elapsed = 0
                timeout_threshold = 60
                await asyncio.sleep(5)
                while user_is_authenticating and time_elapsed < timeout_threshold:
                    current_url = self.browser.current_url
                    if (
                        LINKEDIN_AUTHENTICATION_URL not in current_url
                    ):  # pyright: ignore
                        user_is_authenticating = False
                        self.logger.debug("Authentication completed")
                        return True
                    await asyncio.sleep(10)
                    time_elapsed += 10
                self.__is_healthy = False
                return False
            except Exception as E:
                while retry_count < 3:
                    await asyncio.sleep(10)
                    retry_successful = await self.__authenticate(retry_count + 1)
                    if retry_successful is True:
                        return True
                    else:
                        retry_count += 1
                        continue
                self.logger.error(
                    f"Error authenticating user. Marking '{self.name}' module as unhealthy ({E}"
                )
                self.__is_healthy = False
                return False

    def is_healthy(self):
        return self.__is_healthy

    async def __is_authenticated(self, retry_count=0):
        await self.__start_browser()
        try:
            self.browser.get(LINKEDIN_FEED_PAGE_URL)  # pyright: ignore
            await asyncio.sleep(10)
            matches = self.browser.find_elements(  # pyright: ignore
                By.XPATH, "//span[@title='Messaging']"
            )  # pyright: ignore
            await asyncio.sleep(10)
            await asyncio.sleep(2)
            if len(matches) < 1:
                while retry_count < 3:
                    self.logger.debug("User is not authenticated")
                    self.logger.info(f"Initiating user authentication (Please sign in)")
                    await self.__authenticate()
                    self.logger.info(
                        f"Retrying user authentication check (attempt #{retry_count+1})"
                    )
                    retry_successful = await self.__is_authenticated(retry_count + 1)
                    if retry_successful is True:
                        return True
                    else:
                        retry_count += 1
                        continue
            else:
                self.logger.debug("User is authenticated")
                return True
            self.logger.error(
                f"User is not authenticated. Marking '{self.name}' module as unhealthy"
            )
            self.__is_healthy = False
            return False

        except Exception as E:
            if retry_count > 3:
                self.logger.error(
                    f"Error checking if user is authenticated. Marking '{self.name}' module as unhealthy ({E})"
                )
                self.__is_healthy = False
                return False
            else:
                self.logger.error(
                    f"Error checking if user is authenticated. Retrying (attempt #{retry_count+1}) ({E})"
                )
                await asyncio.sleep(10)
                await self.__is_authenticated(retry_count + 1)
                return True

    async def run(self):
        while self.__is_healthy:
            if not await self.__is_authenticated():
                await self.__authenticate()
            for query in self.configuration.queries:
                self.logger.debug(
                    f"[Module: Linkedin] Gathering results for query: '{query}'"
                )
                await self.__gather_jobs(query)
                for job in self.jobs.postings:
                    await self.database.add_job(
                        job.title,
                        job.company,
                        job.link,
                        job.location,
                        job.date_scraped,
                        "LinkedIn",
                    )
                self.jobs.postings.clear()
                await asyncio.sleep(10)
            await asyncio.sleep(self.configuration.check_interval)
        return
