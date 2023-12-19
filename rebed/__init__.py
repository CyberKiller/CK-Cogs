from .rebed import Rebed

async def setup(bot):
    await bot.add_cog(Rebed(bot))
