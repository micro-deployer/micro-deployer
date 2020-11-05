import asyncio
from io import BytesIO
from pathlib import Path

import pexpect as pexpect
import pytest
import sys
import time

import deployer.deployer
from deployer.model import Device


@pytest.fixture
def device_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("device_root")


@pytest.fixture
def deployer_server(device_tmp_path) -> pexpect.spawn:
    micropython_device = Path(__file__).parent.parent.parent / Path("micropython-device")
    _deployer_server = pexpect.spawnu(
        command="micropython",
        cwd=str(device_tmp_path),
        args=[
            "-c",
            f"import sys;sys.path.append('{micropython_device.absolute()}');import deployer.deployer;deployer.deployer.run(35551)"
        ],
        logfile=sys.stderr,
    )
    time.sleep(1)
    assert _deployer_server.isalive(), (
        _deployer_server.exitstatus, _deployer_server.stderr.read()
    )
    yield
    _deployer_server.terminate()


@pytest.fixture
def application():
    return deployer.model.Application()


@pytest.fixture
def root_path():
    return Path(__file__).parent / Path("device_data")


def test_deployer_write(root_path):
    writer = BytesIO()
    assert list(map(str, deployer.deployer._write(writer, root_path))) == [
        "file.txt",
        "directory/file.txt",
    ]


@pytest.mark.asyncio
async def test_deployer_deploy(root_path, device_tmp_path, deployer_server):
    device = Device(uid=b'unique_id', ip="127.0.0.1", port=35551, root_path=root_path)
    asyncio.create_task(deployer.deployer.deploy(device))
    await asyncio.sleep(2)
    assert [str(path.relative_to(device_tmp_path)) for path in device_tmp_path.glob("**/*") if path.is_file()] == [
        "file.txt",
        "directory/file.txt",
    ]