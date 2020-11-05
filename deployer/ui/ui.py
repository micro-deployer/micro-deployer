import asyncio
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtCore import QModelIndex, Qt
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtQuickControls2 import QQuickStyle

from cue import subscribe
import deployer.deployer
from deployer.model import Application, Device, DeviceDict, DeviceID


class TableModel(QtCore.QAbstractTableModel):
    columns = {
        index: (field_name, display_func)
        for index, (field_name, display_func) in enumerate((
            ("is_known", lambda x: x),
            ("name", lambda x: x),
            ("uid", lambda x: x.hex(":", 1)),
            ("is_available", lambda x: x),
            ("deployment_progress", lambda x: x / 100 if x is not None else None),
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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Saved"
            elif section == 1:
                return "Name"
            elif section == 2:
                return "UID"
            elif section == 3:
                return "Deploy"
        return None

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
        asyncio.create_task(deployer.deploy(device))


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
    QQuickStyle.setStyle('Fusion')
    engine.load(qml_filepath)

    while application.is_running:
        app.processEvents()
        await asyncio.sleep(0.01)
