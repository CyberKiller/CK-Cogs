import discord
from discord.ext import commands
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp
import tempfile

    """Displays a random picture of a dog."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def dog(self, ctx): 
        """Loads a random dog picture from www.randomdoggiegenerator.com"""
        
        url = "http://www.randomdoggiegenerator.com/randomdoggie.php"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                binary = await response.read()
        with open(tempfile.gettempdir() + "/dog.jpeg", 'wb+', buffering = False) as tmp:
            tmp.write(binary)
            tmp.flush()
            await self.bot.send_file(ctx.message.channel, tempfile.gettempdir() + "/dog.jpeg")
            tmp.close()


def setup(bot):
	if soupAvailable:
	else:
		raise RuntimeError("You need to run 'pip3 install beautifulsoup4'")
