import aiosqlite

#########################################################################
#                                                                       #
#                               MOD LOG                                 #
#                                                                       #
#########################################################################

async def get_modlog_channel(guild_id: int):
    """Get modlog channel for the given guild."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT channel_id FROM modlog WHERE guild_id = ?", (guild_id,))
            return await cursor.fetchone()

#########################################################################
#                                                                       #
#                               WELCOME                                 #
#                                                                       #
#########################################################################

async def get_welcome_channel(guild_id: int):
    """Get welcome channel for the given guild."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT channel_id FROM welcome WHERE guild_id = ?", (guild_id,))
            return await cursor.fetchone()

async def get_welcome_message(guild_id: int):
    """Get welcome message for the given guild."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT message FROM welcome WHERE guild_id = ?", (guild_id,))
            return await cursor.fetchone()

async def get_welcome_role(id: int):
    """Get welcome role for the given guild."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT role_id FROM welcome WHERE guild_id = ?", (id,))
            return await cursor.fetchone()

#########################################################################
#                                                                       #
#                               ISSUES                                  #
#                                                                       #
#########################################################################

async def get_issue(issue_id: str):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
            return await cursor.fetchone()