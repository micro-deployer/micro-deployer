import asyncio
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtQuickControls2 import QQuickStyle
from PySide2.QtWidgets import QStyleFactory

from cue import subscribe
from model import Application, Device, DeviceDict, DeviceID


class TableModel(QtCore.QAbstractTableModel):
    columns = {
        index: (field_name, display_func)
        for index, (field_name, display_func) in enumerate((
            ("is_known", lambda x: x),
            ("uid", lambda x: x.hex()),
            ("is_available", lambda x: x),
        ))
    }

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        key = list(self._data.keys())[index.row()]
        field_name, display_func = self.columns[index.column()]
        return display_func(getattr(self._data[key], field_name))

    def setData(self, index, value, role) -> bool:
        key = list(self._data.keys())[index.row()]
        field_name, _ = self.columns[index.column()]
        setattr(self._data[key], field_name, value)
        return True

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        return len(self.columns)

    @subscribe(Application.devices.__setitem__)
    def on_devices_setitem(
        self,
        devices: DeviceDict,
        device_id: DeviceID,
        _device: Device
    ) -> None:
        row_index = list(devices.keys()).index(device_id)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.endInsertRows()

    @subscribe.before(Application.devices.__delitem__)
    def on_devices_delitem(self, devices: DeviceDict, device_id: DeviceID) -> None:
        row_index = list(devices.keys()).index(device_id)
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


async def run(application: Application) -> None:
    app = QGuiApplication([])
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
