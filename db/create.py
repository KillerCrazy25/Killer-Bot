import aiosqlite

# TABLES: issues, infractions, modlog, welcome
# await cursor.execute("CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY, name TEXT, modlog_channel_id INTEGER, welcome_channel_id INTEGER, welcome_message TEXT, welcome_role_id INTEGER)")

async def create_tables():
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("CREATE TABLE IF NOT EXISTS issues (guild_id INTEGER, user_id INTEGER, priority TEXT, status TEXT, description TEXT, issue_id TEXT)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS modlog (guild_id INTEGER, channel_id INTEGER)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS welcome (guild_id INTEGER, channel_id INTEGER, message TEXT, role_id INTEGER)")
		await db.commit()