# Imports
import discord
import time
import pymongo
import os
import re
from datetime import datetime
from helper import *
from discord.ext import commands


# Connect to mongodb database
dbclient = pymongo.MongoClient(os.environ.get('dbconn'))
db = dbclient['DaedBot']
guildcol = db['prefix']
queuecol = db['queue']
playlistcol = db['playlist']
blacklist_admin = db['adminblacklist']


def blacklist_check():
    def predicate(ctx):
        author_id = ctx.author.id
        if blacklist_admin.find_one({'user_id': author_id}):
            return False
        return True
    return commands.check(predicate)


class Administration(commands.Cog, name='Administration'):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command(
        name='ping',
        description='Check the latency',
        usage='`.ping`'
    )
    @blacklist_check()
    async def ping(self, ctx):
        time = int(self.client.latency * 1000)
        await ctx.send(
            embed=create_embed(
                f'The ping is {time} ms!'
            ),
            delete_after=10
        )

    @commands.command(
        name='clear',
        description='Delete messages (default = 5)',
        aliases=['purge', ],
        usage='`.clear [number of messages]`'
    )
    @blacklist_check()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount+1)

    @commands.command(
        name='nuke',
        description='Send a nuclear missile head that destroys all messages in a text channel',
        usage='`.nuke`'
    )
    @blacklist_check()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                ),
                delete_after=10
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Please reply with **Y** to confirm action\nThe command will be automatically cancelled after 20 second'
                ),
                delete_after=30
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
                        queue = queuecol.find_one(
                            {'guild_id': ctx.guild.id}
                        )
                        if queue['text_channel'] == channel_id:
                            queuecol.update_one(
                                {'guild_id': ctx.guild.id},
                                {
                                    '$set': {
                                        'text_channel': new_channel.id
                                    }
                                }
                            )
                        print(f'{ctx.channel} of {ctx.guild} just got nuked')
                        break
                    else:
                        counter -= 1
                        if counter == 0:
                            await ctx.send(
                                embed=create_embed(
                                    'The nuke got cancelled because the timer ran out'
                                ),
                                delete_after=10
                            )

    @commands.command(
        name='kick',
        description='Kick someone from the server',
        usage='`.kick [@member]`'
    )
    @blacklist_check()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author == member:
            await ctx.send(
                embed=create_embed(
                    'You cannot kick yourself'
                ),
                delete_after=10
            )
        elif ctx.guild.owner == member:
            await ctx.send(
                embed=create_embed(
                    'You cannot kick the server owner'
                ),
                delete_after=10
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Please reply with "Y" to confirm action\nThe command will be automatically cancelled after 20 second'
                ),
                delete_after=30
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
                                ),
                                delete_after=10
                            )
                        else:
                            await ctx.send(
                                embed=create_embed(
                                    f'**{member}** was kicked from **{member.guild}** for **{reason}**'
                                ),
                                delete_after=10
                            )
                        await member.kick(reason=reason)
                        break
                    else:
                        counter -= 1
                        if counter == 0:
                            await ctx.send(
                                embed=create_embed(
                                    'The command got cancelled because the timer ran out'
                                ),
                                delete_after=10
                            )

    @commands.command(
        name='ban',
        description='Ban someone from the server',
        usage='`.ban [@member]`'
    )
    @blacklist_check()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author == member:
            await ctx.send(
                embed=create_embed(
                    'You cannot ban yourself'
                ),
                delete_after=10
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Please reply with "Y" to confirm action\nThe command will be automatically cancelled after 20 second'
                ),
                delete_after=30
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
                                ),
                                delete_after=10
                            )
                        else:
                            await ctx.send(
                                embed=create_embed(
                                    f'**{member}** was banned from **{member.guild}** for **{reason}**'
                                ),
                                delete_after=10
                            )
                        await member.ban(reason=reason)
                        break
                    else:
                        counter -= 1
                        if counter == 0:
                            await ctx.send(
                                embed=create_embed(
                                    'The command got cancelled because the timer ran out'
                                ),
                                delete_after=10
                            )

    @commands.command(
        name='the_purge',
        description='Initiates the purge event',
        usage='`.the_purge`'
    )
    @blacklist_check()
    @commands.has_guild_permissions(kick_members=True)
    async def purge(self, ctx, *, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'The command takes in no additional arguments'
                ),
                delete_after=10
            )
        else:
            estimation = await ctx.guild.estimate_pruned_members(days=30)
            await ctx.send(
                embed=create_embed(
                    f'This command will purge the channel of all inactive members\nEstimated casualties: {estimation}\nPlease reply with "Y" if you wish to continue with the purge\nThe command will be automatically cancelled after 20 seconds'
                ),
                delete_after=30
            )
            counter = 20
            while counter > 0:
                time.sleep(1)
                async for message in ctx.channel.history(after=ctx.message.created_at):
                    if message.author == ctx.author and message.content == 'Y':
                        counter = 0
                        await ctx.send(
                            embed=create_embed(
                                'Initiating purge event'
                            ),
                            delete_after=30
                        )
                        time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                'Shooting white people'
                            ),
                            delete_after=30
                        )
                        time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                'Enslaving Africans'
                            ),
                            delete_after=30
                        )
                        time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                'Overthrowing white supremacy'
                            ),
                            delete_after=30
                        )
                        time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                'Establishing Asian World Domination'
                            ),
                            delete_after=30
                        )
                        time.sleep(1)
                        deaths = await ctx.guild.prune_members(days=30, compute_prune_count=True)
                        time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                f'Actual casualties: {deaths}\nEscaped: {estimation-deaths}'
                            ),
                            delete_after=30
                        )
                        time.sleep(1)
                        await ctx.send(
                            embed=create_embed(
                                'Purge completed, the world is now free of capitalism.\nAll hail the Communist Party'
                            ),
                            delete_after=30
                        )
                        break
                    else:
                        counter -= 1
                        if counter == 0:
                            await ctx.send(
                                embed=create_embed(
                                    'The command got cancelled because the timer ran out'
                                ),
                                delete_after=10
                            )

    @commands.command(
        name='userinfo',
        aliases=['info', 'profile'],
        description='Displays the user info',
        usage='`.userinfo`'
    )
    @blacklist_check()
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
        name='avatar',
        aliases=['photo', 'profilephoto', 'ava'],
        description='Shows the user photo',
        usage='`.avatar [member]`'
    )
    @blacklist_check()
    async def avatar(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        embed = discord.Embed(
            color=discord.Color.orange(),
            title=f"**{member.display_name}'s Avatar**",
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=member.avatar_url_as(format=None, size=4096))
        await ctx.send(embed=embed)

    @commands.command(
        name='serverinfo',
        description='Displays the server info',
        aliases=['svinfo', ],
        usage='`.serverinfo`',
    )
    @blacklist_check()
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
    @blacklist_check()
    @commands.has_guild_permissions(manage_guild=True)
    async def setprefix(self, ctx, new_prefix: str):
        info = guildcol.find_one(
            {'guild_id': ctx.guild.id}
        )
        prefixes = info['prefixes']
        prefixes[0] = new_prefix
        guildcol.update_one(
            {'guild_id': ctx.guild.id},
            {
                '$set': {
                    'prefixes': prefixes
                }
            }
        )
        await ctx.send(
            embed=create_embed(
                f'Prefix changed to {new_prefix}'
            )
        )

    @commands.command(
        name='set_join',
        description='Sets the channel for member join and the announcement message',
        usage='`.set_join [#channel] [message]`'
    )
    @blacklist_check()
    @commands.has_guild_permissions(manage_guild=True)
    async def set_join(self, ctx, channel: discord.TextChannel, *, message: str):
        if re.search('\{\}', message) == None:
            await ctx.send(
                embed=create_embed(
                    'Your message must contain "{}" to specify where to put the member name'
                ),
                delete_after=10
            )
        else:
            guildcol.update_one(
                {'guild_id': ctx.guild.id},
                {
                    '$set': {
                        'announcement_join_channel': channel.id,
                        'announcement_join_message': message
                    }
                }
            )
            await ctx.send(
                embed=create_embed(
                    f'Join message set to "{message}" at {channel.mention}'
                ),
                delete_after=60
            )

    @commands.command(
        name='set_leave',
        description='Sets the channel for member leave and the announcement message',
        usage='`.set_leave [#channel] [message]`'
    )
    @blacklist_check()
    @commands.has_guild_permissions(manage_guild=True)
    async def set_leave(self, ctx, channel: discord.TextChannel, *, message: str):
        if re.search('\{\}', message) == None:
            await ctx.send(
                embed=create_embed(
                    'Your message must contain "{}" to specify where to put the member name'
                ),
                delete_after=10
            )
        else:
            guildcol.update_one(
                {'guild_id': ctx.guild.id},
                {
                    '$set': {
                        'announcement_leave_channel': channel.id,
                        'announcement_leave_message': message
                    }
                }
            )
            await ctx.send(
                embed=create_embed(
                    f'Leave message set to "{message}" at {channel.mention}'
                ),
                delete_after=60
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

    @purge.error
    async def purge_error(self, ctx, error):
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

    @avatar.error
    async def avatar_error(self, ctx, error):
        await ctx.send(
            embed=create_embed(
                f"Couldn't get user avatar. Make sure you typed their name correctly or mention them"
            )
        )

    @setprefix.error
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=create_embed(
                    f'You do not have the {"".join(error.missing_perms)} permission for this command'
                )
            )


# Add cog
def setup(client):
    client.add_cog(Administration(client))
