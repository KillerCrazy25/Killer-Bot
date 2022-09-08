from nextcord.ext import commands
from nextcord import Embed, Color, Asset, Member

from typing import (
	Optional,
	Union,
	List
)

from helpers.config import *
from datetime import datetime
from pytz import timezone

# ModLogEmbedBuilder Class
class EmbedBuilder:
	
	# ModLogEmbedBuilder Constructor
	def __init__(self, bot : commands.Bot):
		self.bot : commands.Bot = bot

	# Error Embed Builder
	async def error_embed(self) -> Embed:
		"""Returns an error embed."""
		embed = Embed(
			title = "Something went wrong trying to run this command.",
			color = Color.dark_red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.set_author(name = "Killer Bot | Error", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = "This message will be deleted in 10 seconds...")

		return embed

	# Mod Log Embed Builder
	async def mod_log_embed(
		self,
		icon_url: Optional[str],
		color: Union[Color, int],
		title: Optional[str],
		description: str,
		thumbnail: Optional[Union[str, Asset]] = None,
		timestamp: Optional[datetime] = None,
		footer: Optional[str] = None
	) -> Embed:
		"""Returns a mod log embed."""
		embed = Embed(
			description = description[:4093] + "..." if len(description) > 4096 else description
		)

		if title and icon_url:
			embed.set_author(name = title, icon_url = icon_url)

		embed.color = color
		embed.timestamp = timestamp or datetime.now()

		if footer:
			embed.set_footer(text = footer)

		if thumbnail:
			embed.set_thumbnail(url = thumbnail)

		return embed

	# Guild Join Embed Builder
	async def guild_join_embed(self) -> Embed:
		embed = Embed(
			description = "Thanks for adding me to your server!",
			color = Color.dark_purple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)
		embed.set_author(name = self.bot.user, icon_url = self.bot.user.avatar.url)

		embed.add_field(name = "Basic Information", value = f"- Default Prefix: `{PREFIX}`\n- Developer: <@{DEVELOPER_ID}>\n- Bot Version: `{VERSION}`\n\n**IMPORTANT: Remember that the bot is under development and it's not recommended to be used in public servers.**", inline = False)
		embed.add_field(name = "Commands", value = f"You can find all of my commands by using `{PREFIX}help`", inline = False)
		embed.add_field(name = "Links", value = "[Source Code](https://github.com/KillerCrazy25/Killer-Bot/)\n[Invite](https://discord.com/api/oauth2/authorize?client_id=945158875722702878&permissions=8&scope=bot%20applications.commands)\n[Support Server](https://discord.gg/3WkeV2tNas)", inline = False)

		embed.set_footer(text = f"{self.bot.user.name} v{VERSION} | Guilds: {len(self.bot.guilds)}", icon_url = self.bot.user.avatar.url)

		return embed

	# Help Main Page Embed Builder
	async def help_main_page_embed(self, user : Member) -> Embed:
		embed = Embed(
			title = f"Help",
			color = Color.blurple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)
		embed.set_thumbnail(url = f"{self.bot.user.avatar.url}")
		embed.add_field(name = "Moderation:", value = "`/help Moderation`", inline = False)
		embed.add_field(name = "League Of Legends:", value = "`/help League Of Legends`", inline = False)
		embed.add_field(name = "Music:", value = "`/help Music`", inline = False)
		embed.add_field(name = "Variety:", value = "`/help Variety`", inline = False)
		embed.set_footer(
			text = f"Requested by {user}",
			icon_url = user.avatar.url
		)
		embed.set_author(
			name = "Killer Bot | Help",
			icon_url = self.bot.user.avatar.url
		)

		return embed

	# Help Modules Page Embed Builder
	async def help_modules_page_embed(self, module : str, user : Member) -> Embed:
		embed = Embed(
			title = f"{module.title()} Commands:",
			color = Color.blurple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Help",
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {user}",
			icon_url = user.avatar.url
		)
		for command in self.bot.get_cog(f"{module.title()}").application_commands:
			description = command.description
			options = command.options
			if not description or description is None or description == "":
				description = "No description"

			if not options or options is None or options == "":
				options_message = ""
			
			options_message = ""
			i = 0
			for option_name, option_content in options.items():
				i += 1
				options_message += f"\n    *{i}.* **{option_name}**: `{option_content.description}` {'(**Required**)' if option_content.required else ''}"
				
			embed.add_field(
				name = f"> {command.name.title()} Command",
				value = f"\n- **Description**: `{description}`\n- **Usage**: `/{command.name}`" + f" `<options>`\n- **Options**: {options_message}" if options else f"\n- **Description**: `{description}`\n- **Usage**: `/{command.name}`",
				inline = False
			)
		
		return embed