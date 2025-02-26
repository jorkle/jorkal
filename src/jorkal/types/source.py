from jorkal.types.jobs import Jobs


class Source:
    def __init__(self, logger, configuration, database):
        self.logger = logger
        self.database = database
        self.configuration = configuration
        self.jobs = Jobs()
        self.name = None

    async def run(self):
        # TODO: Implement functionality
        pass
