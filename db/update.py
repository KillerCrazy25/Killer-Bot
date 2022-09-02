import aiosqlite

async def add_message(id : int, author_id : int, content : str, ts : int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (id, author_id, content, ts))
        await db.commit()

async def add_guild(id : int, name : str, owner_id : int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO guilds VALUES (?, ?, ?)", (id, name, owner_id))
        await db.commit()