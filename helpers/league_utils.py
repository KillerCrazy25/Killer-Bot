import cassiopeia as cass

from riotwatcher import LolWatcher
from cassiopeia import *

from helpers.config import *
from helpers.utils import *
from helpers.league_data import *

from typing import List

watcher = LolWatcher(RIOT_TOKEN)
cass.set_riot_api_key(RIOT_TOKEN)

def get_map_id(match_id : int, region : str) -> str:
	"""Get map id of a match."""
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	match = get_match_info(match_id, region_)
	map_ = match["info"]["mapId"]

	return map_

def get_map_name(map_id : int) -> str:
	"""Get map name of a map id."""
	return MAPS[map_id]

def get_teams_info(match_id : int, region : str) -> List[Dict]:
	"""Get teams info of a match."""
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	match = get_match_info(match_id, region_)
	teams = match["info"]["teams"]

	return teams

def get_team_info(match_id : int, region : str, team_id : int) -> List:
	"""Get team information."""
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	teams = get_teams_info(match_id, region_)
	team = list(filter(lambda t: t['teamId'] == team_id, teams))

	return team

def get_team_bans(team_info : List) -> List[Champion]:
	"""Get bans of a team."""
	info = team_info[0]["bans"]
	bans = []
	for ban in info:
		if ban["championId"] != -1:
			champion = Champion(id = ban["championId"], region = "NA")
			bans.append(champion)
		else:
			bans.append(None)

	return bans

def get_match_history(name : str, region : str):
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	summ = watcher.summoner.by_name(region_, name)	
	match_history = watcher.match.matchlist_by_puuid(region_, summ["puuid"]) 

	return match_history

def get_last_match(name : str, region : str):
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	match_history = get_match_history(name, region_)

	return match_history[0]

def get_match_info(match_id : int, region : str):
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	match = watcher.match.by_id(region_, match_id)

	return match

def get_match_participants(match_id : int, region : str):
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	match = get_match_info(match_id, region_)
	data = match["info"]["participants"]

	return data

def get_champions_played(name : str, region : str) -> Dict:
	"""Get champions played on the last match of a summoner."""
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	last_match = get_last_match(name = name, region = region_)
	participants = get_match_participants(match_id = last_match, region = region_)

	data = {}

	try:
		region_ = from_riot_to_cass(region_)
	except KeyError:
		region_ = region_

	for participant in participants:
		champion_id = participant["championId"]
		champion = Champion(id = champion_id, region = region_)
		summoner = participant["summonerName"]

		data[summoner] = champion.name
		
	return data

def get_match_teams(match_id : int, region : str) -> tuple:
	"""
	Get teams of a match.
	THE FIRST ONE ALWAYS IS BLUE TEAM.
	"""
	try:
		region_ = from_cass_to_riot(region)
	except KeyError:
		region_ = region

	participants = get_match_participants(match_id, region_)
	blue_team = list(filter(lambda p: p['teamId'] == 100, participants))
	red_team = list(filter(lambda p: p['teamId'] == 200, participants))

	return blue_team, red_team

def get_team_players(team) -> List[Summoner]:
	"""Get players of a team."""
	players = list(map(lambda p: p['summonerName'], team))
	players = [Summoner(name = player, region = "NA") for player in players]

	return players

def get_team_champions(team) -> List[Champion]:
	"""Get champions of a team."""
	champions = list(map(lambda p: p['championId'], team))
	champions = [Champion(id = champion, region = "NA") for champion in champions]

	return champions

def get_winner_team(match_id : int, region : str) -> str:
	"""Get winner team of a match."""
	match = get_match_info(match_id, region)
	teams = match["info"]["teams"]

	for team in teams:
		if team["win"] == True and team["teamId"] == 100:
			return "blue"
		elif team["win"] == True and team["teamId"] == 200:
			return "red"
		else:
			return None

def get_match_map(match_id : int, region : str) -> str:
	match = get_match_info(match_id, region)
	map_ = match["info"]["mapId"]

	return map_

def get_champion_emoji_by_name(champion_name : str) -> str:
	"""Get emoji of a champion by his name."""
	try:
		return CHAMPION_EMOJIS_BY_NAME[champion_name]
	except KeyError:
		return CHAMPION_EMOJIS_BY_NAME["unknown"]

def get_champion_emoji_by_id(champion_id : str) -> str:
	"""Get emoji of a champion by his ID."""
	try:
		return CHAMPION_EMOJIS_BY_ID[champion_id]
	except KeyError:
		return CHAMPION_EMOJIS_BY_ID["unknown"]

