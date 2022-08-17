from datetime import datetime, timedelta
import nextcord, wavelink
from pytz import timezone
from nextcord.ext import commands

from helpers.config import MAIN_GUILD_ID, TESTING_GUILD_ID, LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD

# Panel View

class Panel(nextcord.ui.View):

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

	@nextcord.ui.button(label = "Pause / Resume", style = nextcord.ButtonStyle.blurple)
	async def pause_resume_callback(self, button : nextcord.ui.Button, interaction : nextcord.Interaction):
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

	@nextcord.ui.button(label = "Queue", style = nextcord.ButtonStyle.blurple)
	async def queue(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
		if not interaction.user == self.ctx.author:
			return await interaction.response.send_message("You can't do that. Run the command yourself to use these buttons.", ephemeral = True)

		for child in self.children:
			child.disabled = False

		button.disabled = True

		if self.vc.queue.is_empty:
			return await interaction.response.send_message("Queue is empty. Add tracks to queue using `k!play`.", ephemeral = True)
	
		embed = nextcord.Embed(title = "Queue")

		embed.set_author(name = "Killer Bot | Music", icon_url = self.bot.user.avatar.url)

		queue = self.vc.queue.copy()
		songCount = 0

		for song in queue:
			songCount += 1
			embed.add_field(name = f"{str(songCount)}) {song}", value = u"\u2063", inline = False)

		await interaction.message.edit(embed = embed, view = self)

	# Skip Button

	@nextcord.ui.button(label = "Skip", style = nextcord.ButtonStyle.blurple)
	async def skip(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
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

	@nextcord.ui.button(label = "Disconnect", style = nextcord.ButtonStyle.red)
	async def disconnect_callback(self, button : nextcord.ui.Button, interaction : nextcord.Interaction):
		if not interaction.user == self.ctx.author:
			return await interaction.response.send_message("You can't do that. Run the command yourself to use these buttons.", ephemeral = True)

		await self.vc.disconnect()

		for child in self.children:
			child.disabled = True

		await interaction.message.edit(content = "❌ Disconnected.", view = self)

# Music Cog

class Music(commands.Cog):

	# Music Constructor

	def __init__(self, bot : commands.Bot):
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
			await ctx.send(f"Now playing: {track.title}")
			return await vc.play(track)

		if vc.queue.is_empty:
			return

		next_song = vc.queue.get()

		await vc.play(next_song)
		await ctx.send(f"Now playing: {next_song.title}")

	# Play Command	

	@commands.command(description = "Play a track.")
	async def play(self, ctx : commands.Context, *, search : wavelink.YouTubeTrack):
		if not ctx.voice_client:
			vc : wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player)

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if vc.queue.is_empty and not vc.is_playing():
			view = Panel(vc, ctx, self.bot)
			await vc.play(search)	

			embed = nextcord.Embed(
				title = f"▶ Playing `{search.title}`",
				description = f"Author: {search.author}",
				color = nextcord.Color.green(),
				timestamp = datetime.now(tz = timezone("US/Eastern"))
			)

			embed.set_author(name = "Killer Bot | Music", icon_url = self.bot.user.avatar.url)
			embed.set_footer(text = f"Requested by {ctx.author}", icon_url = ctx.author.avatar.url)
			embed.set_thumbnail(url = search.thumbnail)
			embed.set_image(url = search.thumbnail)

			view.message = await ctx.send(embed = embed, view = view)

		else:
			await vc.queue.put_wait(search)
			await ctx.send(f'Added `{search.title}` to the queue...')

		vc.ctx = ctx
		try:
			if vc.loop: return
		except Exception:
			setattr(vc, "loop", False)

	# Pause Command

	@commands.command(description = "Pause a track.")
	async def pause(self, ctx : commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.send("Play a track before try to pause something.")

		await vc.pause()
		await ctx.send(embed = nextcord.Embed(
			description = f"⏸ Track is now paused.",
			color = nextcord.Color.red(),
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
		
	@commands.command(description = "Resume a track.")
	async def resume(self, ctx : commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.send("Track is not paused.")
		
		await vc.resume()
		await ctx.send(embed = nextcord.Embed(
			description = f"▶ Track is now resumed.",
			color = nextcord.Color.red(),
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

	@commands.command(description = "Skip to the next track.")
	async def skip(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client
			
		if not vc.is_playing():
			return await ctx.send("Play a track before try to skip something.")
		
		try:
			next_song = vc.queue.get()

			await vc.play(next_song)
			return await ctx.send(f"Now Playing `{next_song}`")		

		except Exception:
			await vc.stop()
			return await ctx.send("⏹ Stopped because queue is empty.")

	# Stop Command

	@commands.command(description = "Stop a track.")
	async def stop(self, ctx : commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.send("Play a track before try to stop something.")

		await vc.stop()
		await ctx.send(embed = nextcord.Embed(
			description = f"⏹ Track is now stopped.",
			color = nextcord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Music", 
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {ctx.author}",
			icon_url = ctx.author.avatar.url
		))

	# Disconnect Command

	@commands.command(description = "Disconnect from voice.")
	async def disconnect(self, ctx : commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		await vc.disconnect()
		await ctx.send(embed = nextcord.Embed(
			description = f"❌ Disconnected from {ctx.author.voice.channel}.",
			color = nextcord.Color.red(),
			timestamp = datetime.now(tz = timezone("US/Eastern"))
		).set_author(
			name = "Killer Bot | Music", 
			icon_url = self.bot.user.avatar.url
		).set_footer(
			text = f"Requested by {ctx.author}",
			icon_url = ctx.author.avatar.url
		))

	# Loop Command

	@commands.command(description = "Loop a track.")
	async def loop(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")

		vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.send("Play a track before try to loop something.")
		
		try: 
			vc.loop ^= True

		except:
			setattr(vc, "loop", False)

		if vc.loop:
			return await ctx.send("🔁 Loop is now enabled.")

		else:
			return await ctx.send("🔁 Loop is now disabled.")

	# Queue Command

	@commands.command(description = "Show the track queue.")
	async def queue(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
		
		vc: wavelink.Player = ctx.voice_client

		if vc.queue.is_empty:
			return await ctx.send("Queue is empty. Add tracks to queue using `k!play`.")
		
		embed = nextcord.Embed(title = "Queue")

		embed.set_author(name = "Killer Bot | Music", icon_url = self.bot.user.avatar.url)

		queue = vc.queue.copy()
		songCount = 0

		for song in queue:
			songCount += 1
			embed.add_field(name = f"{str(songCount)}) {song}", value = u"\u2063", inline = False)
			
		await ctx.send(embed = embed)

	# Clearqueue Command

	@commands.command(description = "Clears track queue.")
	async def clearqueue(self, ctx : commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
		
		vc: wavelink.Player = ctx.voice_client

		if vc.queue.is_empty:
			return await ctx.send("Queue is empty. Cannot clear anything.")

		await ctx.send("Queue has been cleared.")
		return vc.queue.clear()

	# Volume Command

	@commands.command(description = "Set bot's volume.")
	async def volume(self, ctx: commands.Context, volume: int):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.send("Play something before try to set my volume.")
		
		if volume > 100:
			return await ctx.send("🔊 Please select a volume lower than 100.")
			
		elif volume < 0:
			return await ctx.send("🔊 Please select a volume higher than 0.")

		await ctx.send(f"🔊 Set the volume to `{volume}%`")
		return await vc.set_volume(volume)

	@commands.command(description = "Show information about the current track.")
	async def nowplaying(self, ctx: commands.Context):
		if not ctx.voice_client:
			return await ctx.send("I'm not in a voice channel.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.send("You are not in a voice channel.")
			
		else:
			vc: wavelink.Player = ctx.voice_client

		if not vc.is_playing():
			return await ctx.send("Nothing is playing.")

		embed = nextcord.Embed(
			title = f"Now Playing {vc.track.title}", 
			description = f"Artist: {vc.track.author}",
			color = nextcord.Color.yellow()
		).set_author(
			name = "Killer Bot | Music",
			icon_url = self.bot.user.avatar.url
		)

		embed.add_field(name = "Duration", value = f"`{str(timedelta(seconds = vc.track.length))}`")

		return await ctx.send(embed = embed)

def setup(bot):
	bot.add_cog(Music(bot))