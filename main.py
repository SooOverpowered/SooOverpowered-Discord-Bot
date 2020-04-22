# Imports
import discord
import os
import asyncio
import json
from helper import *
from discord.ext import commands


# Load custom prefixes
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


# load up parameters
try:
    exec(open('parameters.py').read())
except FileNotFoundError:
    print('Unable to find parameters')


# Start the bot
client = commands.Bot(command_prefix=get_prefix, owner_id=os.environ['owner'])


# Remove default help command
client.remove_command('help')


# Load up cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# Run the bot
client.run(os.environ['DISCORD_TOKEN'], reconnect=True)
