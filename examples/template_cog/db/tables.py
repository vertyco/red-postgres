from discord.ext.commands.core import check
from piccolo.columns import Serial, Text
from piccolo.table import Table
from redbot.core import commands


def ensure_db_connection():
    def predicate(ctx: commands.Context) -> bool:
        if not ctx.cog.db:
            if ctx.author.id not in ctx.bot.owner_ids:
                txt = "Database connection is not active, try again later"
            else:
                txt = f"Database connection is not active, configure with `{ctx.clean_prefix}clickerset postgres`"
            raise commands.UserFeedbackCheckFailure(txt)
        return True

    return check(predicate)


class MyTable(Table):
    id = Serial
    name = Text(default="Example", help_text="This would show up in piccolo admin")
    value = Text()
