from difflib import SequenceMatcher
import json

from discord.ext import commands
import discord


class AutoMod(commands.Cog):
    """
    Automatic moderation
    """

    def __init__(self, bot):
        self.bot = bot
        self.badwords = set()
        self.read_words()

        with open("src/backend/database.json") as file:
            self.file = json.load(file)

    def read_words(self):
        with open("badwords.txt") as file:
            for line in file:
                self.badwords.add(line.strip().lower())

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

            async for candidate in channel.history(limit=30):
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
                    SequenceMatcher(None, message.content, candidate.content).ratio()
                    > self.file["dupe_thresh"]
                ):
                    # if the message was a command, we can just ignore it
                    ctx = await self.bot.get_context(candidate)
                    if ctx.command:
                        continue

                    return True, candidate

        # To keep from getting errors
        return False, None

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id == self.bot.user.id:
            return
        msg_content = msg.content.lower()
        for word in self.badwords:
            if word not in msg_content:
                continue
            await msg.delete()
            return await msg.channel.send(
                f"{msg.author.mention}, your message contained a word that we do not allow, sorry!"
            )

        is_impatient, duplicate_message = await self.is_duplicate(msg)
        if is_impatient:
            return await msg.reply(
                "Please only post in one channel. Thanks!\n"
                + f"Flagged message: {duplicate_message.jump_url}\n"
                + f"Flagged content: ```\n{duplicate_message.clean_content}```"
            )

    @commands.group(hidden=True, aliases=["duplication"])
    @commands.guild_only()
    async def duplicate(self, ctx):
        """
        Duplication detection options
        """
        if ctx.message.author.id not in self.file["permitted"]:
            return await ctx.send("You do not have authorization to use this command")

        if ctx.invoked_subcommand is None:
            dupe_enabled = "enabled" if self.file["dupe_enabled"] else "disabled"

            e = discord.Embed(
                title=f"Duplicate message detection",
                description="__Options:__"
                + f"►\n**thresh**\n- Current threshold: **{self.file['dupe_thresh']}**\n"
                + f"►\n**toggle**\n- Currently **{dupe_enabled}**",
            )
            return await ctx.send(embed=e)

    @duplicate.command(hidden=True)
    async def thresh(self, ctx, new_thresh):
        """
        Change the threshold for the duplication detection. Default is 0.8
        """
        self.file["dupe_thresh"] = new_thresh
        with open("src/backend/database.json", "w+") as file:
            json.dump(self.file, file)

        await ctx.reply(f"The new duplication match threshold is {new_thresh}")

    @duplicate.command(hidden=True)
    async def toggle(self, ctx):
        """
        Toggle the duplication detection. On by default
        """
        self.file["dupe_enabled"] = not self.file["dupe_enabled"]

        with open("src/backend/database.json", "w+") as file:
            json.dump(self.file, file, indent=4)

        new_enabled = "enabled" if self.file["dupe_enabled"] else "disabled"
        await ctx.reply(f"Duplicated message detection is now {new_enabled}")

    # Commented out because I will do spam detection later
    # @commands.group(hidden=True, aliases=["duplication"])
    # @commands.guild_only()
    # async def spam(self, ctx):
    #     """
    #     Duplication detection options
    #     """
    #     if ctx.message.author.id not in self.file["permitted"]:
    #         return await ctx.send("You do not have authorization to use this command")
    #
    #     if ctx.invoked_subcommand is None:
    #         spam_enabled = "enabled" if self.file["spam_enabled"] else "disabled"
    #
    #         e = discord.Embed(
    #             title=f"Spam message detection",
    #             description="__Options:__"
    #             + f"►\n**thresh**\n- Current threshold: **{self.file['spam_thresh']}**\n"
    #             + f"►\n**toggle**\n- Currently **{spam_enabled}**",
    #         )
    #         return await ctx.send(embed=e)

    # @spam.command(hidden=True)
    # async def thresh(self, ctx, new_thresh):
    #     """
    #     Change the threshold for the spam detection. Default is 5
    #     """
    #     self.file["spam_thresh"] = new_thresh
    #     with open("src/backend/database.json", "w+") as file:
    #         json.dump(self.file, file)

    #     await ctx.reply(f"The new spam match threshold is {new_thresh}")

    # @spam.command(hidden=True)
    # async def toggle(self, ctx):
    #     """
    #     Toggle the spam detection. On by default
    #     """
    #     self.file["spam_enabled"] = not self.file["spam_enabled"]

    #     with open("src/backend/database.json", "w+") as file:
    #         json.dump(self.file, file, indent=4)

    #     new_enabled = "enabled" if self.file["spam_enabled"] else "disabled"
    #     await ctx.reply(f"Spam message detection is now {new_enabled}")


def setup(bot):
    bot.add_cog(AutoMod(bot))
