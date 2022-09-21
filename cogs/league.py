import nextcord 
import cassiopeia as cass
import os
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import arrow

from riotwatcher import LolWatcher
from cassiopeia import *

from nextcord.ext import commands
from helpers.embedder import EmbedBuilder

from helpers.utils import *
from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID, CASSIOPEIA_CONFIG, RIOT_TOKEN
from helpers.logger import Logger
from helpers.league_utils import *
from helpers.scraper import Parser, LeagueScraper

from datetime import datetime
from pytz import timezone

from pandas.plotting import table

cass.set_riot_api_key(RIOT_TOKEN)
cass.apply_settings(CASSIOPEIA_CONFIG)

logger = Logger()
watcher = LolWatcher(RIOT_TOKEN)

# League Cog
class LeagueCommands(commands.Cog, name = "League Of Legends", description = "League of Legends commands."):

	# League Constructor
	def __init__(self, bot : commands.Bot):
		self.bot : commands.Bot = bot

	# Profile Command
	@nextcord.slash_command(
		name = "profile", 
		description = "Profile command.",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def profile(
		self, 
		interaction : nextcord.Interaction, 
		user : str = nextcord.SlashOption(
			name = "summoner",
			description = "The user to get the profile of.",
			required = False,
			default = "Josedeodo"
		), 
		region : str = nextcord.SlashOption(
			name = "region",
			description = "The region to get the profile of.",
			required = False,
			default = "NA",
			choices = REGIONS
		)
	):

		await interaction.response.defer()

		try:
			summoner = await get_summoner_or_fail(user = user, region = region)
		except ValueError:
			await interaction.send("The summoner you entered doesn't exist, at least in that region.")
			return

		embed = nextcord.Embed(
			description = f"{user}'s Profile | Level {summoner.level}",
			color = nextcord.Color.purple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)

		entries = summoner.league_entries		
		try:
			solo_duo_rank = entries.fives.league.tier
			solo_duo_division = entries.fives.division
			solo_duo_lps = entries.fives.league_points
			solo_duo_emoji = get_rank_emoji(str(solo_duo_rank))
			solo_duo_wins = entries.fives.wins
			solo_duo_losses = entries.fives.losses
			solo_duo_total = solo_duo_wins + solo_duo_losses
			solo_duo_winrate = (solo_duo_wins * 100) / (solo_duo_total)

			embed.add_field(name = "> Ranked Solo/Duo", value = f"**Rank**: {solo_duo_emoji} `{solo_duo_rank} {solo_duo_division} {solo_duo_lps} LP`\n**Total Games**: `{solo_duo_total}`\n**Wins**: `{solo_duo_wins}`\n**Losses**: `{solo_duo_losses}`\n**Win Rate**: `{solo_duo_winrate:.2f}%`", inline = True)
		except ValueError:
			embed.add_field(name = "> Ranked Solo/Duo", value = f"Rank: <:Unranked:991907027150458881> `Unranked`", inline = True)
			
		try:
			flex_rank = entries.flex.league.tier
			flex_division = entries.flex.division
			flex_lps = entries.flex.league_points
			flex_emoji = get_rank_emoji(str(flex_rank))
			flex_wins = entries.flex.wins
			flex_losses = entries.flex.losses
			flex_total = flex_wins + flex_losses
			flex_winrate = (flex_wins * 100) / (flex_total)

			embed.add_field(name = "> Ranked Flex", value = f"**Rank**: {flex_emoji} `{flex_rank} {flex_division} {flex_lps} LP`\n**Total Games**: `{flex_total}`\n**Wins**: `{flex_wins}`\n**Losses**: `{flex_losses}`\n**Win Rate**: `{flex_winrate:.2f}%`", inline = True)
		except ValueError:
			embed.add_field(name = "> Ranked Flex", value = f"**Rank**: <:Unranked:991907027150458881> `Unranked`", inline = True)

		masteries = cass.get_champion_masteries(summoner = summoner, region = region)

		best = masteries.filter(lambda cm: cm.level >= 5)
		m7 = masteries.filter(lambda cm: cm.level == 7)
		m6 = masteries.filter(lambda cm: cm.level == 6)
		m5 = masteries.filter(lambda cm: cm.level == 5)

		p = []
		for i in masteries:
			p.append(masteries[i].points)

		total_points = sum(p)
		total_points = human_format(int(total_points))

		counter = 0
		champions = ""

		if len(best) == 0:
			champions = "No champions with mastery level 5 or higher."
		
		for cm in best:
			mastery_emoji = get_mastery_emoji(int(cm.level))
			champion_emoji = get_champion_emoji_by_id(str(cm.champion.id))
			points = human_format(cm.points)
			counter += 1
			if counter <= 5:
				champions += f"{counter}) {mastery_emoji} {champion_emoji} {cm.champion.name} - **{str(points)}**\n"
			else:
				break

		embed.add_field(name = "> Best Champions", value = f"{champions}", inline = False)
		embed.add_field(name = "> Mastery Stats", value = f"{len(m7)}x <:mastery7:993688390723715172> {len(m6)}x <:mastery6:993688366317043772> {len(m5)}x <:mastery5:993688341063159860>\nTotal Mastery Points: {total_points}", inline = True)
	
		embed.set_author(name = "Killer Bot | League Of Legends Profile", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)
		embed.set_thumbnail(url = summoner.profile_icon.url)

		await interaction.send(embed = embed)
			
	# Last Match Command
	@nextcord.slash_command(
		name = "lastmatch",
		description = "Shows the last match of a summoner.",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def lastmatch(
		self, 
		interaction : nextcord.Interaction,
		user : str = nextcord.SlashOption(
			name = "summoner",
			description = "The summoner name to get the last match of.",
			required = True
		),
		region : str = nextcord.SlashOption(
			name = "region",
			description = "The region of the summoner.",
			required = True,
			choices = REGIONS,
			default = "NA"
		)
	):
		await interaction.send(f"> Searching for summoner `{user}` in region `{region}`...")
		# Getting summoner, his match history and the last match
		try:
			summoner = await get_summoner_or_fail(user = user, region = region)
		except ValueError:
			await interaction.edit_original_message(content = "> The summoner you entered doesn't exist, at least in that region.")
			return	
		match_history = MatchHistory(puuid = summoner.puuid, continent = summoner.region.continent)
		if len(match_history) == 0:
			await interaction.edit_original_message(content = "> The summoner you entered doesn't have any matches.")
			return	
		last_match: Match = match_history[0]

		builder = EmbedBuilder(self.bot)
		embed = await builder.match_embed(last_match, summoner, region)	
		embed.set_footer(text = f"Requested by {interaction.user} • Match ID: {last_match.id}", icon_url = interaction.user.avatar.url)

		# Sending embed
		await interaction.edit_original_message(content = None, embed = embed)

	# Champion List Command
	@nextcord.slash_command(
		name = "championlist",
		description = "Shows the list of champions.",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def championlist(self, interaction : nextcord.Interaction, region : str = nextcord.SlashOption(
		name = "region",
		description = "The region of the summoner.",
		required = True,
		choices = REGIONS, 
		default = "NA"
	)):
		await interaction.response.defer(with_message = True)

		# Creating embed
		embed = nextcord.Embed(
			title = "Champion List",
			color = nextcord.Color.blue(),
			timestamp = datetime.now()
		)
		# All champions
		champions = cass.get_champions(region)
		# Champions message
		champions_message = ""
		champions_dict = {}
		count = 0
		for champion in champions:
			count += 1
			champions_message += f"{count}. {champion.name}\n"
			champions_dict[count] = {
				"name": champion.name,
				"id": champion.id
			}
		# Json file
		with open(f"champions_{region.lower()}.json", "w") as file:
			json.dump(champions_dict, file, indent = 4)
		# Chunk message
		champions_message = chunk(champions_message, 1024)
		# Splitting Content
		if len(champions_message) > 1:
			embed.add_field(name = "Champion List", value = f"{champions_message[0]}", inline = False)
			for i in range(1, len(champions_message)):
				embed.add_field(name = "Champion List Continued", value = f"{champions_message[i]}", inline = False)

		else:
			embed.add_field(name = "Champion List", value = f"{champions_message[0]}", inline = False)

		# Author, footer and thumbnail
		embed.set_author(name = "Killer Bot | League Of Legends", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		# Sending embed
		await interaction.send(embed = embed)

	# Champ Command
	@nextcord.slash_command(
		name = "champ", 
		description = "Show champion analytics by U.GG",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def champ(
		self, 
		interaction: nextcord.Interaction, 
		champion: str = nextcord.SlashOption(
			name = "champion",
			description = "Champion name",
			required = True,
			default = "Aatrox" 
		), 
		region: str = nextcord.SlashOption(
			name = "region",
			description = "Region filter.",
			required = False,
			default = "NA",
			choices = REGIONS + ["world"]
		), 
		elo: str = nextcord.SlashOption(
			name = "elo",
			description = "Elo filter.",
			required = False,
			default = "all",
			choices = RANKS
		),
		role: str = nextcord.SlashOption(
			name = "role",
            description = "Role filter.",
			required = False,
			choices = ROLES
		)
	):

		await interaction.response.defer()

		champ = Champion(name = champion.title(), region = "NA")

		parser = Parser()
		scraper = LeagueScraper(parser)
		analytics = scraper.get_champion_analytics(str(champion), str(region), str(elo), str(role))

		tier = analytics[0]
		win_rate = analytics[1]
		ranking = analytics[2]
		pick_rate = analytics[3]
		ban_rate = analytics[4]
		matches = analytics[5]

		embed_color = get_embed_color(tier)
		search_elo = from_normal_to_gg(elo)
		embed_elo = from_gg_to_normal(search_elo)

		embed = nextcord.Embed(
			title = f"{champion.title()} Champion Analytics",
			description = f"Displaying statistics for `{champion.title()}`\nElo: `{embed_elo.capitalize()}`\nRegion: `{region.upper()}`\nRole: `{role.upper()}`\n",
			color = int(embed_color, 16),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)
	
		embed.add_field(name = "Champion Analytics (U.GG)", value = f"Tier: `{tier}`\nWin Rate: `{win_rate}`\nRanking: `{ranking}`\nPick Rate: `{pick_rate}`\nBan Rate: `{ban_rate}`\nMatches: `{matches}`", inline = False)
		embed.set_author(name = "Killer Bot | League Of Legends", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		embed.set_thumbnail(url = champ.image.url)

		await interaction.send(embed = embed)

	# RandomChamp Command
	@nextcord.slash_command(
		name = "randomchamp", 
		description = "Choose a random champion.",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def randomchamp(self, interaction : nextcord.Interaction):
		champs = cass.get_champions(region = "NA")
		
		champ = random.choice(champs)

		embed = nextcord.Embed(
			title = f"Champion: {champ.name}",
			color = nextcord.Color.random(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)

		embed.set_image(url = champ.image.url)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Randomizer", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		await interaction.send(embed = embed)

def setup(bot):
	bot.add_cog(LeagueCommands(bot))