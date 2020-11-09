"""
Verona compiler cog
"""
import datetime

import discord
from discord.ext import commands
from ..backend import verona


class Verona(commands.Cog, name="Verona"):
    """
    Commands made for Verona
    Don't abuse these.
    """

    def __init__(self, bot):
        self.bot = bot

    def sanitize(self, code: str) -> str:
        begin_strip = ["```verona", "```"]
        end_strip = ["```"]
        for each in begin_strip:
            if code.startswith(each):
                code = code[len(each):]

        for each in end_strip:
            if code.endswith(each):
                code = code[:len(code) - len(each)]

        return code

    @commands.command()
    async def verona(self, ctx, *, code: str):
        code = self.sanitize(code)
        num = verona.get_num_and_inc()
        verona.set_code(num, code)
        success, result = await verona.run_container(num)

        if "error generated" in result:
            success = False

        embed = discord.Embed(title=f"Success: {success}", colour=discord.Colour(0xFF0000 if not success else 0x00FF00),
                              description=f"Output:\n```\n{result}```", timestamp=datetime.datetime.utcnow())

        embed.set_footer(text=str(ctx.message.author),
                         icon_url=ctx.message.author.avatar_url)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Verona(bot))
