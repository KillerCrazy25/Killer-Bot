import nextcord
from nextcord.ext import commands

from datetime import datetime

from pytz import timezone

from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID

# Moderation Cog

class ModerationCommands(commands.Cog):

	# Moderation Constructor

	def __init__(self, bot : commands.Bot):
		self.bot : commands.Bot = bot

	# Ban Command

	@commands.command(description = "Ban a user.")
	@commands.has_permissions(ban_members = True)
	async def ban(self, ctx : commands.Context, user : nextcord.Member = None, *, reason : str = "No reason provided."):
		if user == None:
			return await ctx.send(embed = nextcord.Embed(
				description = "Please provide a user to ban.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if user == ctx.author:
			return await ctx.send(embed = nextcord.Embed(
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
			return await ctx.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban the server owner.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if ctx.author.top_role.position < user.top_role.position:
			return await ctx.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban someone with a higher role than you.",
			)
			.set_author(
				name = "Killer Bot | Moderation",
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)
		if ctx.author.top_role.position == user.top_role.position:
			return await ctx.send(embed = nextcord.Embed(
				description = "Sorry, you can't ban someone with the same role as you.",
			)
			.set_author(
				name = "Killer Bot | Moderation",
				icon_url = self.bot.user.avatar.url
			),
			delete_after = 15
		)

		embed = nextcord.Embed(
			description = f"{user} has been banned from {ctx.guild.name}!",
			color = nextcord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.add_field(name = "Moderator", value = ctx.author.mention, inline = True)
		embed.add_field(name = "Duration", value = "Permanent", inline = True)
		embed.add_field(name = "Reason", value = reason, inline = False)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await ctx.send(embed = embed)
		await user.ban(reason = reason)

		print("{} has been banned in {} by {} for {}.".format(user, ctx.author.guild.id, ctx.author, reason))

	# Unban Command

	@commands.command(description = "Unban a user.")
	@commands.has_permissions(ban_members = True)
	async def unban(self, ctx : commands.Context, id : int):
		user = await self.bot.fetch_user(id)

		if user == None:
			return await ctx.send(embed = nextcord.Embed(
				description = "Please provide the user id of the user that you want to unban.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)
		if user == ctx.author:
			return await ctx.send(embed = nextcord.Embed(
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
			description = f"{user} has been unbanned from {ctx.guild.name}!",
			color = nextcord.Color.green(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.add_field(name = "Moderator", value = ctx.author.mention, inline = True)

		embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

		await ctx.send(embed = embed)
		print("{} has been unbanned in {} by {}.".format(user, ctx.author.guild.id, ctx.author))
		await ctx.guild.unban(user)

	# Clear Command
	
	@commands.command(description = "Clear messages in a specified channel.", aliases = ["purge"])
	@commands.has_permissions(manage_messages = True)
	async def clear(self, ctx : commands.Context, limit : int = 5, channel : nextcord.TextChannel = None):
		if channel == None:
			channel = ctx.channel

		if limit < 100:
			embed = nextcord.Embed(
				description = f"{ctx.author} has cleared {limit} messages in {channel}.",
				color = nextcord.Color.og_blurple()
			)

			embed.set_author(name = "Killer Bot | Moderation", icon_url = self.bot.user.avatar.url)

			await channel.purge(limit = limit)
			await ctx.send(embed = embed)

		else:
			await ctx.send(embed = nextcord.Embed(
				description = "Please provide a number less than 100.",
				color = nextcord.Color.dark_gray()
			)
			.set_author(
				name = "Killer Bot | Moderation", 
				icon_url = self.bot.user.avatar.url
			), 
			delete_after = 15
		)

def setup(bot : commands.Bot):
	bot.add_cog(ModerationCommands(bot))