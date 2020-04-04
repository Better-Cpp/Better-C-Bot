from discord.ext import commands
import aiohttp
import json
import discord
from lxml import etree

import os
import glob


class cpp(commands.Cog, name="C++"):
    """Commands made for C++
    Don't abuse these.
    """

    def __init__(self, bot):
        self.bot = bot

    def get_directory_files(self, query, directory):
        for file in glob.iglob(f"{directory}/*"):
            if not query.lower() in file.lower():
                continue
            yield f"http://en.cppreference.com/w/{file[2:]}"
            if not os.path.isdir(file):
                continue
            yield from self.get_directory_files(query, file)

    def get_corresponding_files(self, query):
        if query.startswith("std::"):
            query = query.replace("std::", "")
        query = query.replace("::", "/")
        output = []
        to_queue = list(self.get_directory_files(query, "w/cpp/**"))
        for index, each in enumerate(to_queue):
            if each.endswith(".html"):
                continue
            output.append(
                to_queue.pop(index))
        output.extend(to_queue)
        return output

    @commands.command()
    async def cppref(self, ctx, *, query: str):
        """Search something on cppreference"""
        results = self.get_corresponding_files(query)

        url = f'http://en.cppreference.com/w/cpp/index.php?title=Special:Search?search={query}'

        e = discord.Embed()

        special_pages = []
        description = []
        q = query.replace('std::', '')
        if os.path.isdir(f"w/cpp/{q}"):
            description.append(
                f"[`std::{q}`](http://en.cppreference.com/w/cpp/{q})")
        for _, result in enumerate(results):
            check_name = result.replace("http://en.cppreference.com/", "")
            if check_name.startswith("w/cpp/container"):
                check_name = check_name[:5] + check_name[15:]
            if check_name.startswith("w/cpp/algorithm"):
                check_name = check_name[:5] + check_name[15:]
            if check_name.startswith("w/cpp/memory"):
                check_name = check_name[:5] + check_name[12:]
            f_name = check_name[6:].replace("\\", "::").replace(".html", "")
            if check_name.startswith(("w/cpp/language", "w/cpp/concept")):
                special_pages.append(f'[`{f_name.replace("/", "::")}`]({result})')
                continue

            description.append(f'[`std::{f_name.replace("/", "::")}`]({result})')

        if len(special_pages) > 0:
            e.add_field(name='Language Results', value='\n'.join(
                special_pages), inline=False)
            if len(description):
                e.add_field(name='Library Results', value='\n'.join(
                    description[:10]), inline=False)
        else:
            if not len(description):
                return await ctx.send('No results found.')

            desc_str = '\n'.join(description[:15])
            e.title = 'Search Results'
            e.description = desc_str

        e.add_field(
            name='See More', value=f'[`{discord.utils.escape_markdown(query)}` results]({url})')
        await ctx.send(embed=e)

    @commands.command()
    async def lectures(self, ctx):
        role = ctx.guild.get_role(695993548939722823)
        if role is None:
            return await ctx.send("Failed to find lectures role")
        await ctx.author.add_roles(role)
        await ctx.send("Gave you the role!")

def setup(bot):
    bot.add_cog(cpp(bot))
