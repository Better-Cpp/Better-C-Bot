import discord

from discord.ext.commands import Context
from src import config as conf

async def notify_staff(guild: discord.Guild, message: str):
        role = conf.staff_role

        channel = guild.system_channel
        if channel:
            return await channel.send(f"<@&{role}> {message}")

async def send_big_msg(ctx: Context, msg: str):
        for msg in _chunk_message(msg):
            await ctx.send(msg)

async def reply_chunks(reply: discord.Message, msg: str):
        for msg in _chunk_message(msg):
            reply = await reply.reply(msg)

        return reply

def _chunk_message(msg: str):
        messages: list[str] = []
        while len(msg) > conf.max_msg_size:
            chunk = msg[:conf.max_msg_size]

            end_index = chunk.rfind('\n')
            if end_index == -1:
                end_index = conf.max_msg_size

            messages.append(chunk[:end_index])
            msg = msg[end_index + 1:]

        if len(msg) > 0 and not msg.isspace():
            messages.append(msg)

        return messages
