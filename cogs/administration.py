import discord
import time

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
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        print('{0.name} was banned from {0.guild}'.format(member))

    @commands.command()
    async def nuke(self, ctx):
        await ctx.send(
            embed=discord.Embed(
                description="Initializing nuke process!",
                color=discord.Color.orange()
            )
        )
        time.sleep(1)
        for i in range(5, 0, -1):
            await ctx.send(
                embed=discord.Embed(
                    description=f'Incoming nuke in {i}',
                    color=discord.Color.orange()
                )
            )
            time.sleep(1)
        await ctx.send(
            embed=discord.Embed(
                description='A GIANT NUKE APPEARED',
                color=discord.Color.orange()
            )
        )
        time.sleep(1)
        await ctx.channel.clone()
        await ctx.channel.delete()


def setup(client):
    client.add_cog(Administration(client))
