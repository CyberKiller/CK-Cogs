# CK-Cogs
A collection of cogs for Red Discord Bot V3 made by me.
There isnt much here yet, but there will be eventually.

## Animals
Gets random cat and dog pictures.

## Spotify
**Note: This cog is a currently a little unfinished and buggy, I will be looking into an alternative way by implementing spotify integration into Lavalink/lavaplayer instead.**<br>
Queries a spotify url for the song names, then passes the song names to the [p]play command.<br>
**Disclaimer: This cog does _not_ download or play any audio from spotify because that would be illegal! It only searches for the song on youtube.**<br>
A known side effect of the way the cog queues songs, is that songs queued through the audio cog, take priority over songs queued through this cog. I had to do it this way, because lavalink searches the song on Youtube as soon as it is queued, which can cause flood Youtube with search queries if a massive Spotify playlist is queued into the audio cog all at once.
