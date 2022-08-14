import requests
from bs4 import BeautifulSoup

def get_tierlist():
	url = "https://www.op.gg/champions?region=global&tier=all&position=jungle"
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
	}

	req = requests.get(url = url, headers = headers)

	soup = BeautifulSoup(req.content, "html.parser")

	table = soup.find("table", {"class": "css-i1zhjp e1oulx2j8"})
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

		tier = raw_data[0].find("span").text
		champion = raw_data[1].find("a").text
		level = raw_data[2].text
		winrate = raw_data[3].text
		pickrate = raw_data[4].text
		banrate = raw_data[5].text

		tiers.append(tier)
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

if __name__ == "__main__":
	data = get_tierlist()

	print("------------ Data ------------")
	print(data)