from redbot.core.bot import Red

from .template import Template


async def setup(bot: Red):
    await bot.add_cog(Template(bot))
