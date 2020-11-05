import asyncio

import deployer.listener
import pexpect as pexpect
import pytest
import sys
import time


@pytest.fixture
def advertiser() -> pexpect.spawn:
    _advertiser = pexpect.spawnu(
        command="micropython",
        cwd="../micropython-device/",
        args=[
            "-c",
            "import deployer.advertiser;deployer.advertiser.run('239.1.1.1', 35550, 1, b'unique_id', 35551)"
        ],
        logfile=sys.stderr,
    )
    time.sleep(1)
    assert _advertiser.isalive(), (_advertiser.exitstatus, _advertiser.stderr.read())
    yield
    _advertiser.terminate()


@pytest.fixture
def application():
    return deployer.model.Application()


@pytest.mark.asyncio
async def test_listener(advertiser, application):
    asyncio.create_task(deployer.listener.run(application))
    await asyncio.sleep(2)
    assert len(application.devices) == 1
    device_uid, device = list(application.devices.items())[0]
    assert device_uid == device.uid == b'unique_id'
    assert device.ip
    assert device.port == 35550
