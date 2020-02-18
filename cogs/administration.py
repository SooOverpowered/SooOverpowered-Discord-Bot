import discord
from discord.ext import commands


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        time = round(client.latency * 1000)
        await ctx.send('The ping is {0} ms!'.format(time))

    @commands.command()
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount+1)

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        print('{0.name} was kicked from {0.guild}'.format(member))

    @commands.command()
    async def ban(ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        print('{0.name} was banned from {0.guild}'.format(member))


def setup(client):
    client.add_cog(Administration(client))
