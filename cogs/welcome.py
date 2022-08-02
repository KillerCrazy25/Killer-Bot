import nextcord
from nextcord.ext import commands

from utils.config import WELCOME_CHANNEL_ID

# Welcome Cog

class Welcome(commands.Cog):

	# Welcome Constructor

	def __init__(self, bot : commands.Bot):
		self.bot = bot

	# Welcome Message

	@commands.Cog.listener()
	async def on_member_join(self, member : nextcord.Member):
		welcome_channel = await self.bot.get_channel(WELCOME_CHANNEL_ID)

		await welcome_channel.send(f"**{member}** has joined the server!")

def setup(bot : commands.Bot):
	bot.add_cog(Welcome(bot))