from datetime import datetime
from dataclasses import dataclass
from typing import cast

import discord
from discord.ext import commands
from discord.ext.commands import Context

from src.util.blacklist import blacklist
from src.util.snipe import *
from src.util import util
from src import config as conf

@dataclass
class MessageHistory:
    deleted: datetime
    states: list[discord.Message]

class Sniper(commands.Cog, name="Snipe"):
    def __init__(self, bot):
        self.bot = bot

        # Maps channel : list of history of deleted messages
        self._deleted: dict[int, list[MessageHistory]] = {}

        # Maps message id : history of edited message
        self._message_history: dict[int, list[discord.Message]] = {}

    @commands.hybrid_command(with_app_command=True)
    async def snipe(self, ctx: Context, number: int = 0):
        if ctx.channel.id not in self._deleted:
            return await ctx.send("No message to snipe.")

        histories = self._deleted[ctx.channel.id]
        index = abs(number)

        if index >= len(histories):
            return await ctx.send(f"The bot currently has only {len(histories)} deleted messages stored "
                                  "with index 0 being the most recently deleted message")

        history = histories[-1 - index]

        message = history.states[-1]
        msg_content = message.content.lower()
        if msg_content in blacklist:
            return await ctx.send( "The requested deleted message contained a word that we do not allow, sorry! "
                                           f"(offender {message.author.mention}, reason {blacklist & msg_content})")

        messages = into_embeds_chunks(history.states)

        await ctx.send(f"Deleted <t:{ int(history.deleted.timestamp()) }:R>", embeds=messages.pop(0))

        for msg_embeds in messages:
            await ctx.send(embeds=msg_embeds)

    @commands.command()
    async def history(self, ctx: Context):
        if not ctx.message.reference:
            return await ctx.send("No message is replied to")

        if ctx.message.reference.message_id not in self._message_history:
            return await ctx.send("Message either never edited or too old")

        history = self._message_history[ctx.message.reference.message_id]

        reply = ctx.message
        for embeds in into_embeds_chunks(history):
            reply = await reply.reply(embeds=embeds)

    @commands.hybrid_command()
    @commands.has_role(conf.staff_role)
    async def clear(self, ctx: Context):
        self._deleted[ctx.channel.id] = []

        await ctx.send("Cleared snipe buffer")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        c_id = message.channel.id
        if c_id not in self._deleted:
            self._deleted[c_id] = []

        history = []
        if message.id in self._message_history:
            history = self._message_history.pop(message.id)

        history.append(message)

        buffer = self._deleted[c_id]
        buffer.append(MessageHistory(datetime.now(), history))
        buffer = buffer[-conf.max_del_msgs:]

    @commands.Cog.listener()
    async def on_message_edit(self, old: discord.Message, _):
        if old.id not in self._message_history:
            self._message_history[old.id] = []

        self._message_history[old.id].append(old)

        now = datetime.utcnow()
        self._message_history = {
            k: v for k, v in self._message_history.items()
            if timestamp(v[-1]).replace(tzinfo=None) > now - conf.max_edit_msg_age
        }

async def setup(bot):
    await bot.add_cog(Sniper(bot))
