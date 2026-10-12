import asyncio
from tools import LoggerManager, print_handler
from tools.config import ConfigLoader


async def setup():
    LoggerManager().add_handler(print_handler)
    ConfigLoader().load('config/')


async def loop():
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(setup())
    asyncio.run(loop())
