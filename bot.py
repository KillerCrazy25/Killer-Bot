import asyncio
from asyncio import subprocess
import discord, os
from discord.ext import commands, bridge

from utils.config import DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, TOKEN

from datetime import datetime
from pytz import timezone

intents = discord.Intents.all()

bot = bridge.Bot(command_prefix = commands.when_mentioned_or(PREFIX), intents = intents, help_command = None)

@bot.event
async def on_ready():
	print(f"Bot is ready as {bot.user}")
	await bot.change_presence(activity = discord.Game(name = "Use k!help to see all my commands!"))

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
		print(f"{filename} has been enabled.")

class HelpDropdown(discord.ui.View):
	def __init__(self, user):
		self.user = user
		super().__init__(timeout = None)

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
			for index, command in enumerate(bot.get_cog("ModerationCommands").get_commands()):
				description = command.description
				if not description or description is None or description == "":
					description = "No description"
				embed.add_field(
					name = f"`{PREFIX}{command.name}`",
					value = description,
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
				)
			await interaction.response.edit_message(embed = embed, view = self)

	@discord.ui.button(
		label = "Close",
		style = discord.ButtonStyle.red
	)
	async def close_callback(self, button, interaction : discord.Interaction):
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

@help.command()
async def moderation(ctx):
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
		)
	await ctx.respond(embed = embed, view = view)

@help.command()
async def lol(ctx):
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
		)
	await ctx.respond(embed = embed, view = view)

@help.command()
async def music(ctx):
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
		)
	await ctx.respond(embed = embed, view = view)

bot.run(TOKEN)