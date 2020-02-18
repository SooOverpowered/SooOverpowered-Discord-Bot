import discord
from discord.ext import commands


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def test(self, ctx):
        await ctx.send('test')

    @commands.command()
    async def ping(self, ctx):
        time = round(client.latency * 1000)
        await ctx.send('The ping is {0} ms!'.format(time))


def setup(client):
    client.add_cog(Administration(client))
