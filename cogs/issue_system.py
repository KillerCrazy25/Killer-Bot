import nextcord
import random
import string

from nextcord.ext import commands

from db.update import add_issue, update_issue
from db.read import get_all_issues, get_issue

from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID, ISSUES_CHANNEL_ID
from helpers.utils import trim

PRIORITIES = [
	"High- Security compromised",
	"Medium - Command not working",
	"Low - Grammar related, minimal bugs"
]

PRIORITY_COLORS = {
	"High- Security compromised": "FF0000",
	"Medium - Command not working": "FFF100",
	"Low - Grammar related, minimal bugs": "00FFFA"
}

SEARCH_FILTERS = [
	"Guild",
	"User",
	"Priority",
	"Status",
	"Description"
]

SEARCH_INDEX = {
	"Guild": 0,
	"User": 1,
	"Priority": 2,
	"Status": 3,
	"Description": 4
}

class ReopenIssueButton(nextcord.ui.Button):
	def __init__(self, issue_id):
		self.issue_id = issue_id
		super().__init__(label = "Reopen", style = nextcord.ButtonStyle.blurple)

	async def callback(self, interaction: nextcord.Interaction):
		for child in self.view.children:
			child.disabled = False

		self.view.remove_item(self)
		embed = self.view.message.embeds[0]
		embed.description = f"**__Status__**: Reopened by `{interaction.user}`"

		await self.view.message.edit(view = self.view, embed = embed)
		await update_issue(self.issue_id, f"Reopened by `{interaction.user}`")
		await interaction.send("Issue has been **__reopened__** with success!")

class IssueButtonsView(nextcord.ui.View):
	def __init__(self, issue_id: str):
		self.issue_id = issue_id
		super().__init__(timeout = None)

	@nextcord.ui.button(label = "Solve", style = nextcord.ButtonStyle.green)
	async def solved_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
		for child in self.children:
			child.disabled = True

		self.add_item(ReopenIssueButton(self.issue_id))
		embed = self.message.embeds[0]
		embed.description = f"**__Status__**: Solved by `{interaction.user}`"

		await self.message.edit(view = self, embed = embed)
		await update_issue(self.issue_id, f"Solved by `{interaction.user}`")
		await interaction.send("Issue marked as **__solved__** with success!")

	@nextcord.ui.button(label = "Close", style = nextcord.ButtonStyle.red)
	async def close_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
		for child in self.children:
			child.disabled = True

		self.add_item(ReopenIssueButton(self.issue_id))
		embed = self.message.embeds[0]
		embed.description = f"**__Status__**: Closed by `{interaction.user}`"

		await self.message.edit(view = self, embed = embed)
		await update_issue(self.issue_id, f"Closed by `{interaction.user}`")
		await interaction.send("Issue marked as **__closed__** with success!")

