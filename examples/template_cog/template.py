import asyncio

from discord.ext import commands
from piccolo.engine.postgres import PostgresEngine

from red_postgres import register_cog

from .db.tables import MyTable
from .views.api_modal import SetConnectionView


class Template(commands.Cog):
    """
    This cog is a template for using Piccolo/Postgresql with Red
    """

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.db: PostgresEngine = None

    async def cog_load(self):
        asyncio.create_task(self.initialize())

    async def initialize(self):
        await self.bot.wait_until_red_ready()
        if self.db:
            self.db.pool.terminate()
        config = await self.bot.get_shared_api_tokens("postgres")
        self.db = await register_cog(self, config, [MyTable])

    async def cog_unload(self):
        if self.db:
            await self.db.pool.terminate()

    @commands.command(name="configure")
    async def configure_connection_info(self, ctx: commands.Context):
        """Configure your postgres connection"""
        current = await self.bot.get_shared_api_tokens("postgres")
        view = SetConnectionView(ctx.author, current)
        msg = await ctx.send("Click to configure your settings", view=view)
        await view.wait()
        if not view.data:
            return await msg.edit(content="No data was entered", view=None)
        await self.bot.set_shared_api_tokens("postgres", **view.data)
        await msg.edit(content="Postgres configuration has been set!", view=None)
        await self.initialize()

    @commands.command(name="version")
    async def get_db_connection_test(self, ctx: commands.Context):
        """Refresh database connection"""
        await ctx.send(f"Running postgres version {await self.db.get_version()}")

    @commands.command(name="new")
    async def new_table(self, ctx: commands.Context, name: str):
        """Create a new table entry"""
        table = MyTable(name=name)
        await table.save()
        await ctx.tick()

    @commands.command(name="delete")
    async def del_table(self, ctx: commands.Context, name: str):
        """del a new table entry"""
        deleted = (
            await MyTable.delete()
            .where(MyTable.name == name)
            .returning(*MyTable.all_columns())
        )
        if deleted:
            await ctx.tick()
        else:
            await ctx.send("No table")

    @commands.command(name="tables")
    async def view_table(self, ctx: commands.Context):
        """Create a new table entry"""
        tables = await MyTable.objects()
        for table in tables:
            await ctx.send(table.name)
