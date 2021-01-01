from collections import defaultdict
import contextlib

from PySide6 import QtCore


class BaseModel(QtCore.QAbstractTableModel):
    class Columns:
        pass

    @QtCore.Property('QVariant')
    def columns(self):
        return {
            column.__class__.__name__: index
            for index, column in self._columns.items()
        }

    @QtCore.Property(int)
    def header(self):
        return 0 if self.has_header else -1

    def __init__(self, data):
        super().__init__()
        self._data = data
        self.has_header = True

        self._columns = dict(
            enumerate(
                column()
                    for field_name, column in vars(self.Columns).items()
                    if type(column) == type
            )
        )

        col_indexes_by_field_name = defaultdict(list)
        for index, column in self._columns.items():
            for field_name in column.fields:
                col_indexes_by_field_name[field_name].append(index)

    def rowCount(self, index):
        # The length of the outer list.
        row_count = len(self._data)
        if self.has_header:
            return row_count + 1
        return row_count

    def columnCount(self, index):
        return len(self._columns)

    def setData(self, index, value, role) -> bool:
        obj = self.get_row_data(index.row())
        column = self._columns[index.column()]
        try:
            column.edit(obj, value)
        except AttributeError:
            pass
        return True

    def header_data(self, col_index, role):
        """ Set the headers to be displayed. """
        if role != QtCore.Qt.DisplayRole:
            return None

        return self._columns[col_index].label

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
        obj = self.get_row_data(index.row())
        column = self._columns[index.column()]
        attr_name = bytes(self.roleNames()[role]).decode()

        with contextlib.suppress(AttributeError):
            return getattr(column, attr_name)(obj)
        return None
