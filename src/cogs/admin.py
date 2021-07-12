import io
import json
import textwrap
import traceback
from contextlib import redirect_stdout

from discord.ext import commands
import discord


class Administration(commands.Cog, name="Administration"):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

        with open("src/backend/database.json", "r") as file:
            self.file = json.load(file)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        content = (
            content.replace("```", "\n```") # Prevents the last line being cut off
            .replace("'", "\'") # ' -> \'
            .replace('"', '\"') # " -> \"
            .strip() # Remove trailing whitespace
        )

        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        """
        ReLoads all cogs.
        """
        # Atm the only person in the permitted array is the owner, so instead of doing
        # The below, we'll just use the built-in is_owner() check since it's also easier to test these

        # if ctx.message.author.id not in self.file["permitted"]:
        #     return await ctx.send("You do not have authorization to use this command")

        for cog in self.bot.user_cogs:
            self.bot.reload_extension(cog)

        await ctx.send(
            "Updated cogs:\n```\n{}\n```".format("\n".join(self.bot.user_cogs))
        )

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        """
        Evaluates some code
        """
        # if ctx.message.author.id not in self.file["permitted"]:
        #     return await ctx.send("You do not have authorization to use this command")

        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "_": self._last_result,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f"```py\n{value}\n```")
            else:
                self._last_result = ret
                await ctx.send(f"```py\n{value}{ret}\n```")


def setup(bot):
    bot.add_cog(Administration(bot))
