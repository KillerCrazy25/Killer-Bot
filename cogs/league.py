import discord, cassiopeia as cass, os, random

from cassiopeia import *

from discord.ext import commands, bridge

from dotenv import load_dotenv

from utils.utils import from_gg_to_normal, from_normal_to_gg, get_champion_tierlist, get_embed_color, get_mastery_emoji, get_rank_emoji, get_champion_analytics, from_cass_to_riot, from_riot_to_cass, human_format
from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID, CASSIOPEIA_CONFIG

from datetime import datetime, timedelta
from pytz import timezone

load_dotenv()

cass.set_riot_api_key(os.getenv("RIOT_TOKEN"))
cass.apply_settings(CASSIOPEIA_CONFIG)

class LeagueCommands(commands.Cog):
	
	def __init__(self, bot):
		self.bot = bot

	@bridge.bridge_command(description = "Profile command.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def profile(self, ctx: bridge.BridgeContext, user : str = "Josedeodo", region : str = "NA"):
		
		await ctx.send(f"> Please wait...\n> Loading `{user}` profile...", delete_after = 5)

		summoner = Summoner(name = user, region = region)

		embed = discord.Embed(
			description = f"{user}'s Profile | Level {summoner.level}",
			color = discord.Color.nitro_pink(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
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

		masteries = cass.get_champion_masteries(summoner = summoner, region = region)

		best = masteries.filter(lambda cm: cm.level >= 5)
		m7 = masteries.filter(lambda cm: cm.level == 7)
		m6 = masteries.filter(lambda cm: cm.level == 6)
		m5 = masteries.filter(lambda cm: cm.level == 5)

		p = []
		for i in masteries:
			p.append(masteries[i].points)

		total_points = sum(p)
		total_points = human_format(int(total_points))

		counter = 0
		champions = ""
		
		for cm in best:
			mastery_emoji = get_mastery_emoji(int(cm.level))
			points = human_format(cm.points)
			counter += 1
			if counter <= 5:
				champions = champions + f"{mastery_emoji} {cm.champion.name} - **{str(points)}**\n"
			else:
				break

		embed.add_field(name = "Best Champions", value = f"{champions}", inline = False)
		embed.add_field(name = "Mastery Stats", value = f"{len(m7)}x <:mastery7:993688390723715172> {len(m6)}x <:mastery6:993688366317043772> {len(m5)}x <:mastery5:993688341063159860>\nTotal Mastery Points: {total_points}", inline = True)
	
		embed.set_author(name = "Killer Bot | League Of Legends Profile", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
		embed.set_thumbnail(url = summoner.profile_icon.url)

		await ctx.respond(embed = embed)

	@bridge.bridge_command(description = "Show champion analytics by U.GG", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def champ(self, ctx: bridge.BridgeContext, champion : str = "Annie", region : str = "world", elo : str = "all"):
		champ = Champion(name = champion, region = "NA")

		search_elo = from_normal_to_gg(elo)
		analytics = get_champion_analytics(str(champion), str(region), str(search_elo))

		tier = analytics[0]
		win_rate = analytics[1]
		ranking = analytics[2]
		pick_rate = analytics[3]
		ban_rate = analytics[4]
		matches = analytics[5]

		embed_color = get_embed_color(tier)
		embed_elo = from_gg_to_normal(search_elo)

		embed = discord.Embed(
			title = f"{champion} Information",
			description = f"Displaying statistics for {champion}\nElo: {embed_elo.upper()}\nRegion: {region.upper()}",
			color = int(embed_color, 16),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)
	
		embed.add_field(name = "Champion Analytics (U.GG)", value = f"Tier: {tier}\nWin Rate: {win_rate}\nRanking: {ranking}\nPick Rate: {pick_rate}\nBan Rate: {ban_rate}\nMatches: {matches}", inline = False)
		embed.add_field(name = "Free To Play", value = champ.free_to_play, inline = True)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Analytics", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

		embed.set_thumbnail(url = champ.image.url)

		await ctx.respond(embed = embed)
	
	@bridge.bridge_command(description = "Get U.GG Tierlist.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def tierlist(self, ctx: bridge.BridgeContext, region : str = "world", elo : str = "all", role : str = "all_roles"):
		res = get_champion_tierlist(region = region, elo = elo, role = role)

	@bridge.bridge_command(description = "Choose a random champion.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def randomchamp(self, ctx : bridge.BridgeContext):
		champs = cass.get_champions(region = "NA")
		
		champ = random.choice(champs)

		embed = discord.Embed(
			title = f"Champion: {champ.name}",
			color = discord.Color.random(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)

		embed.set_image(url = champ.image.url)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Randomizer", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

		await ctx.respond(embed = embed)

def setup(bot):
	bot.add_cog(LeagueCommands(bot))