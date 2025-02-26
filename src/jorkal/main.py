import sys
import argparse
import asyncio
import nest_asyncio
from datetime import datetime
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
    jorkal --config ./config.yaml
    """
    return usage


def __gather_args():
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())

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


async def __run_discord_bot(configuration, logger, database):
    discord = Discord(configuration, logger, database)
    await discord.run()


async def __gather_tasks(configuration, logger, database):
    await asyncio.gather(__run_sources(), __run_destinations())


def __init_app(cmd_opts) -> None:
    logger = Log(cmd_opts.log_level, cmd_opts.log_file)
    configuration = Configuration(
        {
            "configuration_file": cmd_opts.config_file,
            "log_level": cmd_opts.log_level,
            "log_file": cmd_opts.log_file,
        },
        logger,
    )
    nest_asyncio.apply()
    database = Database(configuration, logger)
    global modules
    modules = Modules(configuration, logger, database)
    asyncio.run(__gather_tasks(configuration, logger, database))


def run():
    cmd_opts = __gather_args()
    __init_app(cmd_opts)


if __name__ == "__main__":
    run()
