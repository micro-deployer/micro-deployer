import asyncio

import deployer.listener
import deployer.storage
from deployer.model import Application
import deployer.ui


async def print_devices(application):
    while True:
        print(application.devices)
        await asyncio.sleep(5)


async def amain():
    application = Application()
    asyncio.create_task(print_devices(application))
    asyncio.create_task(deployer.ui.run(application))
    asyncio.create_task(deployer.listener.run(application))

    await application


asyncio.run(amain())
