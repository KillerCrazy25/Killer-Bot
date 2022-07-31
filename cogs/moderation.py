import discord
from discord.ext import commands, bridge

from datetime import datetime

from pytz import timezone

from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID

# Moderation Cog

class ModerationCommands(commands.Cog):

	# Moderation Constructor

	def __init__(self, bot : bridge.Bot):
		self.bot : bridge.Bot = bot

	# Ban Command

	@bridge.bridge_command(description = "Ban a user.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@commands.has_permissions(ban_members = True)
	async def ban(self, ctx : bridge.BridgeContext, user : discord.Member = None, *, reason : str = "No reason provided."):
		if user == None:
			return await ctx.respond(embed = discord.Embed(
				description = "Please provide a user to ban.",
				color = discord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if user == ctx.author:
			return await ctx.respond(embed = discord.Embed(
				description = "Sorry, you can't ban yourself.",
				color = discord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)
		if user == user.guild.owner:
			return await ctx.respond(embed = discord.Embed(
				description = "Sorry, you can't ban the server owner.",
				color = discord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if ctx.author.top_role.position < user.top_role.position:
			return await ctx.send(embed = discord.Embed(
				description = "Sorry, you can't ban someone with a higher role than you.",
			)
			.set_author(
				name = "Killer Bot | Moderation",
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)
		if ctx.author.top_role.position == user.top_role.position:
			return await ctx.send(embed = discord.Embed(
				description = "Sorry, you can't ban someone with the same role as you.",
			)
			.set_author(
				name = "Killer Bot | Moderation",
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)

		embed = discord.Embed(
			description = f"{user} has been banned from {ctx.guild.name}!",
			color = discord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.add_field(name = "Moderator", value = ctx.author.mention, inline = True)
		embed.add_field(name = "Duration", value = "Permanent", inline = True)
		embed.add_field(name = "Reason", value = reason, inline = False)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await ctx.respond(embed = embed)
		await user.ban(reason = reason)

		print("{} has been banned in {} by {} for {}.".format(user, ctx.author.guild.id, ctx.author, reason))

	# Unban Command

	@bridge.bridge_command(description = "Unban a user.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@commands.has_permissions(ban_members = True)
	async def unban(self, ctx : bridge.BridgeContext, id : int):
		user = await self.bot.fetch_user(id)

		if user == None:
			return await ctx.respond(embed = discord.Embed(
				description = "Please provide the user id of the user that you want to unban.",
				color = discord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if user == ctx.author:
			return await ctx.respond(embed = discord.Embed(
				description = "Sorry, you can't unban yourself.",
				color = discord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)

		embed = discord.Embed(
			description = f"{user} has been unbanned from {ctx.guild.name}!",
			color = discord.Color.green(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.add_field(name = "Moderator", value = ctx.author.mention, inline = True)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await ctx.respond(embed = embed)
		print("{} has been unbanned in {} by {}.".format(user, ctx.author.guild.id, ctx.author))
		await ctx.guild.unban(user)

	# Clear Command
	
	@bridge.bridge_command(description = "Clear messages in a specified channel.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID], aliases = ["purge"])
	@commands.has_permissions(manage_messages = True)
	async def clear(self, ctx : bridge.BridgeContext, limit : int = 5, channel : discord.TextChannel = None):
		if channel == None:
			channel = ctx.channel

		if limit < 100:
			embed = discord.Embed(
				description = f"{ctx.author} has cleared {limit} messages in {channel}.",
				color = discord.Color.og_blurple()
			)

			embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

			await channel.purge(limit = limit)
			await ctx.send(embed = embed)

		else:
			await ctx.respond(embed = discord.Embed(
				description = "Please provide a number less than 100.",
				color = discord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)

def setup(bot : bridge.Bot):
	bot.add_cog(ModerationCommands(bot))