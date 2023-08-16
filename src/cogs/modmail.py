import discord
from discord.ext import commands
from src import config as conf

class Select(discord.ui.Select):
    def __init__(self, options):
        super().__init__(max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        picked_server = int(list(interaction.data.values())[0][0])

        for server in super().options:
            if(server.value == picked_server):
                user = interaction.user
                channel: discord.TextChannel = interaction.client.get_channel(conf.modmail_channel)

                created_thread = await channel.create_thread(
                    name = f"{user.display_name}'s ticket",
                    type = discord.ChannelType.private_thread,
                    invitable = False
                )
                await created_thread.add_user(user)
                await created_thread.send(f"{user.mention} please describe your issue and wait for <@&{conf.staff_role}> to respond.");
                break
        
        await interaction.message.delete()

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, select):
        super().__init__(timeout=timeout)
        self.add_item(select)

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild or ctx.author.id == self.bot.application_id:
            return

        shared_servers = ctx.author.mutual_guilds

        options = []
        for server in shared_servers:
            options.append(discord.SelectOption(label=server.name, value=server.id))

        await ctx.channel.send(
            content = "Please pick a server to send ticket to",
            view = SelectView(select=Select(options))
        )

async def setup(bot):
    await bot.add_cog(Modmail(bot))