import contextlib
import json

from cue import subscribe
from model import Application, Device


class DeviceStorage:

    def serialize(self, device):
        return {
            "ip": device.ip,
            "is_available": device.is_available,
            "is_known": device.is_known,
        }

    @contextlib.contextmanager
    def _update(self):
        with open("devices.json", "w+") as devices_file:
            try:
                devices_dict = json.load(devices_file)
            except json.decoder.JSONDecodeError:
                devices_dict = {}
            yield devices_dict
            json.dump(devices_dict, devices_file)

    @subscribe.after(Application.devices.__delitem__)
    def _on_device_delitem(self, _, device):
        with self._update() as devices_dict:
            del devices_dict[device.uid_hex]

    @subscribe.after(Application.devices.__setitem__)
    def _on_device_change(self, devices, device):
        if not device.is_known:
            return

        with self._update() as devices_dict:
            devices_dict[device.uid_hex] = self.serialize(device)

    @subscribe.after(Device.change)
    def _on_device_change(self, device):
        try:
            device.is_known
        except Exception:
            return
        with self._update() as devices_dict:
            if device.is_known:
                devices_dict[device.uid_hex] = self.serialize(device)
            else:
                devices_dict.pop(device.uid_hex, None)


async def run(application):
    storage = DeviceStorage()
    await application
