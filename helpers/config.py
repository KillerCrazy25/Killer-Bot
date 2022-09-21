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
PASTEBIN_TOKEN = os.getenv("PASTEBIN_TOKEN")

# Version
VERSION = config["version"]

# Prefix
PREFIX = config["prefix"]

# Guild IDs
GUILD_IDS = config["guild_ids"].values()

MAIN_GUILD_ID = config["guild_ids"]["main_guild_id"]
TESTING_GUILD_ID = config["guild_ids"]["testing_guild_id"]

# User IDs
USER_IDS = config["user_ids"].values()

DEVELOPER_ID = config["user_ids"]["developer_id"]

# Channel IDs
CHANNEL_IDS = config["channel_ids"].values()

ERROR_CHANNEL_ID = config["channel_ids"]["error_channel_id"]
LOGS_CHANNEL_ID = config["channel_ids"]["logs_channel_id"]
WELCOME_CHANNEL_ID = config["channel_ids"]["welcome_channel_id"]
MODMAIL_CHANNEL_ID = config["channel_ids"]["modmail_channel_id"]
DEBUG_CHANNEL_ID = config["channel_ids"]["debug_channel_id"]

# Role IDs
ROLE_IDS = config["role_ids"].values()

ADMIN_ROLE_ID = config["role_ids"]["admin_role_id"]
MOD_ROLE_ID = config["role_ids"]["mod_role_id"]
USER_ROLE_ID = config["role_ids"]["user_role_id"]

# Lavalink Things
LAVALINK_HOST = os.getenv("LAVALINK_HOST")
LAVALINK_PORT = os.getenv("LAVALINK_PORT")
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD")

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
		"print_riot_api_key": True, 
		"default": "WARNING", 
		"core": "WARNING"
	}
}

