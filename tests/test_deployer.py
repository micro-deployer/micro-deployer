import asyncio
from io import BytesIO
from pathlib import Path
import socket

import pexpect as pexpect
import pytest
import sys
import time

import deployer.deployer
from deployer.model import Device


@pytest.fixture
def device_tmp_path(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("device_root")

@pytest.fixture
def free_tcp_port() -> int:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port


@pytest.fixture
def deployer_device_port(device_tmp_path: Path, free_tcp_port: int) -> int:
    micropython_device = Path(__file__).parent.parent.parent / Path("micropython-device/src")
    _deployer_server = pexpect.spawnu(
        command="micropython",
        cwd=str(device_tmp_path),
        args=[
            "-c",
            f"import sys;sys.path.append('{micropython_device.absolute()}');import deployer;deployer.run({free_tcp_port})"
        ],
        logfile=sys.stderr,
    )
    time.sleep(1)
    assert _deployer_server.isalive(), (
        _deployer_server.exitstatus, _deployer_server.stderr.read()
    )
    yield free_tcp_port
    _deployer_server.terminate()


@pytest.fixture
def application() -> deployer.model.Application():
    return deployer.model.Application()


@pytest.fixture
def root_path() -> Path:
    return Path(__file__).parent / Path("device_data")


def test_deployer_write(root_path: Path):
    writer = BytesIO()
    assert list(map(str, deployer.deployer._write(writer, root_path))) == [
        "file.txt",
        "directory/file.txt",
    ]


@pytest.mark.asyncio
async def test_deployer_deploy(root_path: Path, device_tmp_path: Path, deployer_device_port: int):
    device = Device(uid=b'unique_id', ip="127.0.0.1", port=deployer_device_port, root_path=root_path)
    asyncio.create_task(deployer.deployer.deploy(device))
    await asyncio.sleep(2)
    assert [str(path.relative_to(device_tmp_path)) for path in device_tmp_path.glob("**/*") if path.is_file()] == [
        "file.txt",
        "directory/file.txt",
    ]