# Imports
import discord
import youtube_dl
import os

a = {'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192'
}]}


# Create embed
def create_embed(text):
    embed = discord.Embed(
        description=text,
        color=discord.Color.orange()
    )
    return embed


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
