import aiosqlite

#########################################################################
#                                                                       #
#                               GENERAL                                 #
#                                                                       #
#########################################################################

async def add_guild(guild_id: int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO modlog VALUES (?, ?)", (guild_id, None,))
            await cursor.execute("INSERT INTO welcome VALUES (?, ?, ?, ?)", (guild_id, None, None, None,))
        await db.commit()

#########################################################################
#                                                                       #
#                               MOD LOG                                 #
#                                                                       #
#########################################################################

async def update_modlog_channel(guild_id: int, channel_id: int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE modlog SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id,))
        await db.commit()

#########################################################################
#                                                                       #
#                               WELCOME                                 #
#                                                                       #
#########################################################################

async def update_welcome_channel(guild_id: int, channel_id: int):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE welcome SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id,))
        await db.commit()

async def update_welcome_message(guild_id: int, message: str):
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE welcome SET message = ? WHERE guild_id = ?", (message, guild_id,))
        await db.commit()

async def update_welcome_role(guild_id: int, role_id: int):
    """Update welcome role."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE welcome SET role_id = ? WHERE guild_id = ?", (role_id, guild_id,))
        await db.commit()

#########################################################################
#                                                                       #
#                               ISSUES                                  #
#                                                                       #
#########################################################################

async def add_issue(guild_id: int, user_id: int, priority: str, status: str, description: str, issue_id: str):
    """Add issue to database."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("INSERT INTO issues VALUES (?, ?, ?, ?, ?, ?)", (guild_id, user_id, priority, status, description, issue_id,))
        await db.commit()

async def update_issue(issue_id: str, status: str):
    """Update issue status."""
    async with aiosqlite.connect("main.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("UPDATE issues SET status = ? WHERE issue_id = ?", (status, issue_id,))
        await db.commit()