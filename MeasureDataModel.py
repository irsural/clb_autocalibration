from typing import List, Iterable, Union
from collections import OrderedDict
from time import perf_counter
from array import array
from enum import IntEnum
import logging
import json
import copy

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QColor

from irspy import utils
from irspy import metrology
from irspy.clb import calibrator_constants as clb

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig


class CellData:
    def __init__(self, a_locked=False, a_init_values=None, a_init_times=None, a_start_time_point=None,
                 a_config=None):
        self.__locked = a_locked
        self.__marked_as_equal = False

        self.__measured_values = a_init_values if a_init_values is not None else array('d')
        self.__measured_times = a_init_times if a_init_times is not None else array('d')
        self.__start_time_point = a_start_time_point if a_start_time_point is not None else perf_counter()
        self.__average = metrology.MovingAverage(999)

        if a_init_values:
            for value in self.__measured_values:
                self.__average.add(value)

        self.config = a_config if a_config is not None else CellConfig()

    def serialize_to_dict(self):
        data_dict = {
            "locked": self.__locked,
            "measured_values": utils.bytes_to_base64(self.__measured_values.tobytes()),
            "measured_times": utils.bytes_to_base64(self.__measured_times.tobytes()),
            "start_time_point": self.__start_time_point,
            "config": self.config.serialize_to_dict(),
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_data_dict: dict):
        init_values = array('d')
        init_values.frombytes(utils.base64_to_bytes(a_data_dict["measured_values"]))

        init_times = array('d')
        init_times.frombytes(utils.base64_to_bytes(a_data_dict["measured_times"]))

        return cls(a_locked=bool(a_data_dict["locked"]),
                   a_init_values=init_values,
                   a_init_times=init_times,
                   a_start_time_point=float(a_data_dict["start_time_point"]),
                   a_config=CellConfig.from_dict(a_data_dict["config"]))

    def reset(self):
        self.__average.reset()
        self.__measured_values = array('d')
        self.__measured_times = array('d')
        self.__start_time_point = perf_counter()

    def has_value(self):
        return bool(self.__measured_values)

    def get_value(self):
        return self.__average.get()

    def set_value(self, a_value: float):
        # Сбрасывает состояние ячейки, без сброса нужно добавлять значения через append_value
        self.reset()
        self.append_value(a_value)

    def append_value(self, a_value: float):
        self.__measured_values.append(a_value)
        self.__measured_times.append(perf_counter() - self.__start_time_point)
        self.__average.add(a_value)

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
    HZ_UNITS = "Гц"

    data_save_state_changed = QtCore.pyqtSignal(str, bool)

    def __init__(self, a_name: str, a_saved=False, a_init_cells: [List[List[CellData]]] = None,
                 a_measured_parameters=None, a_enabled=False, a_parent=None):
        super().__init__(a_parent)

        self.__name = a_name
        self.__saved = a_saved
        self.__cells = a_init_cells if a_init_cells is not None else [[CellData()]]
        self.__measure_parameters = a_measured_parameters if a_measured_parameters else MeasureParameters()
        self.__enabled = a_enabled
        self.__show_equal_cells = False
        self.__cell_to_compare: Union[None, CellConfig] = None

        self.__signal_type_units = clb.signal_type_to_units[self.__measure_parameters.signal_type]

    def __serialize_cells_to_dict(self):
        data_dict = OrderedDict()
        for row, row_data in enumerate(self.__cells):
            for column, cell in enumerate(row_data):
                data_dict[f"{row},{column}"] = cell.serialize_to_dict()
        return data_dict

    def serialize_to_dict(self):
        data_dict = {
            "name": self.__name,
            "row_count": self.rowCount(),
            "column_count": self.columnCount(),
            "enabled": self.__enabled,
            "cells": self.__serialize_cells_to_dict(),
            "measure_parameters": self.__measure_parameters.serialize_to_dict(),
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_measure_name: str, a_data_dict: dict):
        name_in_dict = a_data_dict["name"]
        assert a_measure_name == name_in_dict, "Имена в измерении и в имени файла должны совпадать!"

        row_count = a_data_dict["row_count"]
        column_count = a_data_dict["column_count"]
        assert row_count != 0 and column_count != 0, "Количество строк и колонок должно быть больше нуля!"

        cells_dict: dict = a_data_dict["cells"]
        assert len(cells_dict) == row_count * column_count, \
            "Количество ячеек должно быть равно количество_строк * количество_колонок"

        cells: List[List[CellData]] = [[None] * column_count for _ in range(row_count)]
        for row_column, cell_data in cells_dict.items():
            row, column = int(row_column.split(",")[0]), int(row_column.split(",")[1])
            cells[row][column] = CellData.from_dict(cell_data)

        assert all([cell is not None for cell in cells])

        measure_parameters = MeasureParameters.from_dict(a_data_dict["measure_parameters"])
        enabled = a_data_dict["enabled"]

        return cls(a_name=a_measure_name, a_saved=True, a_init_cells=cells, a_measured_parameters=measure_parameters,
                   a_enabled=enabled)

    def set_name(self, a_name: str):
        self.__name = a_name

    def get_name(self):
        return self.__name

    def set_save_state(self, a_saved: bool):
        self.__saved = a_saved
        self.data_save_state_changed.emit(self.__name, self.__saved)

    def is_saved(self):
        return self.__saved

    def get_measure_parameters(self) -> MeasureParameters:
        return copy.deepcopy(self.__measure_parameters)

    def set_measure_parameters(self, a_measure_parameters: MeasureParameters):
        self.__measure_parameters = copy.deepcopy(a_measure_parameters)
        self.verify_cell_configs(self.__measure_parameters.signal_type, True)
        self.set_save_state(False)

        self.__signal_type_units = clb.signal_type_to_units[self.__measure_parameters.signal_type]
        self.dataChanged.emit(self.index(MeasureDataModel.HEADER_ROW, MeasureDataModel.HEADER_COLUMN),
                              self.index(self.rowCount(), MeasureDataModel.HEADER_COLUMN), (QtCore.Qt.DisplayRole,))

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
            return copy.deepcopy(self.__cells[a_row][a_column].config)

    def set_cell_config(self, a_row, a_column, a_config: CellConfig):
        if self.__is_cell_header(a_row, a_column):
            return None
        else:
            self.__cells[a_row][a_column].config = copy.deepcopy(a_config)
            self.set_save_state(False)
            self.__compare_cells()
            self.dataChanged.emit(self.index(a_row, a_column), self.index(a_row, a_column), (QtCore.Qt.DisplayRole,))

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
        assert a_row != 0, "Строка не должна иметь 0 индекс!"

        new_data_row = []
        for cell_data in self.__cells[a_row - 1]:
            new_data = CellData()
            new_data.config = copy.deepcopy(cell_data.config)
            new_data_row.append(new_data)

        self.beginInsertRows(QModelIndex(), a_row, a_row)
        self.__cells.insert(a_row, new_data_row)
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
        assert a_column != 0, "Столбец не должен иметь 0 индекс!"

        new_data_column = []
        for cell_data_row in self.__cells:
            new_data = CellData()
            new_data.config = copy.deepcopy(cell_data_row[a_column - 1].config)
            new_data_column.append(new_data)

        self.beginInsertColumns(QModelIndex(), a_column, a_column)
        for idx, cells_row in enumerate(self.__cells):
            cells_row.insert(a_column, new_data_column[idx])
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

    def get_amplitude(self, a_row):
        cell_data = self.__cells[a_row][MeasureDataModel.HEADER_COLUMN]
        return 0 if not cell_data.has_value() else cell_data.get_value()

    def get_amplitude_with_units(self, a_row):
        return self.data(self.index(a_row, MeasureDataModel.HEADER_COLUMN))

    def get_frequency(self, a_column):
        cell_data = self.__cells[MeasureDataModel.HEADER_ROW][a_column]
        return 0 if not cell_data.has_value() else cell_data.get_value()

    def get_frequency_with_units(self, a_column):
        return self.data(self.index(MeasureDataModel.HEADER_ROW, a_column))

    def verify_cell_configs(self, a_signal_type: clb.SignalType, a_reset_bad_cells=False):
        bad_cells = []
        for row, row_data in enumerate(self.__cells):
            for column, cell in enumerate(row_data):
                if not self.__is_cell_header(row, column):
                    if not cell.config.verify_scheme(a_signal_type):
                        bad_cells.append((f"{self.get_amplitude(row)} {self.__signal_type_units}",
                                         f"{self.get_frequency(column)} {MeasureDataModel.HZ_UNITS}"))
                        if a_reset_bad_cells:
                            cell.config.reset_scheme(a_signal_type)
                            self.set_save_state(False)
        return bad_cells

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
                (role != Qt.DisplayRole and role != Qt.EditRole and role != Qt.BackgroundRole):
            return QVariant()
        if role == Qt.BackgroundRole:
            return QVariant(QtGui.QBrush(self.__get_cell_color(index)))
        else:
            cell_data = self.__cells[index.row()][index.column()]

            if not cell_data.has_value() or \
                    index.row() == MeasureDataModel.HEADER_ROW and index.column() == MeasureDataModel.HEADER_COLUMN:
                return ""

            else:
                if index.row() == MeasureDataModel.HEADER_ROW:
                    units = MeasureDataModel.HZ_UNITS
                elif index.column() == MeasureDataModel.HEADER_COLUMN:
                    units = self.__signal_type_units
                else:
                    units = CellConfig.meter_to_units[cell_data.config.meter]

                str_value = f"{utils.float_to_string(cell_data.get_value())} {units}"

                return str_value

    def reset_cell(self, a_row, a_column):
        self.__cells[a_row][a_column].reset()
        self.set_save_state(False)
        self.dataChanged.emit(self.index(a_row, a_column), self.index(a_row, a_column), (QtCore.Qt.DisplayRole,))

    def update_cell_with_value(self, a_row, a_column, a_value: float):
        self.__cells[a_row][a_column].append_value(a_value)
        self.set_save_state(False)
        self.dataChanged.emit(self.index(a_row, a_column), self.index(a_row, a_column), (QtCore.Qt.DisplayRole,))

    def setData(self, index: QModelIndex, value: str, role=Qt.EditRole):
        if not index.isValid() or role != Qt.EditRole or self.rowCount() <= index.row():
            return False

        result = True
        cell_data = self.__cells[index.row()][index.column()]

        if not value:
            cell_data.reset()
        else:
            try:
                float_value = utils.parse_input(value)
                if float_value != cell_data.get_value():
                    cell_data.set_value(float_value)
                else:
                    result = False
            except ValueError:
                result = False

        if result:
            self.dataChanged.emit(index, index)
            self.set_save_state(False)

        return result

    def flags(self, index):
        item_flags = super().flags(index)
        if index.isValid():
            if not (index.column() == MeasureDataModel.HEADER_COLUMN and index.row() == MeasureDataModel.HEADER_ROW):
                item_flags |= Qt.ItemIsEditable
        return item_flags
