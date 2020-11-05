from __future__ import annotations

import asyncio
import contextlib
import socket
import struct
from typing import Tuple

from deployer.model import Application, DeviceUID


def _multicast_socket(multicast_group: str, port: int) -> socket.socket:
    server_address = ('', port)

    # Create the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind to the server address
    sock.bind(server_address)

    group = socket.inet_aton(multicast_group)
    member_info = struct.pack('=4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, member_info)
    return sock


MULTICAST_GROUP = '239.1.1.1'
MULTICAST_PORT = 35550


def device_set_unavailable(device):
    device.is_available = False


class Protocol:
    def __init__(self, application: Application) -> None:
        self.application = application
        self.future_device_set_unavailable = {}

    def connection_made(self, _) -> None:
        pass

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        advertise_sleep = data[0]
        port = int.from_bytes(data[1:3], byteorder="big", signed=False)
        device_uid = DeviceUID(data[3:])
        device = self.application.devices.add(device_uid, ip=addr[0], port=port)
        with contextlib.suppress(KeyError):
            self.future_device_set_unavailable[device_uid].cancel()
        self.future_device_set_unavailable[device_uid] = asyncio.get_event_loop().call_later(
            advertise_sleep * 2,
            device_set_unavailable,
            device
        )


async def run(application: Application) -> None:
    loop = asyncio.get_event_loop()
    sock = _multicast_socket(MULTICAST_GROUP, MULTICAST_PORT)
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: Protocol(application),
        sock=sock
    )
    await application
