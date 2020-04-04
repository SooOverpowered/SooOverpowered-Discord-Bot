# Imports
import discord
import youtube_dl
import os
import asyncio
import time
from helper import *
from parameters import *
from discord.ext import commands


def create_ytdl_source(source):
    player = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(
            source,
            before_options=" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1",
            options='-vn'
        ),
        volume=0.5
    )
    return player


def get_video_info(url):
    opts = {
        "default_search": "ytsearch",
        'format': 'bestaudio/best',
        'quiet': True,
        'audioformat': 'mp3',
        'extract_flat': 'in_playlist',
        'extractaudio': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': True,
    }

    def get_info(url):
        with youtube_dl.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                time.sleep(1)
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


class Music(commands.Cog, name='Music'):
    def __init__(self, client):
        self.client = client
        self.queues = {}
        self.loop = {}
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

        def after_playing(error):
            if self.queues[voice] != []:
                info = self.queues[voice].pop(0)
                if self.loop[voice] == 'all':
                    self.queues[voice].append(info)
                elif self.loop[voice] == 'one':
                    self.queues[voice].insert(0, info)
                self.now_playing[voice] = info
                self.play_song(text_channel, voice)
            else:
                asyncio.run_coroutine_threadsafe(
                    text_channel.send(
                        embed=create_embed(
                            'Music queue ended, disconnected from voice'
                        )
                    ), self.client.loop
                )
                asyncio.run_coroutine_threadsafe(
                    voice.disconnect(), self.client.loop)

        voice.play(source, after=after_playing)

    @commands.command(
        name='join',
        aliases=['j', 'connect', ],
        description='Connect to your current voice channel',
        usage=f'`{prefix}join`'
    )
    async def join(self, ctx):
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    "You are not in any voice channel"
                )
            )
        else:
            channel=ctx.author.voice.channel
            voice=ctx.voice_client
            if voice != None and voice.channel == channel:
                await ctx.send(
                    embed=create_embed(
                        'Bot is already connected to your voice channel'
                    )
                )
            elif voice != None and voice.is_connected:
                await voice.move_to(channel)
            else:
                voice=await channel.connect()
                await ctx.send(
                    embed=create_embed(
                        f'Bot connected to **{channel}**'
                    )
                )

    @commands.command(
        name='leave',
        aliases=['dc', 'disconnect'],
        description='Disconnect from the voice channel',
        usage=f'`{prefix}leave`'
    )
    async def leave(self, ctx):
        voice=ctx.voice_client
        if voice != None:
            channel=voice.channel
            self.queues[voice]=[]
            self.now_playing[voice]=None
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
        description='Play music from Youtube',
        usage=f'`{prefix}play`'
    )
    async def play(self, ctx, *, url):
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            text_channel=ctx.channel
            channel=ctx.author.voice.channel
            voice=ctx.voice_client
            if voice != None and voice.is_playing():
                video_source=get_video_info(url)
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
                    voice=await channel.connect()
                    voice=ctx.voice_client
                self.queues[voice]=[]
                self.now_playing[voice]=url
                self.loop[voice]='off'
                await ctx.channel.purge(limit=1)
                self.play_song(text_channel, voice)

    @commands.command(
        name='pause',
        aliases=['pau', 'pa'],
        description='Pauses the music',
        usage=f'`{prefix}pause`'
    )
    async def pause(self, ctx):
        voice=ctx.voice_client
        if voice != None and voice.is_playing():
            voice.pause()
            await ctx.send(
                embed=create_embed(
                    'Music paused'
                )
            )
        elif voice != None and voice.is_paused():
            await ctx.send(
                embed=create_embed(
                    'Cannot pause while bot was already paused'
                )
            )
        elif voice != None and voice.is_connected():
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
        description='Resume the music',
        usage=f'`{prefix}resume`'
    )
    async def resume(self, ctx):
        voice=ctx.voice_client
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
        elif voice != None and voice.is_connected():
            await ctx.send(
                embed=create_embed(
                    'Cannot resume if there is no music to play'
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
        aliases=['s', 'st', ],
        description='Stop playing music',
        usage=f'`{prefix}stop`'
    )
    async def stop(self, ctx):
        voice=ctx.voice_client
        if voice != None and voice.is_playing():
            self.queues[voice]=[]
            self.now_playing[voice]=None
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
        description='Display your current music queue',
        usage=f'`{prefix}queue`'
    )
    async def queue(self, ctx, arg=None):
        voice=ctx.voice_client
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        elif voice != None:
            if self.queues[voice] == []:
                await ctx.send(
                    embed=create_embed(
                        'The music queue is empty'
                    )
                )
            else:
                output=''
                counter=1
                for urls in self.queues[voice]:
                    output += f'{counter}. {get_video_info(urls)[1]}\n'
                    counter += 1
                embed=discord.Embed(
                    color=discord.Color.orange(),
                    description=output
                )
                embed.set_author(
                    name=f'Music queue for {ctx.author.voice.channel}'
                )
                embed.set_footer(text=f'Repeat: {self.loop}')
                await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=create_embed(
                    'You are not connected to any voice channel'
                )
            )

    @commands.command(
        name='loop',
        aliases=['repeat', ],
        description='Toggle between looping all, one or off',
        usage=f'`{prefix}loop [all/one/off]`'
    )
    async def loop(self, ctx, arg=None):
        voice=ctx.voice_client
        if voice == None or voice.is_playing() == False:
            await ctx.send(
                embed=create_embed(
                    'There is no ongoing music being played'
                )
            )
        if arg == None or arg == 'all':
            self.loop[voice]='all'
            voice=ctx.voice_client
            self.queues[voice].append(self.now_playing[voice])
            await ctx.send(
                embed=create_embed(
                    'Repeating all songs in the music queue'
                )
            )
        elif arg == 'one':
            self.loop[voice]='one'
            voice=ctx.voice_client
            self.queues[voice].insert(0, self.now_playing[voice])
            await ctx.send(
                embed=create_embed(
                    'Repeating the current song in the music queue'
                )
            )
        elif arg == 'off':
            self.loop[voice]='off'
            self.queues[voice].remove(self.now_playing[voice])
            await ctx.send(
                embed=create_embed(
                    'Repeating song is now off'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    'Please use the correct argument'
                )
            )

    @commands.command(
        name='skip',
        aliases=['sk', ],
        description='Skip the song currently being played',
        usage=f'`{prefix}skip`'
    )
    async def skip(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        else:
            voice=ctx.voice_client
            if self.queues[voice] != []:
                if self.now_playing[voice] in self.queues[voice]:
                    self.queues[voice].remove(self.now_playing[voice])
            await ctx.send(
                embed=create_embed(
                    f'Skipped {get_video_info(self.now_playing[voice])[1]}, playing next'
                )
            )
            voice.stop()

    @commands.command(
        name='dequeue',
        aliases=['rmq', 'rm'],
        description='Remove a song from the music queue',
        usage=f'`{prefix}dequeue [song position in music queue]`'
    )
    async def dequeue(self, ctx, position):
        voice=ctx.voice_client


# Error handler


# Add cog
def setup(client):
    client.add_cog(Music(client))
