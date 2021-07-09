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
            self.database = json.load(file)

    def read_words(self):
        with open("badwords.txt") as file:
            for line in file:
                self.badwords.add(line.strip().lower())

    async def is_duplicate(self, message):
        everyone = message.guild.default_role

        for channel in message.guild.text_channels:
            # People who actually have a role that is special probably won't do dumb stuff
            _, denied = channel.overwrites_for(everyone).pair()
            if denied.send_messages:
                continue

            if channel == message.channel:
                continue

            async for candidate in channel.history(limit=10):
                if (
                    SequenceMatcher(None, message.content, candidate.content).ratio()
                    > self.database["dupe_thresh"]
                ):
                    return True, candidate

        # To keep from getting errors
        return None, None

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
    @commands.is_owner()
    async def duplicate(self, ctx):
        """
        Duplication detection options
        """
        if ctx.invoked_subcommand is None:
            dupe_enabled = "enabled" if self.database["dupe_enabled"] else "disabled"

            e = discord.Embed(
                title=f"Duplicate message detection",
                description="__Options:__"
                + f"►\n**thresh**\n- Current threshold: **{self.database['dupe_thresh']}**\n"
                + f"►\n**toggle**\n- Currently **{dupe_enabled}**",
            )
            return await ctx.send(embed=e)

    @duplicate.command(hidden=True)
    async def thresh(self, ctx, new_thresh):
        """
        Change the threshold for the duplication detection. Default is 0.8
        """
        self.database["dupe_thresh"] = new_thresh
        with open("src/backend/database.json", "w+") as file:
            json.dump(self.database, file)

        await ctx.reply(f"The new duplication match threshold is {new_thresh}")

    @duplicate.command(hidden=True)
    async def toggle(self, ctx):
        """
        Toggle the duplication detection. On by default
        """
        self.database["dupe_enabled"] = not self.database["dupe_enabled"]

        with open("src/backend/database.json", "w+") as file:
            json.dump(self.database, file, indent=4)

        new_enabled = "enabled" if self.database["dupe_enabled"] else "disabled"
        await ctx.reply(f"Duplicated message detection is now {new_enabled}")

    # Commented out because I will do spam detection later
    # @commands.group(hidden=True, aliases=["duplication"])
    # @commands.guild_only()
    # @commands.is_owner()
    # async def spam(self, ctx):
    #     """
    #     Duplication detection options
    #     """
    #     if ctx.invoked_subcommand is None:
    #         spam_enabled = "enabled" if self.database["spam_enabled"] else "disabled"

    #         e = discord.Embed(
    #             title=f"Spam message detection",
    #             description="__Options:__"
    #             + f"►\n**thresh**\n- Current threshold: **{self.database['spam_thresh']}**\n"
    #             + f"►\n**toggle**\n- Currently **{spam_enabled}**",
    #         )
    #         return await ctx.send(embed=e)

    # @spam.command(hidden=True)
    # async def thresh(self, ctx, new_thresh):
    #     """
    #     Change the threshold for the spam detection. Default is 5
    #     """
    #     self.database["spam_thresh"] = new_thresh
    #     with open("src/backend/database.json", "w+") as file:
    #         json.dump(self.database, file)

    #     await ctx.reply(f"The new spam match threshold is {new_thresh}")

    # @spam.command(hidden=True)
    # async def toggle(self, ctx):
    #     """
    #     Toggle the spam detection. On by default
    #     """
    #     self.database["spam_enabled"] = not self.database["spam_enabled"]

    #     with open("src/backend/database.json", "w+") as file:
    #         json.dump(self.database, file, indent=4)

    #     new_enabled = "enabled" if self.database["spam_enabled"] else "disabled"
    #     await ctx.reply(f"Spam message detection is now {new_enabled}")


def setup(bot):
    bot.add_cog(AutoMod(bot))
