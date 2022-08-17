import nextcord
from nextcord.ext import commands

# Mod Log Cog
class ModLog(commands.Cog):

	# Mod Log Constructor
	def __init__(self, bot : commands.Bot):
		self.bot = bot

def setup(bot : commands.Bot):
	bot.add_cog(ModLog(bot))