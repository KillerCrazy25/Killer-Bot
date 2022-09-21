import aiosqlite, nextcord

async def get_guild(id : int):
    """Get guild from database."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM guilds WHERE id = ?", (id,))
            return await cursor.fetchone()

async def get_modlog_channel(id: int):
    """Get modlog channel for the given guild."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT modlog_channel_id FROM guilds WHERE id = ?", (id,))
            return await cursor.fetchone()