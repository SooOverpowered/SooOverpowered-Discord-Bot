# Imports
import discord
import youtube_dl
import os


# Create embed
def create_embed(text):
    embed = discord.Embed(
        description=text,
        color=discord.Color.orange()
    )
    return embed
