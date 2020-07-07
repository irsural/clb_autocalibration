from typing import List, Iterable, Union
import logging
import copy
import enum

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5.QtGui import QColor

from PyQt5 import QtCore, QtGui

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig


class CellData:
    def __init__(self):
        self.value = ""

        self.__locked = False
        self.__marked_as_equal = False

        self.config = CellConfig()

    def lock(self, a_lock: bool):
        self.__locked = a_lock

    def is_locked(self) -> bool:
        return self.__locked

    def mark_as_equal(self, a_mark_as_equal: bool):
        self.__marked_as_equal = a_mark_as_equal

    def is_marked_as_equal(self):
        return self.__marked_as_equal


class MeasureDataModel(QAbstractTableModel):
    HEADER_ROW = 0
    HEADER_COLUMN = 0
    HEADER_COLOR = QColor(209, 230, 255)
    TABLE_COLOR = QColor(255, 255, 255)
    LOCK_COLOR = QColor(254, 255, 171)
    EQUAL_COLOR = QColor(142, 250, 151)

    data_save_state_changed = QtCore.pyqtSignal(str, bool)

    def __init__(self, a_name: str, a_parent=None):
        super().__init__(a_parent)

        self.__name = a_name
        self.__saved = False
        self.__cells = [[CellData()]]
        self.__measure_parameters = MeasureParameters()
        self.__enabled = False
        self.__show_equal_cells = False
        self.__cell_to_compare: Union[None, CellConfig] = None

    def set_name(self, a_name: str):
        self.__name = a_name

    def get_name(self):
        return self.__name

    def set_save_state(self, a_saved: bool):
        self.__saved = a_saved
        self.data_save_state_changed.emit(self.__name, self.__saved)

    def is_saved(self):
        return self.__saved

    def serialize(self):
        return self.__name

    def get_measure_parameters(self) -> MeasureParameters:
        return self.__measure_parameters

    def set_measure_parameters(self, a_measure_parameters: MeasureParameters):
        self.__measure_parameters = a_measure_parameters
        self.set_save_state(False)

    def is_enabled(self):
        return self.__enabled

    def set_enabled(self, a_enabled: bool):
        self.__enabled = a_enabled
        self.set_save_state(False)

    @staticmethod
    def __is_cell_header(a_row, a_column):
        return a_row == MeasureDataModel.HEADER_ROW or a_column == MeasureDataModel.HEADER_COLUMN

    def get_cell_config(self, a_row, a_column) -> Union[None, CellConfig]:
        if self.__is_cell_header(a_row, a_column):
            return None
        else:
            return self.__cells[a_row][a_column].config

    def set_cell_config(self, a_row, a_column, a_config: CellConfig):
        if self.__is_cell_header(a_row, a_column):
            return None
        else:
            self.__cells[a_row][a_column].config = a_config
            self.__compare_cells()

    def is_cell_locked(self, a_row, a_column) -> bool:
        if self.__is_cell_header(a_row, a_column):
            return False
        else:
            return self.__cells[a_row][a_column].is_locked()

    def lock_cell(self, a_row, a_column, a_lock: bool):
        if not self.__is_cell_header(a_row, a_column):
            self.__cells[a_row][a_column].lock(a_lock)
            self.dataChanged.emit(self.index(a_row, a_column), self.index(a_row, a_column), (QtCore.Qt.BackgroundRole,))

    def __compare_cells(self):
        if self.__show_equal_cells:
            for row, row_data in enumerate(self.__cells):
                for column, cell in enumerate(row_data):
                    is_equal = self.__cell_to_compare == cell.config
                    cell.mark_as_equal(is_equal)
            self.dataChanged.emit(self.index(MeasureDataModel.HEADER_ROW, MeasureDataModel.HEADER_COLUMN),
                                  self.index(self.rowCount(), self.columnCount()), (QtCore.Qt.BackgroundRole,))

    def show_equal_cell_configs(self, a_enable: bool):
        if not a_enable:
            self.__cell_to_compare = None
            self.__compare_cells()
        self.__show_equal_cells = a_enable

    def set_cell_to_compare(self, a_index: QtCore.QModelIndex):
        if a_index.isValid() and self.rowCount() > a_index.row() and \
                not self.__is_cell_header(a_index.row(), a_index.column()):
            self.__cell_to_compare = copy.deepcopy(self.__cells[a_index.row()][a_index.column()].config)
        else:
            self.__cell_to_compare = None
        self.__compare_cells()

    def add_row(self, a_row: int):
        self.beginInsertRows(QModelIndex(), a_row, a_row)
        self.__cells.insert(a_row + 1, [CellData() for _ in range(len(self.__cells[0]))])
        self.endInsertRows()
        self.set_save_state(False)
        self.__compare_cells()

    def remove_row(self, a_row: int):
        if a_row != MeasureDataModel.HEADER_ROW:
            self.beginRemoveRows(QModelIndex(), a_row, a_row)
            del self.__cells[a_row]
            self.endRemoveRows()
            self.set_save_state(False)

    def add_column(self, a_column: int):
        self.beginInsertColumns(QModelIndex(), a_column, a_column)
        for cells_row in self.__cells:
            cells_row.insert(a_column + 1, CellData())
        self.endInsertColumns()
        self.set_save_state(False)
        self.__compare_cells()

    def remove_column(self, a_column: int):
        if a_column != MeasureDataModel.HEADER_COLUMN:
            self.beginRemoveColumns(QModelIndex(), a_column, a_column)
            for cell_row in self.__cells:
                del cell_row[a_column]
            self.endRemoveColumns()
            self.set_save_state(False)

    def rowCount(self, parent=QModelIndex()):
        return len(self.__cells)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__cells[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

    def __get_cell_color(self, a_index: QtCore.QModelIndex):
        if self.__is_cell_header(a_index.row(), a_index.column()):
            return MeasureDataModel.HEADER_COLOR
        else:
            color = MeasureDataModel.TABLE_COLOR
            if self.is_cell_locked(a_index.row(), a_index.column()):
                color = MeasureDataModel.LOCK_COLOR
            if self.__show_equal_cells:
                if self.__cells[a_index.row()][a_index.column()].is_marked_as_equal():
                    color = MeasureDataModel.EQUAL_COLOR
            return color

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or (self.rowCount() < index.row()) or \
                (role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole and role != Qt.UserRole):
            return QVariant()
        if role == Qt.BackgroundRole:
            return QVariant(QtGui.QBrush(self.__get_cell_color(index)))
        else:
            value = self.__cells[index.row()][index.column()].value
            return value

    def setData(self, index: QModelIndex, value: str, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole or self.rowCount() <= index.row():
            return False
        try:
            self.__cells[index.row()][index.column()].value = value
            self.dataChanged.emit(index, index)
            self.set_save_state(False)
            return True
        except ValueError:
            return False

    def flags(self, index):
        item_flags = super().flags(index)
        if index.isValid():
            if not (index.column() == MeasureDataModel.HEADER_COLUMN and index.row() == MeasureDataModel.HEADER_ROW):
                item_flags |= Qt.ItemIsEditable
        return item_flags
