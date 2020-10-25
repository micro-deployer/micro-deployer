import contextlib
import json

from cue import subscribe
from model import Application, Device


class DeviceStorage:

    @contextlib.contextmanager
    def _update(self):
        with open('devices.json') as devices_file:
            devices_dict = json.load(devices_file)
            yield devices_dict
            json.dump(devices_dict, devices_file)

    @subscribe.after(Application.devices.__setitem__)
    def _on_device_setitem(self, _, device):
        with open('devices.json') as devices_file:
            devices_dict = json.load(devices_file)
            yield devices_dict
            json.dump(devices_dict, devices_file)

    @subscribe.after(Application.devices.__delitem__)
    def _on_device_delitem(self, _, device):
        with self._update() as devices_dict:
            del devices_dict[device.id]

    @subscribe.after(Device.change)
    def _on_device_change(self, device):
        with self._update() as devices_dict:
            devices_dict[device.id] = device
