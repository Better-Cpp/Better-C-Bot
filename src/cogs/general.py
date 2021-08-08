import io
import urllib.parse
# import json

from discord.ext import commands
import discord


class General(commands.Cog, name="General"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def lmgtfy(self, ctx, *, term):
        await ctx.send(f"https://letmegooglethat.com/?q={urllib.parse.quote(term)}")

def setup(bot):
    bot.add_cog(General(bot))
