import aiohttp
import datetime
from typing import Generator, List
import io
import discord
from discord.ext import commands
from lxml import etree

from cogs import cpp
from cogs import rules
from cogs import help
from cogs import qt

def prefix(bot, message):
    return [".", "!"]

bot = commands.Bot(prefix, case_insensitive=True)


@bot.event
async def on_ready():
    # await bot.user.edit(username="Better C++ Bot", avatar=open("/home/john/Downloads/c++.png", 'rb').read())
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(discord.utils.oauth_url(bot.user.id))



@bot.event
async def on_member_join(member):
    channel = discord.utils.get(
        member.guild.text_channels, id=583251191866195969)
    rules_channel = discord.utils.get(
        member.guild.text_channels, id=583301260006916099)
    if channel is None:
        return print("Couldn't find arrival channel")
    if rules_channel is None:
        return print("Couldn't find rules channel")
    await channel.send(f"{member.mention}, welcome to Better C++. Please read {rules_channel.mention} for instructions on how to get access to the rest of the channels.\nCreated at: {member.created_at.isoformat(' ', 'seconds')}")


@bot.command()
async def accept(ctx):
    if not ctx.channel.id == 583251191866195969:
        return
    await ctx.message.delete()
    await ctx.author.add_roles(
        discord.utils.get(ctx.guild.roles, id=583254844677160980)
    )
    await ctx.author.send(f"Welcome to Better C++.")

cpp.setup(bot)
help.setup(bot)
qt.setup(bot)
rules.setup(bot)
bot.run("NTgzMjI4MzgxNDc5NTY3Mzkw.XO5UWw.etuGsVBxp9UbUVZyPyB8xKYZLYw")
