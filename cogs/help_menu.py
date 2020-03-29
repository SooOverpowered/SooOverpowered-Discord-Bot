# Imports
import discord
from discord.ext import commands


class HelpMenu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx, arg=None):
        embed = discord.Embed(
            color=discord.Color.orange()
        )
        embed.set_author(name='Help')
        embed.add_field(name='.ping', value='Returns Pong!', inline=False)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(HelpMenu(client))
