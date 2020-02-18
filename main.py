import discord
import os
from discord.ext import commands

token = 'Njc4ODY1ODM2NTEzMTY1MzE5.XkpBLw.rZ72ZbPPllEGfi3daqpJJT2nI3s'
invitelink = 'https://discordapp.com/api/oauth2/authorize?client_id=678865836513165319&permissions=2147483127&scope=bot'
prefix = '.'
client = commands.Bot(command_prefix=prefix)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    print('Bot logged in as {0.user}'.format(client))


@client.event
async def on_member_join(member):
    print("{0} has joined the server .".format(member))


@client.event
async def on_member_remove(member):
    print("{0.user} has left the server.".format(member))


@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    print('{0.name} was kicked from {0.guild}'.format(member))


@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    print('{0.name} was banned from {0.guild}'.format(member))


# run the bot
client.run(token)
