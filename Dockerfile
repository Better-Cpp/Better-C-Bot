FROM python:latest

#RUN python3 py3-pip py3-lxml py3-yarl py3-chardet py3-aiohttp py3-attrs

RUN apt update -y \
    && apt install clang-format python-levenshtein -y
RUN adduser --disabled-password --gecos "" bettercbot
USER bettercbot
WORKDIR /home/bettercbot
ENV PATH="/home/bettercbot/.local/bin:$PATH"

COPY --chown=bettercbot:bettercbot src/cppref src/cppref

COPY --chown=bettercbot:bettercbot requirements.txt requirements.txt
RUN pip install --user -r requirements.txt

# discord.py dependencies seem broken, idk
RUN pip install --user -U aiohttp
RUN pip install --user -U discord.py

COPY --chown=bettercbot:bettercbot token.txt token.txt
COPY --chown=bettercbot:bettercbot badwords.txt badwords.txt
COPY --chown=bettercbot:bettercbot src/util src/util
COPY --chown=bettercbot:bettercbot src/cogs/ src/cogs
COPY --chown=bettercbot:bettercbot src/backend src/backend
COPY --chown=bettercbot:bettercbot src/config.py src/config.py
COPY --chown=bettercbot:bettercbot src/__main__.py src/__main__.py

CMD ["python", "-m", "src"]
