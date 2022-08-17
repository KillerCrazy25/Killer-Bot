import nextcord, os, asyncio
from nextcord.ext import commands, tasks, help_commands

from helpers.config import DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, TOKEN

from datetime import datetime
from pytz import timezone

intents = nextcord.Intents.all()

bot = commands.Bot(command_prefix = commands.when_mentioned_or(PREFIX), intents = intents, help_command = None)

# Ready Event

@bot.event
async def on_ready():
	print(f"Bot is ready as {bot.user}")
	await change_presence_task.start()

# Change Presence Task

@tasks.loop(seconds = 10)
async def change_presence_task():
	await bot.change_presence(activity = nextcord.Game(name = "Use k!help to see all my commands!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Game(name = "Write me on DM to send a message to moderators!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"{len(bot.guilds)} servers!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Activity(type = nextcord.ActivityType.watching, name = f"{len(bot.users)} users!"))
	await asyncio.sleep(5)
	await bot.change_presence(activity = nextcord.Game(name = "Support Server: https://discord.gg/3WkeV2tNas"))	
	
# Load Command

@bot.command(description = "Load extension.")
async def load(ctx : commands.Context, extension : str):
	if ctx.author.id == DEVELOPER_ID:
		try:
			bot.load_extension(f"cogs.{extension}")
			await ctx.send(f"Successfully loaded `{extension}`!")
		except Exception as e:
			await ctx.send(f"Error loading `{extension}`!\n{e}")
	else:
		await ctx.send(f"You are not the developer of this bot!")

# Unload Command

@bot.command(description = "Unload extension.")
async def unload(ctx : commands.Context, extension : str):
	if ctx.author.id == DEVELOPER_ID:
		try:
			bot.unload_extension(f"cogs.{extension}")
			await ctx.send(f"Successfully unloaded `{extension}`!")
		except Exception as e:
			await ctx.send(f"Error unloading `{extension}`!\n{e}")
	else:
		await ctx.send(f"You are not the developer of this bot!")

# Reload Command

@bot.command(description = "Reload extension.")
async def reload(ctx : commands.Context, extension : str):
	if ctx.author.id == DEVELOPER_ID:
		try:
			await ctx.defer()
			bot.unload_extension(f"cogs.{extension}")
			await asyncio.sleep(3)
			bot.load_extension(f"cogs.{extension}")
			await ctx.send(f"Successfully reloaded `{extension}`!")
		except Exception as e:
			await ctx.send(f"Error reloading `{extension}`!\n{e}")
	else:
		await ctx.send(f"You are not the developer of this bot!")

# Load All Cogs 

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
		print(f"{filename} has been enabled.")

# Help View

class HelpDropdown(nextcord.ui.View):

	# Help Dropdown Constructor

	def __init__(self, user):
		super().__init__(timeout = 600)
		self.user = user
		self.add_item(nextcord.ui.Button(label = "Support Server", url = "https://discord.gg/3WkeV2tNas"))
		self.add_item(nextcord.ui.Button(label = "Source Code", url = "https://github.com/KillerCrazy25/Killer-Bot"))

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

@bot.group(invoke_without_command = True)
async def help(ctx):
	view = HelpDropdown(ctx.author)
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
		text = f"Requested by {ctx.author}",
		icon_url = f"{ctx.author.avatar.url}",
	)
	view.message = await ctx.send(embed = embed, view = view)

# Moderation Argument

@help.command()
async def moderation(ctx : commands.Context):
	view = HelpDropdown(ctx.author)
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
	view.message = await ctx.send(embed = embed, view = view)

# League of Legends Argument

@help.command()
async def lol(ctx : commands.Context):
	view = HelpDropdown(ctx.author)
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
	view.message = await ctx.send(embed = embed, view = view)

# Music Argument

@help.command()
async def music(ctx : commands.Context):
	view = HelpDropdown(ctx.author, ctx.message)
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
	view.message = await ctx.send(embed = embed, view = view)

# Run Bot

bot.run(TOKEN)