class IssueSystem(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@nextcord.slash_command(name = "issue", description = "Issue related commands.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def issue_command(self, interaction: nextcord.Interaction):
		pass

	@issue_command.subcommand(name = "create", description = "Report an issue.")
	async def create_subcommand(
		self, 
		interaction: nextcord.Interaction, 
		issue_description: str = nextcord.SlashOption(
			name = "description",
			description = "Description of the issue that you want to report.",
			required = True,
			min_length = 50,
			max_length = 1024
		),
		priority: str = nextcord.SlashOption(
			name = "priority",
			description = "Priority you think the issue needs",
			required = False,
			choices = PRIORITIES
		)
	):
		issues_channel = self.bot.get_channel(ISSUES_CHANNEL_ID)
		if priority:
			embed_color = PRIORITY_COLORS[priority]

		issue_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

		embed = nextcord.Embed(
			title = "New Issue!",
			description = f"**__Status__**: Opened by `{interaction.user}`",
			color = int(embed_color, 16) if priority else None
		)
		embed.add_field(name = "__Issue Description__", value = issue_description, inline = False)
		embed.add_field(name = "__Priority__", value = f"`{priority}`" if priority else "`Not specified`", inline = False)
		embed.add_field(name = "__Reporter Guild Information__", value = f"**Name**: `{interaction.guild.name}`\n**ID**: `{interaction.guild.id}`\n**Owner**: `{interaction.guild.owner}`", inline = True)
		embed.add_field(name = "__Reporter User Information__", value = f"**Name**: `{interaction.user}`\n**ID**: `{interaction.user.id}`")

		embed.set_author(name = "Killer Bot | Issues", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Issue ID: {issue_id}")

		view = IssueButtonsView(issue_id)

		view.message = await issues_channel.send(embed = embed, view = view)
		await add_issue(interaction.guild.id, interaction.user.id, priority if priority else "Not specified", f"Opened by `{interaction.user}`", issue_description, issue_id)
		await interaction.send(f"Your issue has been submited with success! Thanks for reporting and contributing with my development :)\n\nPlease keep direct messages open, when the developer reviews your issue, the bot will send you a message with the response.\n\nIssue ID: `{issue_id}`", ephemeral = True)

	@issue_command.subcommand(name = "view", description = "View information about the given issue.")
	async def view_subcommand(
		self, 
		interaction: nextcord.Interaction,
		issue_id: str = nextcord.SlashOption(
			name = "id", 
			description = "The ID of the issue.",
			required = True
		)
	):	
		issue = await get_issue(issue_id)

		if not issue:
			await interaction.send(f"Couldn't find issue by ID `{issue_id}`", ephemeral = True)
			return

		guild_id = issue[0]
		user_id = issue[1]
		priority = issue[2]
		status = issue[3]
		description = issue[4]
		issue_id_ = issue[5] 

		guild = self.bot.get_guild(guild_id)
		user = self.bot.get_user(user_id)

		if priority:
			embed_color = PRIORITY_COLORS[priority]

		embed = nextcord.Embed(
			title = "Issue Inforamtion",
			description = f"**__Status__**: {status}",
			color = int(embed_color, 16) if priority else None
		)
		embed.add_field(name = "__Issue Description__", value = description, inline = False)
		embed.add_field(name = "__Priority__", value = f"`{priority}`" if priority else "`Not specified`", inline = False)
		embed.add_field(name = "__Reporter Guild Information__", value = f"**Name**: `{guild.name}`\n**ID**: `{guild.id}`\n**Owner**: `{guild.owner}`", inline = True)
		embed.add_field(name = "__Reporter User Information__", value = f"**Name**: `{user}`\n**ID**: `{user.id}`")

		embed.set_author(name = "Killer Bot | Issues", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Issue ID: {issue_id_}")

		await interaction.send(embed = embed)

	@issue_command.subcommand(name = "list", description = "Shows list of all issues.")
	async def list_subcommand(
		self, 
		interaction: nextcord.Interaction, 
		rows: int = nextcord.SlashOption(
			name = "rows",
			description = "The max number of issues that you want to see.",
			required = False,
			min_value = 1,
			max_value = 100
		),
		filter_by: str = nextcord.SlashOption(
			name = "filter",
			description = "The value that will be accompanying the issue ID.",
			required = False,
			choices = SEARCH_FILTERS
		)
	):
		issues = await get_all_issues(rows if rows else 10) # list of tuples
		if len(issues) == 0:
			return await interaction.send("There are no issues reported at the moment.", ephemeral = True)
		
		if filter_by:
			index = SEARCH_INDEX[filter_by]
		else:
			index = 3

		

		embed = nextcord.Embed(
			title = f"Showing `{len(issues)}` issue{'s' if len(issues) > 1 else ''}.",
			color = nextcord.Color.blurple()
		)
		embed.add_field(name = "__ID__", value = "\n".join([f'**{count}.** `{issue[5]}`' for count, issue in enumerate(issues, 1)]), inline = True)
		embed.add_field(name = f"__{filter_by}__" if filter_by else "__Status__", value = "\n".join([f'**{count}.** {trim(str(issue[index]), 50)}' for count, issue in enumerate(issues, 1)]), inline = True)

		embed.set_author(name = "Killer Bot | Issues", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = "Use /issue view <issueId> to see more information about an issue.", icon_url = interaction.user.avatar.url if interaction.user.avatar else None)

		await interaction.send(embed = embed)

def setup(bot: commands.Bot):
	bot.add_cog(IssueSystem(bot))