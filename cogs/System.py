# Imports
import discord
from parameters import *
from helper import *
from discord.ext import commands


class System(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def reload(self, ctx, extension):
        self.client.reload_extension(f'cogs.{extension}')
        print(f"Cog {extension} reloaded successfully")
        await ctx.send(embed=create_embed(f"Cog **{extension}** reloaded successfully"))

    @reload.error
    async def reload_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=create_embed(f'Cog not found, please use `{prefix}help reload` for list of cogs'))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=create_embed(f"Missing required argument, please use `{prefix}help reload` for correct usage"))

    @commands.command()
    async def load(self, ctx, extension):
        self.client.load_extension(f'cogs.{extension}')
        print(f'Cog {extension} loaded successfully')
        await ctx.send(embed=create_embed(f"Cog **{extension}** loaded successfully"))

    @load.error
    async def load_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(embed=create_embed(f'Cog not found, please use `{prefix}help reload` for list of cogs'))

    @commands.command()
    async def unload(self, ctx, extension):
        self.client.unload_extension(f'cogs.{extension}')
        print(f'Cog {extension} unloaded successfully')
        await ctx.send(embed=create_embed(f"Cog **{extension}** unloaded successfully"))


def setup(client):
    client.add_cog(System(client))
