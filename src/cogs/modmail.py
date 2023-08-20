import discord
from discord.ext import commands
from discord.ui import Button, View, Modal
from random import randrange
import time
from src import config as conf
from src.util import permissions

class ModmailModal(Modal):
    name = discord.ui.TextInput(label = "Subject")
    issue = discord.ui.TextInput(label = "Content", style = discord.TextStyle.paragraph, max_length = 1000)

    def __init__(self, selected):
        super().__init__(title = f"Describe your issue")
        self.selected = selected

    async def on_submit(self, interaction):
        user = interaction.user
        channel: discord.TextChannel = interaction.client.get_channel(conf.modmail_channel)

        created_thread = await channel.create_thread(
            name = f"{self.name.value}",
            type = discord.ChannelType.private_thread,
            invitable = False
        )

        embed = discord.Embed(title = f"**{self.selected}**")
        embed.add_field(name="", value=f"{self.issue.value}")
        embed.set_author(name = user.name, icon_url = user.avatar.url)

        await created_thread.add_user(user)

        if self.selected == "There's an issue with a moderative action":
            await created_thread.send(
                f"{user.mention} please wait for <@&{conf.admin_role}> to respond.\n",
                embeds = [embed]
            )
        else:
            await created_thread.send(
                f"{user.mention} please wait for <@&{conf.staff_role}> to respond.\n",
                embeds = [embed]
            )

        await interaction.response.send_message(
            f"Channel created in <t:{int(time.time())}:f>\n{created_thread.jump_url}", 
            ephemeral = True
        )

class ModmailView(View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.select(placeholder = "Select issue type", custom_id = "persistent_view:selection", options = [
        discord.SelectOption(label = "I want to report a user or message"),
        discord.SelectOption(label = "There's an issue with a moderative action"),
        discord.SelectOption(label = "I want to appeal a ban"),
        discord.SelectOption(label = "Other")
    ])
    async def select_type(self, interaction, selection):
        await interaction.response.defer(ephemeral = True, thinking = False)

    @discord.ui.button(label = "Create ticket", custom_id = "persistent_view:create_ticket")
    async def button_callback(self, interaction, button):
        if len(self.children[0].values) == 0:
            await interaction.response.send_message("Please select an option", ephemeral = True)
            return

        await interaction.response.send_modal(ModmailModal(self.children[0].values[0]))

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