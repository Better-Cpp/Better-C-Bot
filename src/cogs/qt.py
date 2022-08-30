from discord.ext import commands
import json
import discord

import os


class Qt(commands.Cog, name="Qt"):
    """Commands made for the Qt Reference
    Don't abuse these.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def qt(self, ctx, *, query):
        """
        Search for any Qt class
        """
        e = discord.Embed()
        description = []
        qt_hits = self.get_qt_hits()
        for key, url in qt_hits.items():
            if not query.lower() in key.lower():
                continue
            description.append(f"[`{key}`](https://doc.qt.io/qt-5/{url})")

        if not description:
            return await ctx.send('No results found.')

        e.title = "Search Results"
        e.description = "\n".join(description[:15])
        await ctx.send(embed=e)

    def get_qt_hits(self) -> dict:
        with open("src/backend/qt5.json", 'r') as file:
            return json.load(file)


async def setup(bot):
    await bot.add_cog(Qt(bot))
