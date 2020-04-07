# Imports
import discord
from helper import *
from parameters import *
from discord.ext import commands


class HelpMenu(commands.Cog, name='Help'):
    def __init__(self, client):
        self.client = client

    @commands.group(
        invoke_without_command=True
    )
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=discord.Color.orange(),
                description=f'Use `{prefix}help [module name]` for more information'
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
        cog = self.client.get_cog('Administration')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of administrative commands**'
        )
        embed.set_author(
            name=cog.qualified_name,
        )
        for command in commands:
            if command.aliases != []:
                alias_list = command.aliases
                for i in range(len(alias_list)):
                    alias_list[i] = f'{prefix}'+alias_list[i]
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(alias_list)}`',
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                )
        await ctx.send(embed=embed)

    @help.command(
        name='Music',
        aliases=['music', ],
        description='Show list of music commands'
    )
    async def Music(self, ctx):
        cog = self.client.get_cog('Music')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of music commands**'
        )
        embed.set_author(
            name=cog.qualified_name
        )
        for command in commands:
            if command.aliases != []:
                alias_list = command.aliases
                for i in range(len(alias_list)):
                    alias_list[i] = f'{prefix}'+alias_list[i]
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(alias_list)}`',
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(HelpMenu(client))
