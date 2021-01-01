import asyncio

from cue import publisher, subscribe
from deployer.models.device import DeviceDict
from deployer.models.role import Role, RoleDict


class Application:
    devices = DeviceDict()
    roles = RoleDict()

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

    @subscribe.before(RoleDict.__delitem__)
    @classmethod
    def _on_role_delitem(cls, role_dict: RoleDict, role_name: str):
        for device in cls.devices.values():
            if device.role.name is role_name:
                raise ValueError("Device {device} uses the role '{role_name}'.")
