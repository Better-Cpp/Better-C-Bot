from discord.ext import commands
import discord

from src import config as conf
from src.util import permissions


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == self.bot.user.id:
            return

        if any([role == conf.ping_role for role in msg.raw_role_mentions]):
            if not permissions.has_role(msg.author, conf.ping_role):
                await msg.author.add_roles(permissions.get_role(conf.ping_role, msg.guild)),
                await msg.reply(f"<@&{conf.ping_role}> please welcome {msg.author.mention}")
                

async def setup(bot):
    await bot.add_cog(Ping(bot))