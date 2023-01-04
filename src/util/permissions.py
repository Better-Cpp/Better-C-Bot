import discord
from typing import Union, Optional

from src import config as conf


def is_staff(member: discord.Member, source: Optional[discord.abc.GuildChannel] = None) -> bool:
    """ Checks if a user is staff.
    If source is a channel check if the user can delete messages.
    If no source was given check that permission using the system channel instead.
    If both options failed look for the staff role instead.
    Args:
        member (discord.Member): Which user to check
        source (_type_, optional): Optional channel to check against

    Returns:
        bool: True if the user is staff, False otherwise
    """
    permissions = None
    if isinstance(source, discord.abc.GuildChannel):
        permissions = source.permissions_for(member)
    else:
        permissions = member.guild.system_channel.permissions_for(member)

    if permissions:
        return permissions.manage_messages
    return has_role(member, conf.staff_role)


def get_role(role: Union[discord.Role, int, str], guild: Optional[discord.Guild] = None) -> discord.Role:
    """ 
    If role is a discord.Role then nothing is pulled from cache
    If role is an integer then a discord.Role object is pulled from cache
    if role is a string, then a discord.Role object is pulled from the `guild.roles` cache.
    If `guild` is None, and `role` is int or str, then TypeError is raised
    Throws:
        TypeError see above
        ValueError if the `role` cannot be retrieved from cache
    """
    if role is None:
        raise ValueError("Role could not be retrieved from cache")

    if guild is None and isinstance(role, (str, int, )):
        raise TypeError(
            "Expected a guild since role was str or int, but got None")
    
    if isinstance(role, int):
        role = discord.utils.get(guild.roles, id=role)

    elif isinstance(role, str):
        role = discord.utils.get(guild.roles, name=role)

    elif not isinstance(role, discord.Role):
        raise TypeError(f"Expected discord.Role, got {type(role)}")

    return role


def has_role(member: discord.Member, role: Union[discord.Role, int, str]) -> bool:
    """ Checks if a user has a role.
    Returns True if the member has the role, False if not
    """
    role = get_role(role, member.guild)
    return role in member.roles
