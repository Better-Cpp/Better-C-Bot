
from discord.ext import commands
from fuzzywuzzy import fuzz, process
import discord

from src.util.blacklist import blacklist
from src import config as conf

class AutoMod(commands.Cog):
    """
    Automatic moderation
    """
    def __init__(self, bot):
        self.bot = bot
        self.duplicate_msg_detect = True

    async def is_duplicate(self, message):
        # apparently @everyone is in this list
        if len(message.author.roles) > 1:
            return False, None

        if len(message.clean_content) < 50:
            return False, None

        everyone = message.guild.default_role

        for channel in message.guild.text_channels:
            # People who actually have a role that is special probably won't do dumb stuff
            _, denied = channel.overwrites_for(everyone).pair()
            if denied.send_messages:
                continue

            if channel == message.channel:
                continue

            history = await channel.history(limit=30).flatten()
            async for candidate in history:
                if candidate.author != message.author:
                    continue

                # if sent more than 12 hours ago, ignore it, it's probably fine
                if (
                    message.created_at.timestamp() - candidate.created_at.timestamp()
                    > 3600 * 12
                ):
                    continue

                msg_attachments = [str(i) for i in message.attachments]
                can_attachments = [str(i) for i in candidate.attachments]
                # if the message has the same attachments, we probably don't need to check the text
                if message.attachments and msg_attachments == can_attachments:
                    return True, candidate

                if (
                    fuzz.ratio(None, message.content, candidate.content)
                    > conf.dupe_thresh
                ):
                    # if the message was a command, we can just ignore it
                    ctx = await self.bot.get_context(candidate)
                    if ctx.command:
                        continue

                    return True, candidate

        # To keep from getting errors
        return False, None

    async def apply_filter(self, message):
        msg_content = message.content.lower()
        if msg_content in blacklist:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, your message contained a word that we do not allow, sorry! (reason {blacklist & msg_content})"
            )
            return True
        return False
    
    @commands.Cog.listener()
    async def on_message_edit(self, _, after):
        try:
            if after.author.id == self.bot.user.id:
                return
            
            await self.apply_filter(after)
        except Exception as e:
            print(e)
            
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == self.bot.user.id:
            return
        
        if await self.apply_filter(msg):
            return

        is_impatient, duplicate_message = await self.is_duplicate(msg)
        if is_impatient:
            return await msg.reply(
                "Please only post in one channel. Thanks!\n"
                + f"Flagged message: {duplicate_message.jump_url}\n"
                + f"Percent Match: {fuzz.ratio(duplicate_message.clean_content, msg.clean_content)}"
            )

    @commands.group(aliases=["duplication"])
    @commands.guild_only()
    @commands.has_role(conf.staff_role)
    async def duplicate(self, ctx):
        """
        Duplication detection options
        """
        if ctx.invoked_subcommand is None:
            dupe_enabled = "enabled" if self.duplicate_msg_detect else "disabled"

            e = discord.Embed(
                title=f"Duplicate message detection",
                description="__Options:__"
                + f"►\n**toggle**\n- Currently **{dupe_enabled}**",
            )
            return await ctx.send(embed=e)

    @duplicate.command()
    async def toggle(self, ctx):
        """
        Toggle the duplication detection. On by default
        """
        self.duplicate_msg_detect = not self.duplicate_msg_detect

        new_enabled = "enabled" if self.duplicate_msg_detect else "disabled"
        await ctx.reply(f"Duplicated message detection is now {new_enabled}")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
