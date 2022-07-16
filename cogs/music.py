from datetime import datetime
import discord, wavelink
from pytz import timezone
from discord.ext import commands, bridge

from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID, LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD

class Music(commands.Cog):

	def __init__(self, bot : bridge.Bot):
		self.bot = bot
		bot.loop.create_task(self.node_connect())

	@commands.Cog.listener()
	async def on_wavelink_node_ready(self, node : wavelink.Node):
		print(f"Node {node.identifier} is ready to use!")

	async def node_connect(self):
		await self.bot.wait_until_ready()
		await wavelink.NodePool.create_node(bot = self.bot, host = LAVALINK_HOST, port = LAVALINK_PORT, password = LAVALINK_PASSWORD, https = True)

	@bridge.bridge_command(description = "Play a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def play(self, ctx : bridge.BridgeContext, *, search : wavelink.YouTubeTrack):
		if not ctx.voice_client:
			vc : wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player)

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")

		else:
			vc : wavelink.Player = ctx.voice_client

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

		await ctx.respond(embed = embed)

	@bridge.bridge_command(description = "Pause a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def pause(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("You are not playing anything.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")

		else:
			vc : wavelink.Player = ctx.voice_client

		await vc.pause()
		await ctx.respond("⏸ Paused.")
		
	@bridge.bridge_command(description = "Resume a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def resume(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("You are not playing anything.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")

		else:
			vc : wavelink.Player = ctx.voice_client
		
		await vc.resume()
		await ctx.respond("▶ Resumed.")

	@bridge.bridge_command(description = "Stop a track.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def stop(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("You are not playing anything.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")

		else:
			vc : wavelink.Player = ctx.voice_client

		await vc.stop()
		await ctx.respond("⏹ Stopped.")

	@bridge.bridge_command(description = "Disconnect from voice.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def disconnect(self, ctx : bridge.BridgeContext):
		if not ctx.voice_client:
			return await ctx.respond("You are not playing anything.")

		elif not getattr(ctx.author.voice, "channel", None):
			return await ctx.respond("You are not in a voice channel.")

		else:
			vc : wavelink.Player = ctx.voice_client

		await vc.disconnect()
		await ctx.respond("❌ Disconnected.")

def setup(bot):
	bot.add_cog(Music(bot))