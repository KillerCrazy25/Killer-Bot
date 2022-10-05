from typing import Optional
from requests_html import HTMLSession

RUNES_BY_NAME = {
	# Rune Trees
	"domination": "<:DominationKeystone:1026324297750413354>",
	"precision": "<:PrecisionKeystone:1026324246802219099>",
	"sorcery": "<:SorceryKeystone:1026324801037549679>",
	"resolve": "<:ResolveKeystone:1026324786168741958>",
	"inspiration": "<:InspirationKeystone:1026324360316846111>",
	# Precision Keys
	"press_the_attack": "<:PressTheAttack:1026324256029687889>",
	"lethal_tempo": "<:LethalTempoTemp:1026324380613103637>",
	"fleet_footwork": "<:FleetFootwork:1026324314728955956>",
	"conqueror": "<:Conqueror:1026324280738324561>",
	# Precision 1
	"overheal": "<:Overheal:1026324234244456508>",
	"triumph": "<:Triumph:1026324752043876362>",
	"presence_of_mind": "<:PresenceOfMind:1026324251936039034>",
	# Precision 2
	"legend_alacrity": "<:LegendAlacrity:1026324367547838494>",
	"legend_tenacity": "<:LegendTenacity:1026324376737554534>",
	"legend_bloodline": "<:LegendBloodline:1026324371930894387>",
	# Precision 3
	"coup_de_grace": "<:CoupDeGrace:1026324285213655090>",
	"cut_down": "<:CutDown:1026324288753651722>",
	"last_stand": "<:LastStand:1026324362225262643>",
	# Domination Keys
	"electrocute": "<:Electrocute:1026324299558162543>",
	"predator": "<:Predator:1026324250245734430>",
	"dark_harvest": "<:DarkHarvest:1026324292968923197>",
	"hail_of_blades": "<:HailOfBlades:1026324348484718695>",
	# Domination 1
	"cheap_shot": "<:CheapShot:1026324273918390293>",
	"taste_of_blood": "<:GreenTerror_TasteOfBlood:1026324341916442655>",
	"sudden_impact": "<:SuddenImpact:1026324833765687386>",
	# Domination 2
	"zombie_ward": "<:ZombieWard:1026324778090508330>",
	"ghost_poro": "<:GhostPoro:1026324327051833455>",
	"eyeball_collection": "<:EyeballCollection:1026324303312080976>",
	# Domination 3
	"treasure_hunter": "<:TreasureHunter:1026324748168339566>",
	"ingenious_hunter": "<:IngeniousHunter:1026324356349054986>",
	"relentless_hunter": "<:RelentlessHunter:1026324783324987403>",
	"ultimate_hunter": "<:UltimateHunter:1026324753310568519>",
	# Sorcery Keys
	"summon_aery": "<:SummonAery:1026324737632243722>",
	"arcane_comet": "<:ArcaneComet:1026324261767483484>",
	"phase_rush": "<:PhaseRush:1026324241580310549>",
	# Sorcery 1
	"nullifying_orb": "<:Pokeshield:1026324244071714916>",
	"manaflow_band": "<:ManaflowBand:1026324393208582164>",
	"nimbus_cloak": "<:NimbusCloak:1026324405841825792>",
	# Sorcery 2
	"transcendence": "<:Transcendence:1026324745257504798>",
	"celerity": "<:CelerityTemp:1026324270411943947>",
	"absolute_focus": "<:AbsoluteFocus:1026324257518653490>",
	# Sorcery 3
	"scorch": "<:Scorch:1026324794070810666>",
	"waterwalking": "<:Waterwalking:1026324775611678770>",
	"gathering_storm": "<:GatheringStorm:1026324324795289670>",
	# Resolve Keys
	"grasp_of_the_undying": "<:GraspOfTheUndying:1026324333221646418>",
	"aftershock": "<:VeteranAftershock:1026324772931506216>",
	"guardian": "<:Guardian:1026324344454008903>",
	# Resolve 1
	"demolish": "<:Demolish:1026324294407557151>",
	"font_of_life": "<:FontOfLife:1026324316528332810>",
	"shield_bash": "<:MirrorShell:1026324403866316841>",
	# Resolve 2
	"conditioning": "<:Conditioning:1026324278368534633>",
	"second_wind": "<:SecondWind:1026324797677899797>",
	"bone_plating": "<:BonePlating:1026324266779684934>",
	# Resolve 3
	"overgrowth": "<:Overgrowth:1026324414079438858>",
	"revitalize": "<:Revitalize:1026324789255733328>",
	"unflitching": "<:Unflinching:1026324756569542667>",
	# Inspiration Keys
	"glacial_augment": "<:GlacialAugment:1026324329295786024>",
	"unsealed_spellbook": "<:UnsealedSpellbook:1026324758767349830>",
	"first_strike": "<:FirstStrike:1026324308148092963>",
	# Inspiration 1
	"hextech_flashtraption": "<:HextechFlashtraption:1026324353522073651>",
	"magical_footwear": "<:MagicalFootwear:1026324387844075630>",
	"perfect_timing": "<:PerfectTiming:1026324236438097992>",
	# Inspiration 2
	"futures_market": "<:FuturesMarket:1026324320324173914>",
	"minion_dematerializer": "<:MinionDematerializer:1026324395616116816>",
	"biscuit_delivery": "<:BiscuitDelivery:1026324265223589969>",
	# Inspiration 3
	"cosmic_insight": "<:CosmicInsight:1026324283452035083>",
	"approach_velocity": "<:ApproachVelocity:1026324259796176947> ",
	"time_warp_tonic": "<:TimeWarpTonic:1026324743130976308>",
	# Avoid errors
	"unknown": ":question:"
}

