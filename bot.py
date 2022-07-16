import discord, os
from discord.ext import commands, bridge

from utils.config import MAIN_GUILD_ID, TESTING_GUILD_ID, TOKEN

from datetime import datetime
from pytz import timezone

intents = discord.Intents.all()

bot = bridge.Bot(command_prefix = commands.when_mentioned_or("k!"), intents = intents, help_command = None)

@bot.event
async def on_ready():
	print(f"Bot is ready as {bot.user}")
	await bot.change_presence(activity = discord.Game(name = "Use k!help to see all my commands!"))

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
		print(f"{filename} has been enabled.")

@bot.bridge_command(description = "Manage Bot Extensions (ADMIN ONLY).", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
@commands.has_permissions(administrator = True)
async def extension(ctx : bridge.BridgeContext, extension : str, option : str):
	if extension:
		if option == "enable" or "on" or "true":
			bot.load_extension(f"cogs.{extension}")
			await ctx.send(f"La extensión `{extension}` ha sido activada.")
			print(f"{extension} has been enabled.")
		elif option == "disable" or "off" or "false":
			bot.unload_extension(f"cogs.{extension}")
			await ctx.send(f"La extensión `{extension}` ha sido desactivada.")
			print(f"{extension} has been disabled.")
		elif option == "reload":
			bot.reload_extension(f"cogs.{extension}")
			await ctx.send(f"La extensión `{extension}` ha sido reiniciada.")
			print(f"{extension} has been reloaded.")
		else:
			await ctx.send("La opción introducida no es válida.")
	else:
		await ctx.send("La extensión introducida no es válida o no existe.")

# Help Command

@bot.bridge_command(description = "Shows this message.", guild_ids = [MAIN_GUILD_ID, TESTING_GUILD_ID])
async def help(ctx : bridge.BridgeContext):
	embed = discord.Embed(
		color = discord.Color.nitro_pink(),
		timestamp = datetime.now(tz = timezone("US/Eastern"))	
	)

	for command in bot.walk_commands():
		description = command.description
		if not description or description is None or description == "":
			description = "No existe descripción para este comando."
		embed.add_field(name = f"!{command.name} {command.signature}", value = description, inline = False)

	embed.set_author(name = "Killer Bot | Help", icon_url = bot.user.avatar.url)	

	await ctx.respond(embed = embed)

bot.run(TOKEN)