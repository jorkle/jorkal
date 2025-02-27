import sqlite3

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
            return connection
        except Exception as E:
            self.logger.critical(f"Failed to connect to Sqlite Database. ({E})")

    async def __job_exists(self, company: str, link: str):

        # defining these as None so that if they are assigned actual values in the future then they can be closed in the event of an exception.
        cursor, connection = None, None

        try:
            # Attempt to establish a database connection
            connection = await self.__connect()
            if connection is None:
                raise Exception("Issue connecting to the database.")
        except aiosqlite.OperationalError as e:
            self.logger.critical(
                f"[DATABASE] : Failed to connect to the database. Operational error: {e}"
            )
            return False
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error during connection attempt: {e}"
            )
            return False
        try:
            already_added_query = """SELECT id, link FROM Jobs WHERE company = ?"""
            cursor = await connection.cursor()

            # Attempt to execute the query
            await cursor.execute(already_added_query, (company,))
            await connection.commit()

        except aiosqlite.ProgrammingError as e:
            self.logger.error(f"[DATABASE] : SQL syntax or query execution error: {e}")
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return False
        except aiosqlite.DatabaseError as e:
            self.logger.error(
                f"[DATABASE] : Database error during query execution: {e}"
            )
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return False
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error occurred during query execution: {e}"
            )
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return False
        try:
            # Fetch all rows from the query
            jobs = await cursor.fetchall()
            await cursor.close()
            await connection.close()
            for job in jobs:
                if job[1] == link:
                    return True
                else:
                    continue
            return False
        except Exception as e:
            self.logger.error(
                f"[DATABASE] : Error occurred while processing fetched data: {e}"
            )
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return False

    async def __generate_sql_args(
        self, destination: str, only_unseen: bool, source: str | None
    ) -> tuple[str, str]:
        """
        A helper function that generates the SQL query and parameters for the `get_jobs` function.
        Depending on the parameters passed in, the function will return the appropriate SQL query and parameters.

        Logic Paths (in the order that they appear)
        ----------------------
            (source = None) and (only_unseen = True):
                SQL arguments are returned that cause the `get_jobs` function to return every job that hasn't already
                been notified through the specified destination regardless of the source that originally added that job to the database.
            (source = None) and (only_unseen = False):
                SQL arguments are returned that cause the `get_jobs` function to return every job within the database regardless if the
                destination has already been notified of the jobs and regardless of the source that originally added that job to the database.
            (source = string) and (only_unseen = True):
                SQL arguments are returned that cause the `get_jobs` function to return every job that was added to the database by the
                source specified in the `source` parameter that hasn't already been notified through the specified destination.
            (source = string) and (only_unseen = False):
                SQL arguments are returned that cause the `get_jobs` function to return every job within the database that was added by the
                source specified in the `source` paramater regardless if the destination has already been notified of the jobs.

        """
        if source is None:
            if only_unseen:
                # SQL arguments are returned that cause the `get_jobs` function to return every job that hasn't already
                # been notified through the specified destination regardless of the source that originally added that job to the database.
                new_jobs_query = f"SELECT id, title, company, location, link, date_scraped, source FROM Jobs WHERE {destination} = 0;"
                update_status_query = f"UPDATE Jobs SET {destination} = 1 WHERE id in ("
            else:
                # SQL arguments are returned that cause the `get_jobs` function to return every job within the database regardless if the
                # destination has already been notified of the jobs and regardless of the source that originally added that job to the database.
                new_jobs_query = "SELECT id, title, company, location, link, date_scraped, source FROM Jobs;"
                update_status_query = f"UPDATE Jobs SET {destination} = 1 WHERE id in ("
        else:
            if only_unseen:
                # SQL arguments are returned that cause the `get_jobs` function to return every job that was added to the database by the
                # source specified in the `source` parameter that hasn't already been notified through the specified destination.
                new_jobs_query = f"SELECT id, title, company, location, link, date_scraped, source FROM Jobs WHERE {destination} = 0 AND source = {source};"
                update_status_query = f"UPDATE Jobs SET {destination} = 1 WHERE source = {source} AND id in ("
            else:
                # SQL arguments are returned that cause the `get_jobs` function to return every job within the database that was added by the
                # source specified in the `source` paramater regardless if the destination has already been notified of the jobs.
                new_jobs_query = f"SELECT id, title, company, location, link, date_scraped, source FROM Jobs WHERE source = {source};"
                update_status_query = f"UPDATE Jobs SET {destination} = 1 WHERE source = {source} AND id in ("
        return new_jobs_query, update_status_query

    async def get_jobs(self, destination: str, only_unseen=True, source=None) -> Jobs:

        # defining these as None so that if they are assigned actual values in the future then they can be closed in the event of an exception.
        cursor, connection = None, None

        try:
            # Generate SQL arguments
            new_jobs_query, update_status_query = await self.__generate_sql_args(
                destination, only_unseen, source
            )

        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Error while generating SQL arguments: {e}"
            )
            return Jobs()

        try:
            # Establish database connection
            connection = await self.__connect()
            if connection is None:
                return Jobs()
        except aiosqlite.OperationalError as e:
            self.logger.critical(
                f"[DATABASE] : Failed to connect to the database. Operational error: {e}"
            )
            return Jobs()
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error during connection attempt: {e}"
            )
            return Jobs()

        try:
            cursor = await connection.cursor()
            await cursor.execute(new_jobs_query)
            await connection.commit()
            results = await cursor.fetchall()
            await cursor.close()
            await connection.close()
        except aiosqlite.ProgrammingError as e:
            self.logger.error(f"[DATABASE] : SQL syntax or query execution error: {e}")
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return Jobs()
        except aiosqlite.DatabaseError as e:
            self.logger.error(
                f"[DATABASE] : Database error during query execution: {e}"
            )
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return Jobs()
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error occurred during query execution: {e}"
            )
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return Jobs()

            # Process the results
        jobs = Jobs()
        try:
            # if statement evaluates to True if results is None or 'results' iterable contains at least one element.
            if results is None or sum([1 for _ in results]) < 1:
                return Jobs()

            # Add job postings
            for job in results:
                update_status_query += f"{job[0]},"
                jobs.add_posting(Job(job[1], job[2], job[3], job[4], job[6]))

            # Finalize the update status query
            update_status_query = update_status_query[:-1] + ");"

            # Update job status
            connection = await self.__connect()
            if connection is None:
                return Jobs()
            cursor = await connection.cursor()
            await cursor.execute(update_status_query)
            await connection.commit()
            await cursor.close()
            await connection.close()
            return jobs
        except aiosqlite.ProgrammingError as e:
            self.logger.error(f"[DATABASE] : SQL error during job status update: {e}")
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return jobs
        except aiosqlite.DatabaseError as e:
            self.logger.error(
                f"[DATABASE] : Database error during job status update: {e}"
            )
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return jobs
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error occurred during job status update: {e}"
            )
            if cursor is not None:
                await cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                await connection.close()  # Ensure connection is closed on error
            return jobs

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
            # Sanitize input values
            company = await normalize.sanitize_company(company)
            title = await normalize.sanitize_title(title)

            # Check if the job already exists
            if await self.__job_exists(company, link):
                self.logger.debug(
                    "[DATABASE] : Skipping.. Job already added to the database."
                )
                return
            add_job_query = """INSERT INTO Jobs (title, company, location, link, date_scraped, source)
                                VALUES (?, ?, ?, ?, ?, ?);"""

            add_job_data = (title, company, location, link, date_scraped, source)
            connection = await self.__connect()
            if connection is None:
                return
            cursor = await connection.cursor()
            await cursor.execute(add_job_query, add_job_data)
            await connection.commit()
            await cursor.close()
            await connection.close()
            self.logger.debug(
                f"[DATABASE] : Job added to the database ({title} @ {company} - {link})"
            )
            return
        except Exception as E:
            self.logger.critical(
                f"[DATABASE] : Unknown error encountered while performing query. ({E})"
            )

    def __initialize(self):

        # defining these as None so that if they are assigned actual values in the future then they can be closed in the event of an exception.
        cursor, connection = None, None

        create_table_query = """CREATE TABLE IF NOT EXISTS Jobs (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT NOT NULL,
                                company TEXT NOT NULL,
                                location TEXT,
                                link TEXT NOT NULL,
                                notified BOOLEAN DEFAULT FALSE,
                                date_scraped TEXT NOT NULL,
                                source TEXT NOT NULL"""
        for destination in self.configuration.destinations:
            create_table_query += f", {destination} BOOLEAN DEFAULT FALSE"
        create_table_query += ");"
        try:
            connection = sqlite3.connect(self.configuration.database_file)
        except sqlite3.OperationalError as e:
            self.logger.critical(
                f"[DATABASE] : Failed to connect to the database. Operational error: {e}"
            )
            return
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error during connection attempt: {e}"
            )
            return
        try:
            cursor = connection.cursor()
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
            connection.close()
            self.logger.info("Database initialization complete.")
            return
        except aiosqlite.ProgrammingError as e:
            self.logger.error(f"[DATABASE] : SQL syntax or query execution error: {e}")
            if cursor is not None:
                cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                connection.close()  # Ensure connection is closed on error
            return
        except aiosqlite.DatabaseError as e:
            self.logger.error(
                f"[DATABASE] : Database error during query execution: {e}"
            )
            if cursor is not None:
                cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                connection.close()  # Ensure connection is closed on error
            return
        except Exception as e:
            self.logger.critical(
                f"[DATABASE] : Unknown error occurred during query execution: {e}"
            )
            if cursor is not None:
                cursor.close()  # Ensure cursor is closed on error
            if connection is not None:
                connection.close()  # Ensure connection is closed on error
            return
