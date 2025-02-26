import logging
import sys
import os


class Log:
    def __init__(self, log_level, log_file):
        if "logs/" in log_file and not os.path.isdir("logs"):
            os.mkdir("logs")
        self.log_level = log_level
        level = self.get_log_level(log_level)
        logging.basicConfig(
            filename=log_file,
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger()

    def debug(self, message: str):
        """debug() verifies that the log level is equal to 0 (DEBUG).
        If the current log level is equal to 0 (DEBUG), then a log entry is written to the log file and a message is printed to STDOUT.


        Args:
            message: debug message
        """
        if self.log_level == 0:
            print(f"DEBUG: {message}", file=sys.stdout)
            self.logger.debug(message)

    def info(self, message: str):
        """info() verifies that the log level is less than or equal to 1 (INFO).
        If the current log level is less than or equal to 1 (INFO), then a log entry is written to the log file and a message is printed to STDOUT.


        Args:
            message: info message
        """
        self.logger.info(message)
        if self.log_level <= 1:
            print(f"INFO: {message}")

    def error(self, message: str):
        """error() verifies that the log level is less than or equal to 2 (ERROR).
        If the current log level is less than or equal to 2 (ERROR), then a log entry is written to the log file and a message is printed to STDERR.


        Args:
            message: error message
        """
        self.logger.error(message)
        if self.log_level <= 2:
            print(f"ERROR: {message}")

    def critical(self, message: str):
        """critical() verifies that the log level is less than or equal to 3 (CRITICAL).
        If the current log level is less than or equal to 3 (CRITICAL), then a log entry is written to the log file, a message is printed to STDERR, and the application exits with an exit status of 1.


        Args:
            message: critical message
        """
        self.logger.critical(message)
        if self.log_level <= 3:
            print(f"CRITICAL: {message}")
            sys.exit(1)

    def get_log_level(self, log_level: int):
        match log_level:
            case 0:
                return logging.DEBUG
            case 1:
                return logging.INFO
            case 2:
                return logging.ERROR
            case 3:
                return logging.CRITICAL
            case _:
                return logging.DEBUG
