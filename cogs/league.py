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

from helpers.utils import *
from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID, CASSIOPEIA_CONFIG, RIOT_TOKEN
from helpers.logger import Logger
from helpers.league_utils import *

from datetime import datetime
from pytz import timezone

from pandas.plotting import table

cass.set_riot_api_key(RIOT_TOKEN)
cass.apply_settings(CASSIOPEIA_CONFIG)

logger = Logger()
watcher = LolWatcher(RIOT_TOKEN)

# League Cog
class LeagueCommands(commands.Cog):

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

		summoner = Summoner(name = user, region = region)

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

			embed.add_field(name = "> Ranked Solo/Duo", value = f"Rank: {solo_duo_emoji} {solo_duo_rank} {solo_duo_division} {solo_duo_lps} LP\nTotal Games: {solo_duo_total}\nWins: {solo_duo_wins}\nLosses: {solo_duo_losses}\nWin Rate: {solo_duo_winrate:.2f}%", inline = True)
		except ValueError:
			solo_duo_emoji = "<:Unranked:991907027150458881>"

			embed.add_field(name = "> Ranked Solo/Duo", value = f"Rank: {solo_duo_emoji} Unranked", inline = True)
			
		try:
			flex_rank = entries.flex.league.tier
			flex_division = entries.flex.division
			flex_lps = entries.flex.league_points
			flex_emoji = get_rank_emoji(str(flex_rank))
			flex_wins = entries.flex.wins
			flex_losses = entries.flex.losses
			flex_total = flex_wins + flex_losses
			flex_winrate = (flex_wins * 100) / (flex_total)

			embed.add_field(name = "> Ranked Flex", value = f"Rank: {flex_emoji} {flex_rank} {flex_division} {flex_lps} LP \nTotal Games: {flex_total}\nWins: {flex_wins}\nLosses: {flex_losses}\nWin Rate: {flex_winrate:.2f}%", inline = True)
		except ValueError:
			flex_emoji = "<:Unranked:991907027150458881>"

			embed.add_field(name = "> Ranked Flex", value = f"Rank: {flex_emoji} Unranked", inline = True)

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
		
		for cm in best:
			mastery_emoji = get_mastery_emoji(int(cm.level))
			champion_emoji = get_champion_emoji_by_id(str(cm.champion.id))
			points = human_format(cm.points)
			counter += 1
			if counter <= 5:
				champions += f"{counter}) {mastery_emoji} {champion_emoji} {cm.champion.name} - **{str(points)}**\n"
			else:
				break

		champs_ = []
		points_ = []
		counter_ = 0

		for i in best:
			counter_ +=1
			if counter_ <= 5:
				champs_.append(i.champion.name)
				points_.append(i.points)
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
			required = True
		)
	):
		await interaction.response.defer()
		# Getting summoner, his match history and the last match
		summoner = Summoner(name = user, region = region)
		match_history = MatchHistory(puuid = summoner.puuid, continent = summoner.region.continent)
		last_match : Match = match_history[0]
		# Getting teams and teams information
		blue_team = get_match_teams(last_match.id, region)[0]
		red_team = get_match_teams(last_match.id, region)[1]
		blue_info = get_team_info(last_match.id, region, 100)
		red_info = get_team_info(last_match.id, region, 200)
		# Getting team's players
		blue_team_players = get_team_players(blue_team)
		red_team_players = get_team_players(red_team)
		# Getting team's champions
		blue_champions = get_team_champions(blue_team)
		red_champions = get_team_champions(red_team)
		# Getting team's bans
		blue_bans = get_team_bans(blue_info)
		red_bans = get_team_bans(red_info)
		# Getting match winner
		winner = get_winner_team(last_match.id, region)
		# Getting match queue and map
		map_ = get_map_name(get_map_id(last_match.id, region))
		queue = last_match.queue.value.replace("_", " ").title()

		blue_stats = get_match_stats(last_match)[0]
		red_stats = get_match_stats(last_match)[1]

		# get participant.id == summoner.id
		participant = next(filter(lambda p: p.summoner.id == summoner.id, last_match.participants), None)

		# Red team champions message
		red_message = ""
		for player, champion, stats in zip(red_team_players, red_champions, red_stats):
			emoji = get_champion_emoji_by_id(str(champion.id))
			cm = f"{emoji + ' __**' + champion.name + '**__' if player.name == summoner.name else emoji + ' ' + champion.name}"
			pm = f"{'__**' + player.name + '**__' if player.name == summoner.name else player.name}"
			sm = f"{'**' + str(stats.kills) + '**/**' + str(stats.deaths) + '**/**' + str(stats.assists) + '** | **' + str(stats.total_minions_killed) + 'cs** | **' + human_format(stats.total_damage_dealt_to_champions) + ' DMG**' if player.name == summoner.name else str(stats.kills) + '/' + str(stats.deaths) + '/' + str(stats.assists) + ' | ' + str(stats.total_minions_killed) + ' cs | ' + human_format(stats.total_damage_dealt_to_champions) + ' DMG'}"
			red_message += f"{cm} - {pm} ({sm})\n"
		# Blue team champions message
		blue_message = ""
		for player, champion, stats in zip(blue_team_players, blue_champions, blue_stats):
			emoji = get_champion_emoji_by_id(str(champion.id))
			cm = f"{emoji + ' __**' + champion.name + '**__' if player.name == summoner.name else emoji + ' ' + champion.name}"
			pm = f"{'__**' + player.name + '**__' if player.name == summoner.name else player.name}"
			sm = f"{'**' + str(stats.kills) + '**/**' + str(stats.deaths) + '**/**' + str(stats.assists) + '** | **' + str(stats.total_minions_killed) + 'cs** | **' + human_format(stats.total_damage_dealt_to_champions) + ' DMG**' if player.name == summoner.name else str(stats.kills) + '/' + str(stats.deaths) + '/' + str(stats.assists) + ' | ' + str(stats.total_minions_killed) + ' cs | ' + human_format(stats.total_damage_dealt_to_champions) + ' DMG'}"
			blue_message += f"{cm} - {pm} ({sm})\n"
		# Red team bans message
		red_bans_message = ""
		for ban in red_bans:
			if ban != None:
				emoji = get_champion_emoji_by_id(str(ban.id))
				red_bans_message += f"{emoji} {ban.name}\n"
			else:
				red_bans_message += ""
				continue
		# Blue team bans message
		blue_bans_message = ""
		for ban in blue_bans:
			if ban != None:
				emoji = get_champion_emoji_by_id(str(ban.id))
				blue_bans_message += f"{emoji} {ban.name}\n"
			else:
				blue_bans_message += ""
				continue

		# Creating embed
		embed = nextcord.Embed(
			color = nextcord.Color.blue() if participant.stats.win == True else nextcord.Color.red()
		)

		# Summoner info field
		embed.add_field(
			name = "> Summoner Information", 
			value = f"**Name:** `{summoner.name}`\n**Region:** `{region}`",
			inline = False
		)		
		# Match info field
		# create unix timestamp from Arrow object
		embed.add_field(
			name = "> Match Information", 
			value = f"**Map**: `{map_}`\n**Queue**: `{queue}`\n**Date**: <t:{arrow.get(last_match.creation).timestamp}> (<t:{arrow.get(last_match.creation).timestamp}:R>)\n**Duration**: `{last_match.duration}`\n**Result**: `{'Win' if participant.stats.win == True else 'Defeat'}`",
			inline = False
		)
		# Bans info field
		if last_match.queue in cass.data.RANKED_QUEUES:	
			embed.add_field(
				name = "> Blue Team Bans",
				value = blue_bans_message,
				inline = True
			)
			embed.add_field(
				name = "> Red Team Bans",
				value = red_bans_message,
				inline = True
			)
		# Team fields
		embed.add_field(name = "> Blue Team", value = blue_message, inline = False)
		embed.add_field(name = "> Red Team", value = red_message, inline = False)
		# Author, footer and thumbnail
		embed.set_author(name = "Killer Bot | League Of Legends", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user} • Match ID: {last_match.id}", icon_url = interaction.user.avatar.url)
		embed.set_thumbnail(url = summoner.profile_icon.url)

		# Sending embed
		await interaction.send(embed = embed)
		
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
		interaction : nextcord.Interaction, 
		champion : str = nextcord.SlashOption(
			name = "champion",
			description = "Champion name",
			required = True,
			default = "Aatrox" 
		), 
		region : str = nextcord.SlashOption(
			name = "region",
			description = "Region",
			required = True,
			default = "world",
			choices = REGIONS
		), 
		elo : str = nextcord.SlashOption(
			name = "elo",
			description = "Elo",
			required = True,
			default = "all"
		)
	):

		await interaction.response.defer()

		champ = Champion(name = champion, region = "NA")

		analytics = get_champion_analytics(str(champion), str(region), str(elo))

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
			title = f"{champion} Information",
			description = f"Displaying statistics for {champion}\nElo: {embed_elo.capitalize()}\nRegion: {region.upper()}",
			color = int(embed_color, 16),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)
	
		embed.add_field(name = "Champion Analytics (U.GG)", value = f"Tier: {tier}\nWin Rate: {win_rate}\nRanking: {ranking}\nPick Rate: {pick_rate}\nBan Rate: {ban_rate}\nMatches: {matches}", inline = False)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Analytics", icon_url = self.bot.user.avatar.url)
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

	# Tierlist Command
	@nextcord.slash_command(
		name = "tierlist", 
		description = "Show champion tierlist by OP.GG", 
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def tierlist(
		self, 
		interaction : nextcord.Interaction, 
		region : str = nextcord.SlashOption(
			name = "region",
			description = "Region",
			required = True,
			default = "NA",
			choices = REGIONS
		), 
		elo : str = nextcord.SlashOption(
			name = "elo",
			description = "Elo",
			required = True,
			default = "platinum+"
		), 
		role : str = nextcord.SlashOption(
			name = "role",
			description = "Role",
			required = True,
			default = "top"
		)
	):
		embed = nextcord.Embed(
			title = "Champion Tierlist",
			description = f"Data provided by OP.GG",
			color = nextcord.Color.purple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)

		tierlist = get_tierlist(region = region, tier = elo, position = role)	

		df = pd.DataFrame(tierlist)

		df.columns = ["Rank", "Champion", "Tier", "Win Rate", "Pick Rate", "Ban Rate"]

		df.sort_values(by = "Tier", inplace = True, ascending = True)
		df.reset_index(drop = True, inplace = True)
		df.drop(columns = ["Rank"], inplace = True)
		df.index = np.arange(1, len(df) + 1)

		fig, ax = plt.subplots(figsize = (21, 15))

		ax.xaxis.set_visible(False) 
		ax.yaxis.set_visible(False)
		
		ax.set_frame_on(False)
		ax.set_title(
			"Tierlist for " + region.upper() + " | " + elo.capitalize() + " | " + role.capitalize(), 
			fontsize = 30, 
			fontweight = "bold", 
			color = "white"
		)

		table_ = table(ax, df, loc = "upper right", colWidths = [0.17] * len(df.columns))
		table_.auto_set_font_size(False)
		table_.set_fontsize(15)
		table_.scale(1.1, 1.2)

		plt.savefig("tierlist.png", transparent = True)

		file_ = nextcord.File("tierlist.png")

		embed.set_image(url = "attachment://tierlist.png")
		embed.set_author(name = "Killer Bot | League Of Legends Champion Tierlist", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		await interaction.send(embed = embed, file = file_)

		try:
			os.remove(f"tierlist.png")	
		except:
			print(f"tierlist.png was not found on local files.")

def setup(bot):
	bot.add_cog(LeagueCommands(bot))