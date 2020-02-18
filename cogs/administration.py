import discord
from discord.ext import commands

class Administration(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.command()
    async def test(self,ctx):
        await ctx.send('test')

def setup(client):
    client.add_cog(Administration(client))