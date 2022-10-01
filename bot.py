import nextcord
import os
import asyncio
import traceback

from nextcord.ext import commands, tasks

from helpers.config import PREFIX, TOKEN
from helpers.embedder import EmbedBuilder
from helpers.logger import Logger

from db import create_guild, remove_guild, create_tables

bot = commands.Bot(command_prefix = commands.when_mentioned_or(PREFIX), intents = nextcord.Intents.all())
logger = Logger()

# Ready Event
@bot.event
async def on_ready():
	logger.info(f"Bot is ready as {bot.user}")
	await create_tables()
	await change_presence_task.start()

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		try:
			bot.load_extension(f"cogs.{filename[:-3]}")
			logger.info(f"{filename[:-3].title()} extension has been enabled.")
		except Exception as e:
			logger.error(f"{filename[:-3].title()} extension has failed to load!\n{e}")
			logger.error(traceback.print_exception(e))

# Guild Join Event
@bot.event
async def on_guild_join(guild: nextcord.Guild):
	logger.info(f"Joined guild {guild.name} ({guild.id}).")
	builder = EmbedBuilder(bot)

	await create_guild(guild.id)
	logger.info("Added guild to database.")

	embed = await builder.guild_join_embed()

	system_channel = guild.system_channel
	if system_channel:
		await system_channel.send(embed = embed)
	else:
		logger.info(f"System channel not found for guild {guild.name} ({guild.id}).")

@bot.event
async def on_guild_remove(guild: nextcord.Guild):
	logger.info(f"Left guild {guild.name} ({guild.id}).")
	await remove_guild(guild.id)
	logger.info("Removed guild from database.")

# Change Presence Task
@tasks.loop(seconds = 10)
async def change_presence_task():
	await bot.change_presence(activity = nextcord.Game(name = "Use /help to see all my commands!"))
	await asyncio.sleep(10)
	await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"{len(bot.guilds)} servers!"))
	await asyncio.sleep(10)
	await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"{len(bot.users)} users!"))
	await asyncio.sleep(10)
	await bot.change_presence(activity = nextcord.Game(name = "Support Server: https://discord.gg/3WkeV2tNas"))	
	await asyncio.sleep(10)
	await bot.change_presence(activity = nextcord.Game(name = "Moved to slash commands!"))	
	await asyncio.sleep(10)

# Run Bot
bot.run(TOKEN)