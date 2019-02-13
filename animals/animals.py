import discord
from redbot.core import commands
from io import BytesIO
import aiohttp
import imghdr
import random

class Animals(commands.Cog):
    """Commands to display random pictures of animals."""

    @commands.command()
    async def cat(self, ctx):
        """Get a random cat picture from random.cat"""
        msg = await ctx.send("`Searching for a cat...`")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://aws.random.cat/meow") as response:
                result = await response.json()
                await msg.edit(content=result['file'])
                
    @commands.command()
    async def dog(self, ctx):
        """Get a random dog picture from random.dog"""
        msg = await ctx.send("`Searching for a dog...`")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://random.dog/woof.json") as response:
                result = await response.json()
                await msg.edit(content=result['url'])

    @commands.command()
    async def dog2(self, ctx):
        """Get a random dog picture from www.randomdoggiegenerator.com"""
        msg = await ctx.send("`Searching for a dog...`")
        await self._get_and_upload_dynamic_jpg(ctx, "http://www.randomdoggiegenerator.com/randomdoggie.php")
        await msg.delete()

    @commands.command()
    async def kitten(self, ctx):
        """Get a random kitten picture from www.randomkittengenerator.com"""
        msg = await ctx.send("`Searching for a kitten...`")
        await self._get_and_upload_dynamic_jpg(ctx, "http://www.randomkittengenerator.com/cats/rotator.php")
        await msg.delete()
        
    @commands.command()
    async def puppy(self, ctx):
        """Get a random puppy gif from https://openpuppies.com"""
        msg = await ctx.send("`Searching for a puppy...`")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://openpuppies.com/puppies.json") as response:
                result = await response.json()
                await msg.edit(content="https://openpuppies.com/mp4/" + random.choice(result) + ".mp4")
        
    async def _get_and_upload_dynamic_jpg(self, ctx, url):
        """Gets a jpeg from a dynamic link such as a php link then uploads it to the channel.
        This is a work-around for the discord client caching the link's dynamic content."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status() #raise exception if status code >= 400
                with BytesIO(await response.read()) as tmpStrm:
                    file_ext = imghdr.what(tmpStrm) #determine the image file extention
                    if file_ext == None: #data is not an image file!
                        raise RuntimeError("Got file data that was not an image.")
                    await ctx.send(file=discord.File(tmpStrm, "image." + file_ext))
