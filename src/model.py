import asyncio
import dataclasses
from typing import NewType, Optional

from cue import CueDict, publisher, subscribe

DeviceID = NewType("DeviceID", bytes)


@publisher
@dataclasses.dataclass
class Device:
    uid: DeviceID
    name: str = ""
    ip: str = ""
    port: int = 0
    is_known: bool = False
    is_available: bool = False
    deployment_progress: Optional[int] = None

    @publisher
    def change(self):
        pass


@subscribe(Device.uid)
@subscribe(Device.ip)
@subscribe(Device.name)
@subscribe(Device.is_available)
@subscribe(Device.is_known)
@subscribe(Device.deployment_progress)
def _change(device, *_args):
    device.change()


class DeviceDict(CueDict):
    @subscribe(Device.is_known)
    @subscribe(Device.is_available)
    def _on_change(self, device, value):
        if not device.is_known and not device.is_available:
            del self[device.uid]

    def add(self, device_id, ip, port) -> None:
        try:
            device = self[device_id]
        except KeyError:
            device = Device(
                uid=device_id,
                ip=ip,
                port=port,
                is_available=True,
            )
            self[device_id] = device
        else:
            device.ip = ip
            device.port = port
            device.is_available = True
        return device


class Application:
    devices = DeviceDict()

    @publisher
    def __init__(self) -> None:
        self._stopped = asyncio.Event()

    def stop(self) -> None:
        self._stopped.set()

    @property
    def is_running(self) -> bool:
        return not self._stopped.is_set()

    @is_running.setter
    def is_running(self, value: bool) -> None:
        if value:
            self._stopped.set()
        else:
            self._stopped.clear()

    def __await__(self):
        return self._stopped.wait().__await__()
