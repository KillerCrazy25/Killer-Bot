import aiosqlite

async def update_modlog_channel(guild_id: int, channel_id: int):
	"""Update ModLog channel in the database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE modlog SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id,))
		await db.commit()

async def update_welcome_channel(guild_id: int, channel_id: int):
	"""Update welcome channel in the database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE welcome SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id,))
		await db.commit()

async def update_welcome_message(guild_id: int, message: str):
	"""Update welcome message in the database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE welcome SET message = ? WHERE guild_id = ?", (message, guild_id,))
		await db.commit()

async def update_welcome_role(guild_id: int, role_id: int):
	"""Update welcome role in the database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE welcome SET role_id = ? WHERE guild_id = ?", (role_id, guild_id,))
		await db.commit()

async def update_issue(issue_id: str, status: str):
	"""Update issue status in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE issues SET status = ? WHERE issue_id = ?", (status, issue_id,))
		await db.commit()

async def update_gym_profile_name(profile_id: str, name: str):
	"""Update gym profile name in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymprofiles SET name = ? WHERE profile_id = ?", (name, profile_id,))
		await db.commit()

async def update_gym_profile_weight(profile_id: str, weight: int):
	"""Update gym profile weight in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymprofiles SET weight = ? WHERE profile_id = ?", (weight, profile_id,))
		await db.commit()

async def update_gym_profile_height(profile_id: str, height: str):
	"""Update gym profile height in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymprofiles SET height = ? WHERE profile_id = ?", (height, profile_id,))
		await db.commit()
#guild_id: int, user_id: int, name: str, description: str, muscle_group: str, workout_day: str, routine_id: int
async def update_gym_routine_name(routine_id: str, name: str):
	"""Update gym routine name in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymroutines SET name = ? WHERE routine_id = ?", (name, routine_id,))
		await db.commit()

async def update_gym_routine_description(routine_id: str, description: str):
	"""Update gym routine description in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymroutines SET description = ? WHERE routine_id = ?", (description, routine_id,))
		await db.commit()

async def update_gym_routine_muscle_group(routine_id: str, muscle_group: str):
	"""Update gym routine muscle group in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymroutines SET muscle_group = ? WHERE routine_id = ?", (muscle_group, routine_id,))
		await db.commit()

async def update_gym_routine_workout_day(routine_id: str, workout_day: str):
	"""Update gym routine workout day in the database.."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("UPDATE gymroutines SET workout_day = ? WHERE routine_id = ?", (workout_day, routine_id,))
		await db.commit()