def get_match_stats(match : Match) -> tuple:
	"""
	Get match stats.
	Returns:
		tuple: (blue_team_stats, red_team_stats)
	"""
	blue_team = match.blue_team.participants
	red_team = match.red_team.participants

	blue_stats = [player.stats for player in blue_team]
	red_stats = [player.stats for player in red_team]

	return blue_stats, red_stats

async def get_summoner_or_fail(user : str, region : str) -> Summoner:
	"""Get summoner object."""
	summoner = Summoner(name = user, region = region)
	if summoner.puuid == '?':
		raise ValueError
	
	return summoner

async def get_champion_or_fail(champion: str, region: str) -> Champion:
	"""Get champion object."""
	champion = Champion(name = champion,)

# Function That Parses Roles
def op_gg_role_parser(role : str) -> str:
	match role:
		case "top":
			return "top"
		case "jungle":
			return "jungle"
		case "mid":
			return "mid"
		case "adc":
			return "adc"
		case "support":
			return "support"
		case _:
			return "top"

# Function That Converts Cassiopeia's Region Format To Riot's Region Format
def from_cass_to_riot(region : Optional[str]):
	regions = {
		"BR" : "br1",
		"EUNE" : "eun1",
		"EUW" : "euw1",
		"JP" : "jp1",
		"KR" : "kr",
		"LAN" : "la1",
		"LAS" : "la2",
		"NA" : "na1",
		"OCE" : "oc1",
		"TR" : "tr1",
		"RU" : "ru"
	}
	return regions[region]

# Function That Converts Riot's Region Format To Cassiopeia's Region Format
def from_riot_to_cass(region : Optional[str]):
	regions = {
		"br1" : "BR",
		"eun1" : "EUNE",
		"euw1" : "EUW",
		"jp1" : "JP",
		"kr" : "KR",
		"la1" : "LAN",
		"la2" : "LAS",
		"na1" : "NA",
		"oc1" : "OCE",
		"tr1" : "TR",
		"ru" : "RU"
	}
	return regions[region]

# Function That Returns A Emoji Based On Summoner's Rank
def get_rank_emoji(rank : Optional[str]):
	ranks = {
		"Iron" : "<:Iron:991124255985111112>",
		"Bronze" : "<:Bronze:991124244001992745>",
		"Silver" : "<:Silver:991124269302022174>",
		"Gold" : "<:Gold:991124251337826324>",
		"Platinum" : "<:Platinum:991124264830914571>",
		"Diamond" : "<:Diamond:991124249169379458>",
		"Master" : "<:Master:991124258090668052>",
		"Grandmaster" : "<:Grandmaster:991124253153955870>",
		"Challenger" : "<:Challenger:991124247390986331>"
	}
	return ranks[rank]

# Function That Returns Hex Color Based On Champion Tier
def get_embed_color(tier : Optional[str]):
	colors = {
		"S+" : "FF8500",
		"S" : "0000FF",
		"A" : "82B1FF",
		"B" : "FFFFFF",
		"C" : "FF6B6B",
		"D" : "FF0000"
	}
	return colors[tier]

# Function That Converts U.GG Elo's Format To Normal Format 
def from_gg_to_normal(elo : Optional[str]):
	values = {
		"platinum_plus" : "Platinum+",
		"diamond_plus" : "Diamond",
		"diamond_2_plus" : "Diamond 2+",
		"master_plus" : "Master+",
		"overall" : "All Ranks",
		"challenger" : "Challenger",
		"grandmaster" : "Grandmaster",
		"master" : "Master",
		"diamond" : "Diamond",
		"platinum" : "Platinum",
		"gold" : "Gold",
		"silver" : "Silver",
		"bronze" : "Bronze",
		"iron" : "Iron" 
	}
	return values[elo]

# Function That Converts Normal Elo To Be U.GG Readed
def from_normal_to_gg(elo : Optional[str]):
	values = {
		"platinum+" : "platinum_plus",
		"diamond+" : "diamond_plus",
		"diamond2+" : "diamond_2_plus",
		"master+" : "master_plus",
		"all" : "overall",
		"challenger" : "challenger",
		"grandmaster" : "grandmaster",
		"master" : "master",
		"diamond" : "diamond",
		"platinum" : "platinum",
		"gold" : "gold",
		"silver" : "silver",
		"bronze" : "bronze",
		"iron" : "iron"
	}
	return values[elo]

# Function That Returns Mastery Level Emoji
def get_mastery_emoji(mastery : Optional[int]) -> str:
	masteries = {
		4 : "<:mastery4:993688312894197840>",
		5 : "<:mastery5:993688341063159860>",
		6 : "<:mastery6:993688366317043772>",
		7 : "<:mastery7:993688390723715172>"
 	}
	return masteries[mastery]