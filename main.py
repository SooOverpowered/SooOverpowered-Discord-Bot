# Imports
import discord
import os
import asyncio
import json
from helper import *
from discord.ext import commands

# Load environmental variables
try:
    exec(open('variable.py').read())
except:
    print('shit does not work, abort mission')


# Load custom prefixes
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    extras = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(*extras)(client, message)


# Start the bot
client = commands.Bot(
    command_prefix=get_prefix,
    owner_id=int(os.environ.get('owner'))
)


# Remove default help command
client.remove_command('help')


# Load up cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


# Run the bot
client.run(os.environ.get('DISCORD_TOKEN'), reconnect=True)
