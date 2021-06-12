from discord.ext import commands
import urllib.parse as parse
import discord
import subprocess
import re
import io
import datetime

_code_block_regex = re.compile(r"\s?```(c|cpp|cxx|cc)?\n([\s\S]+?)```\s?", re.I | re.M)
_inline_code_regex = re.compile(r"(?<!`)(``?)(?!`)(.+?)(?<!`)\1(?!`)", re.M)

def _clang_format(code, style: str = None):
    valid_styles = ["llvm", "gnu", "google", "chromium", "microsoft", "mozilla", "webkit"]

    command = ["/usr/bin/clang-format"]
    if style in valid_styles:
        command.extend(["--style", style])

    return subprocess.run(command, input=code, capture_output=True, text=True).stdout

def _create_format_body(non_code_list, code_list):
    result = ""
    for non_code, code in zip(non_code_list, code_list):
        result += non_code
        result += f"```c\n{code}```"
    result += non_code_list[-1]

    return result

def _create_alt_format_body(non_code_list, code_list):
    result = ""

    # if there's no non-code, just return empty string
    # because there's no point in signifying where the
    # code blocks were if the original text was solely code blocks
    if len("".join(non_code_list).strip()) == 0:
        return result

    for i, (non_code, _) in enumerate(zip(non_code_list, code_list)):
        result += non_code
        result += f"\n[Block #{i + 1}]\n"
    result += non_code_list[-1]

    return result

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
    @commands.command(aliases=["f"])
    async def format(self, ctx: commands.Context, style = None):
        """Format C or C++ code in the message you are replying to. Usage: !format [style]"""

        target_msg: discord.Message = ctx.message.reference and ctx.message.reference.resolved
        if target_msg == None:
            await ctx.send("You must reply to an existing message with this command in order to format it.")
            return

        # This will be for when support for formatting attached text files is added.
        text_attachments = [x for x in ctx.message.attachments if x.content_type.startswith("text/")]

        # Convert inline code into code blocks, if any exist they will be formatted in the next part of the code.
        processed = target_msg.content
        inline_code_matches = list(_inline_code_regex.finditer(processed))

        for match in reversed(inline_code_matches):
            start_inner = match.start(2)
            end_inner = match.end(2)
            processed = f"{processed[:match.start()]}```\n{processed[start_inner:end_inner]}```{processed[match.end():]}"

        code_block_matches = list(_code_block_regex.finditer(processed))

        # array of non-code related text
        non_code = []
        # array of code block contents
        code = []

        if len(code_block_matches) != 0:
            last_end = 0

            for match in code_block_matches:
                # Start and end of group 2 of the match, which is the inner part of the inline code
                start_inner = match.start(2)
                end_inner = match.end(2)

                formatted_code = _clang_format(processed[start_inner:end_inner], style)
                non_code.append(processed[last_end:match.start()])
                code.append(formatted_code)
                last_end = match.end()

            non_code.append(processed[last_end:])
        else:
            formatted_code = _clang_format(target_msg.content, style)
            non_code = ["", ""]
            code = [formatted_code]

        if ctx.message.author != target_msg.author:
            name_target_author = f"{target_msg.author}'s"
        else:
            name_target_author = "Your"

        result = f"{name_target_author} formatted code:\n{_create_format_body(non_code, code)}"

        if len(result) <= 4000:
            await ctx.send(result)
        else:
            if len(code) <= 10:
                files_ = [io.StringIO(x) for x in code]
                files = [discord.File(f, f"block_{i + 1}.cpp") for i, f in enumerate(files_)]
            else:
                file = io.StringIO()
                for i, c in enumerate(code):
                    file.write(f"/* [Block #{i + 1}] */\n{c}\n")
                files_ = [file]
                files = [discord.File(file, "formatted_code.cpp")]

            result = f"{name_target_author} formatted code:\n{_create_alt_format_body(non_code, code)}"

            await ctx.send(result, files=files)
        if (datetime.datetime.now() - target_msg.created_at).total_seconds() <= 7200:
            await target_msg.delete();

def setup(bot):
    bot.add_cog(cpp(bot))
