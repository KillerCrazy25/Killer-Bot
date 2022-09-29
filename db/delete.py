import aiosqlite

async def delete_table(table: str):
	async with aiosqlite.connect("main.db") as db:
		async with db.cursor() as cursor:
			await cursor.execute(f"DROP TABLE {table}")
		await db.commit()