import discord
from discord.ext import tasks, commands
import nest_asyncio

from jorkal.database import Database
from jorkal.log import Log
from jorkal.config import Configuration


class JorkalBot(discord.Client):
    """
    Discord bot class (using discord.py). Discord Commands and tasks are defined here.
    """

    def __init__(self, intents, database, configuration, logger):
        super().__init__(intents=intents)
        self.database = database
        self.logger = logger
        self.configuration = configuration

    # defien the intents for the command.Bot() usage
    _intents = discord.Intents.default()
    _intents.message_content = True

    # register "!jorkal" discord command prefix
    client = commands.Bot(command_prefix="!jorkal", intents=_intents)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.new_jobs.start()

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def new_jobs(self) -> None:
        """
        Query the database for new jobs and post them to the discord channel.
        """

        # get new jobs from all sources that have not been notified through the discord destination module yet.
        jobs = await self.database.get_jobs("discrd", only_unseen=True, source=None)
        if len(jobs.postings) > 0:
            for job in jobs.postings:
                await self.__post_job(
                    job.title,
                    job.company,
                    job.location,
                    job.link,
                    job.source,
                )

    async def __post_job(
        self, title: str, company: str, location: str, link: str, source: str
    ) -> None:

        # defines the channel using the "discord_channel_id" from the configuration file
        channel = self.get_channel(int(self.configuration.discord_channel_id))

        # creates the embed message for the discord post.
        embed = discord.Embed(
            title=f"{title} @ {company} ({location})",
            colour=discord.Colour(0x8EE647),
            url=f"{link}",
        )

        embed.set_thumbnail(url="https://jorkle.com/images/profile.jpg")
        embed.set_author(
            name="Jorkal Jobs",
            url="https://github.com/jorkle/jorkal",
            icon_url="https://jorkle.com/images/profile.jpg",
        )

        # posts the embed message to the discord channel
        await channel.send(  # pyright: ignore
            content=f"**New Job Posting** *({source})*", embed=embed
        )

    @new_jobs.before_loop
    async def before_my_task(self) -> None:
        await self.wait_until_ready()  # wait until the bot logs in

    @client.event
    async def on_ready(ctx) -> None:
        print("Jorkal Jobs is online!")


class Discrd:
    def __init__(self, logger: Log, configuration: Configuration, database: Database):
        self.configuration = configuration
        self.logger = logger
        self.database = database
        self.__is_healthy = True
        self.name = "Discord"
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.client = JorkalBot(
            discord.Intents.default(), self.database, self.configuration, self.logger
        )

    def is_healthy(self) -> bool:
        """
        Returns the health status of the discord destination module.
        """
        return self.__is_healthy

    async def run(self) -> None:
        """
        Triggers the execution of the discord destination module.
        """
        nest_asyncio.apply()
        self.client.run(self.configuration.discord_token)
