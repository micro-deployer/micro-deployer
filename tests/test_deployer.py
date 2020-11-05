import asyncio

import deployer.deployer
import pexpect as pexpect
import pytest
import sys
import time

from deployer.model import Device


@pytest.fixture
def deployer_server() -> pexpect.spawn:
    _deployer_server = pexpect.spawnu(
        command="micropython",
        cwd="../micropython-device/",
        args=[
            "-c",
            "import deployer.deployer;deployer.deployer.run(35551)"
        ],
        logfile=sys.stderr,
    )
    time.sleep(1)
    assert _deployer_server.isalive(), (_deployer_server.exitstatus, _deployer_server.stderr.read())
    yield
    _deployer_server.terminate()


@pytest.fixture
def application():
    return deployer.model.Application()


@pytest.mark.asyncio
async def test_deployer(deployer_server):
    device = Device(uid=b'unique_id', ip="127.0.0.1", port=35551)
    asyncio.create_task(deployer.deployer.deploy(device))
    await asyncio.sleep(2)

