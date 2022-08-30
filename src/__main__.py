import aiohttp
import discord
from discord.ext import commands
from src.util.blacklist import blacklist

def prefix(bot, message):
    return [".", "++"]


bot = commands.Bot(prefix, case_insensitive=True,
                   intents=discord.Intents.all())


@bot.event
async def on_ready():
    bot.user_cogs = [
        # "src.cogs.verona",
        "src.cogs.ping",
        "src.cogs.help_channels",
        "src.cogs.cpp",
        "src.cogs.help",
        "src.cogs.qt",
        "src.cogs.rules",
        "src.cogs.challenges",
        "src.cogs.stats",
        "src.cogs.rust",
        "src.cogs.auto_mod",
        "src.cogs.general",
        "src.cogs.admin",
        "src.cogs.error_handler",
    ]
    for cog in bot.user_cogs:
        print(f"Loading {cog}...")
        await bot.load_extension(cog)
        print(f"Loaded {cog}!")

    bot.http_client = aiohttp.ClientSession()

    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print(discord.utils.oauth_url(bot.user.id))
    
    blacklist.load("badwords.txt")
# @bot.event
# async def on_member_join(member):
#     channel = discord.utils.get(
#         member.guild.text_channels, id=583251191866195969)
#     rules_channel = discord.utils.get(
#         member.guild.text_channels, id=583301260006916099)
#     if channel is None:
#         return print("Couldn't find arrival channel")
#     if rules_channel is None:
#         return print("Couldn't find rules channel")
#     await channel.send(f"{member.mention}, welcome to Better C++. Please read {rules_channel.mention} for instructions on how to get access to the rest of the channels.\nCreated at: {member.created_at.isoformat(' ', 'seconds')}")


with open("token.txt", 'r') as file:
    TOKEN = file.read().strip()

bot.run(TOKEN)
