from redbot.core import commands, Config, checks
from redbot.core.bot import Red
import discord
import lavalink

import re
from random import randrange

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException

class Spotify(commands.Cog):
    """Commands to play spotify urls."""
    
    NULL_CFG_VAL = "NULL"
    
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}

        #Config stuff
        self.config_valid = False
        self.config = Config.get_conf(self, identifier=7157861795, force_registration=True)
        default_global = {
            "client_id": Spotify.NULL_CFG_VAL,
            "client_secret": Spotify.NULL_CFG_VAL
        }
        self.config.register_global(**default_global)
        
        self.uriParser = re.compile(r"spotify(?:\.com)?[:/](?:user[:/](?P<user>\w+)[:/])?(?P<uriType>album|artist|playlist|track)[:/](?P<id>[0-9a-zA-Z]+)")
    
    async def initialize(self):
        self.sp = await self._init_config() #load the config and init spotipy

        #lavalink stuff
        #get the lavalink config from the audio cog
        audio_cog = self.bot.get_cog("Audio")

        host = await audio_cog.config.host()
        password = await audio_cog.config.password()
        rest_port = await audio_cog.config.rest_port()
        ws_port = await audio_cog.config.ws_port()

        await lavalink.initialize(
            bot=self.bot,
            host=host,
            password=password,
            rest_port=rest_port,
            ws_port=ws_port,
            timeout=60,
        )
        lavalink.register_event_listener(self._event_handler)

    async def _event_handler(self, player, event_type, extra):
        if event_type == lavalink.LavalinkEvents.TRACK_START and len(self.queues[player.channel.guild]):
            await self._play_track(player.channel.guild)

        if event_type == lavalink.LavalinkEvents.QUEUE_END:
            del self.queues[player.channel.guild] #clear the spotify queue as well
        
    @commands.command()
    @commands.guild_only()
    async def spotify(self, ctx, *, query):
        """Play a Spotify url/uri using YouTube."""
        if not await self._checkconfig(ctx): return False
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
            top_tracks = self.sp.artist_top_tracks(artist["id"], "GB") #need to implement country selection
            tracks = top_tracks["tracks"]
            await ctx.send("Playing " + artist["name"] + "'s top tracks")
        elif uriType == "playlist": #Needs changing to the new user-less playlist api once spotipy supports it
            tracks = []
            offset = 0
            while True:
                playlist_tracks = self.sp.user_playlist_tracks(namedGroups["user"], namedGroups["id"], limit=100, offset=offset)
                for item in playlist_tracks["items"]: #extract all the tracks from the playlist
                    tracks.append(item["track"])
                offset += 100
                if offset >= playlist_tracks["total"]:
                    break
        elif uriType == "track":
            tracks = []
            tracks.append(self.sp.track(query))
        else:
            await ctx.send("Error determining Spotify URL or URI type.")
            return
        queue = []
        for track in tracks:
            artists = ""
            for artist in track["artists"]:
                artists += artist["name"] + " "
            queue.append({"ctx": ctx, "track": artists + track["name"]})

        self.queues[ctx.guild] = queue
        await self._play_track(ctx.guild) #needs changing to only play if bot is not playing in this server already

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
        self.sp = await self._init_config() #reload the config and init spotipy
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
                " it is recommended to reset it right now. Go to the following link, "
                "select the app this bot uses, select `Show Client Secret` and `Reset`."
                "\n\nhttps://developer.spotify.com/dashboard/applications"
            )
            return
        
        await self.config.client_secret.set(secret)
        self.sp = await self._init_config() #reload the config and init spotipy
        await ctx.send("Spotify Client Secret set.")
        
    async def _init_config(self):
        client_id = await self.config.client_id()
        client_secret = await self.config.client_secret()
        #Check config is valid
        if client_id != Spotify.NULL_CFG_VAL or client_secret != Spotify.NULL_CFG_VAL:
            try:
                client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
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
        
    async def _checkconfig(self, ctx, *args, **kwargs):
        if self.config_valid == False:
            await ctx.send(
                ("Spotify config is not valid, please set the Client ID and Client Secret using the "
                    "{prefix}spotifyset clientid and {prefix}spotifyset clientsecret commands"
                ).format(prefix=ctx.prefix)
            )
            return False
        else: 
            return True
    
    async def _play_track(self, guild_id):
        audio_cog = self.bot.get_cog("Audio")
        shuffle = await audio_cog.config.guild(guild_id).shuffle()
        if shuffle:
            track_dict = self.queues[guild_id].pop(randrange(len(self.queues[guild_id])))
        else:
            track_dict = self.queues[guild_id].pop(0)
        await track_dict["ctx"].invoke(audio_cog.play, query=track_dict["track"])
