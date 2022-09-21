from typing import Optional
from requests_html import HTMLSession

class Parser:
	# Function That Converts Normal Region Format To OP.GG Region Format
	def region_parser(self, region: str) -> str:
		"""
		Parses a league of legends region
		Parameters:
			region: Region that's gonna be parsed
		Returns:
			Parsed region string
		"""
		region = region.lower()
		regions = {
			"na": "na1",
			"euw": "euw1",
			"eune": "eune1",
			"br": "br1",
			"kr": "kr1",
			"lan": "lan1",
			"las": "las1",
			"oce": "oc1",
			"ru": "ru",
			"tr": "tr1",
			"jp": "jp1",
			"world": "world"
		}
		try:
			return regions[region]
		except KeyError:
			return "world"

	# Function That Converts User's Input Role To U.GG's Roles Format
	def role_parser(self, role : Optional[str]):
		roles = {
			"top" : "top",
			"jungle" : "jungle",
			"mid" : "mid",
			"adc" : "adc",
			"support" : "support"
		}
		try:
			return roles[role]
		except KeyError:
			return "top"

	def tierlist_role_parser(self, role: str):
		roles = {
			"top": "top-lane-tier-list",
			"jungle": "jungle-tier-list",
			"mid": "mid-lane-tier-list",
			"adc": "adc-tier-list",
			"support": "support-tier-list",
			"all": "tier-list"
		}
		try:
			return roles[role]
		except KeyError:
			return "tier-list"

	# Function That Converts Normal Elo To Be U.GG Readed
	def from_normal_to_gg(self, elo: Optional[str]):
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
		try:
			return values[elo]
		except KeyError:
			return "platinum_plus"

class LeagueScraper:
	BASE_STATS_URL = "https://u.gg/lol/champions/{}/build/{}?region={}&rank={}"
	BASE_TIERLIST_URL = "https://u.gg/lol/{}?region={}&rank={}"

	def __init__(self, parser: Parser):
		self.parser = parser
		self.session = HTMLSession()

	def _get_stats_url(self, champion: str, region: str, rank: str, role: str) -> str:
		region = self.parser.region_parser(region)
		rank = self.parser.from_normal_to_gg(rank)
		role = self.parser.role_parser(role)

		return self.BASE_STATS_URL.format(champion, role, region, rank)

	def _get_tierlist_url(self, region: str, elo: str, role: str):
		region = self.parser.region_parser(region)
		elo = self.parser.from_normal_to_gg(elo)
		role = self.parser.tierlist_role_parser(role)

		print(region)
		print(elo)
		print(role)

		return self.BASE_TIERLIST_URL.format(role, region, elo)

	def get_champion_analytics(self, champion: str = "annie", region: str = "NA", elo: str = "platinum+", role: str = "top") -> list:
		"""
		Returns a list of champions analytics for the given champion.

		Parameters:
			champion: The champion to analytics for.
			region: The region to analytics for.
			elo: The elo to analytics for.
			role: The role to analytics for.

		Returns:
			A list with the champion analytics with the next format:

			[tier, winrate, rank, pickrate, banrate, matches]
		
		Example:
			>>> parser = Parser()
			>>> scraper = Scraper(parser)
			>>> annie = scraper.get_champion_analytics('annie', 'world', 'platinum+', 'mid')
			>>> print(annie)
			['A', '51.57%', '15 / 57', '1.4%', '0.3%', '20,040']
			>>> print(annie[2])
			15 / 57
		"""

		url = self._get_stats_url(champion = champion, role = role, region = region, rank = elo)
		r = self.session.get(url)
		container = r.html.find(".content-section", first = True)
		divs = container.find(".value") # Tier, Win Rate, Rank, Pick Rate, Ban Rate, Matches

		data = [div.text for div in divs]
		
		return data

	def get_tierlist(self, region: str, elo: str, role: str):
		"""
		Returns a tierlist for the given region, tier and position

		Parameters:
			region: The region to analytics for.
			elo: The elo to analytics for.
			role: The role to analytics for.

		Returns:
			A list with the champion analytics with the next format:

			[tier, winrate, rank, pickrate, banrate, matches]
		
		Example:
			>>> parser = Parser()
			>>> scraper = Scraper(parser)
			>>> annie = scraper.get_tierlist('world', 'platinum+', 'mid', 10)
			>>> print(annie)
			['A', '51.57%', '15 / 57', '1.4%', '0.3%', '20,040']
			>>> print(annie[2])
			15 / 57
		"""

		url = self._get_tierlist_url(region = region, elo = elo, role = role)
		r = self.session.get(url)
		container = r.html.find(".rt-tbody", first = True)
		print(container)
		champ_div = container.find(".rt-tr")
		print(champ_div)

		ranks = []
		champions = []
		tiers = []
		winrates = []
		pickrates = []
		banrates = []
		matches = []

		for div in champ_div:
			rank = div.find("span").text
			champion = div.find("a").text
			tier = div.find("span").text
			winrate = div.find("span").text
			pickrate = div.find("span").text
			banrate = div.find("span").text
			match = div.find("span").text

			ranks.append(rank)
			champions.append(champion)
			tiers.append(tier)
			winrates.append(winrate)
			pickrates.append(pickrate)
			banrates.append(banrate)
			matches.append(match)

			data = {
				"rank": ranks,
				"champion": champions,
				"tier": tiers,
				"winrate": winrates,
				"pickrate": pickrates,
				"banrate": banrates,
				"matches": matches
			}

		return data

if __name__ == "__main__":
	parser = Parser()
	scraper = LeagueScraper(parser)
	data = scraper.get_tierlist("world", "platinum+", "all")

	print(data)