SHARDS_BY_NAME = {
	"adaptive_force": "<:statmodsadaptiveforceicon:1026324807089913916>",
	"armor": "<:statmodsarmoricon:1026324813037441024>",
	"attack_speed": "<:statmodsattackspeedicon:1026324820570415124>",
	"magic_resist": "<:statmodsmagicresicon:1026324826253697074>",
	"scaling_bonus_health": "<:statmodshealthscalingicon:1026324821879042079>",
	"scaling_cdr": "<:statmodscdrscalingicon:1026693809939152996>",
	"unknown": ":question:"
}

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
			"lan": "la1",
			"las": "la1",
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

	def format_rune_name(self, rune: str):
		result = rune.replace("The Keystone ", "").replace("The Rune ", "").replace("'", "").replace(":", "")
		
		return result

	def format_shard_name(self, shard: str):
		result = shard.replace("The ", "").replace(" Shard", "")

		return result

	def get_rune_emoji(self, rune: str):
		rune = rune.lower().replace("the keystone ", "").replace("the rune ", "").replace("'", "").replace(" ", "_").replace(":", "")
		try:
			emoji = RUNES_BY_NAME[rune]
		except KeyError:
			emoji = RUNES_BY_NAME["unknown"]

		return emoji

	def get_rune_key_emoji(self, rune_key: str):
		rune_key = rune_key.lower()
		try:
			emoji = RUNES_BY_NAME[rune_key]
		except KeyError:
			emoji = RUNES_BY_NAME["unknown"]
		return emoji

	def get_shard_emoji(self, shard: str):
		shard = shard.lower().replace("the ", "").replace(" shard", "").replace(" ", "_")
		try:
			emoji = SHARDS_BY_NAME[shard]
		except KeyError:
			emoji = SHARDS_BY_NAME["unknown"]
		return emoji

	def get_rune_tree_by_key(self, rune_tree: str):
		"""Insert a parsed rune."""
		if rune_tree == "Electrocute" or rune_tree == "Predator" or rune_tree == "Dark Harvest" or rune_tree == "Hail Of Blades":
			return "Domination"
		elif rune_tree == "Press the Attack" or rune_tree == "Fleet Footwork" or rune_tree == "Lethal Tempo" or rune_tree == "Conqueror":
			return "Precision"
		elif rune_tree == "Summon Aery" or rune_tree == "Arcane Comet" or rune_tree == "Phase Rush":
			return "Sorcery"
		elif rune_tree == "Grasp of the Undying" or rune_tree == "Aftershock" or rune_tree == "Guardian":
			return "Resolve"
		elif rune_tree == "Glacial Augment" or rune_tree == "Unsealed Spellbook" or rune_tree == "First Strike":
			return "Inspiration"
		else:
			return "Unknown"

	def get_rune_tree_by_rune(self, rune: str):
		if (rune == "Cheap Shot" or rune == "Taste of Blood" or rune == "Sudden Impact" or rune == "Zombie Ward" or rune == "Ghost Poro" or rune == "Eyeball Collection" or rune == "Treasure Hunter" or rune == "Ingenious Hunter" or rune == "Relentless Hunter" or rune == "Ultimate Hunter"):
			return "Domination"
		elif (rune == "Overheal" or rune == "Triumph" or rune == "Presence of Mind" or rune == "Legend Alacrity" or rune == "Legend Tenacity" or rune == "Legend Bloodline" or rune == "Coup de Grace" or rune == "Cut Down" or rune == "Last Stand"):
			return "Precision"
		elif (rune == "Nullifying Orb" or rune == "Manaflow Band" or rune == "Nimbus Cloak" or rune == "Transcendence" or rune == "Celerity" or rune == "Absolute Focus" or rune == "Scorch" or rune == "Waterwalking" or rune == "Gathering Storm"):
			return "Sorcery"
		elif (rune == "Demolish" or rune == "Font of Life" or rune == "Shield Bash" or rune == "Conditioning" or rune == "Second Wind" or rune == "Bone Plating" or rune == "Overgrowth" or rune == "Revitalize" or rune == "Unflitching"):
			return "Resolve"
		elif (rune == "Hextech Flashtraption" or rune == "Magical Footwear" or rune == "Perfect Timing" or rune == "Futures Market" or rune == "Minion Dematerializer" or rune == "Biscuit Delivery" or rune == "Cosmic Insight" or rune == "Approach Velocity" or rune == "Time Warp Tonic"):
			return "Inspiration"
		else:
			return "Unknown"

class LeagueScraper:
	BASE_STATS_URL = "https://u.gg/lol/champions/{}/build/{}?region={}&rank={}"

	def __init__(self, parser: Parser):
		self.parser = parser
		self.session = HTMLSession()

	def _get_stats_url(self, champion: str, region: str, rank: str, role: str) -> str:
		region = self.parser.region_parser(region)
		rank = self.parser.from_normal_to_gg(rank)
		role = self.parser.role_parser(role)

		return self.BASE_STATS_URL.format(champion, role, region, rank)

	def get_champion_analytics(self, champion: str = "annie", region: str = "NA", elo: str = "platinum+", role: str = "top") -> tuple:
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
		runes_container = r.html.find(".recommended-build_runes", first = True)
		data_divs = container.find(".value") # Tier, Win Rate, Rank, Pick Rate, Ban Rate, Matches

		primary_runes_div = runes_container.find(".primary-tree", first = True)
		secondary_runes_div = runes_container.find(".secondary-tree", first = True)

		data = [div.text for div in data_divs]

		primary_active_runes_div = primary_runes_div.find("div.perk-active")
		secondary_active_runes_div = secondary_runes_div.find("div.perk-active")
		active_shards_div = secondary_runes_div.find("div.shard-active")

		primary_image_elements = [element.find("img", first = True) for element in primary_active_runes_div]
		secondary_image_elements = [element.find("img", first = True) for element in secondary_active_runes_div]
		shard_image_elements = [element.find("img", first = True) for element in active_shards_div]

		# primary_images = [img.attrs["alt"].lower().replace("the keystone ", "").replace("the rune ", "").replace("'", "").replace(" ", "_").replace(":", "") for img in primary_image_elements]
		# secondary_images = [img.attrs["alt"].lower().replace("the rune ", "").replace(" ", "_").replace(":", "") for img in secondary_image_elements]
		# shard_images = [img.attrs["alt"].lower().replace("the ", "").replace(" shard", "").replace(" ", "_").replace(":", "") for img in shard_image_elements]

		primary_images = [img.attrs["alt"] for img in primary_image_elements]
		secondary_images = [img.attrs["alt"] for img in secondary_image_elements]
		shard_images = [img.attrs["alt"] for img in shard_image_elements]

		runes = (primary_images, secondary_images, shard_images)
		
		return data, runes
	
if __name__ == "__main__":
	parser = Parser()
	scraper = LeagueScraper(parser)

	stats, runes = scraper.get_champion_analytics("sion", "world", "platinum+", "top")

	print("---------------------------------------------------------------")
	print("STATS")
	print("---------------------------------------------------------------")
	print(stats)
	print("---------------------------------------------------------------")
	print("RUNES")
	print("---------------------------------------------------------------")
	print(runes)
	print("---------------------------------------------------------------")
	print(str(parser))