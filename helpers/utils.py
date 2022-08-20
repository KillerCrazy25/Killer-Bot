import requests, datetime, arrow

from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

# Function That Gets Champion Analytics Via WebScraping U.GG Website
def get_champion_analytics(champion : str = "annie", region : str = "NA", elo : str = "platinum_plus"):
	if region != "world":
		region = from_cass_to_riot(region)

	if region == "world" and elo == "platinum_plus":
		url = f"https://u.gg/lol/champions/{champion}/build"
		print(f"Sending request to {url}")
		r = requests.get(url = url)

		soup = BeautifulSoup(r.content, "html.parser")

		stats_div = soup.find('div', class_ = 'additional-stats-container')
		stats_ = stats_div.find_all('div', class_ = 'value')

		stats = []

		for stat in stats_:
			stats.append(stat.text)

		return stats

	elif region == "world" and elo != "platinum_plus":
		url = f"https://u.gg/lol/champions/{champion}/build?rank={elo}"
		print(f"Sending request to {url}")
		r = requests.get(url = url)

		soup = BeautifulSoup(r.content, "html.parser")

		stats_div = soup.find('div', class_ = 'additional-stats-container')
		stats_ = stats_div.find_all('div', class_ = 'value')

		stats = []

		for stat in stats_:
			stats.append(stat.text)

		return stats

	elif region != "world" and elo != "platinum_plus":
		url = f"https://u.gg/lol/champions/{champion}/build?rank={elo}&region={region}"
		print(f"Sending request to {url}")
		r = requests.get(url = url)

		soup = BeautifulSoup(r.content, "html.parser")

		stats_div = soup.find('div', class_ = 'additional-stats-container')
		stats_ = stats_div.find_all('div', class_ = 'value')

		stats = []

		for stat in stats_:
			stats.append(stat.text)

		return stats

# Constants
BASE_URL = "https://na.op.gg/champions"

# Function That Gets Champions Tierlist Via WebScraping U.GG Website
def get_tierlist(region : Optional[str] = "na", tier : Optional[str] = "platinum_plus", position : Optional[str] = "top") -> Dict:
	url = get_url(region, tier, position)
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

def get_url(region : str, tier : str, position : str) -> str:
	region = opgg_region_parser(region)
	tier = op_gg_tier_parser(tier)
	position = op_gg_role_parser(position)

	if region == "na" and tier == "platinum_plus" and position == "top":
		return BASE_URL

	elif region != "na" and tier == "platinum_plus" and position == "top":
		return f"{BASE_URL}?region={region}&tier=platinum_plus&position=top"

	elif region == "na" and tier != "platinum_plus" and position == "top":
		return f"{BASE_URL}?region=na&tier={tier}&position=top"

	elif region == "na" and tier == "platinum_plus" and position != "top":
		return f"{BASE_URL}?region=na&tier=platinum_plus&position={position}"

	elif region != "na" and tier != "platinum_plus" and position == "top":
		return f"{BASE_URL}?region={region}&tier={tier}&position=top"

	elif region != "na" and tier != "platinum_plus" and position != "top":
		return f"{BASE_URL}?region={region}&tier={tier}&position={position}"
	
	elif region != "na" and tier == "platinum_plus" and position != "top":
		return f"{BASE_URL}?region={region}&tier=platinum_plus&position={position}"

	elif region == "na" and tier != "platinum_plus" and position != "top":
		return f"{BASE_URL}?region=na&tier={tier}&position={position}"

	else:
		return BASE_URL	

# Function That Parses Roles
def op_gg_role_parser(role : str) -> str:
	if role == "top":
		return "top"

	elif role == "jungle":
		return "jungle"

	elif role == "mid":
		return "mid"

	elif role == "adc":
		return "adc"

	elif role == "support":
		return "support"

	else:
		return "error"

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

# Function That Converts Numbers To Human Format (e.i, 1.000 to 1k)
def human_format(num : Optional[Any]):
	num = float('{:.3g}'.format(num))
	magnitude = 0
	while abs(num) >= 1000:
		magnitude += 1
		num /= 1000.0

	return "{}{}".format("{:f}".format(num).rstrip("0").rstrip("."), ["", "k", "M", "B", "T"][magnitude])

# Function That Returns Mastery Level Emoji
def get_mastery_emoji(mastery : Optional[int]) -> str:
	masteries = {
		4 : "<:mastery4:993688312894197840>",
		5 : "<:mastery5:993688341063159860>",
		6 : "<:mastery6:993688366317043772>",
		7 : "<:mastery7:993688390723715172>"
 	}
	return masteries[mastery]