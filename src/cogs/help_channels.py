from discord.ext import commands
import discord

from src import config as conf
from src.util.channels import channels, category


class HelpChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channels = channels(bot)
        self.prefix = tuple(self.bot.command_prefix(None, None))
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        try:
            if msg.author.id == self.bot.user.id:
                return

            if msg.channel not in category['available']:
                return
            
            if msg.content.startswith(self.prefix):
                return
                                    
            channel = self.channels[msg.channel]
            await channel.claim(msg)
        except Exception as e:
            print(e)
            
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.id == self.bot.user.id or \
           reaction.message.channel not in category['dormant'] or \
           reaction.message.channel.last_message_id != reaction.message.id or \
           reaction.message.author.id != self.bot.user.id:
            return

        channel = self.channels[reaction.message.channel]
        if channel.is_privileged(user):
            if reaction.emoji == conf.no_react:
                await channel.reactivate()
            if reaction.emoji == conf.yes_react:
                await channel.release()

    @commands.command(aliases=['done', 'close'])
    async def _done(self, ctx):
        """Set the current help channel as available. 
        Can only be issued by the channel's occupant and staff."""

        if ctx.channel not in category['occupied'] and ctx.channel not in category['dormant']:
            await ctx.send("This command can only be used in owned or available help channels.")
            return

        channel = self.channels[ctx.channel]

        # assume anyone can free a channel up if we don't know who owns it
        # this could happen due to bot restarts
        if channel.owner == None:
            await channel.release("Owner unknown. This channel has become available.")
            return

        if channel.is_privileged(ctx.author):
            await channel.release()
        else:
            await ctx.send(f"Only {channel.owner.mention} or staff can manually make this channel available.")


async def setup(bot):
    await bot.add_cog(HelpChannels(bot))
