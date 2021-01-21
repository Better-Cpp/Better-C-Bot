from discord.ext import commands
import discord


class cpp(commands.Cog, name="C++"):
    """Commands made for C++
    Don't abuse these.
    """

    def __init__(self, bot):
        self.bot = bot
        self.repeat_namespaces = ["experimental", "chrono", "filesystem"]

    def get_libs_list(self, language: str):
        with open(f"src/cppref/{language}libs.txt", "r") as libs:
            for item in libs:
                if " " in item:
                    # The [:-1] is to remove the '\n' written to the end of each line
                    yield item[:-1].split(" ")

    def get_language_list(self, language: str):
        with open(f"src/cppref/{language}lang.txt", "r") as lang:
            for item in lang:
                if " " in item:
                    yield item[:-1].split(" ")

    def find_results(self, language: str, query: str):
        libs = self.get_libs_list(language)
        lang = self.get_language_list(language)

        res = {"language": [], "libs": []}

        count = 0
        for path in lang:
            if count >= 10:
                break
            for i in path:
                if query.lower() in i:
                    count += 1
                    res["language"].append(path)

        count = 0
        for path in libs:
            if count >= 10:
                break
            for i in path:
                if query.lower() in path:
                    count += 1
                    res["libs"].append(path)

        return res

    @commands.command()
    async def cppref(self, ctx, *, query: str):
        """Search something on cppreference"""

        query = query.lower().replace("std::", "")

        results = self.find_results("cpp", query)

        e = discord.Embed()
        e.title = f"Search Results for {query}"
        e.colour = discord.Color.blurple()  # Subject to change
        # IF this isn't here, it breaks when test is the query
        e.add_field(inline=False, name="Language:", value="C++")

        if not results["language"] and not results["libs"]:
            return await ctx.send("No results found")

        url = f'https://en.cppreference.com/mwiki/index.php?title=Special%3ASearch&search={query}'

        lang_results = []
        lib_results = []

        if results["language"]:
            for i in results["language"]:
                lang_results.append(
                    f"[`({i[0]}) {'/'.join(i[1:])}`](http://en.cppreference.com/w/cpp/{'/'.join(i)})")

        if results["libs"]:
            for i in results["libs"]:
                if i[0] in self.repeat_namespaces:
                    lib_results.append(
                        f"[`({i[0]}) std::{'::'.join(i)}`](http://en.cppreference.com/w/cpp/{'/'.join(i)})")
                    continue
                lib_results.append(
                    f"[`({i[0]}) std::{'::'.join(i[1:])}`](http://en.cppreference.com/w/cpp/{'/'.join(i)})")

        e.add_field(inline=False, name="Language Results:",
                    value="\n".join(lang_results))
        e.add_field(inline=False, name="Library Results:",
                    value="\n".join(lib_results))

        e.add_field(name="Didn't find what you were looking for?",
                    value=f'See more [`{query}` results]({url})', inline=False)

        await ctx.send(embed=e)

    @ commands.command()
    async def cref(self, ctx, *, query: str):
        """Search something on cppreference"""

        results = self.find_results("c", query)

        url = f'https://en.cppreference.com/mwiki/index.php?title=Special%3ASearch&search={query}'

        e = discord.Embed()
        e.title = f"C Search Results for {query}"
        e.color = discord.Color.blurple()  # Subject to change

        lang_results = []
        lib_results = []

        for i in results["language"]:
            lang_results.append(
                f"[`({i[0]}) {'/'.join(i[1:])}`](http://en.cppreference.com/w/c/{'/'.join(i)})")

        for i in results["libs"]:
            lib_results.append(
                f"[`({'/'.join(i[:-1])}) {i[-1]}`](http://en.cppreference.com/w/c/{'/'.join(i)})")

        e.add_field(inline=False, name="Language Results:",
                    value="\n".join(lang_results))
        e.add_field(inline=False, name="Library Results:",
                    value="\n".join(lib_results))

        e.add_field(name="Didn't find what you were looking for?",
                    value=f'See more [`{query}` results]({url})', inline=False)

        await ctx.send(embed=e)

    @ commands.command()
    async def lectures(self, ctx):
        role = ctx.guild.get_role(695993548939722823)
        if role is None:
            return await ctx.send("Failed to find lectures role")
        await ctx.author.add_roles(role)
        await ctx.send("Gave you the role!")


def setup(bot):
    bot.add_cog(cpp(bot))
