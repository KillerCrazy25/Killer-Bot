import random
import discord, os
from discord.ext import commands, bridge

from datetime import datetime
from pytz import timezone

from utils.config import ERROR_CHANNEL_ID, MAIN_GUILD_ID, TESTING_GUILD_ID, DEVELOPER_ID

class ErrorHandler(commands.Cog):

	def __init__(self, bot : bridge.Bot):
		self.bot = bot

	async def embed_constructor(self):
		embed = discord.Embed(
			title = "Something went wrong trying to run this command.",
			color = discord.Color.dark_gray(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)

		embed.set_author(name = "Killer Bot | Error", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = "This message will be deleted in 10 seconds...")

		return embed

	@commands.Cog.listener()
	async def on_ready(self):
		self.developer = self.bot.get_user(DEVELOPER_ID)
		self.error_channel = self.bot.get_channel(ERROR_CHANNEL_ID)
		print("Developer ID: ", self.developer)

	@commands.Cog.listener()
	async def on_command_error(self, ctx : bridge.BridgeContext, error):

		if isinstance(error, commands.CommandNotFound):
			print(f"Command not found: {ctx.command}")
			return

		elif isinstance(error, commands.MissingAnyRole):
			embed = await self.embed_constructor()

			roles = ", ".join(error.missing_roles)

			embed.add_field(name = "Error", value = f"You are missing at least one of the required roles: `{roles}`")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.MissingRole):
			embed = await self.embed_constructor()

			embed.add_field(name = "Error", value = f"You need the role `{error.missing_role}` to run this command.")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.MissingPermissions):
			embed = await self.embed_constructor()

			permissions = ", ".join(error.missing_permissions)

			embed.add_field(name = "Error", value = f"You are missing `{permissions}` permission(s) to run this command.")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.BotMissingAnyRole):
			embed = await self.embed_constructor()

			roles = ", ".join(error.missing_roles)

			embed.add_field(name = "Error", value = f"I'm missing at least one of the required roles: `{roles}`")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.BotMissingRole):
			embed = await self.embed_constructor()

			embed.add_field(name = "Error", value = f"I need the role `{error.missing_role}` to run this command.")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.BotMissingPermissions):
			embed = await self.embed_constructor()

			permissions = ", ".join(error.missing_permissions)

			embed.add_field(name = "Error", value = f"I'm missing `{permissions}` permission(s) to run this command.")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.CommandOnCooldown):
			embed = await self.embed_constructor()

			embed.add_field(name = "Error", value = f"This command is under cooldown. Please retry again in: **{error.retry_after:.1f} seconds**")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.MissingRequiredArgument):
			embed = await self.embed_constructor()

			embed.add_field(name = "Error", value = f"You are missing some required arguments to run this commands: `{error.param.name}`")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.NoPrivateMessage):
			embed = await self.embed_constructor()

			embed.add_field(name = "Error", value = "This command isn't runnable outside a guild!")

			return await ctx.respond(embed = embed, delete_after = 10)

		elif isinstance(error, commands.PrivateMessageOnly):
			embed = await self.embed_constructor()

			embed.add_field(name = "Error", value = "This command isn't runnable outside a private message!")

			return await ctx.respond(embed = embed, delete_after = 10)

		else:
			embed = await self.embed_constructor()

			error_id = ctx.message.id

			embed.add_field(name = "Error", value = "Unknown error has ocurred. The error has been sent to the Bot Developer.")

			print(f"Ignoring exception in command {ctx.command}\nError ID: {error_id}")

			with open(f"{error_id}.txt", 'a') as f:
				f.write(f"Error in command {ctx.command} in guild {ctx.guild.name}\n\n{str(error)}\n\nDate: {datetime.now(tz = timezone('US/Eastern'))}\nError ID: {error_id}")

			with open(f"{error_id}.txt", 'rb') as f:
				await self.error_channel.send(f"An error has ocurred in command `{ctx.command}` in guild `{ctx.guild.name}`.", file = discord.File(f, f"{error_id}.txt"))

			embed.set_footer(text = f"Error ID: {error_id}")

			os.remove(f"{error_id}.txt")

			return await ctx.send(embed = embed)

	@bridge.bridge_command(guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def testing(self, ctx : bridge.BridgeContext, color: discord.Color):
		await ctx.reply("si")

def setup(bot):
	bot.add_cog(ErrorHandler(bot))