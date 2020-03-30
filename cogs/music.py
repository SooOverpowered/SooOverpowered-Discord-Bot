# Imports
import discord
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def join(self, ctx):
        voice_channel = ctx.author.voice.channel
        await voice_channel.connect()

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
    
    @commands.command()





# Add cog
def setup(client):
    client.add_cog(Music(client))
