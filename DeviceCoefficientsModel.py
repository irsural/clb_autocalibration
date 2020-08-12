from enum import IntEnum
from typing import List
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5 import QtCore, QtGui

from irspy import utils


class CorrectionTableModel(QAbstractTableModel):
    class Column(IntEnum):
        FREQUENCY = 0
        COEFFICIENT = 1

    COLUMN_TO_NAME = {
        Column.FREQUENCY: "Частота, Гц",
        Column.COEFFICIENT: "Коэффициент",
    }

    DISPLAY_DATA_PRECISION = 9
    EDIT_DATA_PRECISION = 15

    def __init__(self, a_frequencies: List[float], a_coefficients: List[float], a_parent=None):
        super().__init__(a_parent)

        assert len(a_frequencies) > 0, "Списки частот и коэффициентов не должны быть пустые!"
        assert len(a_frequencies) == len(a_coefficients), "Размеры списков частот и коэффициентов должны быть равны!"

        self.__values = [[frequency, coefficient] for frequency, coefficient in zip(a_frequencies, a_coefficients)]

    def rowCount(self, parent=QModelIndex()):
        return len(self.__values)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__values[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Vertical:
            return section + 1
        else:
            return CorrectionTableModel.COLUMN_TO_NAME[CorrectionTableModel.Column(section)]

    @utils.exception_decorator
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or (self.rowCount() < index.row()) or (role != Qt.DisplayRole and role != Qt.EditRole):
            return QVariant()

        cell_value = self.__values[index.row()][index.column()]

        if role == Qt.DisplayRole:
            str_value = utils.float_to_string(cell_value, a_precision=CorrectionTableModel.DISPLAY_DATA_PRECISION)
        else:
            str_value = utils.float_to_string(cell_value, a_precision=CorrectionTableModel.EDIT_DATA_PRECISION)

        return str_value

    def setData(self, index: QModelIndex, value: str, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole or self.rowCount() <= index.row():
            return False

        try:
            self.__values[index.row()][index.column()] = \
                utils.parse_input(value, a_precision=CorrectionTableModel.EDIT_DATA_PRECISION)
            result = True
        except ValueError:
            result = False

        if result:
            self.dataChanged.emit(index, index)

        return result
