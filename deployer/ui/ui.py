import asyncio
from collections import defaultdict
import dataclasses
from pathlib import Path
from typing import Any, Callable, List, Optional

from PySide6 import QtCore
from PySide6.QtCore import QModelIndex
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from cue import subscribe
from deployer.model import Application, Device, DeviceDict, DeviceUID





ProgressRole = QtCore.Qt.UserRole + 1


class TableModel(QtCore.QAbstractTableModel):
    class Columns:
        class SavedColumn:
            label = "Saved"
            fields = ["is_known"]

            def display(self, device):
                return device.is_known

            def edit(self, device, is_known):
                device.is_known = is_known

        class NameColumn:
            label = "Name"
            fields = ["name"]

            def display(self, device):
                return device.name

            def edit(self, device, name):
                device.name = name

        class UIDColumn:
            label = "UID"
            fields = ["uid"]

            def display(self, device):
                return device.uid.hex(":", 1)

        class RootPathColumn:
            label = "Root path"
            fields = ["root_path"]

            def display(self, device):
                return str(device.root_path) if device.root_path else ""

            def edit(self, device, root_path):
                device.root_path = Path(root_path)

        class IsAvailableColumn:
            label = "Available"
            fields = ["is_available"]

            def display(self, device):
                return device.is_available


        class DeployColumn:
            label = "Deploy"
            fields = [
                "is_available",
                "root_path",
                "deployment_total",
                "deployment_progress"
            ]

            def display(self, device):
                return device.is_available and bool(device.root_path) and (
                    device.deployment_total is None or device.deployment_progress == device.deployment_total)

        class ProgressColumn:
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

    columns = dict(
        enumerate(
            column()
            for field_name, column in vars(Columns).items()
            if type(column) == type
        )
    )
    col_indexes_by_field_name = defaultdict(list)
    for index, column in columns.items():
        for field_name in column.fields:
            col_indexes_by_field_name[field_name].append(index)

    def __init__(self, data):
        super().__init__()
        self._data = data
        self.has_header = True

    def roleNames(self):
        return {
            **super().roleNames(),
            ProgressRole: b"progress",
        }

    def get_row_data(self, row_index):
        if self.has_header:
            data_index = row_index - 1
        else:
            data_index = row_index

        key = list(self._data.keys())[data_index]
        return self._data[key]

    def get_row_index(self, key):
        row_index = list(self._data.keys()).index(key)
        if self.has_header:
            return row_index + 1
        return row_index

    def data(self, index, role):
        if self.has_header and index.row() == 0:
            return self.header_data(index.column(), role)
        device = self.get_row_data(index.row())
        column = self.columns[index.column()]
        if role == QtCore.Qt.DisplayRole:
            try:
                return column.display(device)
            except AttributeError:
                return None
        elif role == ProgressRole:
            try:
                return column.progress(device)
            except AttributeError:
                return None
        return None

    def setData(self, index, value, role) -> bool:
        device = self.get_row_data(index.row())
        column = self.columns[index.column()]
        try:
            column.edit(device, value)
        except AttributeError:
            pass
        return True

    def header_data(self, col_index, role):
        """ Set the headers to be displayed. """
        if role != QtCore.Qt.DisplayRole:
            return None

        return self.columns[col_index].label

    def rowCount(self, index):
        # The length of the outer list.
        row_count = len(self._data)
        if self.has_header:
            return row_count + 1
        return row_count

    def columnCount(self, index):
        return len(self.columns)

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


class ApplicationProxy(QtCore.QObject):
    def __init__(self, application: Application) -> None:
        super().__init__()
        self._application = application
        self._devices = TableModel(application.devices)

    @QtCore.Slot()
    def stop(self) -> None:
        self._application.stop()

    @QtCore.Property(QtCore.QObject)
    def devices(self) -> TableModel:
        return self._devices

    @QtCore.Slot(int)
    def deploy(self, device_index: int):
        device = self._devices.get_row_data(device_index)
        asyncio.create_task(device.deploy())


async def run(application: Application) -> None:
    app = QApplication([])
    qml_filepath = str(Path(__file__).parent / "window.qml")
    engine = QQmlApplicationEngine()

    # bind model
    context = engine.rootContext()
    application_proxy = ApplicationProxy(application)
    context.setContextProperty("application", application_proxy)

    # import_paths = engine.importPathList()
    # import_paths.append('/usr/lib/qt/qml')
    # engine.setImportPathList(import_paths)
    QQuickStyle.setStyle('Imagine')
    engine.load(qml_filepath)

    while application.is_running:
        app.processEvents()
        await asyncio.sleep(0.01)
