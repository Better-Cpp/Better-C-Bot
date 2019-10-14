import io
import os
import sys
import json
import inspect
import textwrap
import importlib
import traceback
from contextlib import redirect_stdout

from discord.ext import commands
import discord


class RulesEnforcer(commands.Cog, name="Rules"):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command()
    async def rule(self, ctx, number):
        """Display a rule"""
        try:
            int(number)
        except ValueError:
            return await ctx.send(f"Invalid rule number: `{number}`")

        with open("backend/database.json") as file:
            j = json.load(file)

        await ctx.send(f"**Rule {number}**:\n{j['rules'][number]}")

    def has_role(self, id, user):
        return any([id == each.id for each in user.roles])

    @commands.command()
    async def mute(self, ctx, mention: discord.Member):
        if not self.has_role(583646707938623489, ctx.author):
            return await ctx.send("Only staff may use this command")

        role = discord.utils.get(ctx.guild.roles, name="muted")
        if role is None:
            role = await ctx.guild.create_role(name="muted")

        await mention.add_roles(role)
        await ctx.send(f"Muted {mention.mention}")

    @commands.command()
    async def setup(self, ctx, mention: discord.Member):
        if not self.has_role(583646707938623489, ctx.author):
            return await ctx.send("Only staff may use this command")

        role = discord.utils.get(ctx.guild.roles, name="muted")
        if role is None:
            role = await ctx.guild.create_role(name="muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

        await ctx.send("Server has been set up properly :)")

    @commands.command()
    async def unmute(self, ctx, mention: discord.Member):
        if not self.has_role(583646707938623489, ctx.author):
            return await ctx.send("Only staff may use this command")

        role = discord.utils.get(ctx.guild.roles, name="muted")
        if role is None:
            role = await ctx.guild.create_role(name="muted")

        await mention.remove_roles(role)
        await ctx.send(f"Unmuted {mention.mention}")

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    async def reload(self, ctx):
        def get_permitted():
            with open("backend/database.json", 'r') as file:
                return json.load(file)["permitted"]

        if ctx.message.author.id not in get_permitted():
            return await ctx.send("You do not have authorization to use this command")

        for cog in self.bot.user_cogs:
            self.bot.reload_extension(f"cogs/{cog}")

        await ctx.send("Updated cogs:\n```\n{}\n```".format('\n'.join(self.bot.user_cogs)))

    @commands.command()
    async def lmgtfy(self, ctx, *, term):
        await ctx.send(f"https://lmgtfy.com/?q={term.replace(' ', '+')}")

    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates code"""

        def get_permitted():
            with open("backend/database.json", 'r') as file:
                return json.load(file)["permitted"]

        if ctx.message.author.id not in get_permitted():
            return await ctx.send("You do not have authorization to use this command")

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(RulesEnforcer(bot))
