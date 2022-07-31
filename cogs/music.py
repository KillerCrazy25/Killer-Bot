from datetime import datetime, timedelta
import discord, wavelink
from pytz import timezone
from discord.ext import commands, bridge

from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID, LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD

# Panel View

class Panel(discord.ui.View):

	# Panel Constructor

	def __init__(self, vc, ctx, bot):
		super().__init__(timeout = None)
		self.vc = vc
		self.ctx = ctx
		self.bot = bot

	# Timeout Event

	async def on_timeout(self):
		for child in self.children:
			child.disabled = True

		await self.message.edit(view = self)

	# Pause / Resume Button

	@discord.ui.button(label = "Pause / Resume", style = discord.ButtonStyle.blurple)
	async def pause_resume_callback(self, button : discord.ui.Button, interaction : discord.Interaction):
		if not interaction.user == self.ctx.author:
			return await interaction.response.send_message("You can't do that. Run the command yourself to use these buttons.", ephemeral = True)

		for child in self.children:
			child.disabled = False

		if self.vc.is_paused():
			await self.vc.resume()
			await interaction.message.edit(content = "▶ Resumed", view = self)
		else:
			await self.vc.pause()
			await interaction.message.edit(content = "⏸ Paused", view = self)

	# Queue Button

	@discord.ui.button(label = "Queue", style = discord.ButtonStyle.blurple)
	async def queue(self, button: discord.ui.Button, interaction: discord.Interaction):
		if not interaction.user == self.ctx.author:
			return await interaction.response.send_message("You can't do that. Run the command yourself to use these buttons.", ephemeral = True)

		for child in self.children:
			child.disabled = False

		button.disabled = True

		if self.vc.queue.is_empty:
			return await interaction.response.send_message("Queue is empty. Add tracks to queue using `k!play`.", ephemeral = True)
	
		embed = discord.Embed(title = "Queue")

		embed.set_author(name = "Killer Bot | Music", icon_url = self.bot.user.avatar.url)

		queue = self.vc.queue.copy()
		songCount = 0

		for song in queue:
			songCount += 1
			embed.add_field(name = f"{str(songCount)}) {song}", value = u"\u2063", inline = False)

		await interaction.message.edit(embed = embed, view = self)

	# Skip Button

	@discord.ui.button(label = "Skip", style = discord.ButtonStyle.blurple)
	async def skip(self, button: discord.ui.Button, interaction: discord.Interaction):
		if not interaction.user == self.ctx.author:
			return await interaction.response.send_message("You can't do that. Run the command yourself to use these buttons.", ephemeral = True)

		for child in self.children:
			child.disabled = False

		button.disabled = True
		if self.vc.queue.is_empty:
			return await interaction.response.send_message("Queue is empty. Add tracks to queue using `k!play`.", ephemeral = True)

		try:
			next_song = self.vc.queue.get()
			await self.vc.play(next_song)
			await interaction.message.edit(content = f"Now Playing `{next_song}`", view = self)

		except Exception:
			return await interaction.response.send_message("Queue is empty. Add tracks to queue using `k!play`.", ephemeral = True)

	# Disconnect Button

	@discord.ui.button(label = "Disconnect", style = discord.ButtonStyle.red)
	async def disconnect_callback(self, button : discord.ui.Button, interaction : discord.Interaction):
		if not interaction.user == self.ctx.author:
			return await interaction.response.send_message("You can't do that. Run the command yourself to use these buttons.", ephemeral = True)

		await self.vc.disconnect()

		for child in self.children:
			child.disabled = True

		await interaction.message.edit(content = "❌ Disconnected.", view = self)

# Music Cog

