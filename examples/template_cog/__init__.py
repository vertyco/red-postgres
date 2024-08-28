from .template import Template


async def setup(bot):
    await bot.add_cog(Template(bot))
