from discord.ext import commands
import discord

from src import config as conf
from src.util import permissions


class Forums(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mapping = {}

        for channel_id, close_tag in conf.closeable.items():
            if close_tag is None:
                continue

            channel = self.bot.get_channel(channel_id)
            if not isinstance(channel, discord.ForumChannel):
                continue

            for tag in channel.available_tags:
                if tag.name != close_tag:
                    continue
                self.mapping[channel_id] = tag

    @commands.hybrid_command(aliases=['close'], with_app_command=True)
    async def done(self, ctx: commands.Context):
        if not isinstance(ctx.channel, discord.Thread):
            return

        if ctx.channel.parent.id not in conf.closeable:
            return

        if ctx.channel.id == ctx.message.id:
            await ctx.send("No.")
            return

        if ctx.author == ctx.channel.owner \
                or permissions.is_staff(ctx.author, ctx.channel) \
                or permissions.has_role(ctx.author, conf.helpful_role):

            if not ctx.interaction:
                await ctx.message.delete()
            else:
                # respond to the user invoking the slash command
                await ctx.send("Closing.", ephemeral=True)

            apply_tags = {}
            if ctx.channel.parent.id in self.mapping:
                close_tag = self.mapping[ctx.channel.parent.id]
                tags = ctx.channel.applied_tags
                if close_tag not in tags:
                    tags = tags[:4]  # can only set 5 tags at a time
                    tags.insert(0, close_tag)
                apply_tags = {'applied_tags': tags}

            await ctx.channel.edit(locked=True, archived=True, **apply_tags)


async def setup(bot):
    await bot.add_cog(Forums(bot))
