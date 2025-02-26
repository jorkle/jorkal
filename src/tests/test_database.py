import pytest
from jorkal.database import Database
from jorkal.log import Log
from jorkal.configuration import Configuration


@pytest.fixture(scope="session")
def tmp_log_file(tmp_path_factory):
    return f"{tmp_path_factory.mktemp("jorkal-pytest")}/jorkal_log_pytest.log"


@pytest.fixture(scope="session")
def tmp_db_file(tmp_path_factory):
    return f"{tmp_path_factory.mktemp("jorkal-pytest")}/jorkal_log_pytest.db"


@pytest.fixture(scope="session")
def tmp_config_file(tmp_path_factory):
    return f"{tmp_path_factory.mktemp("jorkal-pytest")}/jorkal_log_pytest.yaml"


class TestDatabase:
    def test_add_job(self, tmp_log_file, tmp_db_file, caplog, tmp_config_file):
        correct_message = f"Job added to the database (Test Job @ Test Company - http://fake.link/fake-job)"
        logger = Log(0, tmp_log_file)
        configuration = Configuration(
            {
                "configuration_file": tmp_config_file,
                "log_level": 0,
                "log_file": tmp_log_file,
            },
            logger,
        )
        configuration.database_file = tmp_db_file
        database = Database(configuration, logger)
        database.add_job(
            "Test Job",
            "Test Company",
            "http://fake.link/fake-job",
            "A really good fake job",
            "Remote, US",
        )
        for record in caplog.records:
            if (
                record.levelname == "ERROR"
                and "The specified configuration file" in caplog.text
                and "could not be found." in caplog.text
            ):
                continue
            assert record.levelname == "DEBUG" and correct_message in caplog.text
