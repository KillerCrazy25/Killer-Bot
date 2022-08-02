import discord, os, asyncio
from discord.ext import commands, bridge

from utils.config import DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, TOKEN

from datetime import datetime
from pytz import timezone

intents = discord.Intents.all()

bot = bridge.Bot(command_prefix = commands.when_mentioned_or(PREFIX), intents = intents, help_command = None)

# Ready Event

@bot.event
async def on_ready():
	print(f"Bot is ready as {bot.user}")
	await bot.change_presence(activity = discord.Game(name = "Use k!help to see all my commands!"))
	
# Load Command

@bot.bridge_command(description = "Load extension.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def load(ctx : bridge.BridgeContext, extension : str):
	if ctx.author.id == DEVELOPER_ID:
		try:
			bot.load_extension(f"cogs.{extension}")
			await ctx.respond(f"Successfully loaded `{extension}`!")
		except Exception as e:
			await ctx.respond(f"Error loading `{extension}`!\n{e}")
	else:
		await ctx.respond(f"You are not the developer of this bot!")

# Unload Command

@bot.bridge_command(description = "Unload extension.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def unload(ctx : bridge.BridgeContext, extension : str):
	if ctx.author.id == DEVELOPER_ID:
		try:
			bot.unload_extension(f"cogs.{extension}")
			await ctx.respond(f"Successfully unloaded `{extension}`!")
		except Exception as e:
			await ctx.respond(f"Error unloading `{extension}`!\n{e}")
	else:
		await ctx.respond(f"You are not the developer of this bot!")

# Reload Command

@bot.bridge_command(description = "Reload extension.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def reload(ctx : bridge.BridgeContext, extension : str):
	if ctx.author.id == DEVELOPER_ID:
		try:
			await ctx.defer()
			bot.unload_extension(f"cogs.{extension}")
			await asyncio.sleep(3)
			bot.load_extension(f"cogs.{extension}")
			await ctx.respond(f"Successfully reloaded `{extension}`!")
		except Exception as e:
			await ctx.respond(f"Error reloading `{extension}`!\n{e}")
	else:
		await ctx.respond(f"You are not the developer of this bot!")

# Load All Cogs 

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
		print(f"{filename} has been enabled.")

# Help View

class HelpDropdown(discord.ui.View):

	# Help Dropdown Constructor

	def __init__(self, user):
		self.user = user
		super().__init__(timeout = 600)

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True

		await self.message.edit(view = self)

	# Select Menu

	@discord.ui.select(
		placeholder = "Choose your help page",
		min_values = 1,
		max_values = 1,
		options = [
			discord.SelectOption(
				label = "Moderation", description = f"`{PREFIX}help moderation`"
			),
			discord.SelectOption(
				label = "League Of Legends", description = f"`{PREFIX}help lol`"
			),
			discord.SelectOption(
				label = "Music", description = f"`{PREFIX}help music`"
			),
		],
	)

	# Select Menu Callback

	async def help_callback(self, select, interaction: discord.Interaction):
		if interaction.user.id != self.user.id:
			embed = discord.Embed(
				description = "This is not for you!",
				color = discord.Color.red(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			return await interaction.response.send_message(embed = embed, ephemeral = True)
		select.placeholder = f"{select.values[0]} Help Page"
		if select.values[0] == "Moderation":
			embed = discord.Embed(
				title = f"Moderation Commands:",
				color = discord.Color.blurple(),
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
					name = f"`{PREFIX}{command.name}`",
					value = description,
					inline = False
				)
			await interaction.response.edit_message(embed = embed, view = self)
		elif select.values[0] == "League Of Legends":
			embed = discord.Embed(
				title = f"League Of Legends Commands:",
				color = discord.Color.blurple(),
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
					name = f"`{PREFIX}{command.name}`",
					value = description,
					inline = False
				)
			await interaction.response.edit_message(embed = embed, view = self)
		elif select.values[0] == "Music":
			embed = discord.Embed(
				title = f"Music Commands:",
				color = discord.Color.blurple(),
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
					name = f"`{PREFIX}{command.name}`",
					value = description,
					inline = False
				)
			await interaction.response.edit_message(embed = embed, view = self)

	# Close Button

	@discord.ui.button(
		label = "Close",
		style = discord.ButtonStyle.red
	)
	async def close_callback(self, button, interaction : discord.Interaction):
		if interaction.user.id != self.user.id:
			embed = discord.Embed(
				description = "This is not for you!",
				color = discord.Color.red(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			).set_author(
				name = "Killer Bot | Help",
				icon_url = bot.user.avatar.url
			)
			return await interaction.response.send_message(embed = embed, ephemeral = True)

		await interaction.response.send_message("Closed help menu!", ephemeral = True)
		await interaction.message.delete()

# Help Command

@bot.group(invoke_without_command = True)
async def help(ctx):
	view = HelpDropdown(ctx.author)
	embed = discord.Embed(
		title = f"Help",
		color = discord.Color.blurple(),
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
		text = f"Requested by {ctx.author}",
		icon_url = f"{ctx.author.avatar.url}",
	)
	await ctx.respond(embed = embed, view = view)

# Moderation Argument

@help.command()
async def moderation(ctx : bridge.BridgeContext):
	view = HelpDropdown(ctx.author)
	embed = discord.Embed(
		title=f"Moderation Commands:",
		color = discord.Color.blurple(),
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
			name = f"`{PREFIX}{command.name}`",
			value = description,
			inline = False
		)
	await ctx.respond(embed = embed, view = view)

# League of Legends Argument

@help.command()
async def lol(ctx : bridge.BridgeContext):
	view = HelpDropdown(ctx.author)
	embed = discord.Embed(
		title=f"League Of Legends Commands:",
		color = discord.Color.blurple(),
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
			name = f"`{PREFIX}{command.name}`",
			value = description,
			inline = False
		)
	await ctx.respond(embed = embed, view = view)

# Music Argument

@help.command()
async def music(ctx : bridge.BridgeContext):
	view = HelpDropdown(ctx.author, ctx.message)
	embed = discord.Embed(
		title = f"Music Commands:",
		color = discord.Color.blurple(),
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
			name = f"`{PREFIX}{command.name}`",
			value = description,
			inline = False
		)
	await ctx.respond(embed = embed, view = view)

# Run Bot

bot.run(TOKEN)