import asyncio
import nextcord
import wavelink

from nextcord.ext import commands, application_checks
from nextcord.abc import GuildChannel

from helpers.config import LAVALINK_HOST, LAVALINK_PASSWORD, LAVALINK_PORT, MAIN_GUILD_ID, TESTING_GUILD_ID
from helpers.logger import Logger

logger = Logger()

# Music Cog
class Music(commands.Cog):

	# Music Constructor
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.queue = []
		self.position = 0
		self.repeat = False
		self.repeat_mode = "NONE"
		self.playing_text_channel = 0
		bot.loop.create_task(self.create_nodes())
	
	# Create Nodes Function
	async def create_nodes(self):
		await self.bot.wait_until_ready()
		node: wavelink.Node = wavelink.Node(uri = "lava1.horizxon.studio:80", password = "horizxon.studio")
		await wavelink.NodePool.connect(client = self.bot, nodes = [node])

	# Wavelink Node Ready Event
	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, node: wavelink.Node):
		logger.info(f"Node <{node.id}> is now Ready!")

	# Wavelink Track Start Event
	@commands.Cog.listener()
	async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.YouTubeTrack):
		try:
			self.queue.pop(0)
		except:
			pass

	# Wavelink Track Start Event
	@commands.Cog.listener()
	async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
		if str(reason) == "FINISHED":
			if not len(self.queue) == 0:
				next_track: wavelink.YouTubeTrack = self.queue[0]
				channel = self.bot.get_channel(self.playing_text_channel)

				try:
					await player.play(next_track)
				except:
					return await channel.send(
						embed = nextcord.Embed(
							title = f"Something went wrong while playing **{next_track.title}**",
							color = nextcord.Color.dark_red()
						)
					)
				
				await channel.send(
					embed = nextcord.Embed(
						title = f"Now playing: {next_track.title}", 
						color = nextcord.Color.blurple()
					)
				)
			else:
				pass
		else:
			logger.info(reason)
	
	# Join Command
	@nextcord.slash_command(name = "join", description = "The bot joins to the specified voice channel or your current voice channel.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def join_command(
		self, 
		interaction: nextcord.Interaction, 
		channel: GuildChannel = nextcord.SlashOption(
			name = "channel",
			description = "Channel that the bot is gonna join.",
			required = False,
			channel_types = [nextcord.ChannelType.voice]
		)
	):
		if channel is None:
			channel = interaction.user.voice.channel
		
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if player is not None:
			if player.is_connected():
				return await interaction.send("Bot is already connected to a voice channel")
		
		await channel.connect(cls = wavelink.Player)
		embed = nextcord.Embed(
			title = f"Connected to {channel.name}", 
			color = nextcord.Color.blurple()
		)
		await interaction.send(embed = embed)

	# Leave Command
	@nextcord.slash_command(name = "leave", description = "The bot leaves your voice channel.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def leave_command(self, interaction: nextcord.Interaction):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if player is None:
			return await interaction.send("Bot is not connected to any voice channel")
		
		await player.disconnect()
		embed = nextcord.Embed(
			title = "Disconnected", 
			color = nextcord.Color.dark_blue()
		)
		await interaction.send(embed = embed)
	
	# Play Command
	@nextcord.slash_command(name = "play", description = "Play a youtube track in the voice channel that the bot is connected.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def play_command(self, interaction: nextcord.Interaction, *, search: str = nextcord.SlashOption(name = "search", description = "The track that you want to play.", required = True)):
		try:
			search = await wavelink.YouTubeTrack.search(search, return_first = True)
		except:
			return await interaction.send(
				embed = nextcord.Embed(
					title = "Something went wrong while searching for this track", 
					color = nextcord.Color.dark_red()
				)
			)

		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if not interaction.guild.voice_client:
			vc: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
		else:
			vc: wavelink.Player = interaction.guild.voice_client
		
		if not vc.is_playing():
			try:
				await vc.play(search)
			except:
				return await interaction.send(
					embed = nextcord.Embed(
						title = "Something went wrong while playing this track", 
						color = nextcord.Color.dark_red()
					)
				)
		else:
			self.queue.append(search)

		embed = nextcord.Embed(title = f"Added {search} To the queue", color = nextcord.Color.blurple())
		await interaction.send(embed = embed)
	
	# Stop Command
	@nextcord.slash_command(name = "stop", description = "Stop the track that's being played.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def stop_command(self, interaction: nextcord.Interaction):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if player is None:
			return await interaction.send("Bot is not connected to any voice channel")

		self.queue.clear()
		
		if player.is_playing():
			await player.stop()
			embed = nextcord.Embed(title = "Playback Stoped", color = nextcord.Color.gold())
			return await interaction.send(embed = embed)
		else:
			return await interaction.send("Nothing is playing right now.")
	
	# Pause Command
	@nextcord.slash_command(name = "pause", description = "Pause the current track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def pause_command(self, interaction: nextcord.Interaction):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if player is None:
			return await interaction.send("Bot is not connected to any voice channel")
		
		if not player.is_paused():
			if player.is_playing():
				await player.pause()
				embed = nextcord.Embed(title = "Playback Paused", color = nextcord.Color.gold())
				return await interaction.send(embed = embed)
			else:
				return await interaction.send("Nothing is playing right now")
		else:
			return await interaction.send("Playback is Already paused")
	
	# Resume Command
	@nextcord.slash_command(name = "resume", description = "Resume the track that if it's paused.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def resume_command(self, interaction: nextcord.Interaction):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if player is None:
			return await interaction.send("Bot is not connnected to any voice channel")
		
		if player.is_paused():
			await player.resume()
			embed = nextcord.Embed(title = "Playback resumed", color = nextcord.Color.gold())
			return await interaction.send(embed = embed)
		else:
			if not len(self.queue) == 0:
				track: wavelink.YouTubeTrack = self.queue[0]
				player.play(track)
				return await interaction.send(
					embed = nextcord.Embed(
						title = f"Now playing: {track.title}",
						color = nextcord.Color.blurple()
					)
				)
			else:
				return await interaction.send("Playback is not paused")

	# Volume Command | Wavelink bug
	@nextcord.slash_command(name = "volume", description = "Set the bot's volume. [BUG]", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def volume_command(self, interaction: nextcord.Interaction, to: int):
		if to > 100:
			return await interaction.send("Volume should be between 0 and 100")
		elif to < 1:
			return await interaction.send("Volume should be between 0 and 100")

		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		await player.set_volume(to)
		embed = nextcord.Embed(title = f"Changed Volume to {to}", color = nextcord.Color.blurple())
		await interaction.send(embed = embed)

	# Play Now Command
	@nextcord.slash_command(name = "playnow", description = "Play a track, ignoring the queue.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	@application_checks.has_permissions(administrator = True)
	async def play_now_command(self, interaction: nextcord.Interaction, *, search: str = nextcord.SlashOption(name = "search", description = "The track that you want to play.", required = True)):
		try:
			search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
		except:
			return await interaction.send(
				embed = nextcord.Embed(
					title = "Something went wrong while searching for this track", 
					color = nextcord.Color.blurple()
				)
			)
		
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if not interaction.guild.voice_client:
			vc: wavelink.Player = await interaction.user.voice.channel(cls=wavelink.Player)
			await player.connect(interaction.user.voice.channel)
		else:
			vc: wavelink.Player = interaction.guild.voice_client
		try:
			await vc.play(search)
		except:
			return await interaction.send(
				embed = nextcord.Embed(
					title = "Something went wrong while playing this track", 
					color = nextcord.Color.dark_red()
				)
			)
		await interaction.send(
			embed = nextcord.Embed(
				title = f"Playing: **{search.title}** Now", 
				color = nextcord.Color.blurple()
			)
		)

	# Now Playing Command
	@nextcord.slash_command(name = "nowplaying", description = "See the track that's being played.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def now_playing_command(self, interaction: nextcord.Interaction):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if player is None:
			return await interaction.send("Bot is not connected to any voice channel")

		if player.is_playing():
			embed = nextcord.Embed(
				title = f"Now Playing: {player.track}",
				color = nextcord.Color.blurple()
			)

			t_sec = int(player.track.length)
			hour = int(t_sec/3600)
			min = int((t_sec%3600)/60)
			sec = int((t_sec%3600)%60)
			length = f"{hour}hr {min}min {sec}sec" if not hour == 0 else f"{min}min {sec}sec"

			embed.add_field(name = "Artist", value = player.track.info['author'], inline = False)
			embed.add_field(name = "Length", value = f"{length}", inline = False)

			return await interaction.send(embed = embed)
		else:
			await interaction.send("Nothing is playing right now")

	# Search Command
	@nextcord.slash_command(name = "search", description = "Search the specified track on youtube and return 5 entries.")
	async def search_command(self, interaction: nextcord.Interaction, *, search: str = nextcord.SlashOption(name = "search", description = "The track that you want to search.", required = True)):
		try:
			tracks = await wavelink.YouTubeTrack.search(query = search)
		except:
			return await interaction.send(embed = nextcord.Embed(title = "Something went wrong while searching for this track", color=nextcord.Color.from_rgb(255, 255, 255)))

		if tracks is None:
			return await interaction.send("No tracks found")

		embed = nextcord.Embed(
			title = "Select the track: ",
			description = ("\n".join(f"**{i+1}. {t.title}**" for i, t in enumerate(tracks[:5]))),
			color = nextcord.Color.blurple()
		)
		msg = await interaction.send(embed = embed)

		emojis_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '❌']
		emojis_dict = {
			'1️⃣': 0,
			"2️⃣": 1,
			"3️⃣": 2,
			"4️⃣": 3,
			"5️⃣": 4,
			"❌": -1
		}

		for emoji in list(emojis_list[:min(len(tracks), len(emojis_list))]):
			await msg.add_reaction(emoji)

		def check(res, user):
			return(res.emoji in emojis_list and user == interaction.user and res.message.id == msg.id)

		try:
			reaction, _ = await self.bot.wait_for("reaction_add", timeout = 60.0, check = check)
		except asyncio.TimeoutError:
			await msg.delete()
			return
		else:
			await msg.delete()

		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		try:
			if emojis_dict[reaction.emoji] == -1: return
			choosed_track = tracks[emojis_dict[reaction.emoji]]
		except:
			return

		vc: wavelink.Player = interaction.guild.voice_client or await interaction.user.voice.channel.connect(cls=wavelink.Player)

		if not player.is_playing() and not player.is_paused():
			try:
				await vc.play(choosed_track)
			except:
				return await interaction.send(
					embed = nextcord.Embed(
						title = "Something went wrong while playing this track", 
						color = nextcord.Color.dark_red()
						)
					)
		else:
			self.queue.append(choosed_track)
		
		await interaction.send(
			embed = nextcord.Embed(
				title = f"Added {choosed_track.title} to the queue", 
				color = nextcord.Color.blurple()
			)
		)

	# Skip Command
	@nextcord.slash_command(name = "skip", description = "Skip the current track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def skip_command(self, interaction: nextcord.Interaction):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)

		if not len(self.queue) == 0:
			next_track: wavelink.YouTubeTrack = self.queue[0]
			try:
				await player.play(next_track)
			except:
				return await interaction.send(
					embed = nextcord.Embed(
						title = "Something went wrong while playing this track", 
						color = nextcord.Color.dark_red()
					)
				)

			await interaction.send(
				embed = nextcord.Embed(
					title = f"Now playing {next_track.title}", 
					color = nextcord.Color.blurple()
					)
				)
		else:
			await interaction.send("The queue is empty")

	# Queue Command
	@nextcord.slash_command(name = "queue", description = "See the tracks that are queued.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def queue_command(self, interaction: nextcord.Interaction, *, search: str = nextcord.SlashOption(name = "search", required = False)):
		node = wavelink.NodePool.get_node()
		player = node.get_player(interaction.guild)
		
		if search is None:
			if not len(self.queue) == 0:
				embed = nextcord.Embed(
					title = f"Now playing: {player.track}" if player.is_playing else "Queue: ",
					description = "\n".join(f"**{i+1}. {track}**" for i, track in enumerate(self.queue[:10])) if not player.is_playing else "**Queue: **\n"+"\n".join(f"**{i+1}. {track}**" for i, track in enumerate(self.queue[:10])),
					color = nextcord.Color.blurple()
				)

				return await interaction.send(embed = embed)
			else:
				return await interaction.send(
					embed = nextcord.Embed(
						title = "The queue is empty", 
						color = nextcord.Color.blurple()
						)
					)
		else:
			try:
				track = await wavelink.YouTubeTrack.search(query = search, return_first = True)
			except:
				return await interaction.send(
					embed = nextcord.Embed(
						title = "Something went wrong while searching for this track", 
						color = nextcord.Color.dark_red()
						)
					)
			
			if not interaction.guild.voice_client:
				vc: wavelink.Player = await interaction.user.voice.channel(cls = wavelink.Player)
				await player.connect(interaction.user.voice.channel)
			else:
				vc: wavelink.Player = interaction.guild.voice_client
			
			if not vc.is_playing():
				try:
					await vc.play(track)
				except:
					return await interaction.send(
						embed = nextcord.Embed(
							title = "Something went wrong while playing this track", 
							color = nextcord.Color.dark_red()
						)
					)
			else:
				self.queue.append(track)
			
			await interaction.send(
				embed = nextcord.Embed(
					title = f"Added {track.title} to the queue", 
					color = nextcord.Color.blurple()
					)
				)          

def setup(bot: commands.Bot):
	bot.add_cog(Music(bot))