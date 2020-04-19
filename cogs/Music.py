# Imports
import discord
import youtube_dl
import os
import asyncio
import json
import math
from helper import *
from parameters import *
from discord.ext import commands


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
    'logtostderr': False,
    'no_warnings': True,
    'sleep_interval': 1,
}


def create_ytdl_source(source, volume=0.5):
    player = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(
            source,
            before_options=" -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1",
            options='-vn'
        ),
        volume=volume
    )
    return player


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


def get_video_info(url):
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

    def play_song(self, voice):
        with open('queue.json', 'r') as f:
            queue = json.load(f)
        info = get_video_info(queue[str(voice)][1]['url'])
        volume = queue[str(voice)][0]['volume']
        source = create_ytdl_source(info[0], volume)
        text_channel = self.client.get_channel(int(
            queue[str(voice)][0]['text_channel']
        ))
        asyncio.run_coroutine_threadsafe(
            text_channel.send(
                embed=create_embed(
                    f'**Now playing**: [{info[1]}]({info[2]})'
                )
            ), self.client.loop
        )

        def after_playing(error):
            with open('queue.json', 'r') as f:
                queue = json.load(f)
            info = queue[str(voice)].pop(1)
            if queue[str(voice)][0]['loop'] == 'all':
                queue[str(voice)].append(info)
            elif queue[str(voice)][0]['loop'] == 'one':
                queue[str(voice)].insert(1, info)
            with open('queue.json', 'w') as f:
                json.dump(queue, f, indent=4)
            if len(queue[str(voice)]) > 1:
                self.play_song(voice)
            else:
                with open('queue.json', 'r') as f:
                    queue = json.load(f)
                queue.pop(str(voice))
                with open('queue.json', 'w') as f:
                    json.dump(queue, f, indent=4)
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
        usage='`.join`'
    )
    async def join(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
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
                voice = await channel.connect(reconnect=True)
                with open('queue.json', 'r') as f:
                    queue = json.load(f)
                queue[str(voice)] = [
                    {
                        'loop': 'off',
                        "text_channel": str(ctx.channel.id),
                        "volume": 0.5
                    },
                ]
                with open('queue.json', 'w') as f:
                    json.dump(queue, f, indent=4)
                await ctx.send(
                    embed=create_embed(
                        f'Bot connected to **{channel}**'
                    )
                )

    @commands.command(
        name='leave',
        aliases=['dc', 'disconnect'],
        description='Disconnect from the voice channel',
        usage='`.leave`'
    )
    async def leave(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
        if arg != None:
            await ctx.send(
                embed=create_embed(
                    'This command does not take in any other argument'
                )
            )
        else:
            voice = ctx.voice_client
            if voice != None:
                with open('queue.json', 'r') as f:
                    queue = json.load(f)
                if len(voice.channel.members) == 1:
                    if voice.is_playing() or voice.is_paused():
                        queue[str(voice)] = queue[str(voice)][:2]
                        queue[str(voice)][0]['loop'] = 'off'
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        voice.stop()
                    else:
                        queue.pop(str(voice))
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await voice.disconnect()
                        await ctx.send(
                            embed=create_embed(
                                f'Bot disconnected from **{voice.channel}**'
                            )
                        )
                else:
                    if voice.is_playing() or voice.is_paused():
                        if ctx.author.voice.channel != voice.channel:
                            await ctx.send(
                                embed=create_embed(
                                    'Please wait until other members are done listening to music'
                                )
                            )
                        else:
                            queue[str(voice)] = queue[str(voice)][:2]
                            queue[str(voice)][0]['loop'] = 'off'
                            with open('queue.json', 'w') as f:
                                json.dump(queue, f, indent=4)
                            voice.stop()
                    else:
                        queue.pop(str(voice))
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
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
        usage='`.play [url or song name]`'
    )
    async def play(self, ctx, *, url):
        await ctx.channel.purge(limit=1)
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
            with open('queue.json', 'r') as f:
                queue = json.load(f)
            if voice != None:
                if voice.channel != channel:
                    if len(voice.channel.members) == 1:
                        info = get_video_info(url)
                        queue.pop(str(voice))
                        await voice.move_to(channel)
                        queue[str(voice)] = [
                            {
                                'loop': 'off',
                                "text_channel": str(text_channel.id),
                                "volume": 0.5
                            },
                        ]
                        queue[str(voice)].append(
                            {
                                'url': info[2],
                                'title': info[1]
                            }
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        self.play_song(voice)
                    elif voice.is_playing() or voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                'Please wait until other members are done listening to music'
                            )
                        )
                    else:
                        info = get_video_info(url)
                        queue.pop(str(voice.channel.id))
                        await voice.move_to(channel)
                        queue[str(voice)] = [
                            {
                                'loop': 'off',
                                "text_channel": str(text_channel.id),
                                "volume": 0.5
                            },
                        ]
                        queue[str(voice)].append(
                            {
                                'url': info[2],
                                'title': info[1]
                            }
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        self.play_song(voice)
                else:
                    if voice.is_playing() or voice.is_paused():
                        info = get_video_info(url)
                        queue[str(voice)].append(
                            {
                                'url': info[2],
                                'title': info[1]
                            }
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await ctx.send(
                            embed=create_embed(
                                f'Song [{info[1]}]({info[2]}) added to queue'
                            )
                        )
                    else:
                        info = get_video_info(url)
                        queue[str(voice)].append(
                            {
                                'url': info[2],
                                'title': info[1]
                            }
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        self.play_song(voice)

            else:
                voice = await channel.connect(reconnect=True)
                info = get_video_info(url)
                queue[str(voice)] = [
                    {
                        'loop': 'off',
                        "text_channel": str(text_channel.id),
                        "volume": 0.5
                    },
                ]
                queue[str(voice)].append(
                    {
                        'url': info[2],
                        'title': info[1]
                    }
                )
                with open('queue.json', 'w') as f:
                    json.dump(queue, f, indent=4)
                self.play_song(voice)

    @commands.command(
        name='pause',
        aliases=['pau', 'pa'],
        description='Pauses the music',
        usage='`.pause`'
    )
    async def pause(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
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
        usage='`.resume`'
    )
    async def resume(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
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
        usage='`.stop`'
    )
    async def stop(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
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
                        with open('queue.json', 'r') as f:
                            queue = json.load(f)
                        queue[str(voice)] = queue[str(voice)][:2]
                        queue[str(voice)][0]['loop'] = 'off'
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await ctx.send(
                            embed=create_embed(
                                'Stopped playing music'
                            )
                        )
                        voice.stop()
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
        description='Skip to a song in the music queue',
        usage='`.skip [position]`'
    )
    async def skip(self, ctx, pos: int = 1):
        await ctx.channel.purge(limit=1)
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
                    with open('queue.json', 'r') as f:
                        queue = json.load(f)
                    info = queue[str(voice)][1]
                    if queue[str(voice)][0]['loop'] == 'one':
                        queue[str(voice)].pop(1)
                    await ctx.send(
                        embed=create_embed(
                            f'Skipped [{info["title"]}]({info["url"]})'
                        )
                    )
                    if queue[str(voice)][0]['loop'] == 'all':
                        for i in range(pos-1):
                            queue[str(voice)].append(queue[str(voice)].pop(1))
                    else:
                        for i in range(pos-1):
                            queue[str(voice)].pop(1)
                    with open('queue.json', 'w') as f:
                        json.dump(queue, f, indent=4)
                    voice.stop()
            else:
                await ctx.send(
                    embed=create_embed(
                        'Bot was not connected to any voice channel'
                    )
                )

    @commands.command(
        name='volume',
        description='Changes the volume (max=100)',
        aliases=['vol', ]
    )
    async def volume(self, ctx, volume: int):
        await ctx.channel.purge(limit=1)
        if ctx.voice_client == None:
            await ctx.send(
                embed=create_embed(
                    'Bot was not connected to any voice channel'
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
            if voice.channel != channel:
                await ctx.send(
                    embed=create_embed(
                        'Please wait until other members are done listening to music'
                    )
                )
            else:
                with open('queue.json', 'r') as f:
                    queue = json.load(f)
                queue[str(voice)][0]['volume'] = volume/200
                with open('queue.json', 'w') as f:
                    json.dump(queue, f, indent=4)
                voice.source.volume = volume/200
                await ctx.send(
                    embed=create_embed(
                        f'Music volume changed to {volume}'
                    )
                )

    @commands.command(
        name='queue',
        aliases=['q', ],
        description='Display your current music queue',
        usage='`.queue`'
    )
    async def queue(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
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
                    with open('queue.json', 'r') as f:
                        queue = json.load(f)
                    if len(queue[str(voice)]) == 1:
                        await ctx.send(
                            embed=create_embed(
                                'The music queue is empty'
                            )
                        )
                    else:
                        info = queue[str(voice)][1]
                        output = f'**Now playing**: [{info["title"]}]({info["url"]})\n'
                        if len(queue[str(voice)]) > 2:
                            counter = 1
                            for song in queue[str(voice)][2:]:
                                output += f'{counter}. [{song["title"]}]({song["url"]})\n'
                                counter += 1
                        embed = discord.Embed(
                            color=discord.Color.orange(),
                            description=output,
                            timestamp=ctx.message.created_at
                        )
                        embed.set_author(
                            name=f'Music queue for {ctx.author.voice.channel}'
                        )
                        embed.set_footer(
                            text=f'Repeat: {queue[str(voice)][0]["loop"]} | Volume: {queue[str(voice)][0]["volume"]*200}'
                        )
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
        usage='`.dequeue [song position in music queue]`'
    )
    async def dequeue(self, ctx, position: int, arg=None):
        await ctx.channel.purge(limit=1)
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
                    with open('queue.json', 'r') as f:
                        queue = json.load(f)
                    if 1 <= position <= len(queue[str(voice)])-2:
                        info = queue[str(voice)][position+1]
                        queue[str(voice)].pop(position+1)
                        await ctx.send(
                            embed=create_embed(
                                f'Song [{info["title"]}]({info["url"]}) removed from music queue'
                            )
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                    else:
                        await ctx.send(
                            embed=create_embed(
                                f'The music queue have **{len(queue[str(voice)])-2}** songs, but you specified more than that!'
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
        usage='`.loop [all/one/off]`'
    )
    async def loop(self, ctx, arg=None):
        await ctx.channel.purge(limit=1)
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
                    with open('queue.json', 'r') as f:
                        queue = json.load(f)
                    if arg == None or arg == 'all':
                        queue[str(voice)][0]['loop'] = 'all'
                        await ctx.send(
                            embed=create_embed(
                                'Repeating all songs in the music queue'
                            )
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                    elif arg == 'one':
                        queue[str(voice)][0]['loop'] = 'one'
                        await ctx.send(
                            embed=create_embed(
                                'Repeating the current song in the music queue'
                            )
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                    elif arg == 'off':
                        queue[str(voice)][0]['loop'] = 'off'
                        await ctx.send(
                            embed=create_embed(
                                'Repeating song is now off'
                            )
                        )
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
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

    @commands.group(
        invoke_without_command=True,
        name='playlist',
        aliases=['pl', 'plist'],
        description='Access playlist features',
        usage='`.playlist [option]`'
    )
    async def playlist(self, ctx):
        await ctx.channel.purge(limit=1)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        if len(playlist[str(ctx.guild.id)].keys()) == 0:
            await ctx.send(
                embed=create_embed(
                    'There is no playlist created in this guild'
                )
            )
        else:
            output = ''
            counter = 1
            for name in playlist[str(ctx.guild.id)].keys():
                output += f'{counter}. {name}\n'
                counter += 1
            embed = discord.Embed(
                color=discord.Color.orange(),
                description=output
            )
            embed.set_author(
                name=f'Playlists in {ctx.guild.name}:'
            )
            await ctx.send(
                embed=embed
            )

    @playlist.command(
        name='play',
        description='Add the playlist to queue and start playing',
        usage='`.playlist play [playlist name]`',
        aliases=['p', ]
    )
    async def playlist_play(self, ctx, name: str):
        await ctx.channel.purge(limit=1)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        if ctx.author.voice == None:
            await ctx.send(
                embed=create_embed(
                    'You must be connected to a voice channel to use this command'
                )
            )
        elif name not in playlist[str(ctx.guild.id)]:
            await ctx.send(
                embed=create_embed(
                    f'Playlist **{name}** not found'
                )
            )
        else:
            text_channel = ctx.channel
            channel = ctx.author.voice.channel
            voice = ctx.voice_client
            with open('queue.json', 'r') as f:
                queue = json.load(f)
            if voice != None:
                if voice.channel != channel:
                    if len(voice.channel.members) == 1:
                        queue.pop(str(voice))
                        await voice.move_to(channel)
                        queue[str(voice)] = [
                            {
                                'loop': 'off',
                                "text_channel": str(text_channel.id),
                                "volume": 0.5
                            },
                        ]
                        for song in playlist[str(ctx.guild.id)][name]:
                            queue[str(voice)].append(song)
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await ctx.send(
                            embed=create_embed(
                                f'Playlist **{name}** added to queue'
                            )
                        )
                        self.play_song(voice)
                    elif voice.is_playing() or voice.is_paused():
                        await ctx.send(
                            embed=create_embed(
                                'Please wait until other members are done listening to music'
                            )
                        )
                    else:
                        queue.pop(str(voice))
                        await voice.move_to(channel)
                        queue[str(voice)] = [
                            {
                                'loop': 'off',
                                "text_channel": str(text_channel.id),
                                "volume": 0.5
                            },
                        ]
                        for song in playlist[str(ctx.guild.id)][name]:
                            queue[str(voice)].append(song)
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await ctx.send(
                            embed=create_embed(
                                f'Playlist **{name}** added to queue'
                            )
                        )
                        self.play_song(voice)
                else:
                    if voice.is_playing() or voice.is_paused():
                        for song in playlist[str(ctx.guild.id)][name]:
                            queue[str(voice)].append(song)
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await ctx.send(
                            embed=create_embed(
                                f'Playlist **{name}** added to queue'
                            )
                        )
                    else:
                        for song in playlist[str(ctx.guild.id)][name]:
                            queue[str(voice)].append(song)
                        with open('queue.json', 'w') as f:
                            json.dump(queue, f, indent=4)
                        await ctx.send(
                            embed=create_embed(
                                f'Playlist **{name}** added to queue'
                            )
                        )
                        self.play_song(voice)

            else:
                voice = await channel.connect(reconnect=True)
                queue[str(voice)] = [
                    {
                        'loop': 'off',
                        "text_channel": str(text_channel.id),
                        "volume": 0.5
                    },
                ]
                for song in playlist[str(ctx.guild.id)][name]:
                    queue[str(voice)].append(song)
                with open('queue.json', 'w') as f:
                    json.dump(queue, f, indent=4)
                await ctx.send(
                    embed=create_embed(
                        f'Playlist **{name}** added to queue'
                    )
                )
                self.play_song(voice)

    @playlist.command(
        name='create',
        description='Create a playlist',
        usage='`.playlist create [playlist name]`'
    )
    async def create(self, ctx, name: str, arg=None):
        await ctx.channel.purge(limit=1)
        if arg == None:
            with open('playlist.json', 'r') as f:
                playlist = json.load(f)
            if name in playlist[str(ctx.guild.id)]:
                await ctx.send(
                    embed=create_embed(
                        'A playlist with the same name already exist'
                    )
                )
            else:
                playlist[str(ctx.guild.id)][name] = []
                with open('playlist.json', 'w') as f:
                    json.dump(playlist, f, indent=4)
                await ctx.send(
                    embed=create_embed(
                        f'Playlist **{name}** created'
                    )
                )
        else:
            await ctx.send(
                embed=create_embed(
                    'Your playlist name can only contain **1** word'
                )
            )

    @playlist.command(
        name='delete',
        description='Delete an existing playlist',
        usage='`.delete [playlist name]`',
        aliases=['del', ]
    )
    async def delete(self, ctx, name: str):
        await ctx.channel.purge(limit=1)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        if name not in playlist[str(ctx.guild.id)]:
            await ctx.send(
                embed=create_embed(
                    f'Playlist **{name}** not found'
                )
            )
        else:
            playlist[str(ctx.guild.id)].pop(name)
            with open('playlist.json', 'w') as f:
                json.dump(playlist, f, indent=4)
            await ctx.send(
                embed=create_embed(
                    f'Playlist **{name}** deleted'
                )
            )

    @playlist.command(
        name='add',
        description='Add a song to an existing playlist',
        usage='`.playlist add [playlist name] [song name or url]`'
    )
    async def add(self, ctx, name: str, *, url: str):
        await ctx.channel.purge(limit=1)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        if name in playlist[str(ctx.guild.id)]:
            info = get_video_info(url)
            playlist[str(ctx.guild.id)][name].append(
                {
                    'url': info[2],
                    'title': info[1]
                }
            )
            with open('playlist.json', 'w') as f:
                json.dump(playlist, f, indent=4)
            await ctx.send(
                embed=create_embed(
                    f'Song [{info[1]}]({info[2]}) added to **{name}**'
                )
            )
        else:
            await ctx.send(
                embed=create_embed(
                    f'Playlist **{name}** not found'
                )
            )

    @playlist.command(
        name='remove',
        description='Remove a song from an existing playlist',
        usage='`.playlist remove [playlist name] [song number]`',
        aliases=['rm']
    )
    async def remove(self, ctx, name: str, position: int):
        await ctx.channel.purge(limit=1)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        if name in playlist[str(ctx.guild.id)]:
            if 1 <= position <= len(playlist[str(ctx.guild.id)]):
                info = playlist[str(ctx.guild.id)][name].pop(position-1)
                with open('playlist.json', 'w') as f:
                    json.dump(playlist, f, indent=4)
                await ctx.send(
                    embed=create_embed(
                        f'Song [{info["title"]}]({info["url"]}) deleted from **{name}**'
                    )
                )
            else:
                await ctx.send(
                    embed=create_embed(
                        f'The playlist have **{len(playlist[str(ctx.guild.id)])}** songs, but you specified more than that!'
                    )
                )
        else:
            await ctx.send(
                embed=create_embed(
                    f'Playlist **{name}** not found'
                )
            )

    @playlist.command(
        name='list',
        description='List the songs in an existing playlist',
        usage='`.playlist list [playlist name] [page]`',
        aliases=['ls']
    )
    async def _list(self, ctx, name: str, page: int = 1):
        await ctx.channel.purge(limit=1)
        with open('playlist.json', 'r') as f:
            playlist = json.load(f)
        if name in playlist[str(ctx.guild.id)]:
            pages = math.ceil(len(playlist[str(ctx.guild.id)])/20)
            if 1 <= page < pages:
                output = ''
                counter = 1 + (page-1)*20
                for song in playlist[str(ctx.guild.id)][name][(page-1)*20:page*20]:
                    output += f'{counter}. [{song["title"]}]({song["url"]})\n'
                    counter += 1
                embed = discord.Embed(
                    color=discord.Color.orange(),
                    description=output
                )
                embed.set_author(
                    name=f'Playlist {name}'
                )
                embed.set_footer(
                    text=f'Page {page} of {pages} | use .playlist list [playlist name] [page]'
                )
                await ctx.send(
                    embed=embed
                )
            elif page == pages:
                output = ''
                counter = 1 + (page-1)*20
                for song in playlist[str(ctx.guild.id)][name][(page-1)*20::]:
                    output += f'{counter}. [{song["title"]}]({song["url"]})\n'
                    counter += 1
                embed = discord.Embed(
                    color=discord.Color.orange(),
                    description=output
                )
                embed.set_author(
                    name=f'Playlist {name}:'
                )
                embed.set_footer(
                    text=f'Page {page} of {pages} | use .playlist list [playlist name] [page]'
                )
                await ctx.send(
                    embed=embed
                )
            else:
                await ctx.send(
                    embed=create_embed(
                        'The page you specified does not exist'
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
