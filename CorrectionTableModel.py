from typing import List
import logging

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QColor

from irspy import utils


class CorrectionTableModel(QAbstractTableModel):
    HEADER_ROW = 0
    HEADER_COLUMN = 0

    HEADER_COLOR = QColor(209, 230, 255)
    TABLE_COLOR = QColor(255, 255, 255)

    HZ_UNITS = "Гц"

    DISPLAY_DATA_PRECISION = 9
    EDIT_DATA_PRECISION = 15

    def __init__(self, a_x_values: List[float], a_y_values: List[float], a_coef_values: List[float], a_parent=None):
        super().__init__(a_parent)

        self.__values = [[0.] + a_x_values]
        for row, y_value in enumerate(a_y_values):
            coefs_from = row * len(a_x_values)
            coefs_to = coefs_from + len(a_x_values)
            self.__values.append([y_value] + a_coef_values[coefs_from:coefs_to])

        # self.__signal_type_units = clb.signal_type_to_units[self.__measure_parameters.signal_type]

    @staticmethod
    def __is_cell_header(a_row, a_column):
        return a_row == CorrectionTableModel.HEADER_ROW or a_column == CorrectionTableModel.HEADER_COLUMN

    def rowCount(self, parent=QModelIndex()):
        return len(self.__values)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__values[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

    def __get_cell_color(self, a_index: QtCore.QModelIndex):
        if self.__is_cell_header(a_index.row(), a_index.column()):
            color = CorrectionTableModel.HEADER_COLOR
        else:
            color = CorrectionTableModel.TABLE_COLOR

        return color

    @utils.exception_decorator
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or (self.rowCount() < index.row()) or \
                (role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole):
            return QVariant()
        if role == Qt.BackgroundRole:
            return QVariant(QtGui.QBrush(self.__get_cell_color(index)))
        else:
            cell_value = self.__values[index.row()][index.column()]

            if index.row() == CorrectionTableModel.HEADER_ROW and index.column() == CorrectionTableModel.HEADER_COLUMN:
                return ""

            if index.row() == CorrectionTableModel.HEADER_ROW:
                units = " " + CorrectionTableModel.HZ_UNITS
            else:
                units = ""
                # units = " " + self.__signal_type_units

            if role == Qt.DisplayRole:
                value = utils.float_to_string(cell_value, a_precision=CorrectionTableModel.DISPLAY_DATA_PRECISION)
            else:
                value = utils.float_to_string(cell_value, a_precision=CorrectionTableModel.EDIT_DATA_PRECISION)

            str_value = f"{value}{units}"
            return str_value

    def setData(self, index: QModelIndex, value: str, role=Qt.EditRole):
        return False
