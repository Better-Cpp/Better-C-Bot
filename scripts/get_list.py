# TODO
# if the file has a directory of the same name in the current directory, it is likely a class
# Put identifiers before the thing telling what it is (class, namespace, header, etc.)
# Find a way for stuff like string instead of basic_string in the display
## there are htmls of each directory
## Each item declared in a header is a .t-dsc in the html file
#
# Use json for this
#
# cpp
#
# namespaces: [ done
#   chrono: [...],
#   ...
# ],
# headers: [ in progress
#    <header>: { done
#       classses: { not done
#           <class>: [ members ]
#        },
#       members: []
#    }
# ],
# aliases: [ done
#   string: basic_string,
#   ...
# ],
# language concepts: { done
#   stuff
# }
# find a way to get the classes
#
# c
#
# headers
# index of everything
# keywords
# language

import re
import json

from bs4 import BeautifulSoup, NavigableString

######################
###### BOTH ##########
######################


def get_language_concepts(lang):
    with open(f"src/cppref/{lang}/language.html", "r") as file:
        language = BeautifulSoup(file, "html.parser")

    categories = language.find_all("table", attrs={"cellpadding": "5"})
    symbols = (i.find_all("a") for i in categories)

    ret = {}
    for i in symbols:
        for x in i:
            if "cppreference.com" in x.get("href"):
                continue

            ret[x.get_text(" ", strip=True)] = x.get("href").replace(".html", "")
    if lang == "cpp":
        with open(f"scripts/cpp/language.json", "w+") as file:
            json.dump(ret, file, indent=4)

    return ret


# Cleans some content up
def get_content(tag):
    content_str = ""

    if tag.parent.get("class"):
        if "mw-geshi" in tag.parent.get("class"):
            for i in tag.parent.contents:
                try:
                    content_str += i.get_text(strip=True)
                except:
                    content_str += i
        else:
            content_str = tag.get_text(strip=True)

    elif tag.contents[0]:
        for child in tag.contents:
            try:
                if "t-lines" in child.get("class"):
                    for i in child.contents:
                        content_str += i.get_text(strip=True) + "\n"
                    continue
            except:
                pass
            try:
                if child.find(attrs={"class": "t-dsc-small"}):
                    content_str += child.get_text(strip=True)
                    continue
            except:
                pass

            try:
                content_str += child.get_text("\n", strip=True)
            except:
                pass

    if "[edit]" in content_str.lower():
        return None
    return content_str.lower()


#####################
######## CPP ########
#####################


def get_namespace_members(namespace):
    with open(f"src/cppref/cpp/symbol_index/{namespace}.html") as file:
        name_index = BeautifulSoup(file, "html.parser")

    categories = name_index.find_all("p")
    members = (i.find_all("a") for i in categories)

    ret = []
    for i in members:
        for x in i:
            desc = x.string

            if not desc:
                continue

            desc = desc.replace("()", "").replace("<>", "")

            # Some things are not in this local stuff...
            if "cppreference.com" in desc:
                continue

            ret.append(desc)

    return ret


# Call in main function
def get_aliases():
    with open("src/cppref/cpp/symbol_index.html", "r") as file:
        std_index = BeautifulSoup(file, "html.parser")

    ret = {}
    categories = std_index.find_all("p")
    symbols = (i.find_all("a") for i in categories)

    for i in symbols:
        for x in i:
            if "cppreference.com" in x.get("href"):
                continue
            link_name = x.get("href").split("/")[-1].replace(".html", "")
            true_name = x.string.replace("()", "").replace("<>", "")
            if true_name != link_name:
                ret[true_name] = x.get("href").replace(".html", "")

    return ret


# Call in main function
def get_cpp_headers():
    with open(f"src/cppref/cpp/header.html", "r") as file:
        header_list = BeautifulSoup(file, "html.parser")

    categories = header_list.find_all(attrs={"class": "t-dsc"})
    headers = (i.find("a") for i in categories)

    ret = {}
    for i in headers:
        if i:
            if " " in i.get_text() or "cppreference.com" in i.get("href"):
                continue
            ret[i.get_text().replace("<", "").replace(">", "")] = i.get("href")

    return ret


# Only needed in C++ because C is nice :)
def get_header_contents(header):
    ret = {"classes": [""], "members": [""]}

    with open(f"src/cppref/cpp/header/{header}.html") as file:
        soup = BeautifulSoup(file, "html.parser")

    categories = soup.find_all(attrs={"class": "t-dsc"})
    headers = (i.find_all("a") for i in categories)

    # CBA to do edge cases, so we have try except
    try:
        classes_section = list(soup.find(id="Classes").parent.next_siblings)[
            1
        ].find_all("a")

        for i in classes_section:
            content = get_content(i)
            if content:
                for item in content.split("\n"):
                    if item:
                        ret["classes"].append(item)
    except:
        pass

    for i in headers:
        for x in i:
            if not x:
                continue
            if " " in x.get_text(" ", strip=True) or "[edit]" in x.get_text(strip=True):
                continue

            content = get_content(x)

            if content in ret["classes"]:
                continue

            if not content:
                content = x.get_text(strip=True)

            for item in content.split("\n"):
                if not item:
                    continue
                # avoid the included headers
                if item[0] == "<" and item[-1] == ">":
                    continue

                # if it's already there
                if item in ret["members"][-1]:
                    continue
                ret["members"].append(item)

    ret["classes"].pop(0)
    ret["members"].pop(0)
    return ret


def get_class_members(class_name):
    ret = [""]
    with open("scripts/cpp/headers.json", "r") as file:
        classes_with_headers = json.load(file)

    header_name = ""
    for key, value in classes_with_headers.items():
        if class_name in value:
            header_name = key

    with open(f"src/cppref/cpp/{header_name}/{class_name}.html", "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    categories = soup.find_all(attrs={"class": "t-dsc"})
    members = (i.contents for i in categories)

    for i in members:
        for x in i:
            if x == "\n" or not x:
                continue
            if " " in x.get_text(strip=True) or "[edit]" in x.get_text(strip=True):
                continue

            re_search = re.compile("\(.*[Cc]\+\+\w\w\)" + "|" + "\[static\]")

            content = get_content(x)

            for match in re_search.findall(content):
                content = content.replace(match, "")

            if not content:
                content = x.get_text(strip=True)

            for item in content.split("\n"):
                # avoid the included headers
                if item[0] == "<" and item[-1] == ">":
                    continue

                # if it's already there
                if item in ret[-1]:
                    continue
                ret.append(item)

    ret.pop(0)
    return ret


def get_cpp_indexes():
    # Get the namespaces and their members
    print("Dumping namespaces...")
    with open("src/cppref/cpp/symbol_index.html", "r") as file:
        std_index = BeautifulSoup(file, "html.parser")

    namespace_list = std_index.find(attrs={"class": "t-nv-begin"}).find_all(
        attrs={"class": "t-nv"}
    )

    namespaces = {}
    for i in namespace_list:
        space_name = i.text.replace("std::", "").split("(")[0]
        namespaces[space_name] = get_namespace_members(space_name)

    print("Done.")
    with open("scripts/cpp/namespaces.json", "w+") as file:
        json.dump(namespaces, file, indent=4)

    # Get the aliases
    print("Dumping aliases")
    with open("scripts/cpp/aliases.json", "w+") as file:
        json.dump(get_aliases(), file, indent=4)
    print("Done.")

    # Get all the headers
    print("Dumping headers and their contents...")
    headers = {}
    for i in get_cpp_headers():
        headers[i] = get_header_contents(i)

    with open("scripts/cpp/headers.json", "w+") as file:
        json.dump(headers, file, indent=4)
    print("Done.")

    # Get the classes and their items
    print("Dumping classes...")
    class_names = {}
    for i, x in headers.items():
        if not x["classes"]:
            continue

        class_names[i] = x["classes"]

    classes = {}
    for i in class_names:
        classes[i] = get_class_members(i)

    with open("scripts/cpp/classes.json", "w+") as file:
        json.dump(classes)
    print("Done.")


################################
############ C #################
################################

# C header list is a lot different
def get_c_headers():
    with open("src/cppref/c/header.html", "r") as file:
        soup = BeautifulSoup(file, "html.parser")

    header_list = soup.find_all(attrs={"class": "t-dsc"})

    ret = {}
    for i in header_list:
        if len(i.contents) < 4:
            continue

        key_str = ""
        for child in i.children:
            if child == "\n":
                continue

            if child.find("a"):
                ret[key_str] = child.find("a").get("href")
                key_str = ""
                continue

            for x in child:
                try:
                    if x.get("class"):
                        continue
                except:
                    pass
                try:
                    key_str += x.get_text(strip=True)
                except:
                    key_str += str(x).strip()

    return ret


def get_c_index():
    with open("src/cppref/c/index.html", "r") as file:
        index = BeautifulSoup(file, "html.parser")

    sections = index.find_all("p")
    links = (i.find_all("a") for i in sections)

    ret = {}
    for i in links:
        for x in i:
            ret[x.get_text()] = x.get("href").replace(".html", "")

    ret.update(get_language_concepts("c"))
    ret.update(get_c_headers())

    with open("scripts/c/index.json", "w+") as file:
        json.dump(ret, file, indent=4)


# get_aliases()
# get_namespaces_and_members()
# get_language_concepts("cpp")
# get_headers_and_contents("cpp")
# print(get_header_contents("cpp", "complex")["classes"])
print(list(get_class_members("string")))
# get_c_index()
