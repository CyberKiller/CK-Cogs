import discord
from redbot.core import commands
from urllib.parse import urlparse, ParseResult
import aiohttp
from bs4 import BeautifulSoup

class Rebed(commands.Cog):
    """Fix reddit, twitter, tiktok and instagram embeds."""

    def __init__(self, bot):
        self.bot = bot
        headers = {'user-agent': 'Mozilla/5.0 (compatible; Discordbot/2.0; +https://discord.com)'}
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def __del__(self):
        await self.session.close()

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return

        urls = self.extract_urls(message.content)
        new_urls = []
        for url in urls:
            if not url.path or url.path == "/": return

            if url.netloc in {"reddit.com", "old.reddit.com", "www.reddit.com"}:
                #TODO handle unavailabilty of packaged media               
                new_urls.append(self.format_url(url, url.netloc.replace("reddit", "rxddit")))
            elif url.netloc in {"twitter.com", "www.twitter.com", "x.com", "www.x.com"}:
                new_urls.append(self.format_url(url, "fxtwitter.com"))
            elif url.netloc in {"tiktok.com", "www.tiktok.com"}:
                new_urls.append(self.format_url(url, "tnktok.com"))
            elif url.netloc in {"instagram.com", "www.instagram.com"}:
                new_urls.append(self.format_url(url, "ddinstagram.com"))
        #try:
        #    embeds = await self.get_embeds(new_urls)
        #    await message.reply(embeds = embeds, silent=True)
        #except discord.Forbidden:
             #fall back to url reply mode
        new_msg = "\n"
        new_msg.join(new_urls)
        await message.edit(suppress=True)
        await message.reply(new_msg, silent=True)

    def extract_urls(self, text: str) -> list[ParseResult]:
        """Return a list of urls from a text string."""
        out = []
        for word in text.split(' '):
            url = urlparse(word.strip())
            if url.scheme:
                out.append(url)
        return out
    
    def format_url(self, url, domain_repl):
        s : str = url.scheme + "://" + domain_repl + url.path
        if url.params:
            s += ";" + url.params
        if url.query:
            s += "?" + url.query
        if url.fragment:
            s += "#" + url.fragment
        return s + "\n"
    
    """
    list of fields to parse:
    author
    colour
    description
    fields (not needed?)
    footer
    image
    provider (?????????)
    thumbnail
    timestamp (don't know if to implement)
    title
    type (not needed?)
    url
    video
    """
    #oembed not implemented yet    
    async def get_embeds(self, urls):
        embeds : list[discord.Embed] = []
        for url in urls:
            embed = discord.Embed()
            async with self.session.get(url) as resp:
                html = await resp.text()    
                soup = BeautifulSoup(html, 'html.parser')        

                title = self.get_tag_content(soup, ["twitter:title", "og:title"])
                if title: embed.title = title

                embed_url = self.get_tag_content(soup, ["og:url"])
                if embed_url: embed.url = embed_url

                author = self.get_tag_content(soup, ["twitter:site", "twitter:creator", "article:author", "book:author"])
                if author: embed.author.name = author
                if embed_url: embed.author.url = embed_url

                colour = None
                colour_str = self.get_tag_content(soup, ["theme-color"])
                if colour_str and colour_str.startswith("#"):
                    colour = int(colour_str.strip("#"), 16)            
                if colour is not None: embed.colour = colour

                description = self.get_tag_content(soup, ["twitter:description", "og:description"])
                if description: embed.description = description

                image = self.get_tag_content(soup, ["twitter:image", "og:image"])
                if image: 
                    embed.image.url = image
                    embed.thumbnail.url = image
                image_alt = self.get_tag_content(soup, ["twitter:image:alt", "og:image:alt"])
                if image_alt: 
                    embed.image.proxy_url = image_alt
                    embed.thumbnail.proxy_url = image_alt
                image_width = self.get_tag_content(soup, ["og:image:width"])
                if image_width: 
                    embed.image.width = image_width
                    embed.thumbnail.width = image_width
                image_height = self.get_tag_content(soup, ["og:image:height"])
                if image_height: 
                    embed.image.height = image_height
                    embed.thumbnail.height = image_height

                video = self.get_tag_content(soup, ["twitter:player", "og:video"])
                if video: 
                    embed.video.url = video
                video_width = self.get_tag_content(soup, ["og:video:width"])
                if video_width: 
                    embed.video.width = video_width
                video_height = self.get_tag_content(soup, ["og:video:height"])
                if video_height: 
                    embed.video.height = video_height
                
                embeds.append(embed)

            return embeds
        
    def get_tag_content(self, soup : BeautifulSoup, property : list[str]) -> str:
        tag = soup.find("meta", property=property)
        if tag:
            try:
                return tag["content"]
            except KeyError:
                return None
        else:
            return None
