from redbot.core.bot import Red

from .templatecog import TemplateCog


async def setup(bot: Red):
    await bot.add_cog(TemplateCog(bot))
