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

# Constants
BASE_TIERLIST_URL = "https://na.op.gg/champions"
BASE_STATS_URL = "https://na.op.gg/champions/{}/{}/build?region={}&tier={}" # champion, role, region, tier

# Function That Gets Champion Analytics Via WebScraping OP.GG Website
def get_champion_analytics(champion : str = "annie", region : str = "NA", elo : str = "platinum+", role : str = "top") -> Dict:
	url = get_stats_url(champion, region, elo, role)
	soup = get_soup(url)

	champ_stats_div = soup.find("div", {"class": "css-c3v1ys ew1oorz7"})
	stats = []

	for div in champ_stats_div:
		stats.append(div.text)

	return stats

async def get_summoner_or_fail(user : str, region : str) -> Summoner:
	"""Get summoner object."""
	summoner = Summoner(name = user, region = region)
	if summoner.puuid == '?':
		raise ValueError
	
	return summoner

# Function That Gets Champions Tierlist Via WebScraping U.GG Website
def get_tierlist(region : Optional[str] = "na", tier : Optional[str] = "platinum_plus", position : Optional[str] = "top") -> Dict:
	url = get_tierlist_url(region, tier, position)
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
	}

	req = requests.get(url = url, headers = headers)

	print("Sending request to {}".format(url))

	soup = BeautifulSoup(req.content, "html.parser")

	table = soup.find("table", {"class": "css-jgru8w e1oulx2j7"})
	tbody = table.find("tbody")
	all_champs_stats = tbody.find_all("tr")

	tiers = []
	champions = []
	levels = []
	winrates = []
	pickrates = []
	banrates = []

	for tr in all_champs_stats:
		raw_data = tr.find_all("td")

		tier_ = raw_data[0].find("span").text
		champion = raw_data[1].find("a").text
		level = raw_data[2].text
		winrate = raw_data[3].text
		pickrate = raw_data[4].text
		banrate = raw_data[5].text

		tiers.append(tier_)
		champions.append(champion)
		levels.append(level)
		winrates.append(winrate)
		pickrates.append(pickrate)
		banrates.append(banrate)

		data = {
			"tier": tiers,
			"champion": champions,
			"level": levels,
			"winrate": winrates,
			"pickrate": pickrates,
			"banrate": banrates
		}

	return data

# Function That Gets Champions Tierlist Url
def get_tierlist_url(region : str, tier : str, position : str) -> str:
	region = opgg_region_parser(region)
	tier = op_gg_tier_parser(tier)
	position = op_gg_role_parser(position)

	if region == "na" and tier == "platinum_plus" and position == "top":
		return BASE_TIERLIST_URL

	elif region != "na" and tier == "platinum_plus" and position == "top":
		return f"{BASE_TIERLIST_URL}?region={region}&tier=platinum_plus&position=top"

	elif region == "na" and tier != "platinum_plus" and position == "top":
		return f"{BASE_TIERLIST_URL}?region=na&tier={tier}&position=top"

	elif region == "na" and tier == "platinum_plus" and position != "top":
		return f"{BASE_TIERLIST_URL}?region=na&tier=platinum_plus&position={position}"

	elif region != "na" and tier != "platinum_plus" and position == "top":
		return f"{BASE_TIERLIST_URL}?region={region}&tier={tier}&position=top"

	elif region != "na" and tier != "platinum_plus" and position != "top":
		return f"{BASE_TIERLIST_URL}?region={region}&tier={tier}&position={position}"
	
	elif region != "na" and tier == "platinum_plus" and position != "top":
		return f"{BASE_TIERLIST_URL}?region={region}&tier=platinum_plus&position={position}"

	elif region == "na" and tier != "platinum_plus" and position != "top":
		return f"{BASE_TIERLIST_URL}?region=na&tier={tier}&position={position}"

	else:
		return BASE_TIERLIST_URL	

# Function That Gets Champions Stats Url
def get_stats_url(champion : str, region : str, rank : str, role : str) -> str:
	region = opgg_region_parser(region)
	rank = op_gg_tier_parser(rank)
	role = op_gg_role_parser(role)

	return BASE_TIERLIST_URL.format(champion, region, rank, role)

def get_soup(url : str) -> BeautifulSoup:
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
	}

	req = requests.get(url = url, headers = headers)

	logger.info(f"Sending request to {url}")

	soup = BeautifulSoup(req.content, "html.parser")

	return soup

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

# Function That Converts Normal Elo Format To OP.GG Elo Format
def op_gg_tier_parser(tier : str) -> str:
	roles = {
		"challenger": "challenger",
		"grandmaster": "grandmaster",
		"master+": "master_plus",
		"master": "master",
		"diamond+": "diamond_plus",
		"diamond": "diamond",
		"platinum+": "platinum_plus",
		"platinum": "platinum",
		"gold": "gold",
		"silver": "silver",
		"bronze": "bronze",
		"iron": "iron",
		"all" : "all"		
	}
	return roles[tier]

# Function That Converts Normal Region Format To OP.GG Region Format
def opgg_region_parser(region : str) -> str:
	region = region.lower()
	regions = {
		"na": "na",
		"euw": "euw",
		"eune": "eune",
		"br": "br",
		"kr": "kr",
		"lan": "lan",
		"las": "las",
		"oce": "oce",
		"ru": "ru",
		"tr": "tr",
		"jp": "jp",
		"world": "global"
	}
	return regions[region]

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

# Function That Converts User's Input Role To U.GG's Roles Format
def role_parser(role : Optional[str]):
	roles = {
		"all" : "all",
		"top" : "top-lane",
		"jungle" : "jungle",
		"mid" : "mid-lane",
		"adc" : "adc",
		"support" : "support"
	}
	return roles[role]

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