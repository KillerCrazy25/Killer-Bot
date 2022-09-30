import aiosqlite

async def delete_table(table: str):
	"""Removes a table from the database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute(f"DROP TABLE {table}")
		await db.commit()

async def remove_guild(guild_id: int):
	"""Removes a guild from database."""
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute("DELETE FROM modlog WHERE guild_id = ?", (guild_id,))
			await cursor.execute("DELETE FROM welcome WHERE guild_id = ?", (guild_id,))
		await db.commit()