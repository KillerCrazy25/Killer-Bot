import nextcord
import os
import asyncio
import traceback

from nextcord.ext import commands, tasks

from helpers.config import DEBUG_CHANNEL_ID, DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, TOKEN, VERSION
from helpers.embedder import EmbedBuilder
from helpers.logger import Logger
from db import *

from datetime import datetime
from pytz import timezone

bot = commands.Bot(command_prefix = commands.when_mentioned_or(PREFIX), intents = nextcord.Intents.all())
logger = Logger()

# Ready Event
@bot.event
async def on_ready():
	logger.info(f"Bot is ready as {bot.user}")
	await create_tables()
	await change_presence_task.start()

# Help View
class HelpDropdown(nextcord.ui.View):

	# Help Dropdown Constructor
	def __init__(self):
		super().__init__(timeout = 600)
		self.add_item(nextcord.ui.Button(label = "Support Server", url = "https://discord.gg/3WkeV2tNas"))
		self.add_item(nextcord.ui.Button(label = "Source Code", url = "https://github.com/KillerCrazy25/Killer-Bot"))

	# Timeout Handler
	async def on_timeout(self):
		for child in self.children:
			child.disabled = True

		await self.message.edit(view = self)

	# Select Menu
	@nextcord.ui.select(
		placeholder = "Choose your help page",
		min_values = 1,
		max_values = 1,
		options = [
			nextcord.SelectOption(
				label = "Main Page",
				description = "/help"
			),
			nextcord.SelectOption(
				label = "Moderation", description = f"/help Moderation"
			),
			nextcord.SelectOption(
				label = "League Of Legends", description = f"/help League Of Legends"
			),
			nextcord.SelectOption(
				label = "Music", description = f"/help Music"
			),
			nextcord.SelectOption(
				label = "Variety", description = f"/help Variety"
			)
		]
	)

	# Select Menu Callback
	async def help_callback(self, select, interaction: nextcord.Interaction):
		select.placeholder = f"{select.values[0]} Help Page"
		builder = EmbedBuilder(bot)
		if select.values[0] == "Main Page":
			return await interaction.response.edit_message(
				embed = await builder.help_main_page_embed(interaction.user),
				view = self
			)
		embed = await builder.help_modules_page_embed(select.values[0], interaction.user)

		await interaction.response.edit_message(embed = embed, view = self)

# Help Command
@bot.slash_command(name = "help", description = "Shows help message.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def help(
	interaction : nextcord.Interaction,
	module : str = nextcord.SlashOption(
		name = "module",
		description = "Show help of the given module.",
		required = False
	)
):
	if not module:
		view = HelpDropdown()
		builder = EmbedBuilder(bot)
		embed = await builder.help_main_page_embed(interaction.user)

		view.message = await interaction.response.send_message(embed = embed, view = view, ephemeral = True)
	else:
		builder = EmbedBuilder(bot)
		embed = await builder.help_modules_page_embed(module, interaction.user)
		view = HelpDropdown()

		view.message = await interaction.response.send_message(embed = embed, view = view, ephemeral = True)

@help.on_autocomplete("module")
async def get_modules(interaction : nextcord.Interaction, module : str):
	modules = [bot.get_cog("Moderation"), bot.get_cog("League Of Legends"), bot.get_cog("Music"), bot.get_cog("Variety")]
	if not module:
		await interaction.response.send_autocomplete([module.__cog_name__ for module in modules])
		return
	
	await interaction.response.send_autocomplete(
		module_list = [module.__cog_name__ for module in modules if module.__cog_name__ in module.__cog_name__]
	)

