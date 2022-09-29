import nextcord
import os
import asyncio
import traceback

from nextcord.ext import commands, tasks

from helpers.config import DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, TOKEN, VERSION
from helpers.embedder import EmbedBuilder
from helpers.logger import Logger
from db import *

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
				label = "Moderation", description = "/help Moderation"
			),
			nextcord.SelectOption(
				label = "League Of Legends", description = "/help League Of Legends"
			),
			nextcord.SelectOption(
				label = "Music", description = "/help Music"
			),
			nextcord.SelectOption(
				label = "Variety", description = "/help Variety"
			),
			nextcord.SelectOption(
				label = "ModLog", description = "/help ModLog"
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
async def get_modules(interaction: nextcord.Interaction, module: str):
	modules = [bot.get_cog("Moderation"), bot.get_cog("League Of Legends"), bot.get_cog("Music"), bot.get_cog("Variety"), bot.get_cog("ModLog")]
	if not module:
		await interaction.response.send_autocomplete([module_.__cog_name__ for module_ in modules])
		return
	
	await interaction.response.send_autocomplete([module_.__cog_name__ for module_ in modules if module_.__cog_name__.lower().startswith(module.lower())])

# Guild Join Event
@bot.event
async def on_guild_join(guild: nextcord.Guild):
	logger.info(f"Joined guild {guild.name} ({guild.id}).")
	builder = EmbedBuilder(bot)

	await add_guild(guild.id)
	logger.info("Added guild to database.")

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
	await bot.change_presence(activity = nextcord.Game(name = "Moved to slash commands!"))	
	await asyncio.sleep(10)

# Run Bot
bot.run(TOKEN)