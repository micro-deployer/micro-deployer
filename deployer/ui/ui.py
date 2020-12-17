import asyncio
import dataclasses
from pathlib import Path
from typing import Any, Callable

from PySide6 import QtCore
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from cue import subscribe
import deployer.deployer
from deployer.model import Application, Device, DeviceDict, DeviceUID


@dataclasses.dataclass
class Column:
    label: str
    field_name: str
    _display_func: Callable[[Any], Any]

    def _fallback_display_func(self, device):
        if self.field_name:
            return getattr(device, self.field_name)
        return self.label

    @property
    def display_func(self):
        return self._display_func or self._fallback_display_func


class TableModel(QtCore.QAbstractTableModel):
    columns = {
        index: Column(label, field_name, display_func)
        for index, (label, field_name, display_func) in enumerate((
            ("Saved", "is_known", None),
            ("Name", "name", None),
            ("UID", "uid", lambda device: device.uid.hex(":", 1)),
            ("Root path", "root_path", lambda device: device.root_path or ""),
            ("...", None, None),
            ("Available", "is_available", None),
            ("Deploy", "is_deployable", None),
            # ("", "deployment_progress", lambda device: x / 100 if x is not None else None),
        ))
    }

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        key = list(self._data.keys())[index.row()]
        column = self.columns[index.column()]
        return column.display_func(self._data[key])


    def setData(self, index, value, role) -> bool:
        key = list(self._data.keys())[index.row()]
        column = self.columns[index.column()]
        setattr(self._data[key], column.field_name, value)
        return True

    # def headerData(self, section, orientation, role=Qt.DisplayRole):
    #     """ Set the headers to be displayed. """
    #     if role != Qt.DisplayRole:
    #         return None
    #
    #     if orientation == Qt.Horizontal:
    #         return self.columns[section].label
    #     return None

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        return len(self.columns)

    @subscribe(Application.devices.__setitem__)
    def on_devices_setitem(
        self,
        devices: DeviceDict,
        device_id: DeviceUID,
        _device: Device
    ) -> None:
        row_index = list(devices.keys()).index(device_id)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.endInsertRows()

    @subscribe.before(Application.devices.__delitem__)
    def on_devices_delitem(self, devices: DeviceDict, device_id: DeviceUID) -> None:
        row_index = list(devices.keys()).index(device_id)
        self.beginRemoveRows(QModelIndex(), row_index, row_index)
        self.endRemoveRows()

    @subscribe.before(Device.change)
    def on_device_change(self, device: Device) -> None:
        row_index = list(self._data.keys()).index(device.uid)
        self.beginRemoveRows(QModelIndex(), row_index, row_index)
        self.endRemoveRows()


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
        device_uid = list(self._application.devices.keys())[device_index]
        device = self._application.devices[device_uid]
        asyncio.create_task(deployer.deployer.deploy(device))


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
