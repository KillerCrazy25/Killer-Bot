import nextcord
from nextcord.ext import commands, application_checks

from datetime import datetime

from pytz import timezone

from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID

# Moderation Cog
class ModerationCommands(commands.Cog, name = "Moderation", description = "Commands for Moderators"):

	# Moderation Constructor
	def __init__(self, bot : commands.Bot):
		self.bot : commands.Bot = bot

	# Ban Command
	@nextcord.slash_command(name = "ban", description = "Bans a user from the server.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@application_checks.has_permissions(ban_members = True)
	async def ban(
		self, 
		interaction : nextcord.Interaction, 
		user : nextcord.Member = nextcord.SlashOption(
			name = "user",
			description = "The user to ban.",
			required = False,
			default = None		
		), 
		*, 
		reason : str = nextcord.SlashOption(
			name = "reason",
			description = "The reason for the ban.",
			required = False,
			default = None
		)
	):
		if user == None:
			return await interaction.send(embed = nextcord.Embed(
				description = "Please provide a user to ban.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if user == interaction.user:
			return await interaction.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban yourself.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)
		if user == user.guild.owner:
			return await interaction.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban the server owner.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if interaction.user.top_role.position < user.top_role.position:
			return await interaction.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban someone with a higher role than you.",
			)
			.set_author(
				name = "Killer Bot | Moderation",
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)
		if interaction.user.top_role.position == user.top_role.position:
			return await interaction.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban someone with the same role as you.",
			)
			.set_author(
				name = "Killer Bot | Moderation",
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)

		embed = nextcord.Embed(
			description = f"{user} has been banned from {interaction.guild.name}!",
			color = nextcord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.add_field(name = "Moderator", value = interaction.user.mention, inline = True)
		embed.add_field(name = "Duration", value = "Permanent", inline = True)
		embed.add_field(name = "Reason", value = reason, inline = False)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await user.ban(reason = reason)
		try:
			await interaction.send(embed = embed)
		except:
			await interaction.send("User has been banned, but there was an error trying to send the embed.")

		print("{} has been banned in {} by {} for {}.".format(user, interaction.user.guild.id, interaction.user, reason))

	# Unban Command
	@nextcord.slash_command(name = "unban", description = "Unbans a user from the server.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@application_checks.has_permissions(ban_members = True)
	async def unban(self, interaction : nextcord.Interaction, id : int):
		user = await self.bot.fetch_user(id)

		if user == None:
			return await interaction.send(embed = nextcord.Embed(
				description = "Please provide the user id of the user that you want to unban.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if user == interaction.user:
			return await interaction.send(embed = nextcord.Embed(
				description = "Sorry, you can't unban yourself.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)

		embed = nextcord.Embed(
			description = f"{user} has been unbanned from {interaction.guild.name}!",
			color = nextcord.Color.green(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.add_field(name = "Moderator", value = interaction.user.mention, inline = True)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await interaction.guild.unban(user)
		try:
			await interaction.send(embed = embed)
		except:
			await interaction.send("User has been unbanned, but there was an error trying to send the embed.")
		print("{} has been unbanned in {} by {}.".format(user, interaction.user.guild.id, interaction.user))	

	# Clear Command
	@nextcord.slash_command(name = "clear", description = "Clears a certain amount of messages a text channel.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@application_checks.has_permissions(manage_messages = True)
	async def clear(
		self, 
		interaction: nextcord.Interaction, 
		limit: int = nextcord.SlashOption(
			name = "limit",
			description = "The amount of messages to clear.",
			required = True,
			min_value = 5,
			max_value = 100
		), 
		channel: nextcord.abc.GuildChannel = nextcord.SlashOption(
			name = "channel",
			description = "The channel to clear messages from.",
			required = False,
			default = None,
			channel_types = [nextcord.ChannelType.text]
		) 
	):
		if not channel:
			channel = interaction.channel
		
		embed = nextcord.Embed(
			description = f"{interaction.user} has cleared {limit} messages in {channel}.",
			color = nextcord.Color.og_blurple()
		)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await channel.purge(limit = limit)
		await interaction.send(embed = embed)

def setup(bot : commands.Bot):
	bot.add_cog(ModerationCommands(bot))