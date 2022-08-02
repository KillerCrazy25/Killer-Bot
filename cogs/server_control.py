import nextcord, asyncio, json

from nextcord.ext import commands
from utils.config import DEVELOPER_ID, MAIN_GUILD_ID, PREFIX, TESTING_GUILD_ID

# Server Buttons View

class ServerButtons(nextcord.ui.View):

	# Server Buttons Constructor

	def __init__(self, server):
		super().__init__(timeout = None)
		self.server = server

	# Start Server Function

	async def start_server(self, server, channel):
		await channel.send(f'Starting server `{server}`. Please wait')

	# Start Server Button

	@nextcord.ui.button(label = "Start Server", style = nextcord.ButtonStyle.success, custom_id = "start_server")
	async def start_callback(self, button : nextcord.ui.Button, interaction : nextcord.Interaction):
		await interaction.response.send_message(f"Sended start instruction to {self.server}")
		await self.start_server(server = self.server, channel = interaction.channel)

	# Stop Server Button

	@nextcord.ui.button(label = "Stop Server", style = nextcord.ButtonStyle.red, custom_id = "stop_server")
	async def stop_callback(self, button : nextcord.ui.Button, interaction : nextcord.Interaction):
		await interaction.response.send_message("Stopping server...")
		await self.stop_server()

	# Restart Server Button

	@nextcord.ui.button(label = "Restart Server", style = nextcord.ButtonStyle.gray, custom_id = "restart_server")
	async def restart_callback(self, button : nextcord.ui.Button, interaction : nextcord.Interaction):
		await interaction.response.send_message("Restarting server...")
		await self.restart_server()

# Server Control Cog

class ServerControl(commands.Cog):

	# Server Control Constructor

	def __init__(self, bot : commands.Bot):
		self.bot = bot
		self.blocked_characters = ["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=", "|", "\\", "{", "}", "[", "]", ":", ";", "\"", "'", ",", "<", ".", ">", "/", "?", " "]

	# Setup Command

	@commands.command(description = "Setup")
	async def setup(self, ctx : commands.Context):
		with open("users.json", "r") as f:
			users = json.load(f)
			await ctx.send("Please enter a username to associate with your nextcord account:")
			def user_check(m):
				return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
			try:
				msg = await self.bot.wait_for("message", check = user_check, timeout = 30)

				if msg.content.startswith(PREFIX):
					return await ctx.send(f"You can't use {PREFIX} as a username!")

				if ctx.author.name in users:
					return await ctx.send(f"You already have a username associated with your nextcord account!")

				if msg.content == "":
					return await ctx.send("You must enter a username!")

				if any(char in msg.content for char in self.blocked_characters):
					return await ctx.send("You can't use special characters in your username!")

				users[ctx.author.name] = {
					"username" : msg.content
				}

				with open("users.json", "w") as f:
					json.dump(users, f, indent = 4)

				username = msg.content

				await ctx.send(f"Your username has been set to {username}")
				await asyncio.sleep(5)

			except asyncio.TimeoutError:
				return await ctx.send("Timed out. Please enter a username in at least 30 seconds.")

			await ctx.send("Please enter a server name to associate with your nextcord account:")
			def server_check(m):
				return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
			try:
				msg = await self.bot.wait_for("message", check = server_check, timeout = 30)

				if msg.content.startswith(PREFIX):
					return await ctx.send(f"You can't use {PREFIX} as a server name!")

				if msg.content == "":
					return await ctx.send("You must enter a server name!")

				if any(char in msg.content for char in self.blocked_characters):
					return await ctx.send("You can't use special characters in your server name!")

				users[ctx.author.name]["server"] = msg.content

				with open("users.json", "w") as f:
					json.dump(users, f, indent = 4)

				server_name = msg.content

				await ctx.send(f"Your server name has been set to {server_name}")
				await asyncio.sleep(5)

				channel_name =  f"{users[ctx.author.name]['username']}-server"

				await ctx.send("Creating your server's panel channel...")
				await asyncio.sleep(5)

				channel : nextcord.TextChannel = await ctx.guild.create_text_channel(channel_name)
				await ctx.send(f"Panel {channel.mention} has been created!")

				users[ctx.author.name]["channel"] = int(channel.id)

				with open("users.json", "w") as f:
					json.dump(users, f, indent = 4)

				view = ServerButtons(server_name)

				await channel.send(embed = nextcord.Embed(
					title = f"{server_name} Control Panel", 
					description = f"Manage {server_name} by clicking buttons below.", 
					color = nextcord.Color.blue()
				), view = view)

			except asyncio.TimeoutError:
				return await ctx.send("Timed out. Please enter a server name in at least 30 seconds.")

def setup(bot : commands.Bot):
	bot.add_cog(ServerControl(bot))