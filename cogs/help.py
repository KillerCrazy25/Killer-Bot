import nextcord

from nextcord.ext import commands
from nextcord.ext.help_commands.slash import SlashHelpCommand

from typing import Optional, Dict, List

from helpers.utils import trim

class NewHelpCommand(SlashHelpCommand):
	def __init__(self):
		super().__init__(help_command_name = "help", help_command_description = "Shows information about bot commands and modules.")

	async def send_bot_help(self, mapping: Dict[Optional[nextcord.ClientCog], List[nextcord.BaseApplicationCommand]]):
		embed = nextcord.Embed(title = "Bot Commands", color = nextcord.Color.blurple())
		embed.description = (
			f'Use `/help command` for more info on a command.\n'
			f'Use `/help category` for more info on a category.'
		)

		embed_fields = []

		for cog, commands in mapping.items():
			name = "No Category" if cog is None else cog.qualified_name
			filtered = await self.filter_commands(commands, sort = True)
			if filtered:
				value = "\n".join(
					f"</help {c.name}:0>" for c in filtered)
				if cog and cog.description:
					value = f"{cog.description}\n\n{value}"
				# add (name, value) pair to the list of fields
				embed_fields.append((name, value))

		for field in embed_fields:
			embed.add_field(name = field[0], value = field[1], inline = False)

		await self.interaction.send(embed = embed, ephemeral = True)

	async def send_cog_help(self, cog: commands.Cog):
		embed = nextcord.Embed(
			title = f"{cog.qualified_name} Commands", color = nextcord.Color.blurple()
		)
		if cog.description:
			embed.description = cog.description

		filtered = await self.filter_commands(cog.application_commands, sort = True)
		for command in filtered:
			embed.add_field(
				name = f"</help {command.name}:0>",
				value = trim(command.description, 50) or "No description provided.",
				inline = False,
			)

		embed.set_footer(text = f"Use /help [command] for more info on a command.")

		await self.interaction.send(embed = embed, ephemeral = True)

	async def send_command_help(self, command: nextcord.SlashApplicationCommand):
		embed = nextcord.Embed(title = command.qualified_name, description = command.description, color = nextcord.Color.blurple())
		options = command.options.items()
		for name, option in options:
			embed.add_field(
				name = name,
				value = option.description,
				inline = False
			)

		await self.interaction.send(embed = embed, ephemeral = True)

class HelpCog(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.__original_help_command = bot.help_command

		NewHelpCommand().add_to_client(bot)

	def cog_unload(self):
		self.bot.help_command = self.__original_help_command

def setup(bot: commands.Bot):
	bot.add_cog(HelpCog(bot))