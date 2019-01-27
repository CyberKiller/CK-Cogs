from redbot.core import commands, Config, checks
from redbot.core.bot import Red
from redbot.cogs import audio
import discord

import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException

class Spotify(commands.Cog):
    """Commands to play spotify urls."""
    
    NULL_CFG_VAL = "NULL"
    
    def __init__(self):
    #Config stuff
        self.config_valid = False
        self.config = Config.get_conf(self, identifier=7157861795)
        default_global = {
            "client_id": Spotify.NULL_CFG_VAL,
            "client_secret": Spotify.NULL_CFG_VAL
        }
        self.config.register_global(**default_global)
        
        self.uriParser = re.compile(r"spotify(?:\.com)?[:/](?:user[:/](?P<user>\w+)[:/])?(?P<uriType>album|artist|playlist|track)[:/](?P<id>[0-9a-zA-Z]+)")
    
    async def initialize(self):
        self.sp = await self.initconfig() #load the config and init spotipy
        
    @commands.command()
    @commands.guild_only()
    async def spotify(self, ctx, *, query):
        """Play a Spotify url/uri using YouTube."""
        if not await self.checkconfig(ctx): return False
        #determine type of url/uri (track, album or playlist)
        mResult = self.uriParser.search(query)
        if mResult == None:
            await ctx.send("That doesn't appear to be a valid Spotify URL or URI.")
            return
        namedGroups = mResult.groupdict()
        uriType = namedGroups["uriType"]
        
        if uriType == "album": #Make it try to play the full album instead?
            album = self.sp.album(query)
            tracks = album["tracks"]["items"]
        elif uriType == "artist": #Play the artists top tracks.
            artist = self.sp.artist(query)
            topTracks = self.sp.artist_top_tracks(artist["id"], "GB") #need to implement country selection
            tracks = topTracks["tracks"]
            await ctx.send("Playing " + artist["name"] + "'s top tracks")
        elif uriType == "playlist": #Needs changing to the new user-less playlist api once spotipy supports it
            tracks = []
            offset = 0
            while True:
                playlistTracks = self.sp.user_playlist_tracks(namedGroups["user"], namedGroups["id"], limit=100, offset=offset)
                for item in playlistTracks["items"]: #extract all the tracks from the playlist
                    tracks.append(item["track"])
                offset += 100
                if offset >= playlistTracks["total"]:
                    break
        elif uriType == "track":
            tracks = []
            tracks.append(self.sp.track(query))
        else:
            await ctx.send("Error determining Spotify URL or URI type.")
            return
        
        cog = ctx.bot.get_cog("Audio")
        if cog == None:
            ctx.send("Error getting Audio cog, please check if Audio cog is enabled.")
        for track in tracks:
            artists = ""
            for artist in track["artists"]:
                artists += artist["name"] + " "
            await ctx.invoke(cog.play, query=artists + track["name"])
    
    @commands.group()
    async def spotifyset(self, ctx):
        """Spotify configuration options."""
        pass
    
    @checks.is_owner()
    @spotifyset.command()
    async def clientid(self, ctx: commands.Context, clientid: str):
        """Sets the Spotify Client ID ."""
        
        if not isinstance(ctx.channel, discord.DMChannel):
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
    
            await ctx.send(
                "Please use that command in DM. Since users probably saw your Client ID,"
                " you might want to consider going to the following link and"
                " creating a new Client ID."
                "\n\nhttps://developer.spotify.com/dashboard/applications"
            )
            return
        
        await self.config.client_id.set(clientid)
        self.sp = await self.initconfig() #reload the config and init spotipy
        await ctx.send("Spotify Client ID set.")
        
    @checks.is_owner()
    @spotifyset.command()
    async def clientsecret(self, ctx: commands.Context, secret: str):
        """Sets the Spotify Client ID ."""
        
        if not isinstance(ctx.channel, discord.DMChannel):
    
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
    
            await ctx.send(
                "Please use that command in DM. Since users probably saw your Client Secret,"
                " it is recommended to reset it right now. Go to the following link, select the app this bot uses,"
                " select `Show Client Secret` and `Reset`."
                "\n\nhttps://developer.spotify.com/dashboard/applications"
            )
            return
        
        await self.config.client_secret.set(secret)
        self.sp = await self.initconfig() #reload the config and init spotipy
        await ctx.send("Spotify Client Secret set.")
    
    @checks.is_owner()
    @commands.command()
    @commands.guild_only()
    async def spotifyaudiocalltest(self, ctx, *, query):
        """Test audio cog interoperability"""
        cog = ctx.bot.get_cog("Audio")
        await ctx.invoke(cog.play, query=query)
        
    async def initconfig(self):
        clientId = await self.config.client_id()
        print("clientId = ", clientId)
        clientSecret = await self.config.client_secret()
        print("clientSecret = ", clientSecret)
        #Check config is valid
        if clientId != Spotify.NULL_CFG_VAL or clientSecret != Spotify.NULL_CFG_VAL:
            try:
                client_credentials_manager = SpotifyClientCredentials(clientId, clientSecret)
                #Init spotipy
                sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            except SpotifyOauthError:
                self.config_valid = False
            else:
                self.config_valid = True
        else:
            self.config_valid = False
            return None
        return sp
        
    async def checkconfig(self, ctx, *args, **kwargs):
        if self.config_valid == False:
            await ctx.send(
                ("Spotify config is not valid, please set the Client ID and Client Secret using the "
                    "{prefix}spotifyset clientid and {prefix}spotifyset clientsecret commands"
                ).format(prefix=ctx.prefix)
            )
            return False
        else: 
            return True
