import discord, os, subprocess, asyncio, sys, json

from discord.ext import commands, bridge
from utils.config import DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID

# Server Buttons View

class ServerButtons(discord.ui.View):

	# Server Buttons Constructor

	def __init__(self, server):
		super().__init__(timeout = None)
		self.server = server

	# Start Server Function

	async def start_server(self, server, channel):
		await channel.send(f'Starting server `{server}`. Please wait')

	# Start Server Button

	@discord.ui.button(label = "Start Server", style = discord.ButtonStyle.success, custom_id = "start_server")
	async def start_callback(self, button : discord.ui.Button, interaction : discord.Interaction):
		await interaction.response.send_message(f"Sended start instruction to {self.server}")
		await self.start_server(server = self.server, channel = interaction.channel)

	# Stop Server Button

	@discord.ui.button(label = "Stop Server", style = discord.ButtonStyle.red, custom_id = "stop_server")
	async def stop_callback(self, button : discord.ui.Button, interaction : discord.Interaction):
		await interaction.response.send_message("Stopping server...")
		await self.stop_server()

	# Restart Server Button

	@discord.ui.button(label = "Restart Server", style = discord.ButtonStyle.gray, custom_id = "restart_server")
	async def restart_callback(self, button : discord.ui.Button, interaction : discord.Interaction):
		await interaction.response.send_message("Restarting server...")
		await self.restart_server()

# Server Control Cog

class ServerControl(commands.Cog):

	# Server Control Constructor

	def __init__(self, bot : bridge.Bot):
		self.bot = bot
		self.blocked_characters = ["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=", "|", "\\", "{", "}", "[", "]", ":", ";", "\"", "'", ",", "<", ".", ">", "/", "?", " "]

	# Setup Command

	@bridge.bridge_command(description = "Setup", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
	async def setup(self, ctx : bridge.BridgeContext):
		with open("users.json", "r") as f:
			users = json.load(f)
			await ctx.send("Please enter a username to associate with your discord account:")
			def user_check(m):
				return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
			try:
				msg = await self.bot.wait_for("message", check = user_check, timeout = 30)

				if msg.content.startswith(PREFIX):
					return await ctx.respond(f"You can't use {PREFIX} as a username!")

				if ctx.author.name in users:
					return await ctx.respond(f"You already have a username associated with your discord account!")

				if msg.content == "":
					return await ctx.respond("You must enter a username!")

				if any(char in msg.content for char in self.blocked_characters):
					return await ctx.respond("You can't use special characters in your username!")

				users[ctx.author.name] = {
					"username" : msg.content
				}

				with open("users.json", "w") as f:
					json.dump(users, f, indent = 4)

				username = msg.content

				await ctx.respond(f"Your username has been set to {username}")
				await asyncio.sleep(5)

			except asyncio.TimeoutError:
				return await ctx.respond("Timed out. Please enter a username in at least 30 seconds.")

			await ctx.send("Please enter a server name to associate with your discord account:")
			def server_check(m):
				return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
			try:
				msg = await self.bot.wait_for("message", check = server_check, timeout = 30)

				if msg.content.startswith(PREFIX):
					return await ctx.respond(f"You can't use {PREFIX} as a server name!")

				if msg.content == "":
					return await ctx.respond("You must enter a server name!")

				if any(char in msg.content for char in self.blocked_characters):
					return await ctx.respond("You can't use special characters in your server name!")

				users[ctx.author.name]["server"] = msg.content

				with open("users.json", "w") as f:
					json.dump(users, f, indent = 4)

				server_name = msg.content

				await ctx.respond(f"Your server name has been set to {server_name}")
				await asyncio.sleep(5)

				channel_name =  f"{users[ctx.author.name]['username']}-server"

				await ctx.send("Creating your server's panel channel...")
				await asyncio.sleep(5)

				channel : discord.TextChannel = await ctx.guild.create_text_channel(channel_name)
				await ctx.send(f"Panel {channel.mention} has been created!")

				users[ctx.author.name]["channel"] = int(channel.id)

				with open("users.json", "w") as f:
					json.dump(users, f, indent = 4)

				view = ServerButtons(server_name)

				await channel.send(embed = discord.Embed(
					title = f"{server_name} Control Panel", 
					description = f"Manage {server_name} by clicking buttons below.", 
					color = discord.Color.blue()
				), view = view)

			except asyncio.TimeoutError:
				return await ctx.respond("Timed out. Please enter a server name in at least 30 seconds.")

def setup(bot : bridge.Bot):
	bot.add_cog(ServerControl(bot))