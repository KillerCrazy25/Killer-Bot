import nextcord 
import cassiopeia as cass
import random

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

cass.set_riot_api_key(RIOT_TOKEN)
cass.apply_settings(CASSIOPEIA_CONFIG)

logger = Logger()

# League Cog
class LeagueCommands(commands.Cog, name = "League Of Legends", description = "League of Legends commands."):

	# League Constructor
	def __init__(self, bot : commands.Bot):
		self.bot = bot

	# Profile Command
	@nextcord.slash_command(
		name = "profile", 
		description = "Profile command.",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def profile_command(
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
	async def lastmatch_command(
		self, 
		interaction: nextcord.Interaction,
		user: str = nextcord.SlashOption(
			name = "summoner",
			description = "The summoner name to get the last match of.",
			required = True
		),
		region: str = nextcord.SlashOption(
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

	# Champ Command
	@nextcord.slash_command(
		name = "champ", 
		description = "Show champion analytics by U.GG",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def champ_command(
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

		champ = Champion(name = champion, region = "NA")

		parser = Parser()
		scraper = LeagueScraper(parser)
		analytics, runes = scraper.get_champion_analytics(str(champion), str(region), str(elo), str(role))

		tier = analytics[0]
		win_rate = analytics[1]
		ranking = analytics[2]
		pick_rate = analytics[3]
		ban_rate = analytics[4]
		matches = analytics[5]

		primary_runes = runes[0]
		secondary_runes = runes[1]
		shards = runes[2]

		primary_rune_names = [parser.format_rune_name(rune) for rune in primary_runes]
		secondary_rune_names = [parser.format_rune_name(rune) for rune in secondary_runes]
		shard_names = [parser.format_shard_name(shard) for shard in shards]

		primary_rune_key = parser.get_rune_tree_by_key(primary_rune_names[0])
		secondary_rune_key = parser.get_rune_tree_by_rune(secondary_rune_names[0])

		primary_rune_key_emoji = parser.get_rune_key_emoji(primary_rune_key)
		secondary_rune_key_emoji = parser.get_rune_key_emoji(secondary_rune_key)

		primary_rune_emojis = [parser.get_rune_emoji(rune) for rune in primary_runes]
		secondary_rune_emojis = [parser.get_rune_emoji(rune) for rune in secondary_runes]
		shard_emojis = [parser.get_shard_emoji(shard) for shard in shards]

		primary_message = ""
		for name, emoji in zip(primary_rune_names, primary_rune_emojis):
			primary_message += f"{emoji} {name}\n"

		secondary_message = ""
		for name, emoji in zip(secondary_rune_names, secondary_rune_emojis):
			secondary_message += f"{emoji} {name}\n"

		shard_message = ""
		for name, emoji in zip(shard_names, shard_emojis):
			shard_message += f"{emoji} {name}\n"

		embed_color = get_embed_color(tier)
		search_elo = from_normal_to_gg(elo)
		embed_elo = from_gg_to_normal(search_elo)

		embed = nextcord.Embed(
			title = f"{champion.title()} Champion Analytics",
			description = f"Displaying statistics for `{champion.title()}`\nElo: `{embed_elo.capitalize()}`\nRegion: `{region.upper()}`\nRole: `{role.upper()}`\n",
			color = int(embed_color, 16),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)
	
		embed.add_field(name = "Statistics", value = f"Tier: `{tier}`\nWin Rate: `{win_rate}`\nRanking: `{ranking}`\nPick Rate: `{pick_rate}`\nBan Rate: `{ban_rate}`\nMatches: `{matches}`", inline = False)
		embed.add_field(name = f"{primary_rune_key_emoji} {primary_rune_key}", value = f"\u2063\n{primary_message}", inline = True)
		embed.add_field(name = f"{secondary_rune_key_emoji} {secondary_rune_key}", value = f"\u2063\n{secondary_message}", inline = True)
		embed.add_field(name = f"<:runesicon:1026324792929964063> **Shards**", value = f"\u2063\n{shard_message}", inline = True)

		embed.set_author(name = "Killer Bot | League Of Legends", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url)

		embed.set_thumbnail(url = champ.image.url)

		await interaction.send(embed = embed)

	@champ_command.on_autocomplete("champion")
	async def champion_autocomplete(self, interaction: nextcord.Interaction, champion: str):
		all_champions = [champion.name for champion in cass.get_champions(region = "NA")]
		if not champion:
			choices = random.choices(all_champions, k = 25)
			await interaction.response.send_autocomplete(choices)
			return

		get_near_champion = [champ for champ in all_champions if champ.lower().startswith(champion.lower())]
		await interaction.response.send_autocomplete(get_near_champion)

	@nextcord.slash_command(
		name = "lolstatus",
		description = "Shows League Of Legends server's status.",
		guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID]
	)
	async def lol_status_command(
		self, 
		interaction: nextcord.Interaction,
		region: str = nextcord.SlashOption(
			name = "region",
			description = "Region that you want to show status of.",
			required = True,
			choices = REGIONS
		),
		locale: str = nextcord.SlashOption(
			name = "locale",
			description = "Language of the response",
			required = True,
			choices = LOCALES
		)
	):
		region_ = from_cass_to_riot(region)
		status = watcher.lol_status_v4.platform_data(region_)
		maintenances = status["maintenances"]
		if len(maintenances) > 0:
			for index, maintenance in enumerate(maintenances, 1):
				for title in maintenance["titles"]:
					if title["locale"] == locale:
						maintenance_content = f"{index}) {title['content']}"

		incidents = status["incidents"]
		if len(incidents) > 0:
			for index, incident in enumerate(incidents, 1):
				for title in incident["titles"]:
					if title["locale"] == locale:
						incident_content = f"{index}) {title['content']}"

		embed = nextcord.Embed(
			title = "League Of Legends Service Status",
			description = f"Displaying status for region `{region}`"
		)
		if len(maintenances) > 0:
			embed.add_field(name = "Maintenances", value = f"{maintenance_content}", inline = False)
		if len(incidents) > 0:
			embed.add_field(name = "Incidents", value = f"{incident_content}", inline = False)

		embed.set_author(name = "Killer Bot | League Of Legends", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {interaction.user}", icon_url = interaction.user.avatar.url if interaction.user.avatar else None)
	
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