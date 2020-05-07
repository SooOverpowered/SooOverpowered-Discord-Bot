# Imports
import discord
import json
import os
import math
import pymongo
from helper import *
from discord.ext import commands

# Connect to mongodb database
client = pymongo.MongoClient(os.environ.get('dbconn'))
db = client['DaedBot']
guildcol = db['prefix']
queuecol = db['queue']
playlistcol = db['playlist']


class System(commands.Cog, name='System'):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command(
        name='reload',
        description='Reload the cog',
        usage='`.reload [cog name]`'
    )
    @commands.is_owner()
    async def reload(self, ctx, extension):
        await ctx.channel.purge(limit=1)
        self.client.reload_extension(f'cogs.{extension}')
        print(f"Cog {extension} reloaded successfully")
        await ctx.send(
            embed=create_embed(
                f"Cog **{extension}** reloaded successfully"
            ),
            delete_after=10
        )

    @commands.command(
        name='load',
        description='Load the cog',
        usage='`.load [cog name]`'
    )
    @commands.is_owner()
    async def load(self, ctx, extension):
        await ctx.channel.purge(limit=1)
        self.client.load_extension(f'cogs.{extension}')
        print(f'Cog {extension} loaded successfully')
        await ctx.send(
            embed=create_embed(
                f"Cog **{extension}** loaded successfully"
            ),
            delete_after=10
        )

    @commands.command(
        name='unload',
        description='Unload the cog',
        usage='`.unload [cog name]`')
    @commands.is_owner()
    async def unload(self, ctx, extension):
        await ctx.channel.purge(limit=1)
        self.client.unload_extension(f'cogs.{extension}')
        print(f'Cog {extension} unloaded successfully')
        await ctx.send(
            embed=create_embed(
                f"Cog **{extension}** unloaded successfully"
            ),
            delete_after=10
        )

    @commands.command(
        name='listserver',
        description='List the servers that the bot is in',
        usage='`.listserver`'
    )
    @commands.is_owner()
    async def listserver(self, ctx, page: int = 1):
        output = ''
        guilds = self.client.guilds
        pages = math.ceil(len(guilds)/20)
        for guild in guilds:
            pass

    @commands.command(
        name='leaveserver'
    )
    @commands.is_owner()
    async def leaveserver(self, ctx):
        pass

    # Error handler
    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=create_embed(
                    f'Cog not found, please use `.help reload` for list of cogs'
                )
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=create_embed(
                    f"Missing required argument, please use `.help reload` for correct usage"
                )
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                embed=create_embed(
                    'You must be the bot owner to use this command'
                )
            )

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=create_embed(
                    f'Cog not found, please use `.help load` for list of cogs'
                )
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                embed=create_embed(
                    'You must be the bot owner to use this command'
                )
            )

    @unload.error
    async def unload_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(
                embed=create_embed(
                    f'Cog not found, please use `.help unload` for list of cogs'
                )
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                embed=create_embed(
                    'You must be the bot owner to use this command'
                )
            )

    # Events
    @commands.Cog.listener()
    async def on_connect(self):
        await self.client.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{os.environ.get('activity')} | type {os.environ.get('default_prefix')}help"
            ),
            status=discord.Status.online
        )

    @commands.Cog.listener()
    async def on_disconnect(self):
        queues = queuecol.find()
        for queue in queues:
            guild = self.client.get_guild(queue['guild_id'])
            if guild.voice_client.is_playing():
                guild.voice_client.pause()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot logged in as {0.user}'.format(self.client))
        guilds = self.client.guilds
        dbguilds = []
        for item in guildcol.find():
            if item['prefixes'][0] != os.environ.get('default_prefix'):
                guildcol.update_one(
                    {'guild_id': item['guild_id']},
                    {
                        '$set': {
                            'prefixes.0': os.environ.get('default_prefix')
                        }
                    }
                )
            dbguilds.append(item['guild_id'])
        for guild in guilds:
            if guild.id not in dbguilds:
                guildcol.insert_one(
                    {
                        'guild_id': guild.id,
                        'prefixes': [
                            os.environ.get('default_prefix'),
                        ],
                        'announcement_join_channel': None,
                        'announcement_join_message': '{} has joined the server.',
                        'announcement_leave_channel': None,
                        'announcement_leave_message': '{} has left the server, RIP'
                    }
                )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guildid = member.guild.id
        guildinfo = guildcol.find_one({'guild_id': guildid})
        if guildinfo['announcement_join_channel'] != None:
            channel = member.guild.get_channel(
                guildinfo['announcement_join_channel']
            )
            await channel.send(
                embed=create_embed(
                    guildinfo['announcement_join_message'].format(
                        member.mention
                    )
                )
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guildid = member.guild.id
        guildinfo = guildcol.find_one({'guild_id': guildid})
        if guildinfo['announcement_leave_channel'] != None:
            channel = member.guild.get_channel(
                guildinfo['announcement_leave_channel']
            )
            await channel.send(
                embed=create_embed(
                    guildinfo['announcement_leave_message'].format(
                        member.mention
                    )
                )
            )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        guildcol.insert_one(
            {
                'guild_id': guild.id,
                'prefixes': [
                    os.environ.get('default_prefix'),
                ],
                'announcement_join_channel': None,
                'announcement_join_message': '**{}** has joined the server.',
                'announcement_leave_channel': None,
                'announcement_leave_message': '**{}** has left the server, RIP'
            }
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guildcol.delete_one({'guild_id': guild.id})
        queuecol.delete_many({'guild_id': guild.id})
        playlistcol.delete_many({'guild_id': guild.id})

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                embed=create_embed(
                    'Command not found'
                ),
                delete_after=10
            )
            await ctx.message.delete()


def setup(client):
    client.add_cog(System(client))
