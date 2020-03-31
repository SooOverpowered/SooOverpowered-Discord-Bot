# Imports
import discord
import time
from parameters import *
from helper import *
from discord.ext import commands


class Administration(commands.Cog, name='Administration'):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command(
        name='ping',
        description='Check the latency',
        usage=f'{prefix}ping'
    )
    async def ping(self, ctx):
        time = round(self.client.latency * 1000)
        await ctx.send(embed=create_embed(f'The ping is {time} ms!'))

    @commands.command(
        name='clear',
        description='Delete messages (default = 5)',
        aliases=['purge', ],
        usage=f'{prefix}clear [number of messages]'
    )
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount+1)

    @commands.command(
        name='kick',
        description='Kick someone from the server',
        usage=f'{prefix}kick [@member]'
    )
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.send(
            embed=create_embed(
                'Please reply with "Y" to confirm action\nThe command will be automatically cancelled after 20 second'
            )
        )
        counter = 20
        while counter > 0:
            time.sleep(1)
            async for message in ctx.channel.history(after=ctx.message.created_at):
                if message.author == ctx.author and message.content == 'Y':
                    counter = 0
                    if reason == None:
                        await ctx.send(
                            embed=create_embed(
                                f'**{member}** was kicked from **{member.guild}** for no reason'
                            )
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                f'**{member}** was kicked from **{member.guild}** for **{reason}**'
                            )
                        )
                    await member.kick(reason=reason)
                    print('{0.name} was kicked from {0.guild}'.format(member))
                    break
                else:
                    counter -= 1
                    if counter == 0:
                        await ctx.send(
                            embed=create_embed(
                                'The command got cancelled because the timer ran out'
                            )
                        )

    @commands.command(
        name='ban',
        description='Ban someone from the server',
        usage=f'{prefix}ban [@member]'
    )
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await ctx.send(
            embed=create_embed(
                'Please reply with "Y" to confirm action\nThe command will be automatically cancelled after 20 second'
            )
        )
        counter = 20
        while counter > 0:
            time.sleep(1)
            async for message in ctx.channel.history(after=ctx.message.created_at):
                if message.author == ctx.author and message.content == 'Y':
                    counter = 0
                    if reason == None:
                        await ctx.send(
                            embed=create_embed(
                                f'**{member}** was banned from **{member.guild}** for no reason'
                            )
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                f'**{member}** was banned from **{member.guild}** for **{reason}**'
                            )
                        )
                    await member.ban(reason=reason)
                    print('{0.name} was banned from {0.guild}'.format(member))
                    break
                else:
                    counter -= 1
                    if counter == 0:
                        await ctx.send(
                            embed=create_embed(
                                'The command got cancelled because the timer ran out'
                            )
                        )

    @commands.command(
        name='nuke',
        description='Send a nuclear missile head that destroys all messages in a text channel',
        usage=f'{prefix}nuke'
    )
    async def nuke(self, ctx):
        if ctx.guild.system_channel == ctx.channel:
            await ctx.send(
                embed=create_embed(
                    "You can't nuke the system channel\nPlease use the clear command instead"
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Please reply with "Y" to confirm action\nThe command will be automatically cancelled after 20 second'
                )
            )
            counter = 20
            while counter > 0:
                time.sleep(1)
                async for message in ctx.channel.history(after=ctx.message.created_at):
                    if message.author == ctx.author and message.content == 'Y':
                        counter = 0
                        await ctx.send(
                            embed=create_embed(
                                "Initializing nuke process!"
                            )
                        )
                        time.sleep(1)
                        for i in range(5, 0, -1):
                            await ctx.send(
                                embed=create_embed(
                                    f'Incoming nuke in {i}'
                                )
                            )
                            time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                '**A GIANT NUKE APPEARED**'
                            )
                        )
                        time.sleep(1)
                        await ctx.channel.clone()
                        await ctx.channel.delete()
                        print(f'{ctx.channel} of {ctx.guild} just got nuked')
                        break
                    else:
                        counter -= 1
                        if counter == 0:
                            await ctx.send(
                                embed=create_embed(
                                    'The nuke got cancelled because the timer ran out'
                                )
                            )

    # Events
    @commands.Cog.listener()
    async def on_connect(self):
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='everything blows up'
            ),
            status=discord.Status.online
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot logged in as {0.user}'.format(self.client))

    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.client.change_presence(
            status=discord.Status.offline
        )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print("{0} has joined the server .".format(member))
        await member.guild.system_channel.send(
            embed=create_embed(
                f"**{member}** has joined the server."
            )
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f"{member} has left the server.")
        await member.guild.system_channel.send(
            embed=create_embed(
                f"**{member}** has left the server, RIP"
            )
        )


# Add cog
def setup(client):
    client.add_cog(Administration(client))
