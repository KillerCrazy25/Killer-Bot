import discord
from discord.ext import commands, bridge

from riotwatcher import LolWatcher, ApiError

lol_watcher = LolWatcher("RGAPI-5b07fa96-73f1-4064-8db8-9fa7a2a68b22")

class LeagueExtension(commands.Cog, description = "League Extension Testing"):

	def __init__(self, bot):
		self.bot = bot

def setup(bot):
	bot.add_cog(LeagueExtension(bot))