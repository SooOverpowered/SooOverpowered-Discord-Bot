# Imports
import discord
import youtube_dl
import os
import asyncio
from helper import *
from parameters import *
from discord.ext import commands


def create_ytdl_source(source):
    player = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(
            source,
            before_options=" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1",
        ),
        volume=0.5
    )
    return player


def get_video_info(url):
    opts = {
        "default_search": "ytsearch",
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': 'in_playlist',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }

    def get_info(url):
        with youtube_dl.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return get_info(
                    info['entries'][0]['url']
                )
            else:
                video = info
            return video
    video = get_info(url)
    video_format = video['formats'][0]
    stream_url = video_format['url']
    video_url = video['webpage_url']
    title = video['title']
    uploader = video["uploader"] if "uploader" in video else ""
    thumbnail = video["thumbnail"] if "thumbnail" in video else None
    return [stream_url, title, video_url]


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queues = {}
        self.loop = None
        self.now_playing = {}

    def play_song(self, text_channel, voice):
        info = get_video_info(self.now_playing[voice])
        source = create_ytdl_source(info[0])
        asyncio.run_coroutine_threadsafe(
            text_channel.send(
                embed=create_embed(
                    f'**Now playing**: [{info[1]}]({info[2]})'
                )
            ), self.client.loop
        )

        def after_playing(err):
            if self.queues[voice] != []:
                info = self.queues[voice].pop(0)
                if self.loop == 'all':
                    self.queues[voice].append(info)
                elif self.loop == 'one':
                    self.queues[voice].insert(0, info)
                self.now_playing[voice] = info
                self.play_song(text_channel, voice, self.now_playing[voice])
            else:
                del self.now_playing[voice]
                asyncio.run_coroutine_threadsafe(
                    voice.disconnect(), self.client.loop)

        voice.play(source, after=after_playing)

    @commands.command(
        name='join',
        description='Connect to your current voice channel'
    )
    async def join(self, ctx):
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    "You are not in any voice channel"
                )
            )
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
        else:
            voice = await channel.connect()
            await ctx.send(
                embed=create_embed(
                    f'Bot connected to **{channel}**'
                )
            )

    @commands.command(
        name='leave',
        aliases=['dc', 'disconnect'],
        description='Disconnect from the voice channel'
    )
    async def leave(self, ctx):
        voice = ctx.voice_client
        if voice != None:
            channel = voice.channel
            del self.queues[voice]
            del self.now_playing[voice]
            await voice.disconnect()
            await ctx.send(
                embed=create_embed(
                    f'Bot disconnected from **{channel}**'
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
        text_channel = ctx.channel
        channel = ctx.author.voice.channel
        voice = ctx.voice_client
        if voice != None and voice.is_playing():
            video_source = get_video_info(url)
            self.queues[voice].append(url)
            await ctx.channel.purge(limit=1)
            await ctx.send(
                embed=create_embed(
                    f'Song [{video_source[1]}]({video_source[2]}) added to queue'
                )
            )
        else:
            if voice != None and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()
            voice = ctx.voice_client
            self.queues[voice] = []
            self.now_playing[voice] = url
            self.play_song(text_channel, voice)
            await ctx.channel.purge(limit=1)

    @commands.command(
        name='pause',
        aliases=['pau', 'pa'],
        description='Pauses the music'
    )
    async def pause(self, ctx):
        voice = ctx.voice_client
        if voice != None and voice.is_playing():
            voice.pause()
            await ctx.send(
                embed=create_embed(
                    'Music paused'
                )
            )
        elif voice != None:
            await ctx.send(
                embed=create_embed(
                    'Cannot pause while bot was not playing music'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Cannot pause while bot was not connected to any voice channel'
                )
            )

    @commands.command(
        name='resume',
        aliases=['res', 're'],
        description='Resume the music'
    )
    async def resume(self, ctx):
        voice = ctx.voice_client
        if voice != None and voice.is_paused():
            voice.resume()
            await ctx.send(
                embed=create_embed(
                    'Resumed music'
                )
            )
        elif voice != None and voice.is_playing():
            await ctx.send(
                embed=create_embed(
                    'Cannot resume if music is already playing'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Cannot resume while bot was not connected to any voice channel'
                )
            )

    @commands.command(
        name='stop',
        aliases=['s', ],
        description='Stop playing music'
    )
    async def stop(self, ctx):
        voice = ctx.voice_client
        if voice != None and voice.is_playing():
            del self.queues[voice]
            del self.now_playing[voice]
            voice.stop()
            await ctx.send(
                embed=create_embed(
                    'Stopped playing music'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Cannot stop if no music is playing'
                )
            )

    @commands.command(
        name='queue',
        aliases=['q', ],
        description='Display the current music queue'
    )
    async def queue(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'The queue command does not take in any other argument'
                )
            )
        elif self.queue[ctx.voice_client] == []:
            ctx.send(
                embed=create_embed(
                    'The music queue is empty'
                )
            )
        else:
            pass

    @commands.command()
    async def loop(self, ctx, arg=None):
        if arg == None:
            self.loop = 'all'
            voice = ctx.voice_client
            self.queues[voice].append(self.now_playing[voice])
            await ctx.send(
                embed=create_embed(
                    'Repeating all songs in the music queue'
                )
            )
        elif arg == 'one':
            self.loop = 'one'
            voice = ctx.voice_client
            self.queues[voice].append(self.now_playing[voice])
            await ctx.send(
                embed=create_embed(
                    'Repeating the current song in the music queue'
                )
            )
        elif arg == 'off':
            self.loop = None


# Add cog
def setup(client):
    client.add_cog(Music(client))
