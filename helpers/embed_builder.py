import nextcord
from nextcord.ext import commands

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
	async def error_embed(self) -> nextcord.Embed:
		"""Returns an error embed."""
		embed = nextcord.Embed(
			title = "Something went wrong trying to run this command.",
			color = nextcord.Color.dark_red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.set_author(name = "Killer Bot | Error", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = "This message will be deleted in 10 seconds...")

		return embed

	# Mod Log Embed Builder
	async def mod_log_embed(
		self,
		icon_url: Optional[str],
		color: Union[nextcord.Color, int],
		title: Optional[str],
		description: str,
		thumbnail: Optional[Union[str, nextcord.Asset]] = None,
		timestamp: Optional[datetime] = None,
		footer: Optional[str] = None,
	) -> nextcord.Embed:
		"""Returns a mod log embed."""
		embed = nextcord.Embed(
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