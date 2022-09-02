import nextcord, psutil
from nextcord.ext import commands

from helpers.config import MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, VERSION

class VarietyCommands(commands.Cog):

	def __init__(self, bot : commands.Bot):
		self.bot : commands.Bot = bot	

	# Bot Info Command
	@nextcord.slash_command(
		name = "botinfo", 
		description = "Bot info command.", 
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def botinfo(self, interaction : nextcord.Interaction):

		embed = nextcord.Embed(
			color = nextcord.Color.yellow()
		)

		embed.add_field(name = "> General Information", value = f"```- Bot Name: {self.bot.user.name}\n- Bot ID: {self.bot.user.id}\n- Bot Version: {VERSION}\n- Bot Prefix: {PREFIX}\n- Bot Developer: KillerCrazy25#2049\n- Birthday: {self.bot.user.created_at.strftime('%b %d, %Y')}```")
		embed.add_field(name = "> Libraries Information", value = f"```\n- Nextcord V2.1.0\n- Cassiopeia V5.0.1\n- RiotWatcher V3.2.3```", inline = False)
		embed.add_field(name = "> Resources Information", value = f"```- CPU: {psutil.cpu_percent()}%\n- RAM: {psutil.virtual_memory().percent}%\n- Disk: {psutil.disk_usage('/').percent}%```", inline = False)

		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)
		embed.set_author(name = "Killer Bot | Bot Information")

		await interaction.send(embed = embed)

def setup(bot : commands.Bot):
	bot.add_cog(VarietyCommands(bot))