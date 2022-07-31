import discord, psutil
from discord.ext import commands, bridge

from utils.config import MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, VERSION

class VarietyCommands(commands.Cog):

	def __init__(self, bot : bridge.Bot):
		self.bot : bridge.Bot = bot					

	@bridge.bridge_command(description = "Bot info command.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def botinfo(self, ctx : bridge.BridgeContext):

		embed = discord.Embed(

			color = discord.Color.yellow()
		)

		embed.add_field(name = "General Information", value = f"```- Bot Name: {self.bot.user.name}\n- Bot ID: {self.bot.user.id}\n- Bot Version: {VERSION}\n- Bot Prefix: {PREFIX}\n- Bot Developer: KillerCrazy25#2049\n- Birthday: {self.bot.user.created_at.strftime('%b %d, %Y')}```")
		embed.add_field(name = "Programming Related Information", value = f"```\n- Library: Py-Cord {discord.__version__}\n- Language: Python 3.10.4\n- OS: Linux | Ubuntu 20.04```", inline = False)
		embed.add_field(name = "Resources Information", value = f"```- CPU: {psutil.cpu_percent()}%\n- RAM: {psutil.virtual_memory().percent}%\n- Disk: {psutil.disk_usage('/').percent}%```", inline = False)

		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
		embed.set_author(name = "Killer Bot | Bot Information")

		await ctx.respond(embed = embed)

def setup(bot : bridge.Bot):
	bot.add_cog(VarietyCommands(bot))