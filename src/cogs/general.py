import io
# import json

from discord.ext import commands
import discord


class General(commands.Cog, name="Rules"):
    def __init__(self, bot):
        self.bot = bot
        
        # with open("src/backend/database.json", 'r') as file:
        #     self.file = json.load(file)

    @commands.command()
    async def lmgtfy(self, ctx, *, term):
        await ctx.send(f"https://letmegooglethat.com/?q={term.replace(' ', '+')}")

def setup(bot):
    bot.add_cog(General(bot))
