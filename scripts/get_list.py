import os
import glob


def get_lists():
    specials = ["named_req", "language", "keyword", "header",
                "concepts", "types", "preprocessor", "keywords", "experimental"]  # experimental is annoying to include
    with open("src/cppref/cpplibs.txt", "w+") as libs:
        dirs = glob.iglob("src/cppref/cpp/**", recursive=True)
        dirs = (a.replace("\\", "/").replace(".html", "") for a in dirs)
        for a in dirs:
            if not a.split("/")[3] in specials:
                libs.write(a[15:].replace("/", " ") + '\n')

    with open("src/cppref/cpplang.txt", "w+") as lang:
        dirs = glob.iglob("src/cppref/cpp/**", recursive=True)
        dirs = (a.replace("\\", "/").replace(".html", "") for a in dirs)
        for a in dirs:
            if a.split("/")[3] in specials:
                lang.write(a[15:].replace("/", " ") + '\n')

    with open("src/cppref/clibs.txt", "w+") as libs:
        dirs = glob.iglob("src/cppref/c/**", recursive=True)
        dirs = (a.replace("\\", "/").replace(".html", "") for a in dirs)
        for a in dirs:
            if not a.split("/")[3] in specials:
                libs.write(a[13:].replace("/", " ") + '\n')

    # Sigh
    with open("scripts/cheaders.txt", "r") as libsource:
        with open("src/cppref/clang.txt", "w+") as lang:
            for line in libsource:
                lang.write("header " + line)

            dirs = glob.iglob("src/cppref/c/**", recursive=True)
            dirs = (a.replace("\\", "/").replace(".html", "") for a in dirs)
            for a in dirs:
                if a.split("/")[3] in specials:
                    lang.write(a[13:].replace("/", " ") + '\n')


get_lists()