# Guilds Command
@bot.slash_command(name = "guilds", description = "Developer only.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def guilds(interaction : nextcord.Interaction):
	if interaction.user.id != DEVELOPER_ID:
		return await interaction.send("You are not the bot developer.")

	await interaction.send("I'm in " + str(len(bot.guilds)) + " guilds\n\n**Guilds**\n" + '\n'.join('Name: ' + guild.name + ' - ' + 'ID: ' + str(guild.id) for guild in bot.guilds))

@bot.slash_command(name = "addguild", description = "test", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def addguild(interaction: nextcord.Interaction):
	await add_guild(interaction.guild.id, interaction.guild.name, None)
	await interaction.send("Success!")

# @bot.event
# async def on_message(message : nextcord.Message):
# 	if message.author.bot:
# 		logger.info("Author is a bot.")
# 		return
# 	if message.guild is None:
# 		logger.info("Message sent in DM.")
# 		return
	
# 	guild = await get_guild(message.guild.id)
# 	if guild is None:
# 		await add_guild(message.guild.id, message.guild.name, message.guild.owner_id)
# 		guild = await get_guild(message.guild.id)
# 		logger.info(f"Added guild {message.guild.name} with ID {message.guild.id}")
# 		return
	
# 	await add_message(message.id, message.author.id, message.content, int(message.created_at.timestamp()))
# 	logger.info("Message added to database.")

# Global Message Command
@bot.slash_command(name = "globalmsg", description = "Sends a global message to all servers the bot is in", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def globalmsg(interaction : nextcord.Interaction, *, message : str = nextcord.SlashOption(
	name = "message",
	description = "The message to send",
	required = True
)):

	if interaction.user.id != DEVELOPER_ID:
		return await interaction.send("You do not have permission to use this command.")

	success = 0
	failed = 0
	owner_success = 0
	owner_failed = 0

	for guild in bot.guilds:
		system_channel = guild.system_channel
		if system_channel:
			await system_channel.send(message)
			success += 1
		else:
			logger.info(f"System channel not found for guild {guild.name} ({guild.id}). Trying to send message to server owner...")
			owner = guild.owner
			failed += 1
			try:
				await owner.send(message)
				owner_success += 1
			except Exception as e:
				logger.info(f"Failed to send message to server owner of guild {guild.name} ({guild.id}): {e}")
				owner_failed += 1

	await interaction.send(f"Sent message to {success} guilds with success!\nFailed to send message to {failed} guilds.\nSent message to {owner_success} guilds with success to server owners!\nFailed to send message to {owner_failed} guilds to server owners.")

# Guild Join Event
@bot.event
async def on_guild_join(guild : nextcord.Guild):
	
	logger.info(f"Joined guild {guild.name} ({guild.id}).")
	builder = EmbedBuilder(bot)

	embed = await builder.guild_join_embed()

	system_channel = guild.system_channel
	if system_channel:
		await system_channel.send(embed = embed)
	else:
		logger.info(f"System channel not found for guild {guild.name} ({guild.id}).")

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
	await bot.change_presence(activity = nextcord.Game(name = "Moving to slash commands!"))	
	await asyncio.sleep(10)
	
# Load Command
@bot.slash_command(name = "load", description = "Load extension.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def load_extension(interaction : nextcord.Interaction, extension : str = nextcord.SlashOption(
	name = "extension",
	description = "The extension to load",
	required = True
)):

	if interaction.user.id != DEVELOPER_ID:
		return await interaction.send("You do not have permission to use this command.")

	try:
		bot.load_extension(f"cogs.{extension}")
		await interaction.send(f"Successfully loaded `{extension}`!")
	except Exception as e:
		await interaction.send(f"Error loading `{extension}`!\n{e}")

# Unload Command
@bot.slash_command(name = "unload", description = "Unload extension.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def unload_extension(interaction : nextcord.Interaction, extension : str = nextcord.SlashOption(
	name = "extension",
	description = "The extension to unload",
	required = True
)):

	if interaction.user.id != DEVELOPER_ID:
		return await interaction.send("You do not have permission to use this command.")

	try:
		bot.unload_extension(f"cogs.{extension}")
		await interaction.send(f"Successfully unloaded `{extension}`!")
	except Exception as e:
		await interaction.send(f"Error unloading `{extension}`!\n{e}")

# Reload Command
@bot.slash_command(name = "reload", description = "Reload extension.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def reload_extension(interaction : nextcord.Interaction, extension : str = nextcord.SlashOption(
	name = "extension",
	description = "The extension to reload",
	required = True
)):

	if interaction.user.id != DEVELOPER_ID:
		return await interaction.send("You are not the bot developer.")

	try:
		bot.reload_extension(f"cogs.{extension}")
		await interaction.send(f"Successfully reloaded `{extension}`!")
	except Exception as e:
		await interaction.send(f"Error reloading `{extension}`!")
		logger.error(e)

# Load All Cogs 
for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		try:
			bot.load_extension(f"cogs.{filename[:-3]}")
			logger.info(f"{filename[:-3].title()} extension has been enabled.")
		except Exception as e:
			logger.error(f"{filename[:-3].title()} extension has failed to load!\n{e}")
			logger.error(traceback.print_exception(e))

# Run Bot
bot.run(TOKEN)