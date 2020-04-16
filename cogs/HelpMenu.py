# Imports
import discord
from helper import *
from parameters import *
from discord.ext import commands
from discord.utils import get


class HelpMenu(commands.Cog, name='Help'):
    def __init__(self, client):
        self.client = client

    @commands.group(
        name='Help',
        description='The help command',
        invoke_without_command=True,
        aliases=['h', ]
    )
    async def help(self, ctx):
        await ctx.channel.purge(limit=1)
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=discord.Color.orange(),
                description='Use `.help [module name]` for more information'
            )
            embed.set_author(
                name='Help',
            )
            embed.add_field(
                name='**Administration**',
                value='Managing the server',
                inline=False
            )
            embed.add_field(
                name='**Music**',
                value='The music player',
                inline=False
            )
            await ctx.send(embed=embed)

    @help.command(
        name='Administration',
        aliases=['admin', 'administration', ],
        description='Show list of administrative commands'
    )
    async def Administration(self, ctx):
        await ctx.channel.purge(limit=1)
        cog = self.client.get_cog('Administration')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of administrative commands**\n\nUse `.help Administration [command name]` for more information'
        )
        embed.set_author(
            name=cog.qualified_name,
        )
        for command in commands:
            if command.aliases != []:
                alias_list = command.aliases
                temp_alias_list = []
                for i in range(len(alias_list)):
                    temp_alias_list.append(f'.'+alias_list[i])
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(temp_alias_list)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                    inline=False
                )
        await ctx.send(embed=embed)

    @help.group(
        name='Music',
        aliases=['music', ],
        description='Show list of music commands'
    )
    async def Music(self, ctx):
        await ctx.channel.purge(limit=1)
        cog = self.client.get_cog('Music')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of music commands**\n\nUse `.help Music [command name]` for more information'
        )
        embed.set_author(
            name=cog.qualified_name
        )
        for command in commands:
            if command.aliases != []:
                alias_list = command.aliases
                temp_alias_list = []
                for i in range(len(alias_list)):
                    temp_alias_list.append(f'.'+alias_list[i])
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(temp_alias_list)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                    inline=False
                )
        await ctx.send(embed=embed)

    @Music.group(
        name='Playlist',
        invoke_without_command=True,
        aliases=['pl', 'plist', 'playlist']
    )
    async def help_playlist(self, ctx):
        await ctx.channel.purge(limit=1)
        cog = self.client.get_cog('Music')
        commands = discord.utils.get(cog.get_commands(), name='playlist')
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of playlist options**\n\nUse `.help Music Playlist [option]` for more information'
        )
        for command in commands.commands:
            if command.aliases != []:
                alias_list = command.aliases
                temp_alias_list = []
                for i in range(len(alias_list)):
                    temp_alias_list.append(f'.'+alias_list[i])
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(temp_alias_list)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                    inline=False
                )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(HelpMenu(client))
