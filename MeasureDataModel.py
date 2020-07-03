import logging
import enum
from typing import List, Iterable

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5.QtGui import QColor

from PyQt5 import QtCore

from edit_measure_parameters_dialog import MeasureParameters


class MeasureDataModel(QAbstractTableModel):
    HEADER_ROW = 0
    HEADER_COLUMN = 0
    HEADER_COLOR = QColor(209, 230, 255)
    TABLE_COLOR = QColor(255, 255, 255)

    data_save_state_changed = QtCore.pyqtSignal(str, bool)

    def __init__(self, a_parent=None):
        super().__init__(a_parent)

        self.__name = ""
        self.__cells = [[""]]
        self.__measure_parameters = MeasureParameters()

    def set_name(self, a_name: str):
        self.__name = a_name

    def get_parameters(self) -> MeasureParameters:
        return self.__measure_parameters

    def set_parameters(self, a_measure_parameters: MeasureParameters):
        self.__measure_parameters = a_measure_parameters
        self.data_were_changed.emit(self.__name, False)

    def add_row(self, a_row: int):
        self.beginInsertRows(QModelIndex(), a_row, a_row)
        self.__cells.insert(a_row + 1, [""] * len(self.__cells[0]))
        self.endInsertRows()

    def remove_row(self, a_row: int):
        if a_row != MeasureDataModel.HEADER_ROW:
            self.beginRemoveRows(QModelIndex(), a_row, a_row)
            del self.__cells[a_row]
            self.endRemoveRows()

    def add_column(self, a_column: int):
        self.beginInsertColumns(QModelIndex(), a_column, a_column)
        for cells_row in self.__cells:
            cells_row.insert(a_column + 1, "")
        self.endInsertColumns()

    def remove_column(self, a_column: int):
        if a_column != MeasureDataModel.HEADER_COLUMN:
            self.beginRemoveColumns(QModelIndex(), a_column, a_column)
            for cell_row in self.__cells:
                del cell_row[a_column]
            self.endRemoveColumns()

    def rowCount(self, parent=QModelIndex()):
        return len(self.__cells)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__cells[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or (self.rowCount() < index.row()) or \
                (role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole and role != Qt.UserRole):
            return QVariant()
        if role == Qt.BackgroundRole:
            if index.column() == MeasureDataModel.HEADER_COLUMN or index.row() == MeasureDataModel.HEADER_ROW:
                return MeasureDataModel.HEADER_COLOR
            else:
                return MeasureDataModel.TABLE_COLOR
        else:
            value = self.__cells[index.row()][index.column()]
            return value

    def setData(self, index: QModelIndex, value: str, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole or self.rowCount() <= index.row():
            return False
        try:
            self.__cells[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        except ValueError:
            return False

    def flags(self, index):
        item_flags = super().flags(index)
        if index.isValid():
            if not (index.column() == MeasureDataModel.HEADER_COLUMN and index.row() == MeasureDataModel.HEADER_ROW):
                item_flags |= Qt.ItemIsEditable
        return item_flags
