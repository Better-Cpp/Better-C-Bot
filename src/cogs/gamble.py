import random
import time
import datetime

from discord.ext import commands
import discord
from discord.ext.commands import Context
from discord import Member

from src import config as conf

class Gamble(commands.Cog, name="Gamble"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error):
        try:
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("Invalid input.")
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("You do not have permission to use this command.")
            if isinstance(error, commands.BadUnionArgument):
                await ctx.send("Invalid input.")
        except Exception as error:
            print(error)

    @commands.hybrid_command(with_app_command=True)
    async def bet(self, ctx: Context, amount_to_bet: int):
        """
        Place a bet (50/50). Enter the amount to bet.
        """
        self.db.check_user(ctx.author.id)

        if amount_to_bet == None:
            await ctx.send("You need to enter the amount to bet.", ephemeral=True)
            return
    
        amount_in_wallet = self.db.get_user_field("money", ctx.author.id)

        if amount_to_bet <= 0:
            await ctx.send("You must enter a positive number greater than 0.", ephemeral=True)
            return
        if amount_to_bet > amount_in_wallet:
            await ctx.send("You don't have enough money.", ephemeral=True)
            return

        won = random.randint(1, 2) == 1

        # Update wallet.
        amount_result = amount_in_wallet + (amount_to_bet if won else -amount_to_bet)
        self.db.set_user_field("money", amount_result, ctx.author.id)

        if won:
            embed = discord.Embed(title="You won!", color=discord.Color.green())
            embed.add_field(name=f"{amount_to_bet}$ has been added to your wallet", value=f"You have {amount_result}$")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="You lost.", color=discord.Color.red())
            embed.add_field(name=f"{amount_to_bet}$ has been removed from your wallet", value=f"You have {amount_result}$")
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(with_app_command=True)
    async def wallet(self, ctx: Context, user: Member = None):
        """
        Check your wallet. (Optional) Enter another user's ID to view their wallet.
        """
        if user is None:
            user = ctx.author

        self.db.check_user(user.id)

        sticker_url = f"https://cdn.discordapp.com/stickers/{conf.wallet_sticker_id}.png"

        embed = discord.Embed(title=f"{user.display_name}'s wallet", color=discord.Color.blurple())
        embed.set_thumbnail(url=sticker_url)
        embed.add_field(name="Money", value=f"{self.db.get_user_field('money', user.id)}$")

        await ctx.send(embed=embed)
    
    @commands.hybrid_command(with_app_command=True)
    async def daily(self, ctx: Context):
        """
        Get a small amount of money, works once per day.
        """
        self.db.check_user(ctx.author.id)

        last_daily_timestamp = int(self.db.get_user_field("last_daily_timestamp", ctx.author.id))
        current_timestamp = int(time.time())
        seconds_in_a_day = 86400
        seconds_since_last_daily = current_timestamp - last_daily_timestamp

        if seconds_since_last_daily < seconds_in_a_day:
            seconds_to_wait = seconds_in_a_day - seconds_since_last_daily

            await ctx.send(f"You need to wait `{str(datetime.timedelta(seconds=seconds_to_wait))}` before you can use this again.", ephemeral=True)
            return
        
        # Update timestamp and add money to user"s wallet.
        self.db.set_user_field("last_daily_timestamp", current_timestamp, ctx.author.id, commit_changes=False)
        self.db.set_user_field("money", conf.daily_amount, ctx.author.id, commit_changes=True, add_value_instead=True)

        await ctx.send(f"{ctx.author.mention} {conf.daily_amount}$ has been added to your wallet.")
    
    @commands.hybrid_command(with_app_command=True)
    async def give(self, ctx: Context, user: Member, amount: int):
        """
        Transfer money to another member. First argument is user ID. Second argument is amount.
        """
        self.db.check_user(ctx.author.id)

        if amount <= 0:
            await ctx.send("You must enter a positive number greater than 0.", ephemeral=True)
            return
        if amount > self.db.get_user_field("money", ctx.author.id):
            await ctx.send("You don't have enough money.", ephemeral=True)
            return

        if not user:
            await ctx.send("User is not a valid user or not a member of this server.", ephemeral=True)
            return
        
        self.db.check_user(user.id)
        
        self.db.set_user_field("money", -amount, ctx.author.id, commit_changes=False, add_value_instead=True)
        self.db.set_user_field("money", amount, user.id, commit_changes=True, add_value_instead=True)

        await ctx.send(f"Transferred {amount}$ from {ctx.author.display_name} to {user.display_name}")

    @commands.hybrid_command(with_app_command=True)
    async def leaderboard(self, ctx: Context, max_entries: int = 10):
        """
        Show the members with the most money.
        """
        # Poor man"s clamp.
        max_entries = max(1, min(max_entries, 50))

        entries = self.db.get_money_leaderboard(max_entries)
        
        member_list = ""

        for index, entry in enumerate(entries):
            user_id = entry[0]
            user_money = entry[1]
            member_list += f"{index + 1}. {self.bot.get_user(user_id).mention} {user_money}$\n"

        embed = discord.Embed(title="Leaderboard", color=discord.Color.blurple())
        embed.add_field(name=f"Showing top {max_entries} members", value=member_list)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gamble(bot))