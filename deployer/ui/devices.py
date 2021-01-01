from typing import Any

from PySide6 import QtCore
from PySide6.QtCore import QModelIndex

from cue import subscribe
from deployer.models.application import Application
from deployer.models.device import Device, DeviceDict, DeviceUID
from deployer.ui.base import BaseModel

ProgressRole = QtCore.Qt.UserRole + 1


class DevicesModel(BaseModel):
    class Columns:
        class IsSaved:
            label = "Saved"
            fields = ["is_known"]

            def display(self, device):
                return device.is_known

            def edit(self, device, is_known):
                device.is_known = is_known

        class Name:
            label = "Name"
            fields = ["name"]

            def display(self, device):
                return device.name

            def edit(self, device, name):
                device.name = name

        class UID:
            label = "UID"
            fields = ["uid"]

            def display(self, device):
                return device.uid.hex(":", 1)

        class IsAvailable:
            label = "Available"
            fields = ["is_available"]

            def display(self, device):
                return device.is_available

        class Deploy:
            label = "Deploy"
            fields = [
                "is_available",
                # "root_path",
                "deployment_total",
                "deployment_progress"
            ]

            def display(self, device):
                return device.is_available and (
                    device.deployment_total is None or device.deployment_progress == device.deployment_total)

        class Progress:
            label = "Progress"
            fields = [
                "deployment_total", "deployment_progress", "deployment_exception"
            ]

            def display(self, device):
                if device.deployment_progress == device.deployment_total and device.deployment_exception is None:
                    return "OK"
                return device.deployment_exception or ""

            def progress(self, device):
                return device.deployment_progress * 100 / device.deployment_total if device.deployment_total else None

    def roleNames(self):
        return {
            **super().roleNames(),
            ProgressRole: b"progress",
        }

    @subscribe(Application.devices.__setitem__)
    def on_devices_setitem(
        self,
        devices: DeviceDict,
        device_id: DeviceUID,
        _device: Device
    ) -> None:
        row_index = self.get_row_index(device_id)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.endInsertRows()

    @subscribe.before(Application.devices.__delitem__)
    def on_devices_delitem(self, devices: DeviceDict, device_id: DeviceUID) -> None:
        row_index = self.get_row_index(device_id)
        self.beginRemoveRows(QModelIndex(), row_index, row_index)
        self.endRemoveRows()

    @subscribe.before(Device.change)
    def on_device_change(self, device: Device, field_name: str, value: Any) -> None:
        row_index = self.get_row_index(device.uid)
        for col_index in self.col_indexes_by_field_name[field_name]:
            self.dataChanged.emit(
                self.createIndex(row_index, col_index),
                self.createIndex(row_index, col_index),
                {QtCore.Qt.DisplayRole, ProgressRole}
            )
