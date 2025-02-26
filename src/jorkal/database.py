import sqlite3
import re
from datetime import datetime
import aiosqlite


class Database:

    def __init__(self, configuration, logger):
        self.configuration = configuration
        self.logger = logger
        self.__initialize()

    async def __connect(self):
        try:
            connection = await aiosqlite.connect(self.configuration.database_file)
            if connection is not None:
                return connection
            else:
                self.logger.critical("Failed to connect to Sqlite Database.")
        except Exception as E:
            self.logger.critical(f"Failed to connect to Sqlite Database. ({E})")

    async def already_added(self, company: str, link: str):
        try:
            connection = await self.__connect()
            already_added_query = """SELECT id, link FROM Jobs WHERE company = ?"""
            cursor = await connection.cursor()  # pyright: ignore
            await cursor.execute(already_added_query, (company,))
            await connection.commit()  # pyright: ignore
            jobs = await cursor.fetchall()
            await cursor.close()
            await connection.close()  # pyright: ignore
            for job in jobs:
                if job[1] == link:
                    return True
                else:
                    continue
            return False
        except Exception as E:
            self.logger.critical(f"Unknown exception has occurred. ({E})")

    async def sanitize_job_title(self, title):
        sanitizations = [
            {"find": "Jr.?\s?", "replace": "Junior "},
            {"find": "Sr.?\s?", "replace": "Senior "},
        ]
        for sanitization in sanitizations:
            title = re.sub(
                sanitization["find"],
                sanitization["replace"],
                title,
                flags=re.IGNORECASE,
            )
        return title

    async def sanitize_company_name(self, company):
        sanitizations = [
            {"find": ",?\s?LLC", "replace": " LLC"},
            {"find": ",?\s?INC", "replace": " INC"},
            {"find": ",?\s?Incorporated", "replace": " INC"},
        ]
        for sanitization in sanitizations:
            company_name = re.sub(
                sanitization["find"], sanitization["replace"], company, re.IGNORECASE
            )
        return company_name  # pyright: ignore

    async def get_new_jobs(self):
        try:
            new_jobs_query = """SELECT id, title, company, location, link, date_scraped, source FROM Jobs WHERE notified = FALSE;"""
            update_status_query = f"""UPDATE Jobs SET notified = TRUE Where id in ("""
            connection = await self.__connect()
            cursor = await connection.cursor()  # pyright: ignore
            await cursor.execute(new_jobs_query)
            await connection.commit()  # pyright: ignore
            jobs = await cursor.fetchall()
            await cursor.close()
            await connection.close()  # pyright: ignore
            new_jobs = []
            if jobs is None or len(jobs) < 1:
                return None
            else:
                for job in jobs:
                    update_status_query += f"{job[0]},"
                    new_job = {}
                    new_job["id"] = job[0]
                    new_job["title"] = job[1]
                    new_job["company"] = job[2]
                    new_job["location"] = job[3]
                    new_job["link"] = job[4]
                    new_job["date_scraped"] = job[5]
                    new_job["source"] = job[6]
                    new_jobs.append(new_job)
                update_status_query = update_status_query[:-1] + ");"
                self.logger.debug(f"sql query {update_status_query}")
                connection = await self.__connect()
                cursor = await connection.cursor()  # pyright: ignore
                await cursor.execute(update_status_query)
                await connection.commit()  # pyright: ignore
                await cursor.close()
                await connection.close()  # pyright: ignore
                return new_jobs
        except Exception as E:
            self.logger.critical(f"Unknown exception has occurred. ({E})")

    async def add_job(
        self,
        title: str,
        company: str,
        link: str,
        location: str,
        date_scraped: str,
        source: str,
    ):
        try:
            company = await self.sanitize_company_name(company)
            title = await self.sanitize_job_title(title)
            if await self.already_added(company, link):
                self.logger.debug(
                    f"Skipping.. Job already added to the database ({title} @ {company} - {link})"
                )
                return
            add_job_query = f"""
INSERT INTO Jobs (title, company, location, link, date_scraped, source)
VALUES (?, ?, ?, ?, ?, ?);"""

            date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_job_data = (title, company, location, link, date_scraped, source)
            connection = await self.__connect()
            cursor = await connection.cursor()  # pyright: ignore
            await cursor.execute(add_job_query, add_job_data)  # pyright: ignore
            await connection.commit()  # pyright: ignore
            await cursor.close()
            await connection.close()  # pyright: ignore
            self.logger.debug(
                f"Job added to the database ({title} @ {company} - {link})"
            )
            return
        except Exception as E:
            self.logger.critical(
                f"Unknown error encountered while performing query. ({E})"
            )

    def __initialize(self):
        try:
            create_table_query = """
CREATE TABLE IF NOT EXISTS Jobs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
company TEXT NOT NULL,
location TEXT,
link TEXT NOT NULL,
notified BOOLEAN DEFAULT FALSE,
date_scraped TEXT NOT NULL,
source TEXT NOT NULL
);"""
            connection = sqlite3.connect(self.configuration.database_file)
            cursor = connection.cursor()
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
            connection.close()
            self.logger.info("Database initialization complete.")
            return
        except Exception as E:
            self.logger.critical(
                f"Unknown error encountered while performing query. ({E})"
            )
