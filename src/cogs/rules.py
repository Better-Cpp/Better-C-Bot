import io
import json
import re

from discord.ext import commands
import discord


class RulesEnforcer(commands.Cog, name="Rules"):
    def __init__(self, bot):
        self.bot = bot

        # Maps channel : discord.Message
        self._deleted = {}
        
        with open("src/backend/database.json", 'r') as file:
            self.file = json.load(file)

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

    async def _update_rules(self):
        channel = self.bot.get_channel(self.file["rules_channel"])
        messages = await channel.history(limit=1000000, oldest_first=True).flatten()
        self._rules = {}

        for message in messages:
            content = message.clean_content
            matches = re.finditer(r"(\d+) - (.+?)(?=[\n ]+\d+? - |$)", content, flags=re.DOTALL)

            for rule in matches:
                if rule[0] == "":
                    continue

                number = rule[1]
                text = rule[2]

                if self._rules.get(number) is None:
                    self._rules[number] = text

    @commands.command()
    async def update_rules(self, ctx):
        if ctx.message.author.id not in self.file["permitted"]:
            return await ctx.send("You do not have authorization to use this command")

        await self._update_rules()
        await ctx.send("The rules were updated successully")
    
def setup(bot):
    bot.add_cog(RulesEnforcer(bot))
