import nextcord
from nextcord.ext import commands

from helpers.config import DEVELOPER_ID, MAIN_GUILD_ID, TESTING_GUILD_ID
from helpers.logger import Logger

from db.update import add_guild

logger = Logger()

class DeveloperCommands(commands.Cog, name = "Developer Commands", description = "Developer commands that you can't execute :D"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@nextcord.slash_command(name = "developer", description = "Developer only command group.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def developer_command(self, interaction: nextcord.Interaction):
		if interaction.user.id != DEVELOPER_ID:
			return await interaction.send("You are not the bot developer.", ephemeral = True)
	
	@developer_command.subcommand(name = "guilds", description = "Shows the guilds that bot is in.")
	async def guilds(self, interaction: nextcord.Interaction):
		await interaction.send("I'm in " + str(len(self.bot.guilds)) + " guilds\n\n**Guilds**\n" + '\n'.join('Name: ' + guild.name + ' - ' + 'ID: ' + str(guild.id) for guild in self.bot.guilds))

	@developer_command.subcommand(name = "addguild", description = "Manually add guild to database.")
	async def addguild(self, interaction: nextcord.Interaction):
		await add_guild(interaction.guild.id)
		await interaction.send("Successfully added this guild to the database!")

	# Global Message Command
	@developer_command.subcommand(name = "globalmsg", description = "Sends a global message to all servers the bot is in")
	async def globalmsg(
		self, 
		interaction : nextcord.Interaction, 
		*, 
		message : str = nextcord.SlashOption(
			name = "message",
			description = "The message to send",
			required = True
		)
	):
		success = 0
		failed = 0
		owner_success = 0
		owner_failed = 0

		for guild in self.bot.guilds:
			system_channel = guild.system_channel
			if system_channel:
				await system_channel.send(message)
				success += 1
			else:
				logger.info(f"System channel not found for guild {guild.name} ({guild.id}). Trying to send message to server owner...")
				owner = guild.owner
				failed += 1
				try:
					await owner.send(message)
					owner_success += 1
				except Exception as e:
					logger.info(f"Failed to send message to server owner of guild {guild.name} ({guild.id}): {e}")
					owner_failed += 1

		await interaction.send(f"Sent message to {success} guilds with success!\nFailed to send message to {failed} guilds.\nSent message to {owner_success} guilds with success to server owners!\nFailed to send message to {owner_failed} guilds to server owners.")

	# Extension Command
	@developer_command.subcommand(name = "extension", description = "Manage bot extensions.")
	async def extension_subcommand(self, interaction: nextcord.Interaction):
		pass
		
	# Load Subcommand
	@extension_subcommand.subcommand(name = "load", description = "Load extension.")
	async def load_subcommand(
		self, 
		interaction: nextcord.Interaction, 
		extension: str = nextcord.SlashOption(
			name = "extension",
			description = "The extension to load",
			required = True
		)
	):
		if interaction.user.id != DEVELOPER_ID:
			return await interaction.send("You do not have permission to use this command.")

		try:
			self.bot.load_extension(f"cogs.{extension}")
			await interaction.send(f"Successfully loaded `{extension}`!")
		except Exception as e:
			await interaction.send(f"Error loading `{extension}`!\n{e}")

	# Unload Subcommand
	@extension_subcommand.subcommand(name = "unload", description = "Unload extension.")
	async def unload_subcommand(
		self,
		interaction: nextcord.Interaction, 
		extension: str = nextcord.SlashOption(
			name = "extension",
			description = "The extension to unload",
			required = True
		)
	):
		if interaction.user.id != DEVELOPER_ID:
			return await interaction.send("You do not have permission to use this command.")

		try:
			self.bot.unload_extension(f"cogs.{extension}")
			await interaction.send(f"Successfully unloaded `{extension}`!")
		except Exception as e:
			await interaction.send(f"Error unloading `{extension}`!\n{e}")

	# Reload Subcommand
	@extension_subcommand.subcommand(name = "reload", description = "Reload extension.")
	async def reload_subcommand(
		self,
		interaction: nextcord.Interaction, 
		extension: str = nextcord.SlashOption(
			name = "extension",
			description = "The extension to reload",
			required = True
		)
	):
		if interaction.user.id != DEVELOPER_ID:
			return await interaction.send("You are not the bot developer.")

		try:
			self.bot.reload_extension(f"cogs.{extension}")
			await interaction.send(f"Successfully reloaded `{extension}`!")
		except Exception as e:
			await interaction.send(f"Error reloading `{extension}`!")
			logger.error(e)

def setup(bot: commands.Bot):
	bot.add_cog(DeveloperCommands(bot))