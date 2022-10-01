import nextcord
from nextcord.ext import commands
from nextcord.abc import GuildChannel

from db.read import get_welcome_channel, get_welcome_message, get_welcome_role
from db.update import update_welcome_channel, update_welcome_message, update_welcome_role

from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID

SUPPORTED_VARIABLES = [
	"member_name",
	"member_tag",
	"member_mention",
	"member_id",
	"guild_name",
	"guild_id"
]

VARIABLE_HELP = {
	"member_name": "This variable represents the name of a discord user.\n\n**Example**: `KillerBot`",
	"member_tag": "This variable represents the discriminator or tag of a discord user.\n\n**Example**: `#1234`",
	"member_mention": "This variable represents the mention of a discord user.\n\n**Example**: <@945158875722702878>",
	"member_id": "This variable represents the ID of a discord user.\n\n**Example**: `945158875722702878`",
	"guild_name": "This variable represents the name of a discord server or guild.\n\n**Example**: `Killer Bot Support Server`",
	"guild_id": "This variable represents the ID of a discord server or guild.\n\n**Example**: `944815705944109087`"
}

# Welcome Cog
class Welcome(commands.Cog):

	# Show Event Help
	async def show_variable_help(self, variable: str):
		if not variable or variable not in SUPPORTED_VARIABLES: return
		help_for_message = f"Help for {variable} variable"
		try:
			event_help_message = VARIABLE_HELP[variable]
		except KeyError:
			event_help_message = "Unknown Variable Help"

		return help_for_message, event_help_message

	# Welcome Constructor
	def __init__(self, bot : commands.Bot):
		self.bot = bot

	@nextcord.slash_command(name = "welcome", description = "Welcome related subcommands.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def welcome_command(self, interaction: nextcord.Interaction):
		pass

	@welcome_command.subcommand(name = "setchannel", description = "Set the channel where new members are gonna be announced.")
	async def set_channel_subcommand(
		self, 
		interaction: nextcord.Interaction, 
		channel: GuildChannel = nextcord.SlashOption(
			name = "channel",
			description = "Channel that you want to set.",
			required = False,
			channel_types = [nextcord.ChannelType.text]
		)
	):
		if not channel:
			channel = interaction.channel

		await update_welcome_channel(interaction.guild.id, channel.id)
		await interaction.send(f"Set welcome channel to {channel.mention}")

	@welcome_command.subcommand(name = "setmessage", description = "Set the message that you want to show when a new members joins this server.")
	async def set_message_subcommand(
		self,
		interaction: nextcord.Interaction,
		*,
		message: str = nextcord.SlashOption(
			name = "message",
			description = "Message that you want to set.",
			required = True,
			min_length = 20,
			max_length = 1024
		)
	):

		await update_welcome_message(interaction.guild.id, message)
		await interaction.send(f"Set welcome message to: **{message}**")

	@welcome_command.subcommand(name = "current_config", description = "Shows the current welcome config for this server.")
	async def current_config_subcommand(
		self, 
		interaction: nextcord.Interaction
	):
		embed = nextcord.Embed(
			description = f"Showing welcome configuration for **{interaction.guild.name}**",
			color = nextcord.Color.orange()
		)
		welcome_channel = await get_welcome_channel(interaction.guild.id)
		if welcome_channel:	
			welcome_channel = self.bot.get_channel(welcome_channel[0])
		else:
			welcome_channel = None

		welcome_message = await get_welcome_message(interaction.guild.id)
		if welcome_message:
			welcome_message = welcome_message[0]
		else:
			welcome_message = None

		welcome_role = await get_welcome_role(interaction.guild.id)
		if welcome_role:
			welcome_role = interaction.guild.get_role(welcome_role[0])
		else:
			welcome_role = None

		embed.add_field(name = "Channel", value = welcome_channel.mention if welcome_channel else "No channel.", inline = True)
		embed.add_field(name = "Message", value = welcome_message if welcome_message else "No message.", inline = True)
		embed.add_field(name = "Role", value = welcome_role.mention if welcome_role else "No role.", inline = True)

		embed.set_author(name = "Killer Bot | Welcome", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url if interaction.user.avatar else None)

		await interaction.send(embed = embed)

	@welcome_command.subcommand(name = "setrole", description = "Set the role that new users are gonna get when they join this server.")
	async def set_rolesubcommand(
		self, 
		interaction: nextcord.Interaction, 
		role: nextcord.Role = nextcord.SlashOption(
			name = "role",
			description = "Role that you want to give to new users.",
			required = True
		)
	):
		# role = nextcord.utils.get(interaction.guild.roles, name = role)
		if not role:
			await interaction.send(f"**Error**: I couldn't find `{role}` role on this guild.\n**Solution**: Choose a valid role.", ephemeral = True)
			return

		if interaction.guild.me.top_role.position < role.position:
			await interaction.send(f"**Error**: I cannot set {role.mention} as a welcome role because I cannot give that role to a member because is too high for my highest role ({interaction.guild.me.top_role.mention}) in the role hierarchy.\n**Solution**: Please give me a higher role than {role.mention} or choose a lower role than {interaction.guild.me.top_role.mention}!", ephemeral = True)
			return

		if interaction.guild.me.top_role.position == role.position:
			await interaction.send(f"**Error**: I cannot set {role.mention} as a welcome role because I cannot give that role to a member because is in the same position of my highest role ({interaction.guild.me.top_role.mention}) in the role hierarchy.\n**Solution**: Please give me a higher role than {role.mention} or choose a lower role than {interaction.guild.me.top_role.mention}!", ephemeral = True)
			return

		if role.is_integration() or role.is_bot_managed():
			await interaction.send(f"**Error**: I cannot set {role.mention} as a welcome role because that role belongs to a bot or integration.\n**Solution**: Choose another role.", ephemeral = True)
			return

		if role.is_premium_subscriber():
			await interaction.send(f"**Error**: I cannot set {role.mention} as a welcome role because that role can be assigned to Nitro Boosters only.\n**Solution**: Choose another role.", ephemeral = True)
			return

		if role.is_default():
			await interaction.send(f"**Error**: I cannot set {role.mention} as a welcome role because that role is default role.\n**Solution**: Choose another role.", ephemeral = True)
			return

		await update_welcome_role(interaction.guild.id, role.id)
		await interaction.send(f"Successfully set welcome role to {role.mention}", ephemeral = True)

	# @set_rolesubcommand.on_autocomplete("role")
	# async def set_roleautocomplete(self, interaction: nextcord.Interaction, role: str):
	# 	roles = interaction.guild.roles
	# 	if not role:
	# 		await interaction.response.send_autocomplete([role.name for role in roles[1:]])
	# 		return
		
	# 	await interaction.response.send_autocomplete([role.name for role in roles[1:] if role.name.lower().startswith(role.lower())])

	@welcome_command.subcommand(name = "varhelp", description = "Shows help about welcome message variables.")
	async def variable_help_subcommand(
		self, 
		interaction: nextcord.Interaction, 
		variable: str = nextcord.SlashOption(
			name = "variable", 
			description = "Variable that you want to show help for.", 
			required = False, 
			choices = SUPPORTED_VARIABLES
		)
	):
		if not variable:
			embed = nextcord.Embed(
				title = "Supported welcome message variables.",
				color = nextcord.Color.greyple()
			)
			embed.add_field(
				name = "Variables", 
				value = "\n".join(SUPPORTED_VARIABLES),
				inline = False
			)

			embed.set_author(name = "Killer Bot | Welcome", icon_url = self.bot.user.avatar.url)
			embed.set_footer(text = "Type /welcome varhelp <variable> for specific variable help.")

			await interaction.send(embed = embed, ephemeral = True)
			return

		help_for, help_message = await self.show_variable_help(variable)

		embed = nextcord.Embed(
			title = help_for,
			color = nextcord.Color.greyple()
		)
		embed.add_field(name = "**__Variable Description__**", value = help_message, inline = False)
		embed.set_author(name = "Killer Bot | Welcome", icon_url = self.bot.user.avatar.url)

		await interaction.send(embed = embed, ephemeral = True)

	# Welcome Message
	@commands.Cog.listener()
	async def on_member_join(self, member: nextcord.Member):
		welcome_channel = await get_welcome_channel(member.guild.id)
		if welcome_channel[0]:
			welcome_channel = self.bot.get_channel(welcome_channel[0])
		else:
			return

		welcome_message = await get_welcome_message(member.guild.id)
		if welcome_message[0]:
			welcome_message = welcome_message[0]
		else:
			return

		await welcome_channel.send(
			welcome_message.format(
				member_name = member.name, 
				member_mention = member.mention, 
				member_tag = member.discriminator,
				member_id = member.id,
				guild_name = member.guild.name, 		
				guild_id = member.guild.id
			)
		)

		welcome_role = await get_welcome_role(member.guild.id)
		if welcome_role[0]:
			welcome_role = member.guild.get_role(welcome_role[0])

			await member.add_roles(welcome_role, reason = "Welcome role")
		else: 
			return

def setup(bot: commands.Bot):
	bot.add_cog(Welcome(bot))