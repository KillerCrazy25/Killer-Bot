from traceback import print_exception
import nextcord, os
from nextcord.ext import commands

from datetime import datetime
from pytz import timezone

from helpers.embedder import EmbedBuilder
from helpers.config import ERROR_CHANNEL_ID, MAIN_GUILD_ID, TESTING_GUILD_ID, DEVELOPER_ID
from helpers.logger import Logger

logger = Logger()

# Error Handler Cog
class ErrorHandler(commands.Cog):

	# Error Handler Constructor
	def __init__(self, bot : commands.Bot):
		self.bot = bot
		self.developer = bot.get_user(DEVELOPER_ID)	
		self.builder = EmbedBuilder(bot)

	@commands.Cog.listener()
	async def on_application_command_error(self, interaction: nextcord.Interaction, error: nextcord.DiscordException):
		if isinstance(error, commands.errors.CheckFailure):
			embed = await self.builder.error_embed("Check Failure", error)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.BotMissingAnyRole):
			roles = {
				"Missing Role": error.missing_roles
			}
			embed = await self.builder.error_embed("Bot Missing Any Role", error, roles)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.BotMissingRole):
			role = {
				"Missing Role": error.missing_role
			}
			embed = await self.builder.error_embed("Bot Missing Role", error, role)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.BotMissingPermissions):
			permissions = {
				"Missing Permissions": error.missing_permissions
			}
			embed = await self.builder.error_embed("Bot Missing Permissions", error, permissions)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.MissingAnyRole):
			roles = {
				"Missing Role": error.missing_roles
			}
			embed = await self.builder.error_embed("Missing Any Role", error, roles)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.MissingRole):
			role = {
				"Missing Role": error.missing_role
			}
			embed = await self.builder.error_embed("Missing Role", error, role)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.MissingPermissions):
			permissions = {
				"Missing Permissions": error.missing_permissions
			}
			embed = await self.builder.error_embed("Missing Permissions", error, permissions)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.ChannelNotFound):
			channel = {
				"Channel": error.argument
			}
			embed = await self.builder.error_embed("Channel Not Found", error, channel)

			return await interaction.send(embed = embed, ephemeral = True)
		elif isinstance(error, commands.errors.BadArgument):
			args = {
				"Argument(s)": error.args
			}
			embed = await self.builder.error_embed("Bad Argument", error, args)

			return await interaction.send(embed = embed, ephemeral = True)
		else:
			embed = await self.builder.error_embed("Unknown Error", error)

			return await interaction.send(embed = embed, ephemeral = True)

		

def setup(bot):
	bot.add_cog(ErrorHandler(bot))