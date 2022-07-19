import os, json

from dotenv import load_dotenv

load_dotenv()

with open("./config.json") as file:
	config = json.load(file)

TOKEN = os.getenv("TOKEN")
RIOT_TOKEN = os.getenv("RIOT_TOKEN")

PREFIX = config["prefix"]

MAIN_GUILD_ID = config["guild_ids"]["main_guild_id"]
TESTING_GUILD_ID = config["guild_ids"]["testing_guild_id"]

DEVELOPER_ID = config["user_ids"]["developer_id"]

ERROR_CHANNEL_ID = config["channel_ids"]["error_channel_id"]
LOGS_CHANNEL_ID = config["channel_ids"]["logs_channel_id"]

LAVALINK_HOST = config["lavalink"]["host"]
LAVALINK_PORT = config["lavalink"]["port"]
LAVALINK_PASSWORD = config["lavalink"]["password"]

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
			"api_key": RIOT_TOKEN
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

