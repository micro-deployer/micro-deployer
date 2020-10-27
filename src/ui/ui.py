import asyncio
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtQuickControls2 import QQuickStyle

from cue import subscribe
from model import Application, Device, DeviceDict, DeviceID


class TableModel(QtCore.QAbstractTableModel):
    columns = {
        index: {Qt.EditRole: edit_field, Qt.DisplayRole: display_field}
        for index, (edit_field, display_field) in enumerate((
            ("is_known", "is_known"),
            ("uid", "uid_hex"),
            ("is_available", "is_available"),
        ))
    }

    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        key = list(self._data.keys())[index.row()]
        field = self.columns[index.column()][role]
        return getattr(self._data[key], field)

    def setData(self, index, value, role) -> bool:
        key = list(self._data.keys())[index.row()]
        field = self.columns[index.column()][role]
        setattr(self._data[key], field, value)
        return True

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        return len(self.columns)

    @subscribe.after(Application.devices.__setitem__)
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
    # qml_filepath = "./gallery/gallery.qml"
    engine = QQmlApplicationEngine()

    # bind model
    # saved_devices = {b'<q\xbf\xab\x15D': Device(uid=b'<q\xbf\xab\x15D'.hex(), ip='192.168.0.192')}
    # saved_devices = {}

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
