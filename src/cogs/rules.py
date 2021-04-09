import io
import json
import textwrap
import traceback
import re
from contextlib import redirect_stdout

from discord.ext import commands
import discord


class RulesEnforcer(commands.Cog, name="Rules"):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

        # Maps channel : discord.Message
        self._deleted = {}

        # Stores parsed rules as number : text
        # self._rules = {}
        
        bot.loop.create_task(self._update_rules())

    @commands.command()
    async def rule(self, ctx, number):
        """Display a rule"""
        if self._rules.get(number) is None:
            return await ctx.send(f"Invalid rule number: `{number}`")
        else:
            await ctx.send(f"**Rule {number}**:\n{self._rules[number]}")

    @commands.command()
    async def snipe(self, ctx):
        if ctx.channel not in self._deleted:
            return await ctx.send("No message to snipe.")

        message: discord.Message = self._deleted[ctx.channel]
        user = str(message.author)
        ts = message.created_at.isoformat(" ")
        content = message.content
        return await ctx.send(f"**{discord.utils.escape_markdown(discord.utils.escape_mentions(user))}** said on {ts} UTC:\n{content}")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self._deleted[message.channel] = message

    def has_role(self, id, user):
        return any([id == each.id for each in user.roles])

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def _update_rules(self):
        with open("src/backend/database.json") as file:
            j = json.load(file)
        
        channel = self.bot.get_channel(j["rules_channel"])
        messages = await channel.history(limit=1000000, oldest_first=True).flatten()
        self._rules = {}

        for message in messages:
            content = message.clean_content
            matches = re.finditer(r"(\d+) - (.+?)(?=[\n ]+\d+? - |$)", content, flags=re.DOTALL)

            for rule in matches:
                if rule[0] != "":
                    number = rule[1]
                    text = rule[2]

                    if self._rules.get(number) is None:
                        self._rules[number] = text

    @commands.command()
    async def update_rules(self, ctx):
        def get_permitted():
            with open("src/backend/database.json", 'r') as file:
                return json.load(file)["permitted"]

        if ctx.message.author.id not in get_permitted():
            return await ctx.send("You do not have authorization to use this command")

        await self._update_rules()
    
    @commands.command()
    async def reload(self, ctx):
        def get_permitted():
            with open("src/backend/database.json", 'r') as file:
                return json.load(file)["permitted"]

        if ctx.message.author.id not in get_permitted():
            return await ctx.send("You do not have authorization to use this command")

        for cog in self.bot.user_cogs:
            self.bot.reload_extension(cog)

        await ctx.send("Updated cogs:\n```\n{}\n```".format('\n'.join(self.bot.user_cogs)))

    @commands.command()
    async def lmgtfy(self, ctx, *, term):
        await ctx.send(f"https://letmegooglethat.com/?q={term.replace(' ', '+')}")

    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates code"""

        def get_permitted():
            with open("src/backend/database.json", 'r') as file:
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
