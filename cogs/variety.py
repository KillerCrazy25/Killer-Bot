import nextcord
import psutil
import random
from nextcord.ext import commands

from helpers.config import MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID, VERSION

# Constants
VERIFICATION_LEVELS = {
	0: "Unrestricted",
	1: "Low - Must have a verified email",
	2: "Medium - Must be registered for 5 minutes",
	3: "High - 10 minutes of membership required",
	4: "Highest - Verified phone required"
}

EXPLICIT_CONTENT_LEVELS = {
	0: "No Scanning Enabled",
	1: "Scanning content from members without a role",
	2: "Scanning content from all members"
}

MFA_LEVELS = {
	0: "Disabled",
	1: "Enabled"
}

class VarietyCommands(commands.Cog, name = "Variety", description = "Commands of a variety of different types."):

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
		embed.set_author(name = "Killer Bot | Bot Information", icon_url = self.bot.user.avatar.url)

		await interaction.send(embed = embed)

	# Guild Info Command
	@nextcord.slash_command(name = "guildinfo", description = "Shows useful information about the guild.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def guildinfo(self, interaction: nextcord.Interaction):
		COLORS = [nextcord.Color.yellow(), nextcord.Color.gold(), nextcord.Color.blurple(), nextcord.Color.red(), nextcord.Color.purple()]
		embed = nextcord.Embed(
			description = f"**Name**: {interaction.guild.name}\n{'**Description**: ' + interaction.guild.description if interaction.guild.description else ''}",
			color = random.choice(COLORS)
		)
		embed.add_field(name = "ID", value = str(interaction.guild.id), inline = True)
		embed.add_field(name = "Owner", value = f"{interaction.guild.owner.mention}", inline = True)
		embed.add_field(name = "Created at", value = f"{interaction.guild.created_at.strftime('%d/%m/%Y, %I:%M %P')} (<t:{round(interaction.guild.created_at.timestamp())}:R>)", inline = False)
		embed.add_field(name = "Total Members", value = str(interaction.guild.member_count), inline = True)
		embed.add_field(
			name = "Channels", 
			value = f"Text: **{len(interaction.guild.text_channels)}**\nVoice: **{len(interaction.guild.voice_channels)}**\nStage: **{len(interaction.guild.stage_channels)}**\nForum: **{len(interaction.guild.forum_channels)}**\nCategories: **{len(interaction.guild.categories)}**\n\nTotal: **{len(interaction.guild.channels)}**",
			inline = True
		)
		embed.add_field(
			name = "Extras", 
			value = f"Roles: **{len(interaction.guild.roles)}**\nEmojis: **{len(interaction.guild.emojis)}**\nFeatures:\n``{', '.join(interaction.guild.features).upper()}``",
			inline = True
		)
		embed.add_field(
			name = "Server Boosts", 
			value = f"Total Boosters: **{interaction.guild.premium_subscription_count}**\nBoost Tier: **{interaction.guild.premium_tier}**",
			inline = False
		)
		embed.add_field(
			name = "Security",
			value = f"Verification: **{VERIFICATION_LEVELS[interaction.guild.verification_level.value]}**\nExplicit Content: **{EXPLICIT_CONTENT_LEVELS[interaction.guild.explicit_content_filter.value]}**\nTwo Factor Authentication: **{MFA_LEVELS[interaction.guild.mfa_level]}**",
			inline = False
		)

		embed.set_thumbnail(url = interaction.guild.icon.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url if interaction.user.avatar else None)
		embed.set_author(name = f"Killer Bot | Guild Information", icon_url = self.bot.user.avatar.url)

		await interaction.send(embed = embed)

	@nextcord.slash_command(name = "userinfo", description = "Shows information about given user.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def userinfo_command(
		self, 
		interaction: nextcord.Interaction, 
		user: str = nextcord.SlashOption(
			name = "user", 
			description = "The user that you want to see his info.", 
			required = False
		)
	):
		if not user:
			member = interaction.user

		# get channel id by name
		if isinstance(user, str):
			member = nextcord.utils.get(interaction.guild.members, name = user)

		embed = nextcord.Embed(
			color = member.colour
		)
		embed.add_field(name = "ID", value = str(member.id), inline = True)
		embed.add_field(name = "Nickname", value = member.display_name, inline = True)
		embed.add_field(name = "Created at", value = f"{member.created_at.strftime('%d/%m/%Y, %I:%M %P')} (<t:{round(member.created_at.timestamp())}:R>)", inline = False)
		embed.add_field(name = "Joined at", value = f"{member.joined_at.strftime('%d/%m/%Y, %I:%M %P')} (<t:{round(member.joined_at.timestamp())}:R>)", inline = False)
		embed.add_field(name = "Booster", value = "User is not server booster." if member not in member.guild.premium_subscribers else "User is server booster.")
		embed.add_field(name = "Roles", value = f", ".join([role.mention for role in member.roles]), inline = False)

		embed.set_thumbnail(url = member.avatar.url if member.avatar else None)
		embed.set_author(name = "Killer Bot | User Information", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		await interaction.send(embed = embed)

	@nextcord.user_command(name = "User Information")
	async def userinfo_context(self, interaction: nextcord.Interaction, member: nextcord.Member):
		embed = nextcord.Embed(
			color = member.colour
		)
		embed.add_field(name = "ID", value = str(member.id), inline = True)
		embed.add_field(name = "Nickname", value = member.display_name, inline = True)
		embed.add_field(name = "Created at", value = f"{member.created_at.strftime('%d/%m/%Y, %I:%M %P')} (<t:{round(member.created_at.timestamp())}:R>)", inline = False)
		embed.add_field(name = "Joined at", value = f"{member.joined_at.strftime('%d/%m/%Y, %I:%M %P')} (<t:{round(member.joined_at.timestamp())}:R>)", inline = False)
		embed.add_field(name = "Booster", value = "User is not server booster." if member not in member.guild.premium_subscribers else "User is server booster.")
		embed.add_field(name = "Roles", value = f", ".join([role.mention for role in member.roles]), inline = False)

		embed.set_thumbnail(url = member.avatar.url if member.avatar else None)
		embed.set_author(name = "Killer Bot | User Information", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		await interaction.send(embed = embed)

	@userinfo_command.on_autocomplete("user")
	async def get_guild_users(self, interaction: nextcord.Interaction, user: str):
		guild_users = [member.name for member in interaction.guild.members]
		if not user:
			await interaction.response.send_autocomplete(guild_users)
			return
		
		get_near_user = [member for member in guild_users if member.lower().startswith(member.lower())]
		await interaction.response.send_autocomplete(get_near_user)

def setup(bot: commands.Bot):
	bot.add_cog(VarietyCommands(bot))