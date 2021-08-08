import json
import asyncio
from discord.ext import commands, tasks

import datetime


class Statistics(commands.Cog):
    """
    Cog to handle statistics for the server
    Posts every day at midnight
    """

    def __init__(self, bot):
        self.bot = bot
        self.reset_stats()
        self.post_statistics.start()

        with open("src/backend/database.json", 'r') as f:  # Seems to be unavoidable
            self.file = json.load(f)

    def reset_stats(self):
        self.joined_count = 0
        self.accept_count = 0
        self.message_count = 0
        self.delete_count = 0
        self.edit_count = 0
        self.ban_count = 0
        self.unban_count = 0
        self.remove_count = 0
        self.socket_recv = 0
        self.socket_send = 0
        self.reactions_add = 0
        self.reactions_remove = 0

    @tasks.loop(hours=24)
    async def post_statistics(self):

        data = {
            'joined_count': self.joined_count,
            'accept_count': self.accept_count,
            'message_count': self.message_count,
            'delete_count': self.delete_count,
            'edit_count': self.edit_count,
            'ban_count': self.ban_count,
            'unban_count': self.unban_count,
            'remove_count': self.remove_count,
            'socket_recv': self.socket_recv,
            'socket_send': self.socket_send,
            'reactions_add': self.reactions_add,
            'reactions_remove': self.reactions_remove,
            'total_member_count': self.bot.get_guild(583251190591258624).member_count
        }

        async with self.bot.http_client.post("https://enqpjmkmtmwme.x.pipedream.net/", data=data) as response:
            print(response.status, await response.text())

        self.reset_stats()

    @post_statistics.before_loop
    async def before_post_statistics(self):
        await self.bot.wait_until_ready()
        now = datetime.datetime.now()
        midnight = datetime.datetime(now.year, now.month, now.day + 1)
        seconds_til_midnight = (midnight - now).total_seconds()
        await asyncio.sleep(seconds_til_midnight)

    @commands.Cog.listener()
    async def on_socket_raw_receive(self, msg):
        self.socket_recv += 1

    @commands.Cog.listener()
    async def on_socket_raw_send(self, msg):
        self.socket_send += 1

    @commands.Cog.listener()
    async def on_message(self, msg):
        # bumping:
        # This ID is the bump bot
        if msg.author.id == self.file['bump_bot_id'] and self.file['bump_bot_content'] in msg.embeds[0].description:
            await asyncio.sleep(2 * 3600 + 60)
            await msg.reply(f'<@&{self.file["bumper_role_id"]}> Bump!')
        self.message_count += 1

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        self.delete_count += 1

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        self.edit_count += 1

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        self.reactions_add += 1

    @commands.Cog.listener()
    async def on_raw_reactions_remove(self, payload):
        self.reactions_remove += 1

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.joined_count += 1

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.remove_count += 1

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        self.ban_count += 1

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        self.unban_count += 1

    @commands.command()
    async def members(self, ctx):
        await ctx.send(ctx.guild.member_count)


def setup(bot):
    bot.add_cog(Statistics(bot))