class Music(commands.Cog):

	# Music Constructor

	def __init__(self, bot : bridge.Bot):
		self.bot = bot
		bot.loop.create_task(self.node_connect())

	# Node Ready Event

	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, node : wavelink.Node):
		print(f"Node {node.identifier} is ready to use!")

	# Connect Node Function

	async def node_connect(self):
		await self.bot.wait_until_ready()
		await wavelink.NodePool.create_node(bot = self.bot, host = LAVALINK_HOST, port = LAVALINK_PORT, password = LAVALINK_PASSWORD, https = True)

	# Node Ready Event

	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, node: wavelink.Node):
		print(f'Node <{node.identifier}> is ready!')

	# On Track End Event

	@commands.Cog.listener()
	async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
		ctx = player.ctx
		vc: player = ctx.voice_client
		
		if vc.loop:
			await ctx.respond(f"Now playing: {track.title}")
			return await vc.play(track)

		if vc.queue.is_empty:
			return

		next_song = vc.queue.get()

		await vc.play(next_song)
		await ctx.respond(f"Now playing: {next_song.title}")

	# Play Command	

	@bridge.bridge_command(description = "Play a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def play(self, ctx : bridge.BridgeContext, *, search : wavelink.YouTubeTrack):
		await ctx.defer()

		if not ctx.voice_client:
			vc : wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player)

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if vc.queue.is_empty and not vc.is_playing():
			await vc.play(search)	

			embed = discord.Embed(
				title = f"▶ Playing `{search.title}`",
				description = f"Author: {search.author}",
				color = discord.Color.green(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			)

			embed.set_author(name = "Killer Bot | Music", icon_url = self.bot.user.avatar.url)
			embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
			embed.set_thumbnail(url = search.thumbnail)
			embed.set_image(url = search.thumbnail)

			await ctx.respond(embed = embed, view = Panel(vc, ctx, self.bot))

		else:
			await vc.queue.put_wait(search)
			await ctx.respond(f'Added `{search.title}` to the queue...')

		vc.ctx = ctx
		try:
			if vc.loop: return
		except Exception:
			setattr(vc, "loop", False)

	# Pause Command

	@bridge.bridge_command(description = "Pause a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def pause(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.respond("Play a track before try to pause something.")

		await vc.pause()
		await ctx.respond(embed = discord.Embed(
			description = f"⏸ Track is now paused.",
			color = discord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Music", 
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {ctx.author}",
			icon_url = ctx.author.avatar.url
		)
	)

	# Resume Command
		
	@bridge.bridge_command(description = "Resume a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def resume(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.respond("Track is not paused.")
		
		await vc.resume()
		await ctx.respond(embed = discord.Embed(
			description = f"▶ Track is now resumed.",
			color = discord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Music", 
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {ctx.author}",
			icon_url = ctx.author.avatar.url
		)
	)

	# Skip Command

	@bridge.bridge_command(description = "Skip to the next track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def skip(self, ctx: bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client
			
		if not vc.is_playing():
			return await ctx.respond("Play a track before try to skip something.")
		
		try:
			next_song = vc.queue.get()

			await ctx.respond(f"Now Playing `{next_song}`")		
			return await vc.play(next_song)

		except Exception:
			return await ctx.respond("Queue is empty. Add tracks to queue using `k!play`.")

	# Stop Command

	@bridge.bridge_command(description = "Stop a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def stop(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.respond("Play a track before try to stop something.")

		await vc.stop()
		await ctx.respond(embed = discord.Embed(
			description = f"⏹ Track is now stopped.",
			color = discord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Music", 
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {ctx.author}",
			icon_url = ctx.author.avatar.url
		))

	# Disconnect Command

	@bridge.bridge_command(description = "Disconnect from voice.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def disconnect(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		await vc.disconnect()
		await ctx.respond(embed = discord.Embed(
			description = f"❌ Disconnected from {ctx.author.voice.channel}.",
			color = discord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Music", 
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {ctx.author}",
			icon_url = ctx.author.avatar.url
		))

	# Loop Command

	@bridge.bridge_command(description = "Loop a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def loop(self, ctx: bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")

		vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.respond("Play a track before try to loop something.")
		
		try: 
			vc.loop ^= True

		except:
			setattr(vc, "loop", False)

		if vc.loop:
			return await ctx.respond("🔁 Loop is now enabled.")

		else:
			return await ctx.respond("🔁 Loop is now disabled.")

	# Queue Command

	@bridge.bridge_command(description = "Show the track queue.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def queue(self, ctx: bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
		
		vc: wavelink.Player = ctx.voice_client

		if vc.queue.is_empty:
			return await ctx.respond("Queue is empty. Add tracks to queue using `k!play`.")
		
		embed = discord.Embed(title = "Queue")

		embed.set_author(name = "Killer Bot | Music", icon_url = self.bot.user.avatar.url)

		queue = vc.queue.copy()
		songCount = 0

		for song in queue:
			songCount += 1
			embed.add_field(name = f"{str(songCount)}) {song}", value = u"\u2063", inline = False)
			
		await ctx.respond(embed = embed)

	# Clearqueue Command

	@bridge.bridge_command(description = "Clears track queue.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def clearqueue(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
		
		vc: wavelink.Player = ctx.voice_client

		if vc.queue.is_empty:
			return await ctx.respond("Queue is empty. Cannot clear anything.")

		await ctx.respond("Queue has been cleared.")
		return vc.queue.clear()

	# Volume Command

	@bridge.bridge_command(description = "Set bot's volume.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def volume(self, ctx: bridge.BridgeContext, volume: int):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.respond("Play something before try to set my volume.")
		
		if volume > 100:
			return await ctx.respond("🔊 Please select a volume lower than 100.")
			
		elif volume < 0:
			return await ctx.respond("🔊 Please select a volume higher than 0.")

		await ctx.respond(f"🔊 Set the volume to `{volume}%`")
		return await vc.set_volume(volume)

	@bridge.bridge_command(description = "Show information about the current track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def nowplaying(self, ctx: bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.respond("Nothing is playing.")

		embed = discord.Embed(
			title = f"Now Playing {vc.track.title}", 
			description = f"Artist: {vc.track.author}",
			color = discord.Color.yellow()
		).set_author(
			name = "Killer Bot | Music",
			icon_url = self.bot.user.avatar.url
		)

		embed.add_field(name = "Duration", value = f"`{str(timedelta(seconds = vc.track.length))}`")

		return await ctx.send(embed = embed)

def setup(bot):
	bot.add_cog(Music(bot))