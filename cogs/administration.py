import discord
import time
from helper import *
from discord.ext import commands


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command()
    async def ping(self, ctx):
        time = round(self.client.latency * 1000)
        await ctx.send(embed=create_embed(f'The ping is {time} ms!'))

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
        if ctx.guild.system_channel == ctx.channel:
            await ctx.send(
                embed=create_embed(
                    "You can't nuke the system channel\nPlease use the clear command instead")
            )
        else:
            await ctx.send(
                embed=create_embed("Initializing nuke process!")
            )
            time.sleep(1)
            for i in range(5, 0, -1):
                await ctx.send(
                    embed=create_embed(f'Incoming nuke in {i}')
                )
                time.sleep(1)
            await ctx.send(
                embed=create_embed('**A GIANT NUKE APPEARED**')
            )
            time.sleep(1)
            await ctx.channel.clone()
            await ctx.channel.delete()
            print(f'{ctx.channel} of {ctx.guild} just got nuked')

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot logged in as {0.user}'.format(self.client))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("{0} has joined the server .".format(member))
        await member.guild.system_channel.send(
            embed=create_embed(f"**{member}** has joined the server.")
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f"{member} has left the server.")
        await member.guild.system_channel.send(
            embed=create_embed(f"**{member}** has left the server, RIP")
        )


def setup(client):
    client.add_cog(Administration(client))
