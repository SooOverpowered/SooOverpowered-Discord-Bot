# Imports
import discord
import os
from bot_plugin import *
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


# Custom activities


# Logging
@client.event
async def on_ready():
    print('Bot logged in as {0.user}'.format(client))


@client.event
async def on_member_join(member):
    print("{0} has joined the server .".format(member))
    await member.guild.system_channel.send(
        embed=create_embed(f"**{member}** has joined the server.")
    )


@client.event
async def on_member_remove(member):
    print(f"{member} has left the server.")
    await member.guild.system_channel.send(
        embed=create_embed(f"**{member}** has left the server, RIP")
    )


# System commands
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print("Cogs reloaded successfully")
    await ctx.send(embed=create_embed("Cogs reloaded successfully"))


@client.command()
async def help(ctx):
    embed = discord.Embed(
        color=discord.Color.orange()
    )
    embed.set_author(name='Help')
    embed.add_field(name='.ping', value='Returns Pong!', inline=False)
    await ctx.send(embed=embed)


# Run the bot
client.run(token)
