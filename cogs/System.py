# Imports
import discord
from helper import *
from parameters import *
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
        self.client.unload_extension(f'cogs.{extension}')
        print(f'Cog {extension} unloaded successfully')
        await ctx.send(
            embed=create_embed(
                f"Cog **{extension}** unloaded successfully"
            )
        )

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


def setup(client):
    client.add_cog(System(client))
