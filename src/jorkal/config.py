import yaml
import json
from yaml import YAMLError
from cerberus import Validator
import base64


class Configuration:
    def __init__(self, cmd_opts: dict, logger):
        self.__log = logger
        self.log_level = cmd_opts["log_level"]
        self.log_file = cmd_opts["log_file"]
        self.database_file = None

        self.__load_configuration(configuration_file=cmd_opts["configuration_file"])

    def __is_configuration_valid(self, yaml_data):
        config_schema = self.__get_schema()
        v = Validator(config_schema)  # pyright: ignore
        return v.validate(yaml_data)  # pyright: ignore

    def __load_configuration(self, configuration_file):
        self.__log.debug(
            f"Attempting to load the configuration file ({configuration_file})."
        )
        try:
            with open(configuration_file, "r") as data_stream:

                configuration = yaml.safe_load(data_stream)

                if self.__is_configuration_valid(configuration):
                    self.__log.debug(
                        f"Configuration file is valid ({configuration_file})."
                    )

                    self.sources = configuration["sources"]
                    self.__log.debug(
                        "Loaded source settings from the configuration file."
                    )

                    self.destinations = configuration["destinations"]
                    self.__log.debug(
                        "Loaded destination (notification) settings from the configuration file."
                    )

                    self.check_interval = configuration["check_interval"]
                    self.__log.debug(
                        "Loaded frequency setting from the configuration file."
                    )

                    self.database_file = configuration["database_file"]
                    self.__log.debug(
                        "Loaded database_file setting from the configuration file."
                    )
                    self.chrome_data_dir = configuration["chrome_data_dir"]
                    self.__log.debug(
                        "Loaded chrome_data_dir setting from the configuration file."
                    )

                    self.queries = configuration["queries"]
                    self.__log.debug("Loaded queries setting from configuration file.")

                    self.job_title_expressions = configuration["job_title_expressions"]
                    self.__log.debug(
                        "Loaded job title expressions from the configuration file."
                    )

                    self.discord_token = configuration["discord_token"]
                    self.__log.debug(
                        "Loaded discord token setting from the configuration file."
                    )

                    self.discord_channel_id = configuration["discord_channel_id"]
                    self.__log.debug(
                        "Loaded the discord channel id setting from the configuration file."
                    )
                else:
                    self.__log.critical("The configuration file is not valid.")

            self.__log.info(f"{configuration_file} has been loaded successfully.")
            return

        except YAMLError as e:
            self.__log.critical(f"Issue processing yaml configuration file. ({e})")
        except FileNotFoundError:
            self.__log.error(
                f"The specified configuration file '{configuration_file}' could not be found."
            )
            self.__generate_configuration(configuration_file)
            self.__load_configuration(configuration_file)
        except PermissionError:
            self.__log.critical(
                "You do not have permission to access the configuration file."
            )
        except IsADirectoryError:
            self.__log.critical("The specified path is a directory, not a file.")
        except IOError as e:
            self.__log.critical(f"An I/O error occurred. ({e})")
        except UnicodeDecodeError:
            self.__log.critical(
                "Could not decode the file with the specified encoding."
            )
        except Exception as e:
            self.__log.critical(f"An unexpected error occurred. ({e})")

    def __save_configuration(
        self, configuration_file: str, configuration_data: str
    ) -> None:
        try:
            with open(configuration_file, mode="w") as data_stream:
                data_stream.write(configuration_data)
            self.__log.debug(f"Saved configuration to '{configuration_file}'.")
        except PermissionError:
            self.__log.critical(
                "You do not have permission to access the configuration file."
            )
        except IsADirectoryError:
            self.__log.critical("The specified path is a directory, not a file.")
        except IOError as e:
            self.__log.critical(f"An I/O error occurred. ({e})")
        except UnicodeDecodeError:
            self.__log.critical(
                "Could not decode the file with the specified encoding."
            )
        except Exception as e:
            self.__log.critical(f"An unexpected error occurred. ({e})")

    def __generate_configuration(self, configuration_file: str) -> None:
        self.__log.info(
            f"Generating new configuration and saving it to '{configuration_file}'"
        )
        configuration_data = """---
sources:
  linkedin: True
  indeed: True
destinations:
  discrd: True
check_interval: 10
database_file: jorkal.db
queries:
  - Penetration Tester
  - SOC Analyst
  - Security Analyst
job_title_expressions:
  - '.*security.*analyst.*'
  - '.*cyber.*analyst.*'
  - '.*cybersecurity.*analyst.*'
  - '.*soc.*analyst.*'
  - '.*Penetration.*Tester.*'
  - '.*Pentester.*'
  - '.*Red.*Team.*'
  - '.*Security.*Engineer.*'
  - '.*soc.*Engineer.*'
  - '.*cyber.*engineer.*'
  - '.*detection.*engineer.*'
  - '.*detection.*analyst.*'
chrome_data_dir: /home/jorkle/.config/google-chrome/
discord_channel_id: <enter your discord channel id here>
discord_token: <enter your discord token here>"""

        self.__save_configuration(configuration_file, configuration_data)

    def __get_schema(self):

        schema = {
            "sources": {
                "required": True,
                "type": "dict",
                "schema": {
                    "linkedin": {"required": True, "type": "boolean"},
                    "indeed": {"required": True, "type": "boolean"},
                },
            },
            "destinations": {
                "required": True,
                "type": "dict",
                "schema": {
                    "discrd": {"required": True, "type": "boolean"},
                },
            },
            "check_interval": {"required": True, "type": "integer"},
            "database_file": {"required": True, "type": "string"},
            "queries": {
                "required": True,
                "type": "list",
                "schema": {
                    "type": "string",
                },
            },
            "job_title_expressions": {
                "required": True,
                "type": "list",
                "schema": {
                    "type": "string",
                },
            },
            "chrome_data_dir": {"required": True, "type": "string"},
            "discord_channel_id": {"required": True, "type": "string"},
            "discord_token": {"required": True, "type": "string"},
        }

        return schema
