from discord.ext import commands
import discord

from typing import Union, Optional
from src.util import permissions

async def trigger_role(member: discord.Member, role: Union[discord.Role, int, str], guild: Optional[discord.Guild] = None) -> bool:
    """
    Triggers a role on a member.
    If member already has `role` then role is removed, if the member does not yet have the `role`, then it will be applied.
    Throws:
        Whatever permissions.has_role can throw
        Whatever discord.Member.add_roles can throw
    returns False if role was removed, True if it was added
    """
    role = permissions.get_role(role, guild)
    
    if permissions.has_role(member, role):
        await member.remove_roles(role)
        return False

    await member.add_roles(role)
    return True


class Challenges(commands.Cog):
    """Cog to handle the challenges command"""

    @commands.command()
    async def challenges(self, ctx):
        result = await trigger_role(ctx.author, "challenges", ctx.guild)
        if result == True:
            await ctx.send("Added challenges role.")
        else:
            await ctx.send("Removed challenges role.")


async def setup(bot):
    await bot.add_cog(Challenges(bot))
