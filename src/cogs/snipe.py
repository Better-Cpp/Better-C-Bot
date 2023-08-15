from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict, deque

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context

from src.util.snipe import *
from src import config as conf

@dataclass
class DeletedHistory:
    deleted: datetime
    states: list[discord.Message]

class Sniper(commands.Cog, name="Snipe"):
    def __init__(self, bot):
        self.bot = bot

        # Maps channel : list of history of deleted messages
        self._deleted: dict[int, deque[DeletedHistory]] = defaultdict(lambda: deque(maxlen=conf.max_del_msgs))

        # Maps message id : history of edited message
        self._message_history: dict[int, list[discord.Message]] = defaultdict(list)

        self.clean_edits.start()

    @commands.hybrid_command(with_app_command=True)
    async def snipe(self, ctx: Context, number: int = 0):
        if ctx.channel.id not in self._deleted:
            return await ctx.send("No message to snipe.")

        deleted_msgs = self._deleted[ctx.channel.id]
        index = abs(number)

        if index >= len(deleted_msgs):
            return await ctx.send(f"The bot currently has only {len(deleted_msgs)} deleted messages stored "
                                  "with index 0 being the most recently deleted message")

        history = deleted_msgs[-1 - index]
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
        del self._deleted[ctx.channel.id]

        await ctx.send("Cleared snipe buffer")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        history = []
        if message.id in self._message_history:
            history = self._message_history.pop(message.id)

        history.append(message)

        self._deleted[message.channel.id].append(DeletedHistory(datetime.now(), history))

    @commands.Cog.listener()
    async def on_message_edit(self, old: discord.Message, _):
        self._message_history[old.id].append(old)

    @tasks.loop(minutes=5)
    async def clean_edits(self):
        now = datetime.utcnow()
        self._message_history = {
            k: v for k, v in self._message_history.items()
            if timestamp(v[-1]).replace(tzinfo=None) > now - conf.max_edit_msg_age
        }


async def setup(bot):
    await bot.add_cog(Sniper(bot))
