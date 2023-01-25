import discord

from src import config as conf

def timestamp(msg: discord.Message):
    return msg.edited_at if msg.edited_at is not None else msg.created_at

def into_embeds_chunks(history: list[discord.Message]):
    author = history[0].author.display_name
    avatar = history[0].author.display_avatar

    embeds: list[tuple[int, discord.Embed]] = []
    for state in reversed(history):
        embed = discord.Embed(description=state.content, timestamp=timestamp(state)).set_author(name=author, icon_url=avatar)
        embeds.append((len(state.content) + len(author), embed))

    messages: list[list[discord.Embed]] = [[]]

    cur_length = 0
    for (length, embed) in embeds:
        if cur_length + length > conf.max_msg_embeds_size or len(messages[-1]) >= 10:
            messages.append([embed])
            cur_length = length
        else:
            messages[-1].append(embed)
            cur_length += length

    return messages
    
