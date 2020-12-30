import asyncio
import dataclasses
from pathlib import Path
from typing import NewType, Optional

from cue import CueDict, publisher, subscribe

DeviceUID = NewType("DeviceUID", bytes)


@publisher
@dataclasses.dataclass
class Device:
    uid: DeviceUID
    name: str = ""
    ip: str = ""
    port: int = 0
    root_path: Optional[Path] = None
    is_known: bool = False
    is_available: bool = False
    deployment_progress: Optional[int] = None

    @publisher
    def change(self, field_name, value):
        pass


@subscribe(Device.uid)
def _change_uid(device, value):
    device.change('uid', value)

@subscribe(Device.ip)
def _change_ip(device, value):
    device.change('ip', value)

@subscribe(Device.name)
def _change_name(device, value):
    device.change('name', value)

@subscribe(Device.is_available)
def _change_is_available(device, value):
    device.change('is_available', value)

@subscribe(Device.is_known)
def _change_is_known(device, value):
    device.change('is_known', value)

@subscribe(Device.deployment_progress)
def _change_deployment_progress(device, value):
    device.change('deployment_progress', value)

@subscribe(Device.root_path)
def _change_root_path(device, value):
    device.change('root_path', value)

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
