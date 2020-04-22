# Imports
import discord
import time
import json
from datetime import datetime
from helper import *
from discord.ext import commands


class Administration(commands.Cog, name='Administration'):
    def __init__(self, client):
        self.client = client
        self.recently_used_command = []

    # Commands
    @commands.command(
        name='ping',
        description='Check the latency',
        usage='`.ping`'
    )
    async def ping(self, ctx):
        time = round(self.client.latency * 1000)
        await ctx.send(
            embed=create_embed(
                f'The ping is {time} ms!'
            )
        )

    @commands.command(
        name='clear',
        description='Delete messages (default = 5)',
        aliases=['purge', ],
        usage='`.clear [number of messages]`'
    )
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

    @commands.command(
        name='nuke',
        description='Send a nuclear missile head that destroys all messages in a text channel',
        usage='`.nuke`'
    )
    @commands.cooldown(1, 60, commands.BucketType.channel)
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx, arg=None):
        if ctx.guild.system_channel == ctx.channel:
            await ctx.send(
                embed=create_embed(
                    "You can't nuke the system channel\nPlease use the clear command instead"
                )
            )
        elif arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Please reply with **Y** to confirm action\nThe command will be automatically cancelled after 20 second'
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
                                '**A GIANT NUKE APPREARED**\n'+'```' +
                                open('nuclear.txt').read()+'```'
                            )
                        )
                        channel_info = [ctx.channel.category,
                                        ctx.channel.position,
                                        ]
                        time.sleep(1)
                        channel_id = ctx.channel.id
                        await ctx.channel.clone()
                        await ctx.channel.delete()
                        new_channel = channel_info[0].text_channels[-1]
                        await new_channel.edit(position=channel_info[1])
                        with open('queue.json', 'r') as f:
                            queue = json.load(f)
                        if queue[str(ctx.voice_client)][0]['text_channel'] == channel_id:
                            queue[str(ctx.voice_client)][0]['text_channel'] = new_channel.id
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
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

    @commands.command(
        name='kick',
        description='Kick someone from the server',
        usage='`.kick [@member]`'
    )
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author == member:
            await ctx.send(
                embed=create_embed(
                    'You cannot kick yourself'
                )
            )
        elif ctx.guild.owner == member:
            await ctx.send(
                embed=create_embed(
                    'You cannot kick the server owner'
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
        usage='`.ban [@member]`'
    )
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author == member:
            await ctx.send(
                embed=create_embed(
                    'You cannot ban yourself'
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
        name='userinfo',
        aliases=['info', ],
        description='Displays the user info',
        usage='`.userinfo`'
    )
    async def userinfo(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        embed = discord.Embed(
            color=discord.Color.orange(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(
            name=f'User info: {member.display_name}'
        )
        embed.add_field(
            name='Account Info',
            value=f"Currently {member.status}\nAccound created on {member.created_at.strftime('%d %b %Y %H:%M')}\nThat's {(datetime.now()-member.created_at).days} days ago!",
            inline=False
        )
        if member.premium_since == None:
            embed.add_field(
                name='Server Info',
                value=f"Joined server on {member.joined_at.strftime('%d %b %Y %H:%M')}\nThat's {(datetime.now()-member.joined_at).days} days ago!\nNot boosting the server",
                inline=False
            )
        else:
            embed.add_field(
                name='Server Info',
                value=f"Joined server on {member.joined_at.strftime('%d %b %Y %H:%M')}\nThat's {(datetime.now()-member.joined_at).days} days ago!\nBoosting the server",
                inline=False
            )
        role_str = ''
        for role in member.roles:
            role_str += str(role)+', '
        embed.add_field(
            name='Roles',
            value=role_str,
            inline=False
        )
        embed.set_footer(
            text=f'ID: {member.id}'
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='serverinfo',
        description='Displays the server info',
        aliases=['svinfo', ],
        usage='`.serverinfo`',
    )
    async def serverinfo(self, ctx):
        embed = discord.Embed(
            color=discord.Color.orange(),
            timestamp=ctx.message.created_at
        )
        embed.set_footer(
            text=f'ID: {ctx.guild.id}'
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.guild.name)
        embed.add_field(
            name='Server info',
            value=f"Created on {ctx.guild.created_at.strftime('%d %b %Y %H:%M')}\nThat's {(datetime.now()-ctx.guild.created_at).days} days ago!\nServer boost level {ctx.guild.premium_tier}\nServer region: {ctx.guild.region}\nServer owner: {ctx.guild.owner.display_name}",
            inline=False
        )
        embed.add_field(
            name='Member',
            value=f"{ctx.guild.member_count} members in the server\n{ctx.guild.premium_subscription_count} people boosted this server",
            inline=False
        )
        role_output = ''
        for role in ctx.guild.roles:
            role_output += str(role)+', '
        embed.add_field(
            name='Roles',
            value=role_output,
            inline=False
        )
        await ctx.send(
            embed=embed
        )

    @commands.command(
        name='setprefix',
        description='Set the custom prefix for the server',
        usage='`.setprefix [new prefix]`'
    )
    async def setprefix(self, ctx, new_prefix: str):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        if len(prefixes[str(ctx.guild.id)]) == 2:
            prefixes[str(ctx.guild.id)][1] = new_prefix
        else:
            prefixes[str(ctx.guild.id)].append(new_prefix)
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        await ctx.send(
            embed=create_embed(
                f'Prefix changed to {new_prefix}'
            )
        )

    # Error handler
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'You do not have the {"".join(error.missing_perms)} permission for this command'
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'Please give the bot {"".join(error.missing_perms)} permission to run this command'
                )
            )

    @nuke.error
    async def nuke_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                embed=create_embed(
                    f'You can only send **1** nuke every **60 seconds**\nTime until next available nuke: {int(error.retry_after)}s'
                )
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'You do not have the {"".join(error.missing_perms)} permission for this command'
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'Please give the bot {"".join(error.missing_perms)} permission to run this command'
                )
            )

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'You do not have the {"".join(error.missing_perms)} permission for this command'
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'Please give the bot {"".join(error.missing_perms)} permission to run this command'
                )
            )

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'You do not have the {"".join(error.missing_perms)} permission for this command'
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'Please give the bot {"".join(error.missing_perms)} permission to run this command'
                )
            )


# Add cog
def setup(client):
    client.add_cog(Administration(client))
