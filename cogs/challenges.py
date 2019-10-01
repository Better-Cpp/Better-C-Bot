from discord.ext import commands
import discord

import datetime


async def trigger_role(member: discord.Member, role: Union[discord.Role, int, str], guild: Optional[discord.Guild] = None) -> bool:
    """
    Triggers a role on a member.
    If member already has `role` then role is removed, if the member does not yet have the `role`, then it will be applied.
    If role is a discord.Role then nothing is pulled from cache
    If role is an integer then a discord.Role object is pulled from cache
    if role is a string, then a discord.Role object is pulled from the `guild.roles` cache.
    If `guild` is None, and `role` is int or str, then TypeError is raised
    Throws:
        TypeError, see above
        ValueError if the `role` cannot be retrieved from cache
        Whatever discord.Member.add_roles can throw
    returns False if role was removed, True if it was added
    """

    if type(role) == int:
        role = discord.utils.get(guild.roles, id=role)

    elif type(role) == str:
        role = discord.utils.get(guild.roles, name=role)

    elif not isinstance(role, discord.Role):
        raise TypeError(f"Expected discord.Role, got {type(role)}")

    if role is None:
        raise ValueError("Role could not be retrieved from cache")

    if guild is None and isinstance(role, (str, int, )):
        raise TypeError(
            "Expected a guild since role was str or int, but got None")

    def has_role(member: discord.Member, role: discord.Role) -> bool:
        """Returns True if the member has the role, false if not"""
        return role in member.roles

    if has_role(member, role):
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


def setup(bot):
    bot.add_cog(Challenges(bot))

