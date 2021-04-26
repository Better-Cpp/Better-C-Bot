import io
import json
import re
import time

from collections import deque
from discord.ext import commands
import discord


class RulesEnforcer(commands.Cog, name="Rules"):
    with open("src/backend/database.json", 'r') as f:
        file = json.load(f)

    def __init__(self, bot):
        self.bot = bot

        # Maps channel : discord.Message
        self._deleted = {}

        self._recent_joins = deque()

        self.massjoin_detect = True

        with open("src/backend/database.json", 'r') as f: # Seems to be unavoidable
            self.file = json.load(f)
        
        bot.loop.create_task(self._update_rules())

    @commands.command()
    async def rule(self, ctx, number):
        """Display a rule"""
        if self._rules.get(number) is None:
            return await ctx.send(f"Invalid rule number: `{discord.utils.escape_mentions(number)}`")
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
    async def on_member_join(self, member):
        self._recent_joins.append([member, time.time()])
        recent_joins = self._recent_joins.copy()

        for join in self._recent_joins:
            secs_since_join = time.time() - join[1]
            if secs_since_join >= self.file["massjoin_window"]:
                recent_joins.popleft()

        self._recent_joins = recent_joins.copy()
        join_amount = len(self._recent_joins)

        if join_amount >= self.file["massjoin_amount"] and self.massjoin_detect == True:
            for member in member.guild.get_role(self.file["staff_role"]).members:
                    count = 0

                    if member.status == discord.Status.online and count < 2:
                        dm_channel = member.dm_channel
                        if dm_channel == None:
                            dm_channel = await member.create_dm()

                        await dm_channel.send("Mass member join detected!")
                        count = count+1
                
    @commands.command()
    @commands.has_role(file["staff_role"])
    async def toggle_massjoin_detection(self, ctx):
        self.massjoin_detect = not self.massjoin_detect
        if self.massjoin_detect:
            await ctx.send("Massjoin detection is now on")
        else:
            await ctx.send("Massjoin detection is now off")

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

    @commands.command(hidden=True)
    @commands.has_role(file["staff_role"])
    async def update_rules(self, ctx):
        await self._update_rules()
        await ctx.send("The rules were updated successully")
    
def setup(bot):
    bot.add_cog(RulesEnforcer(bot))

