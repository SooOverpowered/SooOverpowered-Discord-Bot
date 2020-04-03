# Imports
import discord
import os
import asyncio
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


# Run the bot
client.run(token, reconnect=True)
