import nextcord
import random
import string

from nextcord.ext import commands

from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID
from helpers.gym_data import GYM_MUSCLES

from db.create import create_gym_profile, create_gym_routine
from db.update import update_gym_profile_name, update_gym_profile_weight, update_gym_profile_height
from db.read import get_gym_profile

# Routine Modal Class
class NewRoutineModal(nextcord.ui.Modal):

	# Routine Modal Constructor
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		super().__init__(
			title = "Create your new routine.",
			custom_id = "gym_routine",
			timeout = None
		)

		self.name_field = nextcord.ui.TextInput(
			label = "Name",
			style = nextcord.TextInputStyle.short,
			placeholder = "Best Leg Day Routine",
			required = True,
			min_length = 1,
			max_length = 100
		)

		self.description_field = nextcord.ui.TextInput(
			label = "Description",
			style = nextcord.TextInputStyle.paragraph,
			placeholder = "If you want big legs, try this routine!",
			required = True,
			min_length = 1,
			max_length = 500
		)

		self.muscle_group_field = nextcord.ui.TextInput(
			label = "Muscle Group",
			style = nextcord.TextInputStyle.short,
			placeholder = "Quadriceps, Hamstrings, Glutes and Calves",
			required = True,
			min_length = 1,
			max_length = 250
		)

		self.workout_day_field = nextcord.ui.TextInput(
			label = "Workout Day(s)",
			style = nextcord.TextInputStyle.short,
			placeholder = "Monday",
			required = False,
			min_length = 1,
			max_length = 50
		)

		self.add_item(self.name_field)
		self.add_item(self.description_field)
		self.add_item(self.muscle_group_field)
		self.add_item(self.workout_day_field)

	# Modal Callback
	async def callback(self, interaction: nextcord.Interaction) -> None:
		embed = nextcord.Embed(
			title = "Your routine has been created!",
			color = nextcord.Colour.blurple()
		)

		routine_id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

		embed.add_field(name = "Name", value = self.children[0].value, inline = False)
		embed.add_field(name = "Description", value = f"{self.children[1].value}", inline = False)
		embed.add_field(name = "Muscle Group", value = f"{self.children[2].value}", inline = False)
		embed.add_field(name = "Workout Day(s)", value = f"{self.children[3].value}", inline = False)

		embed.set_author(name = f"Killer Bot | Gym", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Routine ID: {routine_id}")

		await interaction.send(embed = embed)

# Profile Modal Class
class NewProfileModal(nextcord.ui.Modal):

	# Profile Modal Constructor
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		super().__init__(
			title = "Create your gym profile.",
			custom_id = "gym_profile",
			timeout = None
		)

		self.name_field = nextcord.ui.TextInput(
			label = "Name",
			style = nextcord.TextInputStyle.short,
			placeholder = "John Doe",
			required = True,
			min_length = 1,
			max_length = 100
		)

		self.weight_field = nextcord.ui.TextInput(
			label = "Weight (Kilograms)",
			style = nextcord.TextInputStyle.short,
			placeholder = "50",
			required = True,
			min_length = 1,
			max_length = 3	
		)

		self.height_field = nextcord.ui.TextInput(
			label = "Height (Centimeters)",
			style = nextcord.TextInputStyle.short,
			placeholder = "180",
			required = True,
			min_length = 1,
			max_length = 3	
		)

		self.add_item(self.name_field)
		self.add_item(self.weight_field)
		self.add_item(self.height_field)

	# Modal Callback
	async def callback(self, interaction: nextcord.Interaction) -> None:
		embed = nextcord.Embed(
			title = "Your profile has been created!",
			color = nextcord.Colour.blurple()
		)

		embed.add_field(name = "Name", value = self.children[0].value, inline = False)
		embed.add_field(name = "Weight", value = f"{self.children[1].value}kg", inline = False)
		embed.add_field(name = "Height", value = f"{self.children[2].value}cm", inline = False)

		embed.set_author(name = f"Killer Bot | Gym", icon_url = self.bot.user.avatar.url)

		await interaction.send(embed = embed)

class GymCommands(commands.Cog, name = "Gym", description = "This module contains gym related commands."):

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@nextcord.slash_command(name = "gym", description = "Gym related subcommands.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def gym_command(self, interaction: nextcord.Interaction):
		pass

	@gym_command.subcommand(name = "createprofile", description = "Creates a profile with your weight, height, etc")
	async def create_profile_subcommand(self, interaction: nextcord.Interaction):
		await interaction.response.send_modal(NewProfileModal(self.bot))

	@gym_command.subcommand(name = "createroutine", description = "Creates a routine for your workout sessions.")
	async def create_routine_subcommand(self, interaction: nextcord.Interaction):
		await interaction.response.send_modal(NewRoutineModal(self.bot))

	@gym_command.subcommand(name = "muscleinfo", description = "Gives information about the given muscle and some tips / most common exercises to train it.")
	async def muscle_info_subcommand(
		self, 
		interaction: nextcord.Interaction, 
		muscle: str = nextcord.SlashOption(
			name = "muscle", 
			description = "The name of the muscle that you want to see information about.",
			required = True,
			choices = GYM_MUSCLES
		)
	):
		embed = nextcord.Embed(
			title = f"{muscle.capitalize()} Information",
			color = nextcord.Colour.blurple()
		)

		embed.add_field(name = "General Information", value = "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum", inline = False)
		embed.add_field(name = "Exercises", value = "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum", inline = False)
		embed.add_field(name = "Useful Tips", value = "lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum", inline = False)

		await interaction.send(embed = embed)
		
def setup(bot: commands.Bot):
	bot.add_cog(GymCommands(bot))