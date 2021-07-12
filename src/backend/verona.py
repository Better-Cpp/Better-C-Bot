import os

import docker
import asyncio

docker_client = docker.from_env()


def get_num_and_inc() -> int:
    with open("/opt/verona-bot/counter.txt", "r") as file:
        counter = int(file.read().strip())

    old = counter
    counter += 1

    with open("/opt/verona-bot/counter.txt", "w") as file:
        file.seek(0)
        file.truncate()
        file.write(str(counter))

    return old


def set_code(num: int, code: str):
    with open(f"/opt/verona-bot/input/{num}.verona", "a") as file:
        file.write(code.strip())


def get_output_path(num: int) -> str:
    return f"/opt/verona-bot/output/{num}.txt"


async def run_container(
    num: int, timeout_count: int = 30
) -> tuple[bool, str,]:
    container = docker_client.containers.run(
        "yuhanuncitgez/verona-bot:latest",
        f'/opt/verona-bot-scripts/run.sh "{num}"',
        stdout=True,
        stderr=True,
        auto_remove=True,
        detach=True,
        volumes={"/opt/verona-bot": {"bind": "/opt/verona-bot", "mode": "rw"}},
    )
    output_path = get_output_path(num)
    for _ in range(timeout_count + 1):
        if os.path.isfile(output_path):
            await asyncio.sleep(0.1)
            with open(output_path) as file:
                return True, file.read()
        await asyncio.sleep(1)

    container.kill()
    print("Timeout exceeded")
    return False, "Timeout exceeded: 30s\nDocker container killed."
