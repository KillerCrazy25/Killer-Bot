from curses import keyname
import cassiopeia as cass
import cassiopeia_championgg as gg

from cassiopeia_championgg import *
from cassiopeia import *

import discord
from discord.ext import commands, bridge

import os
from dotenv import load_dotenv

import json

from utils.utils import from_gg_to_normal, from_normal_to_gg, get_embed_color, get_rank_emoji, get_champion_analytics, from_cass_to_riot, from_riot_to_cass

with open("./config.json") as file:
	config = json.load(file)

MAIN_GUILD_ID = config["guild_ids"]["main_guild_id"]
TESTING_GUILD_ID = config["guild_ids"]["testing_guild_id"]

load_dotenv()

cass.set_riot_api_key(os.getenv("RIOT_TOKEN"))

class LeagueCommands(commands.Cog):
	
	def __init__(self, bot):
		self.bot = bot

	@bridge.bridge_command(description = "Profile command.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def profile(self, ctx, user : str = "Josedeodo", region : str = "NA"):
		summoner = Summoner(name = user, region = region)

		embed = discord.Embed(
			description = f"{user}'s Profile | Level {summoner.level}",
			color = discord.Color.purple()
		)
		entries = summoner.league_entries		
		try:
			solo_duo_rank = entries.fives.league.tier
			solo_duo_division = entries.fives.division
			solo_duo_lps = entries.fives.league_points
			solo_duo_emoji = get_rank_emoji(str(solo_duo_rank))
			solo_duo_wins = entries.fives.wins
			solo_duo_losses = entries.fives.losses
			solo_duo_total = solo_duo_wins + solo_duo_losses
			solo_duo_winrate = (solo_duo_wins * 100) / (solo_duo_total)

			embed.add_field(name = "Ranked Solo/Duo", value = f"Rank: {solo_duo_emoji} {solo_duo_rank} {solo_duo_division} {solo_duo_lps} LP\nTotal Games: {solo_duo_total}\nWins: {solo_duo_wins}\nLosses: {solo_duo_losses}\nWin Rate: {solo_duo_winrate:.2f}%", inline = True)
		except ValueError:
			solo_duo_emoji = "<:Unranked:991907027150458881>"

			embed.add_field(name = "Ranked Solo/Duo", value = f"Rank: {solo_duo_emoji} Unranked", inline = True)
			
		try:
			flex_rank = entries.flex.league.tier
			flex_division = entries.flex.division
			flex_lps = entries.flex.league_points
			flex_emoji = get_rank_emoji(str(flex_rank))
			flex_wins = entries.flex.wins
			flex_losses = entries.flex.losses
			flex_total = flex_wins + flex_losses
			flex_winrate = (flex_wins * 100) / (flex_total)

			embed.add_field(name = "Ranked Flex", value = f"Rank: {flex_emoji} {flex_rank} {flex_division} {flex_lps} LP \nTotal Games: {flex_total}\nWins: {flex_wins}\nLosses: {flex_losses}\nWin Rate: {flex_winrate:.2f}%", inline = True)
		except ValueError:
			flex_emoji = "<:Unranked:991907027150458881>"

			embed.add_field(name = "Ranked Flex", value = f"Rank: {flex_emoji} Unranked", inline = True)

		embed.set_author(name = "Killer Bot | League Of Legends Profile", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
		embed.set_thumbnail(url = summoner.profile_icon.url)

		await ctx.respond(embed = embed)

	@bridge.bridge_command(description = "Show champion analytics by U.GG", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def champ(self, ctx, champion : str = "Annie", region : str = "world", elo : str = "all"):
		champ = Champion(name = champion, region = "NA")

		parsed_elo = from_normal_to_gg(elo)
		analytics = get_champion_analytics(str(champion), str(region), str(parsed_elo))

		tier = analytics[0]
		win_rate = analytics[1]
		ranking = analytics[2]
		pick_rate = analytics[3]
		ban_rate = analytics[4]
		matches = analytics[5]

		embed_color = get_embed_color(tier)
		converted_elo = from_gg_to_normal(parsed_elo)

		embed = discord.Embed(
			title = f"{champion} Information",
			description = f"Displaying statistics for {champion}\nElo: {converted_elo.upper()}\nRegion: {region.upper()}",
			color = int(embed_color, 16)
		)
	
		embed.add_field(name = "Champion Analytics (U.GG)", value = f"Tier: {tier}\nWin Rate: {win_rate}\nRanking: {ranking}\nPick Rate: {pick_rate}\nBan Rate: {ban_rate}\nMatches: {matches}", inline = False)
		embed.add_field(name = "Free To Play", value = champ.free_to_play, inline = True)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Analytics", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

		embed.set_thumbnail(url = champ.image.url)

		await ctx.respond(embed = embed)

def setup(bot):
	bot.add_cog(LeagueCommands(bot))