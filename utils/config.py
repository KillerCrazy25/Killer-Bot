import os, json

from dotenv import load_dotenv

load_dotenv()

with open("./config.json") as file:
	config = json.load(file)

TOKEN = os.getenv("TOKEN")
RIOT_TOKEN = os.getenv("RIOT_TOKEN")

MAIN_GUILD_ID = config["guild_ids"]["main_guild_id"]
TESTING_GUILD_ID = config["guild_ids"]["testing_guild_id"]

DEVELOPER_ID = config["user_ids"]["developer_id"]

CASSIOPEIA_CONFIG = { 
	"global": {
		"version_from_match": "patch"
	}, 
	"plugins": {
	}, 
	"pipeline": {
		"Cache": {

		},
		"DDragon": {

		}, 
		"RiotAPI": {
			"api_key": "RGAPI-765b518a-4d81-40e2-9daf-0c929f3c1abe"
		},
		"ChampionGG": {
			"package": "cassiopeia_championgg",
			"api_key": "CHAMPIONGG_KEY"
		}
	}, 
	"logging": {
		"print_calls": True,
		"print_riot_api_key": False, 
		"default": "WARNING", 
		"core": "WARNING"
	}
}

