from unicodedata import name
import nextcord
from nextcord.ext import commands

from helpers.config import *
from helpers.embed_builder import ModLogEmbedBuilder

from typing import Union

# Types
GUILD_CHANNEL = Union[nextcord.CategoryChannel, nextcord.TextChannel, nextcord.VoiceChannel, nextcord.StageChannel]
USER = Union[nextcord.User, nextcord.Member]

CHANNEL_CHANGES_UNSUPPORTED = ("permissions",)
CHANNEL_CHANGES_SUPPRESSED = ("_overwrites", "position")
ROLE_CHANGES_UNSUPPORTED = ("colour", "permissions")

VOICE_STATE_ATTRIBUTES = {
    "channel.name": "Channel",
    "self_stream": "Streaming",
    "self_video": "Broadcasting",
}

# Mod Log Cog
class ModLog(commands.Cog):

	# Mod Log Constructor
	def __init__(self, bot : commands.Bot):
		self.bot = bot

	# Mod Log On Ready
	@commands.Cog.listener()
	async def on_ready(self):
		self.log_channel = self.bot.get_channel(LOGS_CHANNEL_ID)

	# Channel Create Event
	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel : GUILD_CHANNEL):
		"""Log channel create event to mod log."""
		if channel.guild.id not in GUILD_IDS: return

		if channel.type == nextcord.ChannelType.private or channel.type == nextcord.ChannelType.group: return

		if isinstance(channel, nextcord.CategoryChannel):
			description = f"Category created {channel.mention}"

		elif isinstance(channel, nextcord.VoiceChannel):
			description = f"Voice channel created {channel.mention}"

		elif isinstance(channel, nextcord.StageChannel):
			description = f"Stage channel created {channel.mention}"

		else:
			description = f"Text channel created {channel.mention}"

		builder = ModLogEmbedBuilder(self.bot)

		async for entry in channel.guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.channel_create:
				author = entry.user
				break

		embed = await builder.build(
			author.avatar.url, nextcord.Color.green(), author, description
		)

		embed.add_field(name = "Name", value = channel.name, inline = False)
		embed.add_field(name = "Position", value = str(channel.position), inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {author.id}\nChannel = {channel.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Channel Delete Event
	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel : GUILD_CHANNEL):
		"""Log channel delete event to mod log."""
		if channel.guild.id not in GUILD_IDS: return

		if channel.type == nextcord.ChannelType.private or channel.type == nextcord.ChannelType.group: return

		if isinstance(channel, nextcord.CategoryChannel):
			description = f"Category deleted ({channel.name})"

		elif isinstance(channel, nextcord.VoiceChannel):
			description = f"Voice channel deleted ({channel.name})"

		elif isinstance(channel, nextcord.StageChannel):
			description = f"Stage channel deleted ({channel.name})"

		else:
			description = f"Text channel deleted ({channel.name})"

		builder = ModLogEmbedBuilder(self.bot)

		async for entry in channel.guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.channel_delete:
				author = entry.user
				break

		embed = await builder.build(
			author.avatar.url, nextcord.Color.red(), author, description
		)

		embed.add_field(name = "Name", value = channel.name, inline = False)
		embed.add_field(name = "Created At", value = f"<t:{round(((channel.id / 4194304) + 1420070400000) / 1000)}:F>", inline = False)
		embed.add_field(name = "Position", value = str(channel.position), inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {author.id}\nChannel = {channel.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Channel Update Event
	@commands.Cog.listener()
	async def on_guild_channel_update(self, before : GUILD_CHANNEL, after : GUILD_CHANNEL):
		"""Log channel update event to mod log."""
		if before.guild.id not in GUILD_IDS: return # Guild not in config.

		if before.type == nextcord.ChannelType.private or before.type == nextcord.ChannelType.group: return # Private and Group channels will not be logged.

		if before.position != after.position: return # Position will not be logged.

		if isinstance(before, nextcord.CategoryChannel):
			description = f"Category {after.mention} was updated ({after.name})"

		elif isinstance(before, nextcord.VoiceChannel):
			description = f"Voice channel {after.mention} was updated ({after.name})"

		elif isinstance(before, nextcord.StageChannel):
			description = f"Stage channel {after.mention} was updated ({after.name})"

		else:
			description = f"Text channel {after.mention} was updated ({after.name})"

		builder = ModLogEmbedBuilder(self.bot)

		async for entry in before.guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.channel_update:
				author = entry.user
				break

		embed = await builder.build(
			author.avatar.url, nextcord.Color.gold(), author, description
		)

		embed.add_field(name = "Created At", value = f"<t:{round(((before.id / 4194304) + 1420070400000) / 1000)}:F>", inline = False)
		embed.add_field(name = "Name", value = f"Before: `{before.name}`\nAfter: `{after.name}`", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {author.id}\nChannel = {after.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Member Ban Event
	@commands.Cog.listener()
	async def on_member_ban(self, guild : nextcord.Guild, user : USER):
		"""Log member ban event to mod log."""
		if guild.id not in GUILD_IDS: return

		builder = ModLogEmbedBuilder(self.bot)

		async for entry in guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.ban:
				author = entry.user
				break

		embed = await builder.build(
			user.avatar.url, nextcord.Color.red(), user, f"{user} was banned"
		)

		embed.add_field(name = "User Information", value = f"{user} ({user.id}) {user.mention}", inline = False)
		embed.add_field(name = "Reason", value = entry.reason if entry.reason else "No reason provided", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {user.id}\nModerator = {author.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Member Unban Event
	@commands.Cog.listener()
	async def on_member_unban(self, guild : nextcord.Guild, user : USER):
		"""Log member unban event to mod log."""
		if guild.id not in GUILD_IDS: return

		builder = ModLogEmbedBuilder(self.bot)

		async for entry in guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.unban:
				author = entry.user
				break

		embed = await builder.build(
			user.avatar.url, nextcord.Color.green(), user, f"{user} was unbanned"
		)

		embed.add_field(name = "User Information", value = f"{user} ({user.id}) {user.mention}", inline = False)
		embed.add_field(name = "Reason", value = entry.reason if entry.reason else "No reason provided", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {user.id}\nModerator = {author.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Guild Emojis Update Event
	@commands.Cog.listener()
	async def on_guild_emojis_update(self, guild : nextcord.Guild, before : list, after : list):
		"""Log guild emojis update event to mod log."""
		if guild.id not in GUILD_IDS: return

		builder = ModLogEmbedBuilder(self.bot)

		async for entry in guild.audit_logs(limit = 1):
			# Check if the action is emoji create.
			if entry.action == nextcord.AuditLogAction.emoji_create:
				type_ = "added"
				author = entry.user
				emoji : nextcord.Emoji = entry.target
				color = nextcord.Color.green()

				break
			
			# Check if the action is emoji update.
			elif entry.action == nextcord.AuditLogAction.emoji_update:
				type_ = "updated"
				author = entry.user
				emoji : nextcord.Emoji = entry.target
				color = nextcord.Color.yellow()

				break
			# Action is not emoji create or update.
			else:
				type_ = "deleted"
				author = entry.user
				emoji = entry.target
				color = nextcord.Color.red()

				break

		embed = await builder.build(author.avatar.url, color, author, f"Guild emojis were updated")

		if type_ == "added":
			embed.add_field(name = "Added Emoji", value = f"```ini\nName = {emoji.name}\nManaged = {'Yes' if emoji.managed == True else 'No'}\nAnimated = {'Yes' if emoji.animated == True else 'No'}```", inline = False)
			embed.set_thumbnail(url = emoji.url)
		
		elif type_ == "updated":
			old_emoji : nextcord.Emoji = next(filter(lambda e: e.id == emoji.id, before), None)

			embed.add_field(name = "Updated Emoji", value = f"```ini\nName = {emoji.name}\nManaged = {'Yes' if emoji.managed == True else 'No'}\nAnimated = {'Yes' if emoji.animated == True else 'No'}\nOld Name = {old_emoji.name}```", inline = False)
			embed.set_thumbnail(url = emoji.url)

		elif type_ == "deleted":
			deleted_emoji : nextcord.Emoji = next(filter(lambda e: e.id == emoji.id, before), None)
			embed.add_field(name = "Deleted Emoji", value = f"```ini\nName = {deleted_emoji.name}\nManaged = {'Yes' if deleted_emoji.managed == True else 'No'}\nAnimated = {'Yes' if deleted_emoji.animated == True else 'No'}```", inline = False)

		embed.add_field(name = "ID", value = f"```ini\nUser = {author.id}\nEmoji = {emoji.id}```", inline = False)

		await self.log_channel.send(embed = embed)

def setup(bot : commands.Bot):
	bot.add_cog(ModLog(bot))