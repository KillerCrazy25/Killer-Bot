from nextcord import Interaction
from helpers.config import DEVELOPER_ID

def is_developer(interaction: Interaction):
	if interaction.user.id == DEVELOPER_ID:		
		return True
	else:
		return False