import aiosqlite

async def create_tables():
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("CREATE TABLE IF NOT EXISTS guilds (id INTEGER PRIMARY KEY, name TEXT, modlog_channel_id INTEGER)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, author_id INTEGER, content TEXT, ts INTEGER)")
		await db.commit()