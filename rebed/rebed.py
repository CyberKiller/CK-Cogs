import discord
from redbot.core import commands
#import re
from urllib.parse import urlparse

class Rebed(commands.Cog):
    """Fix reddit, twitter, tiktok and instagram embeds."""

    def __init__(self, bot):
        self.bot = bot
        #self.regex_reddit = re.compile(r"https?:\/\/((?:old\.|www\.)?reddit\.com)")
        #self.regex_twitter = re.compile(r"https?:\/\/((?:|www\.)?(?:twitter|x)\.com)")
        #self.regex_instagram = re.compile(r"https?:\/\/((?:|www\.)?instagram\.com)")

    @commands.Cog.listener()
    async def on_message(self, message : discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        #new_msg = self.regex_reddit.sub("rxddit.com", message.content)
        #new_msg = self.regex_twitter.sub("fxtwitter.com", message.content)
        #new_msg = self.regex_instagram.sub("ddinstagram.com", message.content)
        urls = self.extract_urls(message.content)
        new_msg = ""
        for url in urls:
            if not url.path or url.path == "/": return

            if url.netloc in {"reddit.com", "old.reddit.com", "www.reddit.com"}:
                #TODO handle unavailabilty of packaged media               
                new_msg += self.format_url(url, url.netloc.replace("reddit", "rxddit"))
            elif url.netloc in {"twitter.com", "www.twitter.com", "x.com", "www.x.com"}:
                new_msg += self.format_url(url, "fxtwitter.com")
            #elif url.netloc in {"tiktok.com", "www.tiktok.com"}:
                #new_msg += self.format_url(url, "tnktok.com")
            elif url.netloc in {"instagram.com", "www.instagram.com"}:
                new_msg += self.format_url(url, "ddinstagram.com")
        if new_msg:
            await message.reply(new_msg, silent=True)

    def extract_urls(self, text: str):
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
            
