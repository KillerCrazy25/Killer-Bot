import arrow

from nextcord.ext import commands
from nextcord import Embed, Color, Asset, Member
from nextcord.errors import DiscordException
from cassiopeia import Match, Summoner

from typing import (
	Optional,
	Union,
	List
)

from helpers.config import *
from helpers.league_utils import *

from datetime import datetime
from pytz import timezone


# ModLogEmbedBuilder Class
class EmbedBuilder:
	
	# ModLogEmbedBuilder Constructor
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	# Error Embed Builder
	async def error_embed(self, error_name: str, error: DiscordException, missing: Optional[Dict] = None) -> Embed:
		"""Returns an error embed."""		
		embed = Embed(
			title = "An error has ocurred executing this command.",
			color = Color.dark_red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)
		embed.add_field(name = f"__Error__: {error_name}", value = f"**__Details__**: {error}")
		if missing:
			embed.add_field(name = missing.keys(), value = "\n".join(list(missing.values())))
		
		embed.set_footer(text = "You can report any bug using /issue create command!")

		return embed

	# Mod Log Embed Builder
	async def mod_log_embed(
		self,
		icon_url: Optional[str],
		color: Union[Color, int],
		title: Optional[str],
		description: str,
		thumbnail: Optional[Union[str, Asset]] = None,
		timestamp: Optional[datetime] = None,
		footer: Optional[str] = None
	) -> Embed:
		"""Returns a mod log embed."""
		embed = Embed(
			description = description[:4093] + "..." if len(description) > 4096 else description
		)

		if title and icon_url:
			embed.set_author(name = title, icon_url = icon_url)

		embed.color = color
		embed.timestamp = timestamp or datetime.now()

		if footer:
			embed.set_footer(text = footer)

		if thumbnail:
			embed.set_thumbnail(url = thumbnail)

		return embed

	# Guild Join Embed Builder
	async def guild_join_embed(self) -> Embed:
		embed = Embed(
			description = "Thanks for adding me to your server!",
			color = Color.dark_purple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		)
		embed.set_author(name = self.bot.user, icon_url = self.bot.user.avatar.url)

		embed.add_field(name = "Basic Information", value = f"- Default Prefix: `{PREFIX}`\n- Developer: <@{DEVELOPER_ID}>\n- Bot Version: `{VERSION}`\n\n**IMPORTANT: Remember that the bot is under development and it's not recommended to be used in public servers.**", inline = False)
		embed.add_field(name = "Commands", value = f"You can find all of my commands by using `{PREFIX}help`", inline = False)
		embed.add_field(name = "Links", value = "[Source Code](https://github.com/KillerCrazy25/Killer-Bot/)\n[Invite](https://discord.com/api/oauth2/authorize?client_id=945158875722702878&permissions=8&scope=bot%20applications.commands)\n[Support Server](https://discord.gg/3WkeV2tNas)", inline = False)

		embed.set_footer(text = f"{self.bot.user.name} v{VERSION} | Guilds: {len(self.bot.guilds)}", icon_url = self.bot.user.avatar.url)

		return embed

	# Match Info Embed Builder
	async def match_embed(self, match: Match, summoner: Summoner, region: str) -> Embed:
		# Getting teams and teams information
		blue_team = get_match_teams(match.id, region)[0]
		red_team = get_match_teams(match.id, region)[1]
		blue_info = get_team_info(match.id, region, 100)
		red_info = get_team_info(match.id, region, 200)
		# Getting team's players
		blue_team_players = get_team_players(blue_team)
		red_team_players = get_team_players(red_team)
		# Getting team's champions
		blue_champions = get_team_champions(blue_team)
		red_champions = get_team_champions(red_team)
		# Getting team's bans
		blue_bans = get_team_bans(blue_info)
		red_bans = get_team_bans(red_info)
		# Getting match queue and map
		map_ = get_map_name(get_map_id(match.id, region))
		queue = match.queue.value.replace("_", " ").title()

		blue_stats = get_match_stats(match)[0]
		red_stats = get_match_stats(match)[1]

		participant = next(filter(lambda p: p.summoner.id == summoner.id, match.participants), None)

		# Red team champions message
		red_message = ""
		for player, champion, stats in zip(red_team_players, red_champions, red_stats):
			emoji = get_champion_emoji_by_id(str(champion.id))
			pm = f"{emoji + ' | __**' + player.name + '**__' if player.name == summoner.name else emoji + ' | ' + player.name}"
			sm = f"{'**' + str(stats.kills) + '**/**' + str(stats.deaths) + '**/**' + str(stats.assists) + '** | **' + str(stats.total_minions_killed) + ' cs** | **' + human_format(stats.total_damage_dealt_to_champions) + ' DMG**' if player.name == summoner.name else str(stats.kills) + '/' + str(stats.deaths) + '/' + str(stats.assists) + ' | ' + str(stats.total_minions_killed) + ' cs | ' + human_format(stats.total_damage_dealt_to_champions) + ' DMG'}"
			red_message += f"{pm} ({sm})\n"
		# Blue team champions message
		blue_message = ""
		for player, champion, stats in zip(blue_team_players, blue_champions, blue_stats):
			emoji = get_champion_emoji_by_id(str(champion.id))
			pm = f"{emoji + ' | __**' + player.name + '**__' if player.name == summoner.name else emoji + ' | ' + player.name}"
			sm = f"{'**' + str(stats.kills) + '**/**' + str(stats.deaths) + '**/**' + str(stats.assists) + '** | **' + str(stats.total_minions_killed) + ' cs** | **' + human_format(stats.total_damage_dealt_to_champions) + ' DMG**' if player.name == summoner.name else str(stats.kills) + '/' + str(stats.deaths) + '/' + str(stats.assists) + ' | ' + str(stats.total_minions_killed) + ' cs | ' + human_format(stats.total_damage_dealt_to_champions) + ' DMG'}"
			blue_message += f"{pm} ({sm})\n"
		# Red team bans message
		red_bans_message = ""
		for ban in red_bans:
			if ban != None:
				emoji = get_champion_emoji_by_id(str(ban.id))
				red_bans_message += f"{emoji} {ban.name}\n"
			else:
				red_bans_message += ""
				continue
		# Blue team bans message
		blue_bans_message = ""
		for ban in blue_bans:
			if ban != None:
				emoji = get_champion_emoji_by_id(str(ban.id))
				blue_bans_message += f"{emoji} {ban.name}\n"
			else:
				blue_bans_message += ""
				continue

		# Creating embed
		embed = Embed(
			color = Color.blue() if participant.stats.win == True else Color.red()
		)

		# Summoner info field
		embed.add_field(
			name = "> Summoner Information", 
			value = f"**Name:** `{summoner.name}`\n**Region:** `{region}`",
			inline = False
		)		
		# Match info field
		embed.add_field(
			name = "> Match Information", 
			value = f"**Map**: `{map_}`\n**Queue**: `{queue}`\n**Date**: <t:{arrow.get(match.creation).timestamp}> (<t:{arrow.get(match.creation).timestamp}:R>)\n**Duration**: `{match.duration}`\n**Result**: `{'Win' if participant.stats.win == True else 'Defeat'}`",
			inline = False
		)
		# Bans info field
		if match.queue in cass.data.RANKED_QUEUES:	
			embed.add_field(
				name = "> Blue Team Bans",
				value = blue_bans_message,
				inline = True
			)
			embed.add_field(
				name = "> Red Team Bans",
				value = red_bans_message,
				inline = True
			)
		# Team fields
		embed.add_field(name = "> Blue Team", value = blue_message, inline = False)
		embed.add_field(name = "> Red Team", value = red_message, inline = False)
		# Author, footer and thumbnail
		embed.set_author(name = "Killer Bot | League Of Legends", icon_url = self.bot.user.avatar.url)
		embed.set_thumbnail(url = summoner.profile_icon.url)

		return embed