import asyncio

import test_listener
import storage
from model import Application
import ui


async def print_devices(application):
    while True:
        print(application.devices)
        await asyncio.sleep(5)


async def amain():
    application = Application()
    asyncio.create_task(print_devices(application))
    asyncio.create_task(ui.run(application))
    asyncio.create_task(test_listener.run(application))

    await application


asyncio.run(amain())
