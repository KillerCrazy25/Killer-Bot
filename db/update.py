import aiosqlite

async def add_message(id : int, author_id : int, content : str, ts : int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (id, author_id, content, ts,))
        await db.commit()

async def add_guild(id : int, name : str, modlog_channel_id: int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO guilds VALUES (?, ?, ?)", (id, name, modlog_channel_id,))
        await db.commit()

async def add_modlog_channel(guild_id: int, channel_id: int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE guilds SET modlog_channel_id = ? WHERE id = ?", (channel_id, guild_id,))
        await db.commit()