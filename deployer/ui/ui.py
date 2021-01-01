import asyncio
from pathlib import Path

from PySide6 import QtCore
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication

from deployer.models.application import Application
from deployer.ui.devices import DevicesModel
from deployer.ui.roles import RolesModel


class ApplicationProxy(QtCore.QObject):
    def __init__(self, application: Application) -> None:
        super().__init__()
        self._application = application
        self._devices = DevicesModel(application.devices)
        self._roles = RolesModel(application.roles)

    @QtCore.Slot()
    def stop(self) -> None:
        self._application.stop()

    @QtCore.Property(QtCore.QObject)
    def devices(self) -> DevicesModel:
        return self._devices

    @QtCore.Property(QtCore.QObject)
    def roles(self) -> RolesModel:
        return self._roles

    @QtCore.Slot(int)
    def deploy(self, device_index: int):
        device = self._devices.get_row_data(device_index)
        asyncio.create_task(device.deploy())


async def run(application: Application) -> None:
    app = QApplication([])
    qml_filepath = str(Path(__file__).parent / "main.qml")
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
