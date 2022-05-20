import discord
import asyncio
from datetime import datetime

from src import config as conf


class category_meta(type):
    categories = {}

    __contains__ = categories.__contains__
    __getitem__ = categories.__getitem__
    __setitem__ = categories.__setitem__
    __iter__ = categories.__iter__
    items = categories.items


class category(metaclass=category_meta):
    def __init__(self, underlying):
        if not isinstance(underlying, discord.CategoryChannel):
            raise ValueError("Not a category.")
        self.id = underlying.id

    def __index__(self):
        return self.id

    def __contains__(self, channel):
        if isinstance(channel, discord.TextChannel):
            return channel.category_id == self.id
        elif isinstance(channel, channels.channel):
            return channel.underlying.category_id == self.id
        else:
            raise ValueError(type(channel))


class channels:
    class channel:
        def __init__(self, underlying):
            if not isinstance(underlying, discord.TextChannel):
                raise ValueError("Not a channel.")
            self.underlying = underlying
            self.owner = None
            self.message = None

        def __index__(self):
            return self.underlying.id

        def is_privileged(self, user):
            return self.owner == user or any(e.id == conf.staff_role for e in user.roles)

        async def move(self, cat, reason=None):
            await self.underlying.move(category=cat,
                                       beginning=True,
                                       reason=reason or "Channel released.")

        async def claim(self, message):
            if not isinstance(message, discord.Message):
                raise RuntimeError("Invalid message type.")
            self.message = message
            self.owner = message.author

            await self.message.pin()
            await self.underlying.send(f"{self.owner.mention} claimed this help channel. Please keep the discussion on topic.\n"
                                       "Please make this channel available again using `++done` once your question has been answered.")
            await self.move(category['occupied'])

        async def release(self, reason=None):
            if self.message:
                await self.message.unpin()
            self.owner = None
            self.message = None

            await self.move(category['available'], reason or "Channel released.")
            await self.open()
            await self.underlying.send("Channel is now available again. Enter a message to claim it.")

        async def reactivate(self):
            await self.underlying.send("Channel reactivated.")
            await self.move(category['occupied'])
            await self.open()
            
        async def close(self):
            await self.underlying.set_permissions(self.underlying.guild.default_role,
                                                  send_messages=False)

        async def open(self):
            await self.underlying.set_permissions(self.underlying.guild.default_role,
                                                  overwrite=None)

        async def check_dormancy(self):
            last = await self.underlying.fetch_message(self.underlying.last_message_id)
            diff = datetime.utcnow() - last.created_at

            if self in category['dormant']:
                print(f"Resetting in {diff}")
                if diff > conf.reset_time:
                    await self.release()

            if self in category['occupied']:
                if diff > conf.dormant_time:
                    msg = await self.underlying.send(f"Channel became dormant. {self.owner.mention} "
                                                     f"can react with {conf.yes_react} to reactivate it "
                                                     f"or with {conf.no_react} to make this channel available again.")
                    await msg.add_reaction(conf.no_react)
                    await msg.add_reaction(conf.yes_react)
                    await self.move(category['dormant'])
                    await self.close()

    def __init__(self, bot):
        self.bot = bot
        self.channels = {}

        for type, id in conf.help_categories.items():
            cat = self.bot.get_channel(id)
            if not isinstance(cat, discord.CategoryChannel):
                raise ValueError("Not a category.")

            category[type] = category(cat)
            self.channels |= {channel.id: channels.channel(channel)
                              for channel in cat.text_channels}
        print(f"found {len(self.channels)} help channels.")

        loop = asyncio.get_event_loop()
        self.dormancy_task = loop.create_task(self._check_dormancy())
        self.dormancy_task.add_done_callback(
            lambda ctx: print("Dormancy task finished."))

    def _fix_key(self, key):
        if isinstance(key, discord.TextChannel):
            return key.id
        return key

    def __getitem__(self, key):
        key = self._fix_key(key)
        return self.channels[key]

    def __contains__(self, key):
        key = self._fix_key(key)
        return key in self.channels

    @asyncio.coroutine
    async def _check_dormancy(self):
        while True:
            for chan in self.channels.values():
                if chan not in category['available']:
                    await chan.check_dormancy()
            await asyncio.sleep(conf.recheck_time)
