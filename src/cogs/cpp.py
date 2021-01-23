from discord.ext import commands
import urllib.parse as parse
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
                    yield item[:-1]

    def get_language_list(self, language: str):
        with open(f"src/cppref/{language}lang.txt", "r") as lang:
            for item in lang:
                if " " in item:
                    yield item[:-1]

    def find_results(self, language: str, query: str):
        libs = self.get_libs_list(language)
        lang = self.get_language_list(language)

        res = {"lang": [], "libs": []}

        count = 0
        for path in lang:
            if count >= 10:
                break
            if query.lower() in path:
                count += 1
                res["lang"].append(path.split(" "))

        count = 0
        for path in libs:
            if count >= 10:
                break
            if query.lower() in path:
                count += 1
                res["libs"].append(path.split(" "))

        return res

    @commands.command()
    async def cppref(self, ctx, *, query: str):
        """Search for a C++ item on cppreference -- WIP, can be better"""

        results = self.find_results("cpp", query.replace(
            "std", "").replace("::", " ").replace("/", " ").strip())

        url = f'https://en.cppreference.com/mwiki/index.php?title=Special%3ASearch&search={parse.quote(query)}'

        e = discord.Embed()
        e.title = f"C++ Search Results for **`{query}`**"
        e.colour = discord.Color.blurple()  # Subject to change

        lang_results = []
        lib_results = []

        if results["lang"]:
            for i in results["lang"]:
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

        e.description = ("\n\n**__Language Results:__**\n" +
                         "\n".join(lang_results) if results["lang"] else "") +\
            ("\n\n**__Library Results:__**\n" +
             "\n".join(lib_results) if results["libs"] else "")

        e.add_field(name="Didn't find what you were looking for?",
                    value=f'See more [`{query}` results]({url})', inline=False)

        await ctx.send(embed=e)

    @commands.command()
    async def cref(self, ctx, *, query: str):
        """Search for a C item on cppreference -- WIP, can be better"""

        results = self.find_results("c", query.replace("/", " ").strip())

        url = f'https://en.cppreference.com/mwiki/index.php?title=Special%3ASearch&search={parse.quote(query)}'

        e = discord.Embed()
        e.title = f"C Search Results for **`{query}`**"
        e.color = discord.Color.blurple()  # Subject to change

        lang_results = []
        lib_results = []

        if results["lang"]:
            for i in results["lang"]:
                lang_results.append(
                    f"[`({i[0]}) {'/'.join(i[1:])}`](http://en.cppreference.com/w/c/{'/'.join(i)})")

        if results["libs"]:
            for i in results["libs"]:
                lib_results.append(
                    f"[`({'/'.join(i[:-1])}) {i[-1]}`](http://en.cppreference.com/w/c/{'/'.join(i)})")

        e.description = ("\n\n**__Language Results:__**\n" +
                         "\n".join(lang_results) if results["lang"] else "") + \
            ("\n\n**__Library Results:__**\n" +
             "\n".join(lib_results) if results["libs"] else "")

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
