import discord
from discord.ext import commands, bridge

import os
from dotenv import load_dotenv

import json

with open("./config.json") as file:
	config = json.load(file)

MAIN_GUILD_ID = config["guild_ids"]["main_guild_id"]
TESTING_GUILD_ID = config["guild_ids"]["testing_guild_id"]

load_dotenv()

intents = discord.Intents.all()

bot = bridge.Bot(command_prefix = commands.when_mentioned_or("k!"), intents = intents)

@bot.event
async def on_ready():
	print(f"Bot is ready as {bot.user}")

for filename in os.listdir("./cogs"):
	if filename.endswith(".py"):
		bot.load_extension(f"cogs.{filename[:-3]}")
		print(f"{filename} has been enabled.")

@bot.bridge_command(description = "Manage Bot Extensions (ADMIN ONLY).", guild_ids = [944815705944109087])
@commands.has_permissions(administrator = True)
async def extension(ctx, extension, option):
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
			bot.unload_extension(f"cogs.{extension}")
			await ctx.send(f"La extensión `{extension}` ha sido reiniciada.")
			print(f"{extension} has been reloaded.")
		else:
			await ctx.send("La opción introducida no es válida.")
	else:
		await ctx.send("La extensión introducida no es válida o no existe.")

# Help Command

@bot.bridge_command(description = "Help Command.", guild_ids = [918985655449681930])
async def help(ctx):
	embed = discord.Embed(title = "Killer Hosting Discord Bot", color = discord.Color.blue())

	for command in bot.walk_commands():
		description = command.description
		if not description or description is None or description == "":
			description = "No existe descripción para este comando."
		embed.add_field(name = f"!{command.name}", value = description)
			
	await ctx.respond(embed = embed)

bot.run(os.getenv("TOKEN"))