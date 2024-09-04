import asyncio
import os

import discord
import nest_asyncio
from discord.ext import commands
from dotenv import load_dotenv

from jorkal.minecraft import Minecraft

load_dotenv()

server_online = False


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)


async def wrapped_bot_start():

    await bot.load_extension("jorkal.spoogles")
    discord_token = os.environ.get("DISCORD_TOKEN")
    await bot.run(discord_token)


async def background():
    while True:
        global server_online
        if server_online is False:
            await asyncio.sleep(60)
            continue
        minecraft_host = os.environ.get("MINECRAFT_HOST")
        rcon_password = os.environ.get("MINECRAFT_RCON_PASSWORD")
        minecraft = Minecraft(minecraft_host, rcon_password)
        player_count_before = minecraft.get_player_count()
        await asyncio.sleep(1200)
        player_count_after = minecraft.get_player_count()
        if player_count_before == "0" and player_count_after == "0":
            minecraft.stop()
            server_online = False


nest_asyncio.apply()


async def start():
    await asyncio.gather(wrapped_bot_start(), background())


def main():
    asyncio.run(start())
