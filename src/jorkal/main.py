from datetime import datetime
from argparse import Namespace, ArgumentParser
import asyncio

import nest_asyncio

from jorkal.config import Configuration
from jorkal.log import Log
from jorkal.modules.loader import Modules
from jorkal.database import Database

global modules


def __description() -> str:
    description = """
    Jorkal is a tool to monitor websites for new job postings and notify you when a new job is posted.
    """
    return description


def __usage() -> str:
    usage = """
    jorkal --config config.yaml
    """

    return usage


def __gather_args():
    parser = ArgumentParser(description=__description(), usage=__usage())

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Configuration file to use",
        default="config.yaml",
        required=False,
        dest="config_file",
    )
    parser.add_argument(
        "--log-level",
        "-ll",
        type=int,
        default=1,
        choices=[0, 1, 2, 3],
        required=False,
        help="Log Level (DEBUG=0, INFO=1, ERROR=2, CRITICAL=3)",
        dest="log_level",
    )
    parser.add_argument(
        "--log-file",
        "-lf",
        type=str,
        default=datetime.now().strftime("logs/log_%Y%m%d_%H%M%S.log"),
        required=False,
        help="Log File (default=./logs/log_<timestamp>.log)",
        dest="log_file",
    )

    cmd_opts = parser.parse_args()
    return cmd_opts


async def __run_sources():
    await modules.run_sources()


async def __run_destinations():
    await modules.run_destinations()


async def __run_tasks():
    await asyncio.gather(__run_sources(), __run_destinations())


def __init_app(cmd_opts: Namespace) -> None:
    """
    Initializes the logger, configuration, and database.

    Parameters
    ----------
    `cmd_opts` : `argparse.Namespace`
        The command line arguments namespace object returned by `argparse.ArgumentParser.parse_args()` method

    """

    # Initalizes the logger with the log level and log file specified in the command line arguments. If no log file/log level is specified, the default is used.
    logger = Log(cmd_opts.log_level, cmd_opts.log_file)

    # Initializes the configuration with the configuration file specified in the command line arguments.
    # If the specified configuration file doesn't exist, then a configuration file is generated at the provided file location.
    configuration = Configuration(
        {
            "configuration_file": cmd_opts.config_file,
            "log_level": cmd_opts.log_level,
            "log_file": cmd_opts.log_file,
        },
        logger,
    )
    # allow nested asyncio calls.
    nest_asyncio.apply()

    # Initializes the database.
    database = Database(configuration, logger)

    # initializes the source and destination modules. Global variable is used to allow __run_sources() and __run_destinations() to
    # leverage the instance of Modules() without being passed the instance as an argument.
    global modules
    modules = Modules(configuration, logger, database)

    # starts the asyncio event loop to run the sources and destinations.
    asyncio.run(__run_tasks())


def run():
    """Main entry point for the Jorkal application.

    Parameters
    ----------
    None

    Returns
    -------
    None

    Raises
    ------
    None
    """
    cmd_opts = __gather_args()
    __init_app(cmd_opts)


if __name__ == "__main__":
    run()
