from bs4 import BeautifulSoup
import requests

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

# Function That Converts Cassiopeia's Elo Format To Riot's Elo Format

def from_cass_to_riot(region : str):
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

# Function That Converts Riot's Elo Format To Cassiopeia's Elo Format

def from_riot_to_cass(region : str):
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

def get_rank_emoji(rank : str):
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

def get_embed_color(tier : str):
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

def role_parser(role : str):
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

def from_gg_to_normal(elo : str):
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

def from_normal_to_gg(elo : str):
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

def human_format(num):
	num = float('{:.3g}'.format(num))
	magnitude = 0
	while abs(num) >= 1000:
		magnitude += 1
		num /= 1000.0
	return "{}{}".format("{:f}".format(num).rstrip("0").rstrip("."), ["", "k", "M", "B", "T"][magnitude])

# Function That Returns Mastery Level Emoji

def get_mastery_emoji(mastery: int) -> str:
	masteries = {
		4 : "<:mastery4:993688312894197840>",
		5 : "<:mastery5:993688341063159860>",
		6 : "<:mastery6:993688366317043772>",
		7 : "<:mastery7:993688390723715172>"
 	}
	return masteries[mastery]