import asyncio
from discord.ext import commands, tasks

import datetime


class Filter(commands.Cog):
    """
    Filters out bad words
    """

    def __init__(self, bot):
        self.bot = bot
        self.badwords = set()
        self.__read_words()

    def __read_words(self):
        with open("badwords.txt") as file:
            for line in file:
                self.badwords.add(line.strip().lower())

    @commands.Cog.listener()
    async def on_message(self, msg):
        msg_content = msg.content.lower()
        for word in self.badwords:
            if word not in msg_content:
                continue
            await msg.delete()
            return await msg.channel.send(f"{msg.author.mention}, your message contained a word that we do not allow, sorry!")

def setup(bot):
    bot.add_cog(Filter(bot))
