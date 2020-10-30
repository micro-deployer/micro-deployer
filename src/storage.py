import contextlib
import json

from cue import subscribe
from model import Application, Device


class DeviceStorage:

    def serialize(self, device):
        return {}

    @contextlib.contextmanager
    def _update(self):
        with open("devices.json", "w+") as devices_file:
            try:
                devices_dict = json.load(devices_file)
            except json.decoder.JSONDecodeError:
                devices_dict = {}
            yield devices_dict
            json.dump(devices_dict, devices_file)

    @subscribe(Application.devices.__delitem__)
    def _on_device_delitem(self, _, device_uid):
        with self._update() as devices_dict:
            devices_dict.pop(device_uid.hex(), None)

    @subscribe(Application.devices.__setitem__)
    def _on_device_change(self, devices, device):
        if not device.is_known:
            return

        with self._update() as devices_dict:
            devices_dict[device.uid.hex()] = self.serialize(device)

    @subscribe(Device.change)
    def _on_device_change(self, device):
        with self._update() as devices_dict:
            if device.is_known:
                devices_dict[device.uid.hex()] = self.serialize(device)
            else:
                devices_dict.pop(device.uid.hex(), None)

    print('before subscribe init')
    @subscribe(Application.__init__)
    def load(self, application):
        with self._update() as devices_dict:
            for device_uid_hex, device_dict in devices_dict.items():
                device_uid = bytes.fromhex(device_uid_hex)
                application.devices[device_uid] = Device(
                    uid=device_uid,
                    is_available=False,
                    ip="",
                    is_known=True
                )

# print(DeviceStorage)

async def run(application):
    storage = DeviceStorage()
    await application
