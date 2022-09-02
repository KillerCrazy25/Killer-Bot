import aiosqlite

async def get_guild(id : int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM guilds WHERE id = ?", (id,))
            return await cursor.fetchone()