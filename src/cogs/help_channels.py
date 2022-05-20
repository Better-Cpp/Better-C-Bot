from discord.ext import commands
import discord

from src import config as conf
from src.util.channels import channels, category


class HelpChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = channels(bot)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == self.bot.user.id:
            return

        if msg.channel not in category['available']:
            return

        channel = self.channels[msg.channel]
        await channel.claim(msg)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id == self.bot.user.id or \
           reaction.message.channel not in category['dormant']:
            return
        
        if reaction.message.channel.last_message_id != reaction.message.id:
            print("not the last message")
            return

        channel = self.channels[reaction.message.channel]
        if channel.is_privileged(user):
            print("user is privieleged")
            if reaction.emoji == conf.yes_react:
                await channel.reactivate()
            if reaction.emoji == conf.no_react:
                await channel.release()

    @commands.command(name="done")
    async def _done(self, ctx):
        """Set the current help channel as available. 
        Can only be issued by the channel's occupant and staff."""

        if ctx.channel not in category['dormant'] and ctx.channel not in category['occupied']:
            await ctx.send("This command can only be used in dormant or occupied help channels.")
            return

        channel = self.channels[ctx.channel]

        # assume anyone can free a channel up if we don't know who owns it
        # this could happen due to bot restarts
        if channel.owner == None:
            await channel.release("Owner unknown, assuming the channel to be available again.")
            return

        if channel.is_privileged(ctx.author):
            await channel.release()
        else:
            await ctx.send(f"Only the channel's current owner {channel.owner.mention} and staff can manually free this channel up.")


def setup(bot):
    bot.add_cog(HelpChannels(bot))
