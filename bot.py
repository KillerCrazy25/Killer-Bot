import nextcord, os, asyncio

from nextcord.ext import commands, tasks

from helpers.config import DEBUG_CHANNEL_ID, DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, TOKEN, VERSION
from helpers.embed_builder import EmbedBuilder
from helpers.logger import Logger

from datetime import datetime
from pytz import timezone

bot = commands.Bot(command_prefix = commands.when_mentioned_or(PREFIX), intents = nextcord.Intents.all(), help_command = None)
logger = Logger()

# Ready Event
@bot.event
async def on_ready():
	logger.info(f"Bot is ready as {bot.user}")
	await change_presence_task.start()

@bot.slash_command(name = "guilds", description = "Developer only.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def guilds(interaction : nextcord.Interaction):
	if interaction.user.id != DEVELOPER_ID:
		return await interaction.send("You are not the bot developer.")

	await interaction.send("I'm in " + str(len(bot.guilds)) + " guilds\n\n**Guilds**\n" + '\n'.join('Name: ' + guild.name + ' - ' + 'ID: ' + str(guild.id) for guild in bot.guilds))

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
	await bot.change_presence(activity = nextcord.Game(name = "Use k!help to see all my commands!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"{len(bot.guilds)} servers!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"{len(bot.users)} users!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Game(name = "Support Server: https://discord.gg/3WkeV2tNas"))	
	await asyncio.sleep(5)
	
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
		print(e)

# Load All Cogs 
for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
		logger.info(f"{filename} has been enabled.")

# Help View
class HelpDropdown(nextcord.ui.View):

	# Help Dropdown Constructor
	def __init__(self, user):
		super().__init__(timeout = 600)
		self.user = user
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
				label = "Moderation", description = f"`{PREFIX}help moderation`"
			),
			nextcord.SelectOption(
				label = "League Of Legends", description = f"`{PREFIX}help lol`"
			),
			nextcord.SelectOption(
				label = "Music", description = f"`{PREFIX}help music`"
			),
		],
	)

	# Select Menu Callback
	async def help_callback(self, select, interaction: nextcord.Interaction):
		if interaction.user.id != self.user.id:
			embed = nextcord.Embed(
				description = "This is not for you!",
				color = nextcord.Color.red(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			return await interaction.response.send_message(embed = embed, ephemeral = True)
		select.placeholder = f"{select.values[0]} Help Page"
		if select.values[0] == "Moderation":
			embed = nextcord.Embed(
				title = f"Moderation Commands:",
				color = nextcord.Color.blurple(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			for command in bot.get_cog("ModerationCommands").walk_commands():
				description = command.description
				if not description or description is None or description == "":
					description = "No description"
				embed.add_field(
					name = f"`{PREFIX}{command.name} {command.signature}`",
					value = description,
					inline = False
				)
			await interaction.response.edit_message(embed = embed, view = self)
		elif select.values[0] == "League Of Legends":
			embed = nextcord.Embed(
				title = f"League Of Legends Commands:",
				color = nextcord.Color.blurple(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			for command in bot.get_cog("LeagueCommands").walk_commands():
				description = command.description
				if not description or description is None or description == "":
					description = "No description"
				embed.add_field(
					name = f"`{PREFIX}{command.name} {command.signature}`",
					value = description,
					inline = False
				)
			await interaction.response.edit_message(embed = embed, view = self)
		elif select.values[0] == "Music":
			embed = nextcord.Embed(
				title = f"Music Commands:",
				color = nextcord.Color.blurple(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			for command in bot.get_cog("Music").walk_commands():
				description = command.description
				if not description or description is None or description == "":
					description = "No description"
				embed.add_field(
					name = f"`{PREFIX}{command.name} {command.signature}`",
					value = description,
					inline = False
				)
			await interaction.response.edit_message(embed = embed, view = self)

	# Close Button
	@nextcord.ui.button(
		label = "Dismiss",
		style = nextcord.ButtonStyle.red
	)
	async def close_callback(self, button, interaction : nextcord.Interaction):
		if interaction.user.id != self.user.id:
			embed = nextcord.Embed(
				description = "This is not for you!",
				color = nextcord.Color.red(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			return await interaction.response.send_message(embed = embed, ephemeral = True)

		for child in self.children:
			child.disabled = True

		await self.message.edit(view = self)

# Help Command
@bot.slash_command(name = "help", description = "Shows help message.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def help_cmd(interaction : nextcord.Interaction):
	view = HelpDropdown(interaction.user)
	embed = nextcord.Embed(
		title = f"Help",
		color = nextcord.Color.blurple(),
		timestamp = datetime.now(tz = timezone("US/Eastern"))
	).set_author(
		name = "Killer Bot | Help",
		icon_url = bot.user.avatar.url
	)
	embed.set_thumbnail(url = f"{bot.user.avatar.url}")
	embed.add_field(
		name = "Moderation:", value = f"`{PREFIX}help moderation`", inline = False
	)
	embed.add_field(name = "League Of Legends:", value = f"`{PREFIX}help lol`", inline = False)
	embed.add_field(name = "Music:", value = f"`{PREFIX}help music`", inline = False)
	embed.set_footer(
		text = f"Requested by {interaction.user}",
		icon_url = f"{interaction.user.avatar.url}",
	)
	view.message = await interaction.send(embed = embed, view = view)

# Main Command
@bot.slash_command(guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def help(interaction : nextcord.Interaction):
	pass

# Moderation Argument
@help.subcommand(name = "moderation", description = "Shows help message for moderation commands.")
async def moderation(interaction : nextcord.Interaction):
	view = HelpDropdown(interaction.user)
	embed = nextcord.Embed(
		title=f"Moderation Commands:",
		color = nextcord.Color.blurple(),
		timestamp = datetime.now(tz = timezone("US/Eastern"))
	).set_author(
		name = "Killer Bot | Help",
		icon_url = bot.user.avatar.url
	)
	for command in bot.get_cog("ModerationCommands").walk_commands():
		description = command.description
		if not description or description is None or description == "":
			description = "No description"
		embed.add_field(
			name = f"`{PREFIX}{command.name} {command.signature}`",
			value = description,
			inline = False
		)
	view.message = await interaction.send(embed = embed, view = view)

# League of Legends Argument
@help.subcommand(name = "lol", description = "Shows help message for League of Legends commands.")
async def lol(interaction : nextcord.Interaction):
	view = HelpDropdown(interaction.user)
	embed = nextcord.Embed(
		title=f"League Of Legends Commands:",
		color = nextcord.Color.blurple(),
		timestamp = datetime.now(tz = timezone("US/Eastern"))
	).set_author(
		name = "Killer Bot | Help",
		icon_url = bot.user.avatar.url
	)
	for command in bot.get_cog("LeagueCommands").walk_commands():
		description = command.description
		if not description or description is None or description == "":
			description = "No description"
		embed.add_field(
			name = f"`{PREFIX}{command.name} {command.signature}`",
			value = description,
			inline = False
		)
	view.message = await interaction.send(embed = embed, view = view)

# Music Argument
@help.subcommand(name = "music", description = "Shows help message for music commands.")
async def music(interaction : nextcord.Interaction):
	view = HelpDropdown(interaction.user)
	embed = nextcord.Embed(
		title = f"Music Commands:",
		color = nextcord.Color.blurple(),
		timestamp = datetime.now(tz = timezone("US/Eastern"))
	).set_author(
		name = "Killer Bot | Help",
		icon_url = bot.user.avatar.url
	)
	for command in bot.get_cog("Music").walk_commands():
		description = command.description
		if not description or description is None or description == "":
			description = "No description"
		embed.add_field(
			name = f"`{PREFIX}{command.name} {command.signature}`",
			value = description,
			inline = False
		)
	view.message = await interaction.send(embed = embed, view = view)

# Run Bot
bot.run(TOKEN)