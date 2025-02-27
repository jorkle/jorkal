import sqlite3
import re
from datetime import datetime

import aiosqlite

from jorkal.types.jobs import Jobs, Job
from jorkal.helpers import normalize


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

    async def __job_exists(self, company: str, link: str):
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

    async def get_jobs(self, destination: str, only_unseen=True, source=None) -> Jobs:
        try:

            if source is None:
                new_jobs_query = f"""SELECT id, title, company, location, link, date_scraped, source FROM Jobs WHERE ? = FALSE;"""
                new_jobs_param = (destination,)
                update_status_query = f"""UPDATE Jobs SET ? = TRUE WHERE id in ("""
                update_status_param = (destination,)
            else:
                new_jobs_query = f"""SELECT id, title, company, location, link, date_scraped, source FROM Jobs WHERE ? = FALSE AND source = ?;"""
                new_jobs_param = (destination, source)
                update_status_query = (
                    f"""UPDATE Jobs SET ? = TRUE WHERE source = ? AND id in ("""
                )
                update_status_param = (destination, source)

            connection = await self.__connect()
            cursor = await connection.cursor()  # pyright: ignore
            await cursor.execute(new_jobs_query, new_jobs_param)
            await connection.commit()  # pyright: ignore
            results = await cursor.fetchall()
            await cursor.close()
            await connection.close()  # pyright: ignore
            jobs = Jobs()
            if results is None or len(results) < 1:
                return Jobs()
            else:
                for job in results:
                    update_status_query += f"{job[0]},"
                    jobs.add_posting(Job(job[1], job[2], job[3], job[4]))
                update_status_query = update_status_query[:-1] + ");"
                self.logger.debug(f"sql query {update_status_query}")
                connection = await self.__connect()
                cursor = await connection.cursor()  # pyright: ignore
                await cursor.execute(update_status_query, update_status_param)
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
            company = await Normalization.sanitize_company(company)
            title = await Normalization.sanitize_title(title)
            if await self.__job_exists(company, link):
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
