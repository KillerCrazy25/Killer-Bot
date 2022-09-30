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