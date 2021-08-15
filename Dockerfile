FROM alpine:3.13.5

RUN apk update \
    && apk add clang gcc \
    python3 py3-pip py3-lxml py3-yarl py3-chardet py3-aiohttp py3-attrs

RUN adduser -D bettercbot
USER bettercbot
WORKDIR /home/bettercbot
ENV PATH="/home/bettercbot/.local/bin:$PATH"

COPY --chown=bettercbot:bettercbot src/cppref src/cppref

COPY --chown=bettercbot:bettercbot requirements.txt requirements.txt
RUN python3 -m pip install --prefer-binary --user -r requirements.txt

COPY --chown=bettercbot:bettercbot token.txt token.txt
COPY --chown=bettercbot:bettercbot badwords.txt badwords.txt
COPY --chown=bettercbot:bettercbot src/__main__.py src/__main__.py
COPY --chown=bettercbot:bettercbot src/cogs/ src/cogs
COPY --chown=bettercbot:bettercbot src/backend src/backend
COPY --chown=bettercbot:bettercbot src/config.py src/config.py


CMD ["python3", "-m", "src"]
