import discord
from discord.ext import commands
from io import BytesIO
import aiohttp
import imghdr

class Animals:
    """Commands to display random pictures of animals."""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cat(self):
        """Get a random cat picture from random.cat"""
        msg = await self.bot.say("`Searching for a cat...`")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://random.cat/meow") as response:
                result = await response.json()
                await self.bot.edit_message(msg, result['file'])

    @commands.command(pass_context=True)
    async def dog(self, ctx):
        """Get a random dog picture from www.randomdoggiegenerator.com"""
        msg = await self.bot.say("`Searching for a dog...`")
        await self.__getAndUploadDynamicJpeg(ctx, "http://www.randomdoggiegenerator.com/randomdoggie.php")
        await self.bot.delete_message(msg)

    @commands.command(pass_context=True)
    async def kitten(self, ctx):
        """Get a random kitten picture from www.randomkittengenerator.com"""
        msg = await self.bot.say("`Searching for a kitten...`")
        await self.__getAndUploadDynamicJpeg(ctx, "http://www.randomkittengenerator.com/cats/rotator.php")
        await self.bot.delete_message(msg)

    async def __getAndUploadDynamicJpeg(self, ctx, url):
        """Gets a jpeg from a dynamic link such as a php link then uploads it to the channel.
        This is a work-around for the discord client caching the link's dynamic content content."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status() #raise exception if status code >= 400
                with BytesIO(await response.read()) as tmpStrm:
                    fileExt = imghdr.what(tmpStrm) #determine the image file extention
                    if fileExt == None: #data is not an image file!
                        raise RuntimeError("Got file data that was not an image.")
                    await self.bot.upload(tmpStrm, filename="image." + fileExt)

def setup(bot):
    bot.add_cog(Animals(bot))