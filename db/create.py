import aiosqlite

async def create_tables():
	"""Create bot tables."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("CREATE TABLE IF NOT EXISTS issues (guild_id INTEGER, user_id INTEGER, priority TEXT, status TEXT, description TEXT, issue_id TEXT)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS modlog (guild_id INTEGER, channel_id INTEGER)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS welcome (guild_id INTEGER, channel_id INTEGER, message TEXT, role_id INTEGER)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS gymprofiles (guild_id INTEGER, user_id INTEGER, registered_name TEXT, weight INTEGER, height INTEGER, profile_id TEXT)")
			await cursor.execute("CREATE TABLE IF NOT EXISTS gymroutines (guild_id INTEGER, user_id INTEGER, name TEXT, description TEXT, muscle_group TEXT, workout_day TEXT, routine_id TEXT)")
		await db.commit()

async def create_guild(guild_id: int):
	"""Add guild to database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("INSERT INTO modlog VALUES (?, ?)", (guild_id, None,))
			await cursor.execute("INSERT INTO welcome VALUES (?, ?, ?, ?)", (guild_id, None, None, None,))
		await db.commit()

async def create_issue(guild_id: int, user_id: int, priority: str, status: str, description: str, issue_id: str):
	"""Add issue to database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("INSERT INTO issues VALUES (?, ?, ?, ?, ?, ?)", (guild_id, user_id, priority, status, description, issue_id,))
		await db.commit()

async def create_gym_profile(guild_id: int, user_id: int, registered_name: str, weight: int, height: int, profile_id: str):
	"""Adds a gym profile to database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("INSERT INTO gymprofiles VALUES (?, ?, ?, ?, ?, ?)", (guild_id, user_id, registered_name, weight, height, profile_id,))
		await db.commit()

async def create_gym_routine(guild_id: int, user_id: int, name: str, description: str, muscle_group: str, workout_day: str, routine_id: str):
	"""Adds a gym routine to database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("INSERT INTO gymroutines VALUES (?, ?, ?, ?, ?, ?, ?)", (guild_id, user_id, name, description, muscle_group, workout_day, routine_id,))
		await db.commit()