from pathlib import Path
import sys
import importlib
import asyncio
import nest_asyncio


class Modules:

    def __init__(self, configuration, logger, database):
        self.logger = logger
        self.configuration = configuration
        self.database = database
        self.sources = []
        self.destinations = []
        self.unhealthy_sources = []
        self.unhealthy_destinations = []
        self.__load_sources()
        self.__load_destinations()
        self.__check_health()

    def __load_source(self, source_name):

        current_directory = Path(__file__).parent
        sys.path.insert(0, f"{str(current_directory)}/sources")

        source_module = importlib.import_module(source_name)
        if source_module is None:
            self.logger.error(f"failed to load module '{source_name}'.")
            return
        module = getattr(source_module, f"{source_name}".capitalize())(
            self.logger, self.configuration, self.database
        )
        self.sources.append(module)
        self.logger.debug(f"Loaded source '{source_name}'.")
        return

    def __load_sources(self):
        for source_name in self.configuration.sources:
            self.__load_source(source_name)
        self.logger.info("Successfully loaded sources")
        return

    async def run_sources(self):
        tasks = []
        for source in self.sources:
            tasks.append(asyncio.create_task(source.run()))
        await asyncio.gather(*tasks)

    def __load_destination(self, destination_name):

        current_directory = Path(__file__).parent
        sys.path.insert(0, f"{str(current_directory)}/destinations")

        destination_module = importlib.import_module(destination_name)
        if destination_module is None:
            self.logger.error(f"failed to load module '{destination_name}'.")
            return
        module = getattr(destination_module, f"{destination_name}".capitalize())(
            self.logger, self.configuration, self.database
        )
        self.destinations.append(module)
        self.logger.debug(f"Loaded destination '{destination_name}'.")
        return

    def __load_destinations(self):
        for destination_name in self.configuration.destinations:
            self.__load_destination(destination_name)
        self.logger.info("Successfully loaded destinations")
        return

    async def run_destinations(self):
        tasks = []
        for destination in self.destinations:
            tasks.append(asyncio.create_task(destination.run()))
        await asyncio.gather(*tasks)

    def __check_health(self):
        for source in self.sources:
            healthy = source.is_healthy()
            if healthy:
                self.logger.info(f"Source '{source.name}' is healthy.")
            else:
                self.logger.error(f"Source '{source.name}' is not healthy.")
                self.unhealthy_sources.append(str(source.name).lower())
                self.sources.remove(source)

        for destination in self.destinations:
            healthy = destination.is_healthy()
            if healthy:
                self.logger.info(f"Destination '{destination.name}' is healthy.")
            else:
                self.logger.error(f"Destination '{destination.name}' is not healthy.")
                self.unhealthy_destinations.append(str(destination.name).lower())
                self.destinations.remove(destination)
