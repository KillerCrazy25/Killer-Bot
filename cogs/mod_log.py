import discord
from discord.ext import commands, bridge

# Mod Log Cog

class ModLog(commands.Cog):

	# Mod Log Constructor

	def __init__(self, bot : bridge.Bot):
		self.bot = bot

	

def setup(bot : bridge.Bot):
	bot.add_cog(ModLog(bot))