import nextcord
from nextcord.ext import commands

from helpers.config import *
from helpers.embed_builder import EmbedBuilder
from helpers.utils import get_difference
from helpers import time

from datetime import datetime
from pytz import timezone
from dateutil.relativedelta import relativedelta

from typing import Union

# Types
GUILD_CHANNEL = Union[nextcord.CategoryChannel, nextcord.TextChannel, nextcord.VoiceChannel, nextcord.StageChannel]
USER = Union[nextcord.User, nextcord.Member]

# Constants
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
		# Check if the mod log channel is set
		if LOGS_CHANNEL_ID:
			self.log_channel = self.bot.get_channel(LOGS_CHANNEL_ID)
		else:
			self.log_channel = None
			print("Log channel not found. Please set 'logs_channel_id' in config.json. LOGS ARE NOT GONNA WORK.")

	# Channel Create Event
	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel : GUILD_CHANNEL):
		"""Log channel create event to mod log."""
		if channel.guild.id not in GUILD_IDS: return

		if channel.type == nextcord.ChannelType.private or channel.type == nextcord.ChannelType.group: return

		# Get channel type
		if isinstance(channel, nextcord.CategoryChannel):
			description = f"Category created {channel.mention}"

		elif isinstance(channel, nextcord.VoiceChannel):
			description = f"Voice channel created {channel.mention}"

		elif isinstance(channel, nextcord.StageChannel):
			description = f"Stage channel created {channel.mention}"

		else:
			description = f"Text channel created {channel.mention}"

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get author
		async for entry in channel.guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.channel_create:
				author = entry.user
				break
		
		# Build embed
		embed = await builder.mod_log_embed(
			author.avatar.url, nextcord.Color.green(), author, description
		)

		# Embed Fields
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

		# Get channel type
		if isinstance(channel, nextcord.CategoryChannel):
			description = f"Category deleted ({channel.name})"

		elif isinstance(channel, nextcord.VoiceChannel):
			description = f"Voice channel deleted ({channel.name})"

		elif isinstance(channel, nextcord.StageChannel):
			description = f"Stage channel deleted ({channel.name})"

		else:
			description = f"Text channel deleted ({channel.name})"

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get author
		async for entry in channel.guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.channel_delete:
				author = entry.user
				break
		
		# Build embed
		embed = await builder.mod_log_embed(
			author.avatar.url, nextcord.Color.red(), author, description
		)

		# Embed Fields
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

		# Get channel type.
		if isinstance(before, nextcord.CategoryChannel):
			description = f"Category {after.mention} was updated ({after.name})"

		elif isinstance(before, nextcord.VoiceChannel):
			description = f"Voice channel {after.mention} was updated ({after.name})"

		elif isinstance(before, nextcord.StageChannel):
			description = f"Stage channel {after.mention} was updated ({after.name})"

		else:
			description = f"Text channel {after.mention} was updated ({after.name})"

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get author.
		async for entry in before.guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.channel_update:
				author = entry.user
				break

		# Build embed.
		embed = await builder.mod_log_embed(
			author.avatar.url, nextcord.Color.gold(), author, description
		)

		# Embed Fields
		embed.add_field(name = "Created At", value = f"<t:{round(((before.id / 4194304) + 1420070400000) / 1000)}:F>", inline = False)
		embed.add_field(name = "Name", value = f"Before: `{before.name}`\nAfter: `{after.name}`", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {author.id}\nChannel = {after.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Member Ban Event
	@commands.Cog.listener()
	async def on_member_ban(self, guild : nextcord.Guild, user : USER):
		"""Log member ban event to mod log."""
		if guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get the moderator who banned the user.
		async for entry in guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.ban:
				author = entry.user
				break

		# Build the embed.
		embed = await builder.mod_log_embed(
			user.avatar.url, nextcord.Color.red(), user, f"{user} was banned"
		)

		# Embed Fields
		embed.add_field(name = "User Information", value = f"{user} ({user.id}) {user.mention}", inline = False)
		embed.add_field(name = "Reason", value = entry.reason if entry.reason else "No reason provided", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {user.id}\nModerator = {author.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Member Unban Event
	@commands.Cog.listener()
	async def on_member_unban(self, guild : nextcord.Guild, user : USER):
		"""Log member unban event to mod log."""
		if guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get the moderator who unbanned the user.
		async for entry in guild.audit_logs(limit = 1):
			if entry.action == nextcord.AuditLogAction.unban:
				author = entry.user
				break

		# Build the embed
		embed = await builder.mod_log_embed(
			user.avatar.url, nextcord.Color.green(), user, f"{user} was unbanned"
		)

		# Embed Fields
		embed.add_field(name = "User Information", value = f"{user} ({user.id}) {user.mention}", inline = False)
		embed.add_field(name = "Reason", value = entry.reason if entry.reason else "No reason provided", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {user.id}\nModerator = {author.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Guild Emojis Create / Delete / Update Event
	@commands.Cog.listener()
	async def on_guild_emojis_update(self, guild : nextcord.Guild, before : list, after : list):
		"""Log guild emojis update event to mod log."""
		if guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get Author
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

		# Build Embed
		embed = await builder.mod_log_embed(author.avatar.url, color, author, f"Guild emojis were updated")

		# Add Fields
		if type_ == "added":
			embed.add_field(
				name = "Added Emoji",
				value = f"```ini\nName = {emoji.name}\nManaged = {'Yes' if emoji.managed == True else 'No'}\nAnimated = {'Yes' if emoji.animated == True else 'No'}```", 
				inline = False
			)
			embed.set_thumbnail(url = emoji.url)
		
		elif type_ == "updated":
			old_emoji : nextcord.Emoji = next(filter(lambda e: e.id == emoji.id, before), None)

			embed.add_field(
				name = "Updated Emoji",
				value = f"```ini\nName = {emoji.name}\nManaged = {'Yes' if emoji.managed == True else 'No'}\nAnimated = {'Yes' if emoji.animated == True else 'No'}\nOld Name = {old_emoji.name}```", 
				inline = False
			)
			embed.set_thumbnail(url = emoji.url)

		elif type_ == "deleted":
			deleted_emoji : nextcord.Emoji = next(filter(lambda e: e.id == emoji.id, before), None)
			
			embed.add_field(
				name = "Deleted Emoji", 
				value = f"```ini\nName = {deleted_emoji.name}\nManaged = {'Yes' if deleted_emoji.managed == True else 'No'}\nAnimated = {'Yes' if deleted_emoji.animated == True else 'No'}```", 
				inline = False
			)

		embed.add_field(name = "ID", value = f"```ini\nUser = {author.id}\nEmoji = {emoji.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Guild Member Join Event
	@commands.Cog.listener()
	async def on_member_join(self, member : USER):
		"""Log member join event to mod log."""
		if member.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		embed = await builder.mod_log_embed(
			member.avatar.url, nextcord.Color.green(), member, f"{member} joined the server"
		)

		# Dates
		now = datetime.now(tz = timezone('US/Eastern'))
		joined_at = datetime.timestamp(member.joined_at)
		created_at = datetime.timestamp(member.created_at)
		difference = abs(relativedelta(now, member.created_at))
		account_age = time.humanize_delta(difference, precision = "days")

		# Embed Fields
		embed.add_field(name = "User Information", value = f"{member} ({member.id}) {member.mention}", inline = False)
		embed.add_field(name = "Account Information", value = f"**Joined At:** <t:{round(joined_at)}:F>\n**Created At:** <t:{round(created_at)}:F>\n**Account Age:** `{account_age}`", inline = False)
		embed.add_field(name = "Member Count", value = f"{member.guild.member_count}", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {member.id}\nGuild = {member.guild.id}```", inline = False)

		await self.log_channel.send(embed = embed)

	# Guild Member Remove Event
	@commands.Cog.listener()
	async def on_member_remove(self, member : USER):
		"""Log member remove event to mod log."""
		if member.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		embed = await builder.mod_log_embed(
			member.avatar.url, nextcord.Color.red(), member, f"{member} left the server"
		)

		# Dates
		now = datetime.now(tz = timezone('US/Eastern'))
		joined_at = datetime.timestamp(member.joined_at)
		created_at = datetime.timestamp(member.created_at)
		difference = abs(relativedelta(now, member.created_at))
		account_age = time.humanize_delta(difference, precision = "days")

		# Roles
		if len(member.roles) > 1:
			roles = [role.name for role in member.roles]
			roles.remove("@everyone")
			roles = ", ".join(roles)
		else:
			roles = "None"

		# Embed Fields
		embed.add_field(name = "User Information", value = f"{member} ({member.id}) {member.mention}", inline = False)
		embed.add_field(name = "Roles", value = f"{roles}", inline = False)
		embed.add_field(name = "Account Information", value = f"**Joined At:** <t:{round(joined_at)}:F>\n**Created At:** <t:{round(created_at)}:F>\n**Account Age:** `{account_age}`", inline = False)
		embed.add_field(name = "Member Count", value = f"{member.guild.member_count}", inline = False)
		embed.add_field(name = "ID", value = f"```ini\nUser = {member.id}\nGuild = {member.guild.id}```", inline = False)

		await self.log_channel.send(embed = embed)

		print(member.guild.features)

	# Guild Member Update Event
	@commands.Cog.listener()
	async def on_member_update(self, before : USER, after : USER):
		"""Log member update event to mod log."""
		if before.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Member Nickname Update
		if before.nick != after.nick:
			embed = await builder.mod_log_embed(
				after.avatar.url, nextcord.Color.blue(), after, f"{after} changed their nickname"
			)

			# Embed Fields
			embed.add_field(
				name = "New Nickname", 
				value = f"{after}", 
				inline = False
			)

			embed.add_field(
				name = "Old Nickname", 
				value = f"{before}", 
				inline = False
			)

			embed.add_field(
				name = "ID", 
				value = f"```ini\nUser = {after.id}```", 
				inline = False
			)
		
		# Member Avatar Update
		elif before.avatar.url != after.avatar.url:
			embed = await builder.mod_log_embed(
				after.avatar.url, nextcord.Color.blue(), after, f"{after} changed their avatar"
			)

			# Embed Fields
			embed.add_field(
				name = "New Avatar", 
				value = f"Displayed on embed image", 
				inline = False
			)

			embed.add_field(
				name = "Old Avatar", 
				value = f"Displayed on embed thumbnail",
				inline = False
			)

			embed.add_field(
				name = "ID", 
				value = f"```ini\nUser = {after.id}```", 
				inline = False
			)

			# Embed Image & Thumbnail
			embed.set_image(url = after.avatar.url)
			embed.set_thumbnail(url = before.avatar.url)

		# Member Role Update
		elif before.roles != after.roles:

			# Get Author Of Update
			async for entry in before.guild.audit_logs(limit = 1, action = nextcord.AuditLogAction.member_role_update):
				moderator = entry.user

				break

			embed = await builder.mod_log_embed(
				after.avatar.url, nextcord.Color.blue(), after, f"{after} changed their roles"
			)

			# Roles

			added_roles = [role for role in after.roles if role not in before.roles]
			removed_roles = [role for role in before.roles if role not in after.roles]

			# ('1' if name is None else '2' if name == '2' else name) 

			# Embed Fields
			embed.add_field(
				name = "Changes", 
				value = "{}{}".format(':white_check_mark: **' + added_roles[0].name + '**' if added_roles.__len__() != 0 else '', '\n:x: **' + removed_roles[0].name + '**' if removed_roles.__len__() != 0 else ''),
				inline = False
			)

			embed.add_field(
				name = "ID", 
				value = f"```ini\nUser = {after.id}\nModerator = {moderator.id}```", 
				inline = False
			)

		# Embed Footer
		embed.set_footer(text = f"{moderator}", icon_url = moderator.avatar.url)

		# Avoid error if there's no value in the field
		if not embed.fields[0].value: return 

		await self.log_channel.send(embed = embed)

	# Guild Role Create Event
	@commands.Cog.listener()
	async def on_guild_role_create(self, role : nextcord.Role):
		"""Log role create event to mod log."""
		if role.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		async for entry in role.guild.audit_logs(limit = 1, action = nextcord.AuditLogAction.role_create):
			perpetrator = entry.user
			break

		# Embed
		embed = await builder.mod_log_embed(
			perpetrator.avatar.url, nextcord.Color.blue(), perpetrator, "A role was created"
		)

		# Embed Fields
		embed.add_field(
			name = "Name",
			value = role.name,
			inline = False
		)

		embed.add_field(
			name = "ID", 
			value = f"```ini\nRole = {role.id}\nPerpetrator = {perpetrator.id}```", 
			inline = False
		)
		
		await self.log_channel.send(embed = embed)

	# Guild Role Delete Event
	@commands.Cog.listener()
	async def on_guild_role_delete(self, role : nextcord.Role):
		"""Log role delete event to mod log."""
		if role.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		async for entry in role.guild.audit_logs(limit = 1, action = nextcord.AuditLogAction.role_delete):
			perpetrator = entry.user
			reason = entry.reason
			break

		# Embed
		embed = await builder.mod_log_embed(
			perpetrator.avatar.url, nextcord.Color.red(), perpetrator, "A role was deleted"
		)

		# Embed Fields
		embed.add_field(name = "Name", value = role.name, inline = False)
		embed.add_field(name = "Reason", value = reason if reason else "None", inline = False)
		embed.add_field(
			name = "ID", 
			value = f"```ini\nRole = {role.id}\nPerpetrator = {perpetrator.id}```", 
			inline = False
		)
		
		await self.log_channel.send(embed = embed)

	# Guild Role Update Event
	@commands.Cog.listener()
	async def on_guild_role_update(self, before : nextcord.Role, after : nextcord.Role):
		"""Log role update event to mod log."""
		if before.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Get Author Of Update
		async for entry in before.guild.audit_logs(limit = 1, action = nextcord.AuditLogAction.role_update):
			perpetrator = entry.user
			break

		# Embed
		embed = await builder.mod_log_embed(
			perpetrator.avatar.url, after.color if after.color else nextcord.Color.gold(), perpetrator, f"A role was updated ({after.name})"
		)

		# Role Properties
		before_properties = {
			"name": before.name,
			"permissions": before.permissions,
			"color": before.color,
			"position": before.position,
			"mentionable": before.mentionable,
			"hoist": before.hoist,
			"tags" : before.tags
		}

		after_properties = {
			"name": after.name,
			"permissions": after.permissions,
			"color": after.color,
			"position": after.position,
			"mentionable": after.mentionable,
			"hoist": after.hoist,
			"tags" : after.tags
		}

		# Embed Fields
		for property in before_properties:
			# Position will not be logged due to channel spam.
			if before_properties[property] != after_properties[property] and property != "position" and property != "permissions" and property != "tags":
				embed.add_field(
					name = property.capitalize(), 
					value = f"Was: {str(before_properties[property])}\nNow: {str(after_properties[property])}", 
					inline = False
				)
		
		# Empty Dicts
		before_perms = dict()
		after_perms = dict()

		before_perms_allowed = dict()
		before_perms_denied = dict()

		after_perms_allowed = dict()
		after_perms_denied = dict()	

		# Get Permissions Before
		for perm, value in iter(before.permissions):
			before_perms[perm] = value
			if value == True:
				before_perms_allowed[perm] = value
			
			else:
				before_perms_denied[perm] = value

		# Get Permissions After
		for perm, value in iter(after.permissions):
			after_perms[perm] = value
			if value == True:
				after_perms_allowed[perm] = value

			else:
				after_perms_denied[perm] = value

		# Checking If Permissions Were Changed
		if after_perms_allowed != before_perms_allowed or after_perms_denied != before_perms_denied:
			field_name = "Permissions changed"
			field_value = "\n"

			different_perms = get_difference(before_perms, after_perms) | get_difference(after_perms, before_perms)

			for perm in different_perms:
				if after_perms[perm] == True and before_perms[perm] == False:
					field_value += f"\n:white_check_mark: {perm.capitalize()}"

				elif after_perms[perm] == False and before_perms[perm] == True:
					field_value += f"\n:x: {perm.capitalize()}"

				else:
					continue
			
			embed.add_field(name = field_name, value = field_value, inline = False)

		# ID Field
		embed.add_field(
			name = "ID", 
			value = f"```ini\nRole = {after.id}\nPerpetrator = {perpetrator.id}```", 
			inline = False
		)
		
		await self.log_channel.send(embed = embed)

	# Message Delete Event
	@commands.Cog.listener()
	async def on_message_delete(self, message : nextcord.Message):
		"""Log message delete event to mod log."""
		if message.guild.id not in GUILD_IDS: return

		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Embed
		embed = await builder.mod_log_embed(
			message.author.avatar.url, message.author.color if message.author.color else nextcord.Color.purple(), message.author, f"Message deleted in {message.channel.mention}"
		)

		# Created At Timestamp
		ts = message.created_at.timestamp()
		
		# Date & ID Fields
		embed.add_field(name = "Content", value = message.content, inline = False)
		embed.add_field(name = "Date", value = f"<t:{round(ts)}:F>")
		embed.add_field(name = "ID", value = f"```ini\nUser = {message.author.id}\nMessage = {message.id}```", inline = False)
		
		await self.log_channel.send(embed = embed)
		
def setup(bot : commands.Bot):
	bot.add_cog(ModLog(bot))