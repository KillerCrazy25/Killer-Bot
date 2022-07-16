import discord
from discord.ext import commands, bridge

from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID

import psutil

from datetime import datetime
from pytz import timezone

class VarietyCommands(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@bridge.bridge_command(description = "Bot info command.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def botinfo(self, ctx : bridge.BridgeContext):

		embed = discord.Embed(
			color = discord.Color.yellow()
		)

		embed.add_field(name = "Library", value = f"PyCord {discord.__version__}", inline = True)

		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
		embed.set_author(name = "Killer Bot | Bot Information")

		await ctx.respond(embed = embed)

def setup(bot):
	bot.add_cog(VarietyCommands(bot))