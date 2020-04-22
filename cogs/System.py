# Imports
import discord
import json
import os
from helper import *
from discord.ext import commands


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
            )
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
            )
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
            )
        )

    @commands.command(
        name='listserver',
        description='List the servers that the bot is in',
        usage='`.listserver`'
    )
    @commands.is_owner()
    async def listserver(self, ctx):
        for guild in self.client.guilds:
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
                name=f"{os.environ['activity']} | type {os.environ['default_prefix']}help"
            ),
            status=discord.Status.online
        )

    @commands.Cog.listener()
    async def on_disconnect(self):
        voiceclients = self.client.voice_clients
        with open('queue.json', 'r') as f:
            queue = json.load(f)
        for voice in voiceclients:
            if voice.is_playing():
                voice.pause()
                channel = self.client.get_channel(
                    int(
                        queue[str(voice)][0]['text_channel']
                    )
                )
                await channel.send(
                    embed=create_embed(
                        'Bot was disconnected from discord, music was paused for you automatically'
                    )
                )

    @commands.Cog.listener()
    async def on_ready(self):
        print('Bot logged in as {0.user}'.format(self.client))
        guilds = self.client.guilds
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        for guild in guilds:
            if str(guild.id) not in prefixes:
                prefixes[str(guild.id)] = ['.', ]
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        for guild in guilds:
            if str(guild.id) not in playlist:
                playlist[str(guild.id)] = {}
        with open('playlist.json', 'w') as f:
            json.dump(playlist, f, indent=4)

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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes[str(guild.id)] = ['.', ]
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        playlist[str(guild.id)] = {}
        with open('playlist.json', 'w') as f:
            json.dump(playlist, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        playlist.pop(str(guild.id))
        with open('playlist.json', 'w') as f:
            json.dump(playlist, f, indent=4)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                embed=create_embed(
                    'Command not found'
                )
            )
            await ctx.message.delete()


def setup(client):
    client.add_cog(System(client))
