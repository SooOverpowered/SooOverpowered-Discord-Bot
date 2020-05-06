# Imports
import discord


# Create embed
def create_embed(text):
    embed = discord.Embed(
        description=text,
        color=discord.Color.orange()
    )
    return embed
