import discord
import youtube_dl
from discord.ext import commands

players = {}


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command
    async def play(self, ctx, url):
        server = ctx.message.server
        channel = ctx.message.author.voice.voice_channel
        client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
        player = await voice_client.create_ytdl_player(url)
        players[server.id] = player
        player.start()


def setup(client):
    client.add_cog(Music(client))
