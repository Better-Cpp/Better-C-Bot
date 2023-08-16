import discord
from discord.ext import commands
from discord.ui import Button, View, Modal
from random import randrange
from src import config as conf
from src.util import permissions

class ModmailModal(Modal):
    answer = discord.ui.TextInput(label = "Answer")

    def __init__(self):
        num1 = randrange(10)
        num2 = randrange(10)
        super().__init__(title = f"Solve the equation: {num1} + {num2}")
        self.solution = num1 + num2

    async def on_submit(self, interaction):
        if(int(self.answer.value) != self.solution):
            await interaction.response.send_message(f'Wrong answer', ephemeral=True)
            return

        user = interaction.user
        channel: discord.TextChannel = interaction.client.get_channel(conf.modmail_channel)

        created_thread = await channel.create_thread(
            name = f"{user.display_name}'s ticket",
            type = discord.ChannelType.private_thread,
            invitable = False
        )
        await created_thread.add_user(user)
        await created_thread.send(f"{user.mention} please describe your issue and wait for <@&{conf.staff_role}> to respond.")

        await interaction.response.send_message(f'Channel has been created!', ephemeral=True)

class ModmailView(View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label="Create Ticket", custom_id='persistent_view:create_ticket')
    async def button_callback(self, interaction, button):
        modal = await interaction.response.send_modal(ModmailModal())

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def modmail(self, ctx, channel: discord.TextChannel):
        if not permissions.is_staff(ctx.author, ctx.channel):
            return

        embed = discord.Embed(
            title = "Create a mod mail",
            type = "rich",
        )

        view = ModmailView()

        await channel.send(embeds = [embed], view = view)

async def setup(bot):
    await bot.add_cog(Modmail(bot))
    bot.add_view(ModmailView())