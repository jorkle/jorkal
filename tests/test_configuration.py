import os
import pytest
from jorkal.config import Configuration
from jorkal.log import Log
import random


@pytest.fixture(scope="session")
def no_perm_file(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("jorkal-pytest")
    random_int = random.randint(2000, 20000)
    file = f"{temp_dir}/jorkal-{random_int}-pytest.yaml"
    with open(file, "w") as file_stream:
        file_stream.write("test_key: 'test_value'")
        os.chmod(file, 0000)
        return file


@pytest.fixture(scope="session")
def non_existing_file(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("jorkal-pytest")
    random_int = random.randint(2000, 20000)
    file = f"{temp_dir}/jorkal-{random_int}-pytest"
    return file


@pytest.fixture(scope="session")
def tmp_path(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("jorkal-pytest")
    return temp_dir


@pytest.fixture(scope="session")
def invalid_yaml_file(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("jorkal-pytest")
    random_int = random.randint(2000, 20000)
    file = f"{temp_dir}/jorkal-{random_int}-pytest.yaml"
    with open(file, "w") as file_stream:
        file_stream.write("invalid_yaml: invalid : really invald- :yaml")
        return file


@pytest.fixture(scope="session")
def tmp_log_file(tmp_path_factory):
    return f"{tmp_path_factory.mktemp("jorkal-pytest")}/jorkal_log_pytest.log"


class TestConfiguration:

    def test_configuration_not_existant(self, non_existing_file, tmp_log_file, caplog):
        correct_message = "The specified configuration file"
        logger = Log(0, tmp_log_file)
        Configuration(
            {
                "configuration_file": non_existing_file,
                "log_level": 0,
                "log_file": "log_file.log",
            },
            logger,
        )
        for record in caplog.records:
            assert record.levelname == "ERROR" and correct_message in caplog.text

    def test_configuration_invalid_yaml(self, invalid_yaml_file, tmp_log_file, caplog):
        correct_message = "Issue processing yaml configuration file."
        logger = Log(0, tmp_log_file)
        with pytest.raises(SystemExit):
            Configuration(
                {
                    "configuration_file": invalid_yaml_file,
                    "log_level": 0,
                    "log_file": "log_file.log",
                },
                logger,
            )
            for record in caplog.records:
                assert record.levelname == "CRITICAL" and correct_message in caplog.text

    def test_configuration_no_permission(self, no_perm_file, tmp_log_file, caplog):
        correct_message = "You do not have permission to access the configuration file."
        logger = Log(0, tmp_log_file)
        with pytest.raises(SystemExit):
            Configuration(
                {
                    "configuration_file": no_perm_file,
                    "log_level": 2,
                    "log_file": "log_file.log",
                },
                logger,
            )
            for record in caplog.records:
                assert record.levelname == "CRITICAL" and correct_message in caplog.text

    def test_configuration_is_directory(self, tmp_path, tmp_log_file, caplog):
        correct_message = "The specified path is a directory, not a file."
        logger = Log(0, tmp_log_file)
        with pytest.raises(SystemExit):
            Configuration(
                {
                    "configuration_file": tmp_path,
                    "log_level": 2,
                    "log_file": "log_file.log",
                },
                logger,
            )
        for record in caplog.records:
            assert record.levelname == "CRITICAL" and correct_message in caplog.text
