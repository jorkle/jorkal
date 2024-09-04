import asyncio
import os

from discord.ext import commands
from dotenv import load_dotenv
from minecraft import Minecraft

load_dotenv()


# This is the Spoogles cog. It is a collection of commands that can be used to interact with the Minecraft server.
class Spoogles(commands.Cog):

    # The __init__ method is a special method that is called when an object is created. In this case, it is called when the Spoogles cog is created.
    def __init__(self, bot):

        self.host = os.genenv(
            "MINECRAFT_HOST"
        )  # This is the IP address of the Minecraft server.
        self.rcon_password = os.getenv(
            "MINECRAFT_RCON_PASSWORD"
        )  # This is the RCON password of the Minecraft server.
        self.minecraft = Minecraft(
            self.host, self.rcon_password
        )  # This is an instance of the Minecraft class that is used to interact with the Minecraft server.
        self.latch = False  # This latch is used to prevent multiple commands from running at the same time.
        self.server_online = False  # This variable is used to keep track of whether the Minecraft server is online or not.
        self.bot = bot

    # The on_ready method is a special method that is called when the bot is
    # ready to start receiving commands.
    async def on_ready(ctx):
        print("Spoogles MC Bot is online and awaiting instructions")

    # 'spoogles' function handles discord command invocations.
    # Different commands can be invoked by passing different arguments
    # to the 'spoogles' function.
    @commands.command(pass_context=True)
    async def spoogles(self, ctx, *args):

        if (
            self.latch
        ):  # if a command is already running, notify via discord and return.
            await ctx.send(
                "A command is already running. Please wait a few minutes before running another command."
            )
            return

        if (
            len(args) == 0
        ):  # if the '$spoogles' command is invoked via discord with no arguments, notify the user that an argument is required.
            await ctx.send("You need to provide an argument")

        elif (
            len(args) == 1
        ):  # if the '$spoogles' command is invoked via discord with one argument, check the argument and execute the corresponding command.
            if args[0] == "start":
                if (
                    self.server_online is True
                ):  # verify that the server is not already online.
                    await ctx.send("The Minecraft Server is already online")
                    return
                self.latch = True  # set the latch to True to prevent multiple commands from running at the same time.
                await ctx.send(
                    "Starting Minecraft Server"
                )  # notify via discord that the server is starting.
                self.minecraft.start()  # start the Minecraft server.
                await ctx.send(
                    "Taking a five minute nap while the Minecraft server boots up. Zzzzzz "
                )  # notify via discord that the server is booting up.
                await asyncio.sleep(300)  # wait for 5 minutes.
                self.latch = (
                    False  # set the latch to False to allow other commands to run.
                )
                self.minecraft._connect()  # establish an rcon session to the Minecraft server.
                ctx.send(
                    "The Minecraft Server is online"
                )  # notify via discord that the server is online.
                self.server_online = True
                return

            elif (
                args[0] == "stop"
            ):  # if the '$spoogles stop' command is invoked via discord, check if the server is online and stop the server.
                if self.server_online is False:  # verify that the server is online.
                    await ctx.send("The Minecraft Server is not online")
                    return
                self.latch = True  # set the latch to True to prevent multiple commands from running at the same time.
                await ctx.send("Stopping the Minecraft Server. Goodbye!")
                self.minecraft.stop()  # stop the Minecraft server.
                await asyncio.sleep(60)  # wait for 1 minute.
                self.latch = (
                    False  # set the latch to False to allow other commands to run.
                )
                self.server_online = False  # set the server_online variable to False to indicate that the server is offline.
                return

            elif (
                args[0] == "players"
            ):  # if the '$spoogles players' command is invoked via discord, check if the server is online and get the list of online players.
                if self.server_online is False:  # verify that the server is online.
                    await ctx.send("The Minecraft Server is not online")
                    return
                await ctx.send("Checking Minecraft Server Players")
                online_players = (
                    self.minecraft.get_online_players()
                )  # get the list of online players.
                if (
                    len(online_players) == 0
                ):  # if there are no players online, notify via discord.
                    await ctx.send("There are no players online")
                else:
                    online_players = ", ".join(
                        [item.encode("utf-8") for item in online_players]
                    )  # convert the list of online players to a string.
                    await ctx.send(f"Players online: {online_players}")
                return

            elif (
                args[0] == "info"
            ):  # if the '$spoogles info' command is invoked via discord, provide information about the Minecraft server.
                if self.server_online is False:  # verify that the server is online.
                    await ctx.send("The Minecraft Server is not online")
                    return
                await ctx.send(
                    f"host: {self.host}:25565\nwhitelist command: '$spoogles whitelist add/remove <username>'"
                )
                return
            elif args[0] == "help":
                await ctx.send(
                    "Available commands: start, stop, players, info, time, weather, whitelist\n - '$spoogles start'\n - '$spoogles stop'\n - '$spoogles players'\n - '$spoogles info'\n - '$spoogles time <day/night>'\n - '$spoogles weather <clear/rain>'\n - '$spoogles whitelist <add/remove> <username>'"
                )
                return

        elif (
            len(args) == 2
        ):  # if the '$spoogles' command is invoked via discord with two arguments, check the arguments and execute the corresponding command.
            if self.server_online is False:  # verify that the server is online.
                await ctx.send("The Minecraft Server is not online")
                return
            if (
                args[0] == "time"
            ):  # if the '$spoogles time' command is invoked via discord, set the time of the Minecraft server.
                if (
                    args[1] == "day"
                ):  # if the time is set to 'day', set the time of the Minecraft server to day.
                    await ctx.send("Setting Minecraft Server to Day Time")
                    self.minecraft.set_time(
                        "day"
                    )  # set the time of the Minecraft server to day.
                if args[1] == "night":
                    await ctx.send("Setting Minecraft Server to Night Time")
                    self.minecraft.set_time(
                        "night"
                    )  # set the time of the Minecraft server to night.

            elif (
                args[0] == "weather"
            ):  # if the '$spoogles weather' command is invoked via discord, set the weather of the Minecraft server.
                if (
                    args[1] == "clear"
                ):  # if the weather is set to 'clear', set the weather of the Minecraft server to clear.
                    self.minecraft.set_weather("clear")
                    await ctx.send("Setting Minecraft Server Weather to Clear")
                elif (
                    args[1] == "rain"
                ):  # if the weather is set to 'clear', set the weather of the Minecraft server to clear.
                    self.minecraft.set_weather("rain")
                    await ctx.send("Setting Minecraft Server Weather to Rain")

        elif (
            len(args) == 3
        ):  # if the '$spoogles' command is invoked via discord with three arguments, check the arguments and execute the corresponding command.
            if self.server_online is False:  # verify that the server is online.
                await ctx.send("The Minecraft Server is not online")
                return
            if (
                args[0] == "whitelist"
            ):  # if the '$spoogles whitelist' command is invoked via discord, add or remove a player from the whitelist.
                if (
                    args[1] == "add"
                ):  # if the player is being added to the whitelist, add the player to the whitelist.
                    self.minecraft.whitelist("add", args[2])
                    await ctx.send(f"Adding {args[2]} to Minecraft Server Whitelist")
                if (
                    args[1] == "remove"
                ):  # if the player is being removed from the whitelist, remove the player from the whitelist.
                    self.minecraft.whitelist("remove", args[2])
                    await ctx.send(
                        f"Removing {args[2]} from Minecraft Server Whitelist"
                    )


async def setup(bot):
    await bot.add_cog(Spoogles(bot))
