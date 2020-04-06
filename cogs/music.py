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
        'noplaylist': True,
        'extract_flat': 'in_playlist',
        'extractaudio': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': True,
        'sleep_interval': 1,
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
    async def join(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        elif ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    "You are not in any voice channel"
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel == channel:
                    await ctx.send(
                        embed=create_embed(
                            'Bot is already connected to your voice channel'
                        )
                    )
                else:
                    if len(voice.channel.members) == 1:
                        await voice.move_to(channel)
                        await ctx.send(
                            embed=create_embed(
                                f'Bot connected to **{channel}**'
                            )
                        )
                    elif voice.is_playing() or voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                'Please wait until other members are done listening to music'
                            )
                        )
                    else:
                        await voice.move_to(channel)
                        await ctx.send(
                            embed=create_embed(
                                f'Bot connected to **{channel}**'
                            )
                        )
            else:
                voice = await channel.connect()
                self.queues[voice] = []
                self.now_playing[voice] = None
                self.loop[voice] = 'off'
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
    async def leave(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        else:
            voice = ctx.voice_client
            if voice != None:
                if len(voice.channel.members) == 1:
                    self.queues[voice] = []
                    self.now_playing[voice] = None
                    self.loop[voice] = 'off'
                    await voice.disconnect()
                    await ctx.send(
                        embed=create_embed(
                            f'Bot disconnected from **{voice.channel}**'
                        )
                    )
                else:
                    if voice.is_playing() or voice.is_paused():
                        if ctx.author.voice == None:
                            await ctx.send(
                                embed=create_embed(
                                    'Please wait until other members are done listening to music'
                                )
                            )
                        elif ctx.author.voice.channel != voice.channel:
                            await ctx.send(
                                embed=create_embed(
                                    'Please wait until other members are done listening to music'
                                )
                            )
                        else:
                            self.queues[voice] = []
                            self.now_playing[voice] = None
                            self.loop[voice] = 'off'
                            await voice.disconnect()
                            await ctx.send(
                                embed=create_embed(
                                    f'Bot disconnected from **{voice.channel}**'
                                )
                            )
                    else:
                        self.queues[voice] = []
                        self.now_playing[voice] = None
                        self.loop[voice] = 'off'
                        await voice.disconnect()
                        await ctx.send(
                            embed=create_embed(
                                f'Bot disconnected from **{voice.channel}**'
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
        usage=f'`{prefix}play [url or song name]`'
    )
    async def play(self, ctx, *, url):
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            text_channel = ctx.channel
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    if len(voice.channel.members) == 1:
                        await voice.move_to(channel)
                        self.queues[voice] = []
                        self.now_playing[voice] = url
                        self.loop[voice] = 'off'
                        await ctx.channel.purge(limit=1)
                        self.play_song(text_channel, voice)
                    elif voice.is_playing() or voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                'Please wait until other members are done listening to music'
                            )
                        )
                    else:
                        await voice.move_to(channel)
                        self.queues[voice] = []
                        self.now_playing[voice] = url
                        self.loop[voice] = 'off'
                        await ctx.channel.purge(limit=1)
                        self.play_song(text_channel, voice)
                else:
                    video_source = get_video_info(url)
                    self.queues[voice].append(url)
                    await ctx.channel.purge(limit=1)
                    await ctx.send(
                        embed=create_embed(
                            f'Song [{video_source[1]}]({video_source[2]}) added to queue'
                        )
                    )

            else:
                voice = await channel.connect()
                voice = ctx.voice_client
                self.queues[voice] = []
                self.now_playing[voice] = url
                self.loop[voice] = 'off'
                await ctx.channel.purge(limit=1)
                self.play_song(text_channel, voice)

    @commands.command(
        name='pause',
        aliases=['pau', 'pa'],
        description='Pauses the music',
        usage=f'`{prefix}pause`'
    )
    async def pause(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        elif ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel == channel:
                    if voice.is_playing():
                        voice.pause()
                        await ctx.send(
                            embed=create_embed(
                                'Music paused'
                            )
                        )
                    elif voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                'Cannot pause while bot was already paused'
                            )
                        )
                    else:
                        await ctx.send(
                            embed=create_embed(
                                'Cannot pause while bot was not playing music'
                            )
                        )
                else:
                    await ctx.send(
                        embed=create_embed(
                            'Please wait until other members are done listening to music'
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
    async def resume(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        elif ctx.author.voice == None:
            ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            'Please wait until other members are done listening to music'
                        )
                    )
                else:
                    if voice.is_paused():
                        voice.resume()
                        await ctx.send(
                            embed=create_embed(
                                'Resumed music'
                            )
                        )
                    elif voice.is_playing():
                        await ctx.send(
                            embed=create_embed(
                                'Cannot resume if music is already playing'
                            )
                        )
                    else:
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
    async def stop(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        elif ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if len(voice.channel.members) == 1:
                    self.queues[voice] = []
                    self.now_playing[voice] = None
                    self.loop[voice] = 'off'
                    if voice.is_playing() or voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                'Stopped playing music'
                            )
                        )
                    voice.stop()
                elif voice.is_playing() or voice.is_paused():
                    if voice.channel != channel:
                        await ctx.send(
                            embed=create_embed(
                                'Please wait until other members are done listening to music'
                            )
                        )
                    else:
                        self.queues[voice] = []
                        self.now_playing[voice] = None
                        self.loop[voice] = 'off'
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
            else:
                await ctx.send(
                    embed=create_embed(
                        'Cannot stop while bot was not connected to any voice channel'
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
        elif ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            'Please wait until other members are done listening to music'
                        )
                    )
                else:
                    if self.loop[voice] == 'one':
                        self.queues[voice].remove(self.now_playing[voice])
                    info = get_video_info(self.now_playing[voice])
                    await ctx.send(
                        embed=create_embed(
                            f'Skipped [{info[1]}]({info[2]}), playing next'
                        )
                    )
                    voice.stop()
            else:
                await ctx.send(
                    embed=create_embed(
                        'Bot was not connected to any voice channel'
                    )
                )

    @commands.command(
        name='queue',
        aliases=['q', ],
        description='Display your current music queue',
        usage=f'`{prefix}queue`'
    )
    async def queue(self, ctx, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        elif ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            'You are not using music'
                        )
                    )
                else:
                    if self.queues[voice] == []:
                        await ctx.send(
                            embed=create_embed(
                                'The music queue is empty'
                            )
                        )
                    else:
                        info = get_video_info(self.now_playing[voice])
                        output = f'**Now playing**: [{info[1]}]({info[2]})\n'
                        counter = 1
                        for urls in self.queues[voice]:
                            output += f'{counter}. {get_video_info(urls)[1]}\n'
                            counter += 1
                        embed = discord.Embed(
                            color=discord.Color.orange(),
                            description=output
                        )
                        embed.set_author(
                            name=f'Music queue for {ctx.author.voice.channel}'
                        )
                        embed.set_footer(text=f'Repeat: {self.loop[voice]}')
                        await ctx.send(embed=embed)
            else:
                await ctx.send(
                    embed=create_embed(
                        'Bot was not connected to any voice channel'
                    )
                )

    @commands.command(
        name='dequeue',
        aliases=['rmq', 'rm'],
        description='Remove a song from the music queue',
        usage=f'`{prefix}dequeue [song position in music queue]`'
    )
    async def dequeue(self, ctx, position: int, arg=None):
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command only takes in one argument'
                )
            )
        elif ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            'Please wait until other members are done listening to music'
                        )
                    )
                else:
                    if position > len(self.queues[voice]):
                        await ctx.send(
                            embed=create_embed(
                                f'The music queue only have **{len(self.queues[voice])}** songs, but you specified more than that!'
                            )
                        )
                    else:
                        info = get_video_info(
                            self.queues[voice].pop(position-1))
                        await ctx.send(
                            embed=create_embed(
                                f'Song [{info[1]}]({info[2]}) removed from music queue'
                            )
                        )
            else:
                await ctx.send(
                    embed=create_embed(
                        'Bot was not connected to any voice channel'
                    )
                )

    @commands.command(
        name='loop',
        aliases=['repeat', ],
        description='Toggle between looping all, one or off',
        usage=f'`{prefix}loop [all/one/off]`'
    )
    async def loop(self, ctx, arg=None):
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        else:
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            if voice != None:
                if voice.channel != channel:
                    await ctx.send(
                        embed=create_embed(
                            'Please wait until other members are done listening to music'
                        )
                    )
                else:
                    if self.now_playing[voice] == None:
                        await ctx.send(
                            embed=create_embed(
                                'There is no ongoing music being played'
                            )
                        )
                    elif arg == None or arg == 'all':
                        if self.loop[voice] == 'one':
                            self.queues[voice].pop(0)
                        self.loop[voice] = 'all'
                        voice = ctx.voice_client
                        if self.now_playing[voice] not in self.queues[voice]:
                            self.queues[voice].append(self.now_playing[voice])
                        await ctx.send(
                            embed=create_embed(
                                'Repeating all songs in the music queue'
                            )
                        )
                    elif arg == 'one':
                        self.loop[voice] = 'one'
                        voice = ctx.voice_client
                        if self.now_playing[voice] in self.queues[voice]:
                            index = self.queues[voice].index(
                                self.now_playing[voice])
                            self.queues[voice].insert(
                                0, self.queues[voice].pop(index))
                        else:
                            self.queues[voice].insert(
                                0, self.now_playing[voice])
                        await ctx.send(
                            embed=create_embed(
                                'Repeating the current song in the music queue'
                            )
                        )
                    elif arg == 'off':
                        self.loop[voice] = 'off'
                        if self.now_playing[voice] in self.queues[voice]:
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
            else:
                await ctx.send(
                    embed=create_embed(
                        'Bot was not connected to any voice channel'
                    )
                )

    # Error handler
    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=create_embed(
                    'The play command also need a link or search keyword to work'
                )
            )

    @dequeue.error
    async def dequeue_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                embed=create_embed(
                    'Please use the correct argument'
                )
            )


# Add cog
def setup(client):
    client.add_cog(Music(client))
