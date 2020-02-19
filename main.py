import discord
import os
from discord.ext import commands


try:
    exec(open('parameters.py').read())
except FileNotFoundError:
    print('Unable to find parameters')


client = commands.Bot(command_prefix=prefix)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    custom_type=discord.ActivityType.custom()
    custom_activity=discord.CustomActivity('Ready',type=custom_type)
    await client.change_presence(status=discord.Status.online,afk=False,activity=custom_activity)
    print('Bot logged in as {0.user}'.format(client))


@client.event
async def on_member_join(member):
    print("{0} has joined the server .".format(member))


@client.event
async def on_member_remove(member):
    print("{0.user} has left the server.".format(member))


@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')


# run the bot
client.run(token)
