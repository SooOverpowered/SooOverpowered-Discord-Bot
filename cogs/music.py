# Imports
import discord
import youtube_dl
import os
from helper import *
from parameters import *
from discord.ext import commands
from discord.utils import get


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name='join',
        description='Connect to your current voice channel'
    )
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected:
            await voice.move_to(channel)
            print(f'Bot moved to {channel}')
        else:
            voice = await channel.connect()
            print(f'Bot connected to {channel}')

    @commands.command(
        name='leave',
        aliases=['dc', 'disconnect'],
        description='Disconnect from the voice channel'
    )
    async def leave(self, ctx):
        channel = ctx.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
            print(f'The bot has left {channel}')
            await ctx.send(
                embed=create_embed(
                    f'Bot disconnected from {channel}'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Bot was not connected to any voice channel'
                )
            )


# Add cog
def setup(client):
    client.add_cog(Music(client))
