# Imports
import discord
import youtube_dl
import os
import functools
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
        voice = ctx.voice_client
        if voice != None and voice.channel == channel:
            await ctx.send(
                embed=create_embed(
                    'Bot is already connected to your voice channel'
                )
            )
        elif voice != None and voice.is_connected:
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
        voice = ctx.voice_client
        if voice != None:
            channel = voice.channel
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

    @commands.command(
        name='play',
        aliases=['p', ],
        description='Play music from Youtube'
    )
    async def play(self, ctx, *, url):
        channel = ctx.author.voice.channel
        voice = ctx.voice_client
        video_source = get_video_info(url)
        await ctx.send(
            embed=create_embed(
                f'**Now playing**: [{video_source[1]}]({url})'
            )
        )
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(
                video_source[0],
                before_options=" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1"),
            volume=0.5
        )
        voice.play(source)


# Add cog
def setup(client):
    client.add_cog(Music(client))
