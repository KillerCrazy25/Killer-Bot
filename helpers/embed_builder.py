import nextcord
from nextcord.ext import commands

from typing import (
	Optional,
	Union,
	List
)

from helpers.config import *
from datetime import datetime

class ModLogEmbedBuilder:
	
	def __init__(self, bot : commands.Bot):
		self.bot : commands.Bot = bot

	async def build(
		self,
		icon_url: Optional[str],
		color: Union[nextcord.Color, int],
		title: Optional[str],
		description: str,
		thumbnail: Optional[Union[str, nextcord.Asset]] = None,
		timestamp: Optional[datetime] = None,
		footer: Optional[str] = None,
	) -> nextcord.Embed:
		"""Generate log embed and send to logging channel."""
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