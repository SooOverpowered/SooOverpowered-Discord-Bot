# Imports
import discord
from helper import *
from parameters import *
from discord.ext import commands
from discord.utils import get


class HelpMenu(commands.Cog, name='Help'):
    def __init__(self, client):
        self.client = client

    @commands.group(
        name='Help',
        description='The help command',
        invoke_without_command=True,
        aliases=['h', 'help']
    )
    async def help(self, ctx):
        await ctx.channel.purge(limit=1)
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                color=discord.Color.orange(),
                description='Use `.help [module name]` for more information',
                timestamp=ctx.message.created_at
            )
            embed.set_author(
                name='Help',
            )
            embed.add_field(
                name='**Administration**',
                value='Managing the server',
                inline=False
            )
            embed.add_field(
                name='**Music**',
                value='The music player',
                inline=False
            )
            embed.set_footer(
                text='Server prefix: ' +
                ' and '.join(await self.client.get_prefix(ctx.message))
            )
            await ctx.send(embed=embed)

    @help.command(
        name='Administration',
        aliases=['admin', 'administration', ],
        description='Show list of administrative commands',
    )
    async def Administration(self, ctx):
        await ctx.channel.purge(limit=1)
        cog = self.client.get_cog('Administration')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of administrative commands**\n\nUse `.help [command name]` for more information',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name=cog.qualified_name,
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        for command in commands:
            if command.aliases != []:
                alias_list = command.aliases
                temp_alias_list = []
                for i in range(len(alias_list)):
                    temp_alias_list.append(f'.'+alias_list[i])
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(temp_alias_list)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                    inline=False
                )
        await ctx.send(embed=embed)

    @help.command(
        name='ping',
        description='How to use ping command'
    )
    async def help_ping(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Shows you the WebSocket heartbeat or latency of the Bot',
            timestamp=ctx.message.created_at,
        )
        embed.set_author(
            name='Ping'
        )
        embed.add_field(
            name='Usage',
            value='`.ping`: Show the bot latency',
            inline=False
        )
        embed.add_field(
            name='Examples',
            value='`.ping`',
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='clear',
        description='How to use the clear command',
        aliases=['purge']
    )
    async def help_clear(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Clear command, clear a specific number of command (defaults to 5)\nYou must have the manage message permission to use this command',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Clear'
        )
        embed.add_field(
            name='Usage',
            value='`.clear [number of messages]`: clear a number of messages',
            inline=False
        )
        embed.add_field(
            name='Examples',
            value='`.clear`: deletes the latest 5 messages\n`.clear 10`: deletes the latest 10 messages',
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='nuke',
        description='How to use the nuke command'
    )
    async def help_nuke(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Nuke command, deletes all message in a channel',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Nuke'
        )
        embed.add_field(
            name='Usage',
            value='`.nuke`: nukes the channel, deletes all messages',
            inline=False
        )
        embed.add_field(
            name='Example',
            value='`.nuke`',
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='kick',
        description='How to use the kick command',
    )
    async def help_kick(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Kick command, kicks a member out of the server',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Kick'
        )
        embed.add_field(
            name='Usage',
            value='`.kick [member]`: kicks a member out of the server',
            inline=False
        )
        embed.add_field(
            name='Example',
            value='`.kick @abc`: abc kicked from server',
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='ban',
        description='How to use the ban command',
    )
    async def help_ban(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Ban command, bans a member out of the server',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Ban'
        )
        embed.add_field(
            name='Usage',
            value='`.ban [member]`: bans a member out of the server',
            inline=False
        )
        embed.add_field(
            name='Example',
            value='`.ban @abc`: abc banned from server',
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='userinfo',
        description='How to use the userinfo command',
        aliases=['info', ]
    )
    async def help_userinfo(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Userinfo command, shows the info of a member',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Userinfo'
        )
        embed.add_field(
            name='Usage',
            value='`.userinfo [member]`: shows the info of the member',
            inline=False
        )
        embed.add_field(
            name='Example',
            value="`.userinfo`: shows your membership info\n`.userinfo @abc`: shows abc's membership info",
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='setprefix',
        description='How to use the setprefix command',
    )
    async def help_setprefix(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Setprefix command, sets the custom prefix for the server',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Setprefix'
        )
        embed.add_field(
            name='Usage',
            value='`.setprefix [new prefix]`: sets the custom prefix for the server',
            inline=False
        )
        embed.add_field(
            name='Example',
            value="`.setprefix ?`: changes the command prefix to '?'",
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='Music',
        aliases=['music', ],
        description='Show list of music commands',
    )
    async def Music(self, ctx):
        await ctx.channel.purge(limit=1)
        cog = self.client.get_cog('Music')
        commands = cog.get_commands()
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of music commands**\n\nUse `.help [command name]` for more information',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name=cog.qualified_name
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        for command in commands:
            if command.aliases != []:
                alias_list = command.aliases
                temp_alias_list = []
                for i in range(len(alias_list)):
                    temp_alias_list.append(f'.'+alias_list[i])
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(temp_alias_list)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                    inline=False
                )
        await ctx.send(embed=embed)

    @help.command(
        name='join',
        description='How to use the join command',
        aliases=['j', 'connect']
    )
    async def help_join(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Setprefix command, sets the custom prefix for the server',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Join'
        )
        embed.add_field(
            name='Usage',
            value='`.join`: connects to the voice channel that you are inside',
            inline=False
        )
        embed.add_field(
            name='Example',
            value="`.join`: Bot connected to voice channel",
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.command(
        name='leave',
        description='How to use the leave command',
        aliases=['dc', 'disconnect']
    )
    async def help_leave(self, ctx):
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='Leave command, sets the custom prefix for the server',
            timestamp=ctx.message.created_at
        )
        embed.set_author(
            name='Leave'
        )
        embed.add_field(
            name='Usage',
            value='`.leave`: disconnect from the current voice channel',
            inline=False
        )
        embed.add_field(
            name='Example',
            value="`.leave`: Bot disconnected from voice channel",
            inline=False
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        await ctx.send(
            embed=embed
        )

    @help.group(
        name='playlist',
        invoke_without_command=True,
        aliases=['pl', 'plist']
    )
    async def help_playlist(self, ctx):
        await ctx.channel.purge(limit=1)
        cog = self.client.get_cog('Music')
        commands = discord.utils.get(cog.get_commands(), name='playlist')
        embed = discord.Embed(
            color=discord.Color.orange(),
            description='**List of playlist options**\n\nUse `.help playlist [option]` for more information',
            timestamp=ctx.message.created_at
        )
        embed.set_footer(
            text='Server prefix: ' +
            ' and '.join(await self.client.get_prefix(ctx.message))
        )
        embed.add_field(
            name='playlist',
            value='Description: show list of available playlists in the server\nUsage: `.playlist`\nAliases: `.pl, .plist`'
        )
        for command in commands.commands:
            if command.aliases != []:
                alias_list = command.aliases
                temp_alias_list = []
                for i in range(len(alias_list)):
                    temp_alias_list.append(f'.'+alias_list[i])
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}\nAliases: `{", ".join(temp_alias_list)}`',
                    inline=False
                )
            else:
                embed.add_field(
                    name=command.qualified_name,
                    value=f'Description: {command.description}\nUsage: {command.usage}',
                    inline=False
                )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(HelpMenu(client))
