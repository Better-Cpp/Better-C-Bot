import time
import traceback

from discord.ext import commands
import discord

from src.util import permissions
from src.util.rules import Rules
from src.util import util
from src import config as conf

class RulesEnforcer(commands.Cog, name="Rules"):
    def __init__(self, bot):
        self.bot = bot

        self._recent_joins = []

        self.massjoin_detect = True
        self.massjoin_active = False

        self.rules = Rules()
        bot.loop.create_task(self._update_rules())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.massjoin_detect:
            return

        current_time = time.time()

        if not self.massjoin_active:
            self._recent_joins = [
                x for x in self._recent_joins
                if current_time - x["join_time"] <= conf.massjoin_window
            ]

        is_bot_pfp = member.default_avatar == member.avatar if conf.massjoin_default_pfp else True

        is_bot_age = ( current_time - member.created_at.timestamp() < conf.massjoin_min_acc_age_val
                if conf.massjoin_min_acc_age else True )

        self._recent_joins.append({
            "join_time": current_time,
            "id": member.id,
            "assumed_bot": is_bot_pfp and is_bot_age
        })


        join_amount = len(self._recent_joins)

        if join_amount >= conf.massjoin_amount and not self.massjoin_active:
            try:
                self.massjoin_active = True

                msg = await util.notify_staff(member.guild,
                                               f"Mass member join detected. React with {conf.yes_react} to take action "
                                               + f"or with {conf.no_react} to ignore")

                await msg.add_reaction(conf.no_react)
                await msg.add_reaction(conf.yes_react)

                def _check(reaction, user, reaction_msg):
                    return ( reaction.message.id == reaction_msg.id
                        and permissions.is_staff(user, reaction_msg.channel)
                        and user.id != self.bot.user.id )

                reaction, user = await self.bot.wait_for('reaction_add',
                    check=lambda reaction, user: _check(reaction, user, msg),
                    timeout=conf.massjoin_notif_timeout)

                if reaction.emoji == conf.no_react:
                    await msg.reply("Not taking any action and resetting the join detection")

                if reaction.emoji == conf.yes_react:
                    wizard_msg = ( "Users assumed to be bots:\n" + ",\n".join(map(lambda x: f"<@{x['id']}>",
                        filter(lambda x: x["assumed_bot"], self._recent_joins)))
                        + "\nUsers assumed to not be bots:\n" + ",\n".join(map(lambda x: f"<@{x['id']}>",
                        filter(lambda x: not x["assumed_bot"], self._recent_joins))) )


                    reply = await util.reply_chunks(msg, wizard_msg)

                    await reply.add_reaction(conf.no_react)
                    await reply.add_reaction(conf.yes_react)

                    reaction, user = await self.bot.wait_for('reaction_add',
                        check=lambda reaction, user: _check(reaction, user, reply),
                        timeout=conf.massjoin_wizard_timeout)

                    if reaction.emoji == conf.no_react:
                        await reply.reply("Not banning any users and resetting the join detection")

                    if reaction.emoji == conf.yes_react:
                        bot_count = sum(1 for x in self._recent_joins if x['assumed_bot'])
                        ban_start_msg = await reply.reply(f"Banning {bot_count} user(s)")

                        failed_bans = []
                        for user in self._recent_joins:
                            if not user["assumed_bot"]:
                                continue

                            try:
                                await member.guild.ban(discord.Object(id=user["id"]))

                            except:
                                failed_bans.append(user["id"])
                                await ban_start_msg.reply("Banning failed with the following exception:\n"
                                                          + f"```py\n{traceback.format_exc()}\n```")

                        await util.reply_chunks(
                            ban_start_msg,
                            "Banned all bots except:\n"
                                                + ",\n".join(map(lambda x: f"<@{x}>", failed_bans)))

                    await reply.clear_reactions()

                await msg.clear_reactions()

            finally:
                self._recent_joins.clear()
                self.massjoin_active = False

    @commands.command()
    @commands.has_role(conf.staff_role)
    async def toggle_massjoin_detection(self, ctx):
        self.massjoin_detect = not self.massjoin_detect
        if self.massjoin_detect:
            await ctx.send("Massjoin detection is now on")
        else:
            await ctx.send("Massjoin detection is now off")

    @commands.hybrid_command(with_app_command=True)
    async def rule(self, ctx, rule: int, subrule: int = None):
        """Display a rule"""
        text: str = ""

        if rule not in self.rules:
            return await ctx.send(f"Invalid rule number: `{rule}`")

        if subrule is not None:
            if subrule <= 0 or subrule > len(self.rules[rule].subrules):
                return await ctx.send(f"Invalid rule number: `{rule}` `{subrule}`")

            await ctx.send(self.rules[rule].subrules[subrule - 1])
        else:
            await ctx.send(str(self.rules[rule]))

    async def _update_rules(self):
        channel = self.bot.get_channel(conf.rules_channel)
        messages = [m async for m in channel.history(limit=1, oldest_first=True)]
        assert len(messages) == 1

        self.rules.parse(messages[0].clean_content)

    @commands.command(hidden=True)
    @commands.has_role(conf.staff_role)
    async def update_rules(self, ctx):
        await self._update_rules()
        await ctx.send("The rules were updated successully")


async def setup(bot):
    await bot.add_cog(RulesEnforcer(bot))
