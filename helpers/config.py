import os, json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the config file
with open("./config.json") as file:
	config = json.load(file)

# Tokens
TOKEN = os.getenv("TOKEN")
RIOT_TOKEN = os.getenv("RIOT_TOKEN")

# Version
VERSION = config["version"]

# Prefix
PREFIX = config["prefix"]

# Guild IDs
MAIN_GUILD_ID = config["guild_ids"]["main_guild_id"]
TESTING_GUILD_ID = config["guild_ids"]["testing_guild_id"]

# User IDs
DEVELOPER_ID = config["user_ids"]["developer_id"]

# Channel IDs
ERROR_CHANNEL_ID = config["channel_ids"]["error_channel_id"]
LOGS_CHANNEL_ID = config["channel_ids"]["logs_channel_id"]
WELCOME_CHANNEL_ID = config["channel_ids"]["welcome_channel_id"]
MODMAIL_CHANNEL_ID = config["channel_ids"]["modmail_channel_id"]
DEBUG_CHANNEL_ID = config["channel_ids"]["debug_channel_id"]

# Lavalink Things
LAVALINK_HOST = config["lavalink"]["host"]
LAVALINK_PORT = config["lavalink"]["port"]
LAVALINK_PASSWORD = config["lavalink"]["password"]

# Cassiopeia Config
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

