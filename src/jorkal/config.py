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

    def __validate_configuration(self, yaml_data):
        """
        Validates the provided configuration (yaml) data"""

        # cerberus yaml validation related
        # validate the configuration against the schema returned by self.__get_schema()
        config_schema = self.__get_schema()
        v = Validator(config_schema)  # pyright: ignore

        return v.validate(yaml_data)  # pyright: ignore

    def __load_configuration(self, configuration_file):
        """Attempts to load the configuration file. If the file does not exist, it will be created."""
        self.__log.debug(
            f"Attempting to load the configuration file ({configuration_file})."
        )
        try:
            with open(configuration_file, "r") as data_stream:

                configuration = yaml.safe_load(data_stream)

                if self.__validate_configuration(configuration):
                    self.__log.debug(f"[CONFIG] : '{configuration_file}' is valid")

                    self.sources = configuration["sources"]
                    self.__log.debug("[CONFIG] : 'sources' configuration loaded")

                    self.destinations = configuration["destinations"]
                    self.__log.debug("[CONFIG] : 'destinations' configuration loaded")

                    self.interval = configuration["interval"]
                    self.__log.debug("[CONFIG] : 'interval' configuration loaded")

                    self.database_file = configuration["database_file"]
                    self.__log.debug("[CONFIG] : 'database_file' configuration loaded")

                    self.chrome_data_dir = configuration["chrome_data_dir"]
                    self.__log.debug(
                        "[CONFIG] : 'chrome_data_dir' configuration loaded"
                    )

                    self.queries = configuration["queries"]
                    self.__log.debug("[CONFIG] : 'queries' configuration loaded")

                    self.job_title_expressions = configuration["job_title_expressions"]
                    self.__log.debug(
                        "[CONFIG] : 'job_title_expressions' configuration loaded"
                    )

                    self.discord_token = configuration["discord_token"]
                    self.__log.debug("[CONFIG] : 'discord_token' configuration loaded")

                    self.discord_channel_id = configuration["discord_channel_id"]
                    self.__log.debug(
                        "[CONFIG] : 'discord_channel_id' configuration loaded"
                    )
                else:
                    self.__log.critical(
                        f"[CONFIG] : '{configuration_file}' is not valid!"
                    )

            self.__log.info(
                f"[CONFIG] : Configuration '{configuration_file}' loaded successfully"
            )
            return

        except YAMLError as E:
            self.__log.critical(
                f"[CONFIG] : Issue processing yaml configuration file.\nException Information: {E}"
            )
        except FileNotFoundError:
            self.__log.error(
                f"[CONFIG] : '{configuration_file}' was not found. Proceeding to generate a configuration file at the specified location."
            )
            self.__generate_configuration(configuration_file)
            self.__load_configuration(configuration_file)
        except PermissionError:
            self.__log.critical(
                f"[CONFIG] : Failed to access '{configuration_file}' (check file permissions)"
            )
        except IsADirectoryError:
            self.__log.critical(
                f"[CONFIG] : '{configuration_file} is a directory, not a file."
            )
        except IOError as E:
            self.__log.critical(
                f"[CONFIG] : An I/O error occurred.\nException Information: {E}"
            )
        except UnicodeDecodeError:
            self.__log.critical(
                f"[CONFIG] '{configuration_file}' has invalid encoding (unicode decode error)"
            )
        except Exception as E:
            self.__log.critical(
                f"[CONFIG] Unknown exception has occured. Consider opening a github issue.\nException Information: {E}"
            )

    def __save_configuration(
        self, configuration_file: str, configuration_data: str
    ) -> None:
        try:
            with open(configuration_file, mode="w") as data_stream:
                data_stream.write(configuration_data)
            self.__log.debug(f"Saved configuration to '{configuration_file}'.")

        except PermissionError:
            self.__log.critical(
                f"[CONFIG] : Failed to access '{configuration_file}' (check file permissions)"
            )
        except IsADirectoryError:
            self.__log.critical(
                f"[CONFIG] : '{configuration_file} is a directory, not a file."
            )
        except IOError as E:
            self.__log.critical(
                f"[CONFIG] : An I/O error occurred.\nException Information: {E}"
            )
        except UnicodeDecodeError:
            self.__log.critical(
                f"[CONFIG] '{configuration_file}' has invalid encoding (unicode decode error)"
            )
        except Exception as E:
            self.__log.critical(
                f"[CONFIG] Unknown exception has occured. Consider opening a github issue.\nException Information: {E}"
            )

    def __generate_configuration(self, configuration_file: str) -> None:
        self.__log.info(
            f"[CONFIG] : Generating new configuration file ({configuration_file})"
        )
        configuration_data = """---
sources:
  linkedin: True
destinations:
  discrd: True
interval: 10
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
                "keysrules": {"type": "string"},
                "valuesrules": {"type": "boolean"},
            },
            "destinations": {
                "required": True,
                "type": "dict",
                "keysrules": {"type": "string"},
                "valuesrules": {"type": "boolean"},
            },
            "interval": {"required": True, "type": "integer"},
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
