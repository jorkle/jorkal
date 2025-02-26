from jorkal.types.source import Source
import asyncio


class Indeed(Source):
    def __init__(self, logger, configuration, database):
        super().__init__(logger, configuration, database)
        self.name = "Indeed"

    def __gather_jobs(self):
        pass

    def __authenticate(self):
        pass

    def is_healthy(self):
        return True

    def test(self, message):
        print(message)
        return

    async def run(self):
        await asyncio.sleep(5)
