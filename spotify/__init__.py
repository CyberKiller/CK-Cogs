from .spotify import Spotify
from redbot.core import commands

async def setup(bot: commands.Bot):
    cog = Spotify()
    await cog.initialize()
    bot.add_cog(cog)

