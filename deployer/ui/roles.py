from deployer.ui.base import BaseModel


class RolesModel(BaseModel):
    class Columns:
        class Name:
            label = "Name"
            fields = ["name"]

            def display(self, role):
                return role.name

            def edit(self, role, name):
                role.name = name

    #
    #
    # @subscribe(Application.roles.__setitem__)
    # def on_devices_setitem(
    #     self,
    #     devices: DeviceDict,
    #     device_id: DeviceUID,
    #     _device: Device
    # ) -> None:
    #     row_index = self.get_row_index(device_id)
    #     self.beginInsertRows(QModelIndex(), row_index, row_index)
    #     self.endInsertRows()
    #
    # @subscribe.before(Application.roles.__delitem__)
    # def on_devices_delitem(self, devices: DeviceDict, device_id: DeviceUID) -> None:
    #     row_index = self.get_row_index(device_id)
    #     self.beginRemoveRows(QModelIndex(), row_index, row_index)
    #     self.endRemoveRows()

    # @subscribe.before(Role.change)
    # def on_role_change(self, role: Device, field_name: str, value: Any) -> None:
    #     row_index = self.get_row_index(role.name)
    #     for col_index in self.col_indexes_by_field_name[field_name]:
    #         self.dataChanged.emit(
    #             self.createIndex(row_index, col_index),
    #             self.createIndex(row_index, col_index),
    #             {QtCore.Qt.DisplayRole, ProgressRole}
    #         )
