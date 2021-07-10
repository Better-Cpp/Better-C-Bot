import io
import json
import re
import time

from discord.ext import commands
import discord


class RulesEnforcer(commands.Cog, name="Rules"):
    with open("src/backend/database.json", 'r') as f:
        file = json.load(f)

    def __init__(self, bot):
        self.bot = bot

        # Maps channel : discord.Message
        self._deleted = {}

        self._recent_joins = []

        self.massjoin_detect = True
        self.massjoin_active = False

        with open("src/backend/database.json", 'r') as f: # Seems to be unavoidable
            self.file = json.load(f)
        bot.loop.create_task(self._update_rules())

    @commands.command()
    async def rule(self, ctx, number):
        """Display a rule"""
        if self._rules.get(number) is None:
            return await ctx.send(f"Invalid rule number: `{discord.utils.escape_mentions(number)}`")
        else:
            await ctx.send(f"**Rule {number}**:\n{self._rules[number]}")

    @commands.command()
    async def snipe(self, ctx):
        if ctx.channel not in self._deleted:
            return await ctx.send("No message to snipe.")

        message: discord.Message = self._deleted[ctx.channel]
        user = str(message.author)
        ts = message.created_at.isoformat(" ")
        content = message.content
        return await ctx.send(f"**{discord.utils.escape_markdown(discord.utils.escape_mentions(user))}** said on {ts} UTC:\n{content}")

    async def _notify_staff(self, guild, message):
        role = self.file["staff_role"]

        channel = guild.system_channel
        if channel:
            return await channel.send(f"<@{role}> {message}")


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.massjoin_detect:
            return

        current_time = time.time()

        if not self.massjoin_active:
            self._recent_joins = [
                x for x in self._recent_joins
                if current_time - x["join_time"] <= self.file["massjoin_window"]
            ]

        self._recent_joins.append({"join_time": current_time, "id": member.id,
            "assumed_bot": (
                ( member.default_avatar_url == member.avatar_url if self.file["massjoin_default_pfp"] else True )
                and ( time.time() - member.created_at.timestamp() < self.file["massjoin_min_acc_age_val"]
                    if self.file["massjoin_min_acc_age"] else True ) )
            })


        join_amount = len(self._recent_joins)

        if join_amount >= self.file["massjoin_amount"] and not self.massjoin_active:
            self.massjoin_active = True

            cross = "❎"
            checkmark = "✅"

            msg = await self._notify_staff(member.guild,
                    f"Mass member join detected. React with {checkmark} to take action or with {cross} to ignore")

            await msg.add_reaction(cross)
            await msg.add_reaction(checkmark)

            def _check(reaction, user, msg):
                return ( reaction.message.id == msg.id
                        and any(role.id == self.file["staff_role"] for role in user.roles)
                        and user.id != self.bot.user.id )

            reaction, user = await self.bot.wait_for('reaction_add',
                    check=lambda reaction, user: _check(reaction, user, msg),
                    timeout=self.file["massjoin_notif_timeout"])

            if reaction.emoji == cross:
                await msg.reply("Not taking any action and resetting the join detection")

            if reaction.emoji == checkmark:
                wizard_msg = ( "Users assumed to be bots:\n" + ",\n".join(map(lambda x: f"<@{x['id']}>",
                    filter(lambda x: x["assumed_bot"], self._recent_joins)))
                    + "\nUsers assumed to not be bots:\n" + ",\n".join(map(lambda x: f"<@{x['id']}>",
                    filter(lambda x: not x["assumed_bot"], self._recent_joins))) )

                messages = []
                while len(wizard_msg) > self.file["max_msg_size"]:
                    chunk = wizard_msg[0:self.file["max_msg_size"]]
                    end_index = chunk.rfind('\n')
                    messages.append(chunk[0:end_index])
                    wizard_msg = wizard_msg[end_index:]

                messages.append(wizard_msg)

                reply = msg
                for message in messages:
                    reply = await reply.reply(message)

                await reply.add_reaction(cross)
                await reply.add_reaction(checkmark)

                reaction, user = await self.bot.wait_for('reaction_add',
                        check=lambda reaction, user: _check(reaction, user, reply),
                        timeout=self.file["massjoin_wizard_timeout"])

                if reaction.emoji == cross:
                    await reply.reply("Not banning any users and resetting the join detection")
                    await reply.clear_reactions()

                if reaction.emoji == checkmark:
                    for user in self._recent_joins:
                        if user["assumed_bot"]:
                            await member.guild.ban(
                                    self.bot.get_user(user["id"]) if self.bot.get_user(user["id"])
                                        else await self.bot.fetch_user(user["id"]))

                    await reply.reply("Banned the bots")

                await reply.clear_reactions()

            await msg.clear_reactions()

            self._recent_joins.clear()
            self.massjoin_active = False


    @commands.command()
    @commands.has_role(file["staff_role"])
    async def toggle_massjoin_detection(self, ctx):
        self.massjoin_detect = not self.massjoin_detect
        if self.massjoin_detect:
            await ctx.send("Massjoin detection is now on")
        else:
            await ctx.send("Massjoin detection is now off")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self._deleted[message.channel] = message

    async def _update_rules(self):
        channel = self.bot.get_channel(self.file["rules_channel"])
        messages = await channel.history(limit=1000000, oldest_first=True).flatten()
        self._rules = {}

        for message in messages:
            content = message.clean_content
            matches = re.finditer(r"(\d+) - (.+?)(?=[\n ]+\d+? - |$)", content, flags=re.DOTALL)

            for rule in matches:
                if rule[0] == "":
                    continue

                number = rule[1]
                text = rule[2]

                if self._rules.get(number) is None:
                    self._rules[number] = text

    @commands.command(hidden=True)
    @commands.has_role(file["staff_role"])
    async def update_rules(self, ctx):
        await self._update_rules()
        await ctx.send("The rules were updated successully")
def setup(bot):
    bot.add_cog(RulesEnforcer(bot))

