from traceback import print_exception
import nextcord, os
from nextcord.ext import commands

from datetime import datetime
from pytz import timezone

from helpers.embed_builder import EmbedBuilder
from helpers.config import ERROR_CHANNEL_ID, MAIN_GUILD_ID, TESTING_GUILD_ID, DEVELOPER_ID
from helpers.logger import Logger

logger = Logger()

# Error Handler Cog
class ErrorHandler(commands.Cog):

	# Error Handler Constructor
	def __init__(self, bot : commands.Bot):
		self.bot = bot

	# Ready Event
	@commands.Cog.listener()
	async def on_ready(self):
		self.developer = self.bot.get_user(DEVELOPER_ID)
		self.error_channel = self.bot.get_channel(ERROR_CHANNEL_ID)

	# Command Error Event
	@commands.Cog.listener()
	async def on_command_error(self, ctx : commands.Context, error):
		
		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Command Not Found Error
		if isinstance(error, commands.CommandNotFound):
			print(f"Command not found: {ctx.command}")
			return

		# Missing Any Role Error
		elif isinstance(error, commands.MissingAnyRole):
			embed = await builder.error_embed()

			roles = ", ".join(error.missing_roles)

			embed.add_field(name = "Error", value = f"You are missing at least one of the required roles: `{roles}`")

			return await ctx.send(embed = embed, delete_after = 10)

		# Missing Role Error
		elif isinstance(error, commands.MissingRole):
			embed = await builder.error_embed()

			embed.add_field(name = "Error", value = f"You need the role `{error.missing_role}` to run this command.")

			return await ctx.send(embed = embed, delete_after = 10)

		# Missing Permissions Error
		elif isinstance(error, commands.MissingPermissions):
			embed = await builder.error_embed()

			permissions = ", ".join(error.missing_permissions)

			embed.add_field(name = "Error", value = f"You are missing `{permissions}` permission(s) to run this command.")

			return await ctx.send(embed = embed, delete_after = 10)

		# Bot Missing Any Role Error
		elif isinstance(error, commands.BotMissingAnyRole):
			embed = await builder.error_embed()

			roles = ", ".join(error.missing_roles)

			embed.add_field(name = "Error", value = f"I'm missing at least one of the required roles: `{roles}`")

			return await ctx.send(embed = embed, delete_after = 10)

		# Bot Missing Role Error
		elif isinstance(error, commands.BotMissingRole):
			embed = await builder.error_embed()

			embed.add_field(name = "Error", value = f"I need the role `{error.missing_role}` to run this command.")

			return await ctx.send(embed = embed, delete_after = 10)

		# Bot Missing Permissions Error
		elif isinstance(error, commands.BotMissingPermissions):
			embed = await builder.error_embed()

			permissions = ", ".join(error.missing_permissions)

			embed.add_field(name = "Error", value = f"I'm missing `{permissions}` permission(s) to run this command.")

			return await ctx.send(embed = embed, delete_after = 10)

		# Command On Cooldown Error
		elif isinstance(error, commands.CommandOnCooldown):
			embed = await builder.error_embed()

			embed.add_field(name = "Error", value = f"This command is under cooldown. Please retry again in: **{error.retry_after:.1f} seconds**")

			return await ctx.send(embed = embed, delete_after = 10)

		# Missing Required Argument Error
		elif isinstance(error, commands.MissingRequiredArgument):
			embed = await builder.error_embed()

			embed.add_field(name = "Error", value = f"You are missing some required arguments to run this commands: `{error.param.name}`")

			return await ctx.send(embed = embed, delete_after = 10)

		# No Private Message Error
		elif isinstance(error, commands.NoPrivateMessage):
			embed = await builder.error_embed()

			embed.add_field(name = "Error", value = "This command isn't runnable outside a guild!")

			return await ctx.send(embed = embed, delete_after = 10)

		# Private Message Only Error
		elif isinstance(error, commands.PrivateMessageOnly):
			embed = await builder.error_embed()

			embed.add_field(name = "Error", value = "This command isn't runnable outside a private message!")

			return await ctx.send(embed = embed, delete_after = 10)

		# Other Errors
		else:
			embed = await builder.error_embed()

			error_id = ctx.message.id

			embed.add_field(name = "Error", value = "Unknown error has ocurred. The error has been sent to the Bot Developer.")

			print(f"Ignoring exception in command {ctx.command}\nError ID: {error_id}")

			with open(f"{error_id}.txt", 'a') as f:
				f.write(f"Error in command {ctx.command} in guild {ctx.guild.name}\n\n{str(error)}\n\nDate: {datetime.now(tz = timezone('US/Eastern'))}\nError ID: {error_id}")

			with open(f"{error_id}.txt", 'rb') as f:
				await self.error_channel.send(f"An error has ocurred in command `{ctx.command}` in guild `{ctx.guild.name}`.", file = nextcord.File(f, f"{error_id}.txt"))

			embed.set_footer(text = f"Error ID: {error_id}")

			os.remove(f"{error_id}.txt")

			return await ctx.send(embed = embed)

	@commands.Cog.listener()
	async def on_application_command_error(self, interaction : nextcord.Interaction, error : nextcord.DiscordException):
		
		# Embed Builder
		builder = EmbedBuilder(self.bot)

		# Command Not Found Error
		if isinstance(error, commands.CommandNotFound):
			logger.warning(f"Command not found: {interaction.command}")
			return

		logger.error(f"{error}")

		return await interaction.send(embed = await builder.error_embed())

def setup(bot):
	bot.add_cog(ErrorHandler(bot))