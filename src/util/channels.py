import discord
import asyncio
from datetime import datetime

from src.util import permissions
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
        """Checks whether a channel is contained in this category.
        Args:
            channel (_type_): _description_
        Raises:
            ValueError: if channel was neither a TextChannel nor a channel ID
        """
        
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
            self.asker_role = permissions.get_role(conf.asker_role, self.underlying.guild)
            self.lock = asyncio.Lock()

        def __index__(self):
            return self.underlying.id

        def is_privileged(self, user: discord.Member):
            return self.owner == user or \
                permissions.has_role(user, conf.helpful_role) or \
                permissions.is_staff(user, self.underlying)

        async def move(self, cat, reason=None):
            await self.underlying.move(category=cat,
                                       beginning=True,
                                       sync_permissions=True,
                                       reason=reason or "Channel moved.")

        async def claim(self, message):
            if not isinstance(message, discord.Message):
                raise RuntimeError("Invalid message type.")
            
            async with self.lock:
                self.message = message
                self.owner = message.author
                await self.move(category['occupied'], "Channel got claimed")
                await asyncio.gather(*[self.message.pin(),
                                    self.underlying.send(f"{self.owner.mention} currently owns this help channel. Please make this channel available by using `++done` once your question has been answered.")],
                                    return_exceptions=True)
                await self.owner.add_roles(self.asker_role)

        async def release(self, reason=None):        
            try:
                async with self.lock:
                    await self.owner.remove_roles(self.asker_role)
                    self.owner = None
                    await self.message.unpin()
                    self.message = None
            except Exception as e:
                print(e)
                
            await self.move(category['available'], reason or "Channel released.")
            await self.underlying.send("This channel is now available again. Enter a message to claim it.")

        async def reactivate(self):
            await self.move(category['occupied'], "Channel became occupied")
            await self.underlying.send("Channel reactivated.")

        async def check_dormancy(self):
            last = await self.underlying.fetch_message(self.underlying.last_message_id)
            diff = datetime.utcnow() - last.created_at

            if self in category['dormant']:
                if diff > conf.reset_time:
                    await self.release()

            if self in category['occupied']:
                if diff > conf.dormant_time:
                    if not self.owner:
                        await self.release()
                        return
                    await self.move(category['dormant'])
                    msg = await self.underlying.send(f"This channel is about to become available again. {self.owner.mention} "
                                                     f"can react with {conf.no_react} to re-claim it "
                                                     f"or with {conf.yes_react} to make this channel available again immediately.")
                    await asyncio.gather(*[msg.add_reaction(conf.no_react),
                                           msg.add_reaction(conf.yes_react)],
                                         return_exceptions=True)

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
            await asyncio.gather(*[chan.check_dormancy()
                                   for chan in self.channels.values()
                                   if chan not in category['available']],
                                 return_exceptions=True)
            await asyncio.sleep(int(conf.recheck_time.total_seconds()))
