# Imports
import discord
import os
from helper import *
from discord.ext import commands


# load up parameters
try:
    exec(open('parameters.py').read())
except FileNotFoundError:
    print('Unable to find parameters')


# Start the bot
client = commands.Bot(command_prefix=prefix)


# Remove default help command
client.remove_command('help')


# Load up cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# System commands
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print(f"Cog {extension} reloaded successfully")
    await ctx.send(embed=create_embed(f"Cog {extension} reloaded successfully"))


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    print(f'Cog {extension} loaded successfully')
    await ctx.send(embed=create_embed(f"Cog {extension} loaded successfully"))


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    print(f'Cog {extension} unloaded successfully')
    await ctx.send(embed=create_embed(f"Cog {extension} unloaded successfully"))


# Run the bot
client.run(token)
