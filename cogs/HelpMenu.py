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
                author='Help',
                description=f'Use `{prefix}help [module name]` for more information'
            )
            embed.add_field(name='**Administration**',
                            value='Managing the server', inline=False)
            embed.add_field(name='**Music**',
                            value='The music player', inline=False)
            await ctx.send(embed=embed)

    @help.command(
        name='Administration',
        aliases=['admin', ],
        description='Show list of administrative commands'
    )
    async def Administration(self, ctx):
        cog = self.client.get_cog('Administration')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            author=cog.qualified_name,
            description='**List of administrative commands**'
        )
        for command in commands:
            if command.aliases != []:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Usage: {command.usage}\nDescription: {command.description}\nAliases: `{", ".join(command.aliases)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Usage: {command.usage}\nDescription: {command.description}',
                    inline=False
                )
        await ctx.send(embed=embed)

    @help.command(
        name='Music',
        aliases=['music'],
        description='Show list of music commands'
    )
    async def Music(self, ctx):
        cog = self.client.get_cog('Music')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            author=cog.qualified_name,
            description='**List of music commands**'
        )
        for command in commands:
            if command.aliases != []:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Usage: {command.usage}\nDescription: {command.description}\nAliases: `{", ".join(command.aliases)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Usage: {command.usage}\nDescription: {command.description}',
                    inline=False
                )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(HelpMenu(client))
