import discord
import asyncio
from discord.ext import tasks, commands
import nest_asyncio


class JorkalBot(discord.Client):
    def __init__(self, intents, database, configuration, logger):
        super().__init__(intents=intents)
        self.database = database
        self.configuration = configuration

    dintents = discord.Intents.default()
    dintents.message_content = True

    client = commands.Bot(command_prefix="!jorkal", intents=dintents)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.new_jobs.start()

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def new_jobs(self):
        jobs = await self.database.get_jobs("discord")
        if len(jobs.postings) > 0:
            for job in jobs.postings:
                await self.post_job(
                    job.title,
                    job.company,
                    job.location,
                    job.link,
                    job.source,
                )

    async def post_job(self, title, company, location, link, source):
        channel = self.get_channel(int(self.configuration.discord_channel_id))

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

        await channel.send(content=f"**New Job Posting** *({source})*", embed=embed)

    @new_jobs.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    @client.event
    async def on_ready(ctx):
        print(f"Jorkal Jobs is online!")

    # @client.event
    # async def on_message(message):
    # if message.author == client.user:
    # return

    # if message.content.startswith("!jorkal"):
    # if message.content.startswith("!jorkal query add")


class Discrd:
    def __init__(self, logger, configuration, database):
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

    def is_healthy(self):
        return self.__is_healthy

    async def run(self):
        nest_asyncio.apply()
        self.client.run(self.configuration.discord_token)
