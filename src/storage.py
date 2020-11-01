import contextlib
import json
from pathlib import Path

from cue import subscribe
from model import Application, Device


def _serialize(device):
    return {}


@contextlib.contextmanager
def _open(write=True):
    filename = Path('devices.json')
    if write:
        mode = 'w+'
    else:
        filename.touch(exist_ok=True)
        mode = 'r'

    with filename.open(mode) as devices_file:
        try:
            devices_dict = json.load(devices_file)
        except json.decoder.JSONDecodeError:
            devices_dict = {}
        yield devices_dict
        if write:
            json.dump(devices_dict, devices_file)


@subscribe(Application.devices.__delitem__)
def _on_device_delitem(_, device_uid):
    with _open() as devices_dict:
        devices_dict.pop(device_uid.hex(), None)


@subscribe(Application.devices.__setitem__)
def _on_devices_setitem(devices, device_uid, device):
    if not device.is_known:
        return

    with _open() as devices_dict:
        devices_dict[device_uid.hex()] = _serialize(device)


@subscribe(Device.change)
def _on_device_change(device):
    with _open() as devices_dict:
        if device.is_known:
            devices_dict[device.uid.hex()] = _serialize(device)
        else:
            devices_dict.pop(device.uid.hex(), None)


@subscribe(Application.__init__)
def load(application):
    with _open(write=False) as devices_dict:
        for device_uid_hex, device_dict in devices_dict.items():
            device_uid = bytes.fromhex(device_uid_hex)
            application.devices[device_uid] = Device(
                uid=device_uid,
                is_available=False,
                ip="",
                is_known=True
            )
