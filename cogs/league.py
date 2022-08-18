import nextcord, cassiopeia as cass, os, random, matplotlib.pyplot as plt, pandas as pd, numpy as np, matplotlib.table

from cassiopeia import *

from nextcord.ext import commands

from helpers.utils import *
from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID, CASSIOPEIA_CONFIG, RIOT_TOKEN

from datetime import datetime
from pytz import timezone

from pandas.plotting import table

cass.set_riot_api_key(RIOT_TOKEN)
cass.apply_settings(CASSIOPEIA_CONFIG)

# League Cog
class LeagueCommands(commands.Cog):

	# League Constructor
	def __init__(self, bot):
		self.bot = bot

	# Profile Command
	@commands.command(description = "Profile command.")
	async def profile(self, ctx: commands.Context, user : str = "Josedeodo", region : str = "NA"):

		await ctx.defer()

		summoner = Summoner(name = user, region = region)

		embed = nextcord.Embed(
			description = f"{user}'s Profile | Level {summoner.level}",
			color = nextcord.Color.nitro_pink(),
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

		champs_ = []
		points_ = []
		counter_ = 0

		for i in best:
			counter_ +=1
			if counter_ <= 5:
				champs_.append(i.champion.name)
				points_.append(i.points)
			else:
				break
		
		plt.bar(champs_, points_, color = "pink")

		plt.xlabel = "Champions"
		plt.ylabel = "Mastery Points"

		plt.savefig(f"{user}.png")

		plt.close()

		embed.add_field(name = "Best Champions", value = f"{champions}", inline = False)
		embed.add_field(name = "Mastery Stats", value = f"{len(m7)}x <:mastery7:993688390723715172> {len(m6)}x <:mastery6:993688366317043772> {len(m5)}x <:mastery5:993688341063159860>\nTotal Mastery Points: {total_points}", inline = True)
	
		embed.set_author(name = "Killer Bot | League Of Legends Profile", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
		embed.set_thumbnail(url = summoner.profile_icon.url)

		file_ = nextcord.File(f"{user}.png")
		embed.set_image(url = f"attachment://{user}.png")

		await ctx.send(embed = embed, file = file_)

		try:
			os.remove(f"{user}.png")	
		except:
			print(f"{user}.png was not found on local files.")

	# Champ Command
	@commands.command(description = "Show champion analytics by U.GG")
	async def champ(self, ctx: commands.Context, champion : str = "Annie", region : str = "world", elo : str = "all"):
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

		embed = nextcord.Embed(
			title = f"{champion} Information",
			description = f"Displaying statistics for {champion}\nElo: {embed_elo.capitalize()}\nRegion: {region.upper()}",
			color = int(embed_color, 16),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)
	
		embed.add_field(name = "Champion Analytics (U.GG)", value = f"Tier: {tier}\nWin Rate: {win_rate}\nRanking: {ranking}\nPick Rate: {pick_rate}\nBan Rate: {ban_rate}\nMatches: {matches}", inline = False)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Analytics", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

		embed.set_thumbnail(url = champ.image.url)

		await ctx.send(embed = embed)

	# RandomChamp Command
	@commands.command(description = "Choose a random champion.")
	async def randomchamp(self, ctx : commands.Context):
		champs = cass.get_champions(region = "NA")
		
		champ = random.choice(champs)

		embed = nextcord.Embed(
			title = f"Champion: {champ.name}",
			color = nextcord.Color.random(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)

		embed.set_image(url = champ.image.url)
		embed.set_author(name = "Killer Bot | League Of Legends Champion Randomizer", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

		await ctx.send(embed = embed)

	# Tierlist Command
	@commands.command(description = "Show champion tierlist by OP.GG")
	async def tierlist(self, ctx : commands.Context, region : str = "NA", elo : str = "platinum+", role : str = "top"):
		embed = nextcord.Embed(
			title = "Champion Tierlist",
			description = f"Data provided by OP.GG",
			color = nextcord.Color.purple(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))	
		)

		tierlist = get_tierlist(region = region, tier = elo, position = role)	

		df = pd.DataFrame(tierlist)

		df.columns = ["Rank", "Champion", "Tier", "Win Rate", "Pick Rate", "Ban Rate"]

		df.sort_values(by = "Tier", inplace = True, ascending = True)
		df.reset_index(drop = True, inplace = True)
		df.drop(columns = ["Rank"], inplace = True)
		df.index = np.arange(1, len(df) + 1)

		fig, ax = plt.subplots(figsize = (21, 15))

		ax.xaxis.set_visible(False) 
		ax.yaxis.set_visible(False)
		
		ax.set_frame_on(False)
		ax.set_title(
			"Tierlist for " + region.upper() + " | " + elo.capitalize() + " | " + role.capitalize(), 
			fontsize = 30, 
			fontweight = "bold", 
			color = "white"
		)

		table_ = table(ax, df, loc = "upper right", colWidths = [0.17] * len(df.columns))
		table_.auto_set_font_size(False)
		table_.set_fontsize(15)
		table_.scale(1.1, 1.2)

		plt.savefig("tierlist.png", transparent = True)

		file_ = nextcord.File("tierlist.png")

		embed.set_image(url = "attachment://tierlist.png")
		embed.set_author(name = "Killer Bot | League Of Legends Champion Tierlist", icon_url = self.bot.user.avatar.url)
		embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

		await ctx.send(embed = embed, file = file_)

		try:
			os.remove(f"tierlist.png")	
		except:
			print(f"tierlist.png was not found on local files.")

	# # Tierlist Command Using Embed Instead Of Dataframe
	# @commands.command(description = "Show champion tierlist by OP.GG")
	# async def tierlist(self, ctx : commands.Context, region : str = "NA", elo : str = "platinum+", role : str = "top"):
	# 	embed = nextcord.Embed(
	# 		title = "Champion Tierlist",
	# 		description = f"Data provided by OP.GG",
	# 		color = nextcord.Color.random(),
	# 		timestamp = datetime.now(tz = timezone("US/Eastern"))	
	# 	)

	# 	tierlist = get_tierlist(region = region, tier = elo, position = role)

	# 	tierlist["tier"].sort()

	# 	embed.add_field(name = "Position", value = f"\n".join(tierlist['tier']), inline = True) 
	# 	embed.add_field(name = "Champion", value = f"\n".join(tierlist['champion']), inline = True) 
	# 	embed.add_field(name = "Tier", value = f"\n".join(tierlist['level']), inline = True) 
	# 	embed.add_field(name = "Win Rate", value = f"\n".join(tierlist['winrate']), inline = True) 
	# 	embed.add_field(name = "Pick Rate", value = f"\n".join(tierlist['pickrate']), inline = True) 
	# 	embed.add_field(name = "Ban Rate", value = f"\n".join(tierlist['banrate']), inline = True) 

	# 	embed.set_author(name = "Killer Bot | League Of Legends Champion Tierlist", icon_url = self.bot.user.avatar.url)
	# 	embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)

	# 	await ctx.send(embed = embed)

def setup(bot):
	bot.add_cog(LeagueCommands(bot))