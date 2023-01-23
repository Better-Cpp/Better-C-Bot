import time
from datetime import datetime
from dataclasses import dataclass

import discord
from discord.ext import commands

from src.util.blacklist import blacklist
from src.util import util
from src import config as conf

@dataclass
class Entry:
    time: float
    msg: str

class Sniper(commands.Cog, name="Snipe"):
    def __init__(self, bot):
        self.bot = bot

        # Maps channel : list of history of deleted messages
        self._deleted = {}

        # Maps message id : history of edited message
        self._message_history = {}

    def _change_msg(self, entry, status):
        user = str(entry.msg.author)
        ts = datetime.fromtimestamp(entry.time).isoformat(" ", "seconds")
        content = entry.msg.clean_content

        for attachment in entry.msg.attachments:
            content += "\n" + attachment.proxy_url
            content += "\n" + attachment.url

        return f"**{discord.utils.escape_markdown(discord.utils.escape_mentions(user))}** {status} on {ts} UTC:\n{content}\n"


    @commands.hybrid_command(with_app_command=True)
    async def snipe(self, ctx, number=None):
        if ctx.channel not in self._deleted:
            return await ctx.send("No message to snipe.")

        histories = self._deleted[ctx.channel]
        index = abs(int(number)) if number else 0

        if index >= len(histories):
            return await ctx.send(f"The bot currently has only {len(histories)} deleted messages stored "
                                  "with index 0 being the most recently deleted message")

        history = self._deleted[ctx.channel][-1 - index]
        message = history[-1]

        msg_content = message.msg.content.lower()
        if msg_content in blacklist:
            return await ctx.send( "The requested deleted message contained a word that we do not allow, sorry! "
                                           f"(offender {message.msg.author.mention}, reason {blacklist & msg_content})")

        message = self._change_msg(history[-1], "deleted")

        for state in reversed(history[:-1]):
            message += self._change_msg(state, "edited")

        return await util.send_big_msg(ctx, message)

    @commands.command()
    async def history(self, ctx):
        if not ctx.message.reference:
            return await ctx.send("No message is replied to")

        if ctx.message.reference.message_id not in self._message_history:
            return await ctx.send("Message either never edited or too old")

        history = self._message_history[ctx.message.reference.message_id]

        message = ""
        for state in reversed(history):
            message += self._change_msg(state, "edited")

        return await util.reply_chunks(ctx.message, message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = message.channel

        if channel not in self._deleted:
            self._deleted[channel] = []

        if message.id not in self._message_history:
            self._deleted[channel].append([Entry(time.time(), message)])
        else:
            self._message_history[message.id].append(Entry(time.time(), message))
            self._deleted[channel].append(self._message_history[message.id])
            self._message_history.pop(message.id)

        self._deleted[channel] = self._deleted[channel][-conf.max_del_msgs:]

    @commands.Cog.listener()
    async def on_message_edit(self, old, _):
        if old.id not in self._message_history:
            self._message_history[old.id] = []

        self._message_history[old.id].append(Entry(time.time(), old))

        now = time.time()
        self._message_history = {
            k: v for k, v in self._message_history.items()
            if v[-1].time > now - conf.max_edit_msg_age
        }

