from collections import OrderedDict
from typing import List, Union, Generator, Tuple
from time import perf_counter
from statistics import stdev, mean
from enum import IntEnum
from array import array
import logging
import copy

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QColor

from irspy.clb import calibrator_constants as clb
from irspy import metrology
from irspy import utils

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig


class CellCalculations:
    def __init__(self):
        self.deviation = 0
        self.delta_2 = 0
        self.sko_percents = 0
        self.student_95 = 0
        self.student_99 = 0
        self.student_999 = 0

    def reset(self):
        self.deviation = 0
        self.delta_2 = 0
        self.sko_percents = 0
        self.student_95 = 0
        self.student_99 = 0
        self.student_999 = 0


class CellData:
    class GetDataType(IntEnum):
        MEASURED = 0
        DEVIATION = 1
        DELTA_2 = 2
        SKO_PERCENTS = 3
        STUDENT_95 = 4
        STUDENT_99 = 5
        STUDENT_999 = 6
        COUNT = 7

    def __init__(self, a_locked=False, a_init_values=None, a_init_times=None, a_start_time_point=None, a_result=0.,
                 a_calculations=None, a_have_result=False, a_config=None):
        self.__locked = a_locked
        self.__marked_as_equal = False

        self.__measured_values = a_init_values if a_init_values is not None else array('d')
        self.__measured_times = a_init_times if a_init_times is not None else array('d')
        self.__start_time_point = a_start_time_point if a_start_time_point is not None else perf_counter()
        self.__average = metrology.MovingAverage()
        self.__impulse_filter = metrology.ImpulseFilter()

        self.__result = a_result
        self.__have_result = a_have_result

        self.__calculations = a_calculations if a_calculations is not None else CellCalculations()
        self.__calculated = False
        self.__weight = 0

        self.config = a_config if a_config is not None else CellConfig()

    def serialize_to_dict(self):
        data_dict = {
            "locked": self.__locked,
            "measured_values": utils.bytes_to_base64(self.__measured_values.tobytes()),
            "measured_times": utils.bytes_to_base64(self.__measured_times.tobytes()),
            "start_time_point": self.__start_time_point,
            "result": self.__result,
            "have_result": self.__have_result,
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
                   a_result=float(a_data_dict["result"]),
                   a_have_result=bool(a_data_dict["have_result"]),
                   a_config=CellConfig.from_dict(a_data_dict["config"]))

    def reset(self):
        self.__average.reset()
        self.__measured_values = array('d')
        self.__measured_times = array('d')
        self.__start_time_point = perf_counter()
        self.__impulse_filter.clear()
        self.__result = 0
        self.__have_result = False
        self.__calculations.reset()
        self.__calculated = False

    def has_value(self):
        return self.__have_result

    def get_value(self, a_data_type=GetDataType.MEASURED):
        if a_data_type == CellData.GetDataType.MEASURED:
            return self.__result
        elif a_data_type == CellData.GetDataType.DEVIATION:
            return self.__calculations.deviation
        elif a_data_type == CellData.GetDataType.DELTA_2:
            return self.__calculations.delta_2
        elif a_data_type == CellData.GetDataType.SKO_PERCENTS:
            return self.__calculations.sko_percents
        elif a_data_type == CellData.GetDataType.STUDENT_95:
            return self.__calculations.student_95
        elif a_data_type == CellData.GetDataType.STUDENT_99:
            return self.__calculations.student_99
        elif a_data_type == CellData.GetDataType.STUDENT_999:
            return self.__calculations.student_999

    def set_value(self, a_value: float):
        # Сбрасывает состояние ячейки, без сброса нужно добавлять значения через append_value
        self.reset()
        self.append_value(a_value)

    def append_value(self, a_value: float):
        self.__measured_values.append(a_value)
        self.__measured_times.append(perf_counter() - self.__start_time_point)
        self.__average.add(a_value)
        # До вызова self.finalize в __result хранится последнее добавленное значение
        self.__have_result = True
        self.__result = a_value

    def finalize(self):
        """
        Вызывается, когда все значения считаны, чтобы рассчитать некоторые параметры
        """
        if self.has_value():
            if len(self.__measured_values) < metrology.ImpulseFilter.MIN_SIZE:
                logging.info("Количество измеренных значений слишком мало для импульсного фильтра! "
                             "Результат будет вычислен по среднему значению")
                self.__result = self.__average.get()
            else:
                self.__impulse_filter.assign(self.__measured_values)
                self.__result = self.__impulse_filter.get()

    def calculate_parameters(self, a_setpoint: float, a_data_type: GetDataType):
        assert a_data_type != CellData.GetDataType.MEASURED, "MEASURED не нужно пересчитывать"

        if self.has_value():
            self.__calculated = True

            if a_data_type == CellData.GetDataType.DEVIATION:
                if a_setpoint != 0:
                    self.__calculations.deviation = metrology.deviation_percents(self.__result, a_setpoint)
                else:
                    self.__calculated = False
                    self.__calculations.reset()
            else:
                abs_average = abs(mean(self.__measured_values))
                if abs_average > 0:

                    if a_data_type == CellData.GetDataType.DELTA_2:
                        if len(self.__measured_values) > 1:
                            self.__calculations.delta_2 = \
                                abs(max(self.__measured_values) - min(self.__measured_values)) / abs_average * 100 / 2
                        else:
                            # В этом случае полудальта = 0
                            self.__calculated = False
                            self.__calculations.reset()
                    else:
                        if len(self.__measured_values) > 1:

                            sko_percents = stdev(self.__measured_values) / abs_average * 100
                            if a_data_type == CellData.GetDataType.SKO_PERCENTS:
                                self.__calculations.sko_percents = sko_percents

                            if a_data_type == CellData.GetDataType.STUDENT_95:
                                self.__calculations.student_95 = sko_percents * \
                                    metrology.student_t_inverse_distribution_2x(0.95, len(self.__measured_values))

                            if a_data_type == CellData.GetDataType.STUDENT_99:
                                self.__calculations.student_99 = sko_percents * \
                                    metrology.student_t_inverse_distribution_2x(0.99, len(self.__measured_values))

                            if a_data_type == CellData.GetDataType.STUDENT_999:
                                self.__calculations.student_999 = sko_percents * \
                                    metrology.student_t_inverse_distribution_2x(0.999, len(self.__measured_values))
                        else:
                            self.__calculated = False
                            self.__calculations.reset()
                else:
                    self.__calculated = False
                    self.__calculations.reset()

    def is_calculated(self):
        return self.__calculated

    def set_weight(self, a_weight: float):
        assert 0 <= a_weight <= 1, "Вес должен быть в интервале [0;1]"
        self.__weight = a_weight

    def get_weight(self) -> float:
        """
        Возвращает "Вес" текущего типа данных (который возвращается self.get_value()) от 0 до 1.
        Работает правильно только для параметров из  CellCalculations
        """
        return self.__weight

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

    WEIGHT_COLOR_R = 255
    WEIGHT_COLOR_G = 150
    WEIGHT_COLOR_B = 0

    HZ_UNITS = "Гц"

    DISPLAY_DATA_PRECISION = 9
    EDIT_DATA_PRECISION = 15

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
        self.__displayed_data: CellData.GetDataType = CellData.GetDataType.MEASURED

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
        self.set_save_state(False)

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

    def __first_cell_index(self) -> QModelIndex:
        return self.index(MeasureDataModel.HEADER_ROW + 1, MeasureDataModel.HEADER_COLUMN + 1)

    def __last_cell_index(self) -> QModelIndex:
        return self.index(self.rowCount(), self.columnCount())

    def lock_all_cells(self, a_lock):
        for _, _, cell in self.__get_cells_iterator():
            cell.lock(a_lock)

        self.dataChanged.emit(self.__first_cell_index(), self.__last_cell_index(), (QtCore.Qt.DisplayRole,))

    def __get_cells_iterator(self) -> Generator[Tuple[int, int, CellData], None, None]:
        for row, row_data in enumerate(self.__cells):
            for column, cell in enumerate(row_data):
                if not self.__is_cell_header(row, column):
                    yield row, column, cell

    def __compare_cells(self):
        if self.__show_equal_cells:
            for row, column, cell in self.__get_cells_iterator():
                is_equal = self.__cell_to_compare == cell.config
                cell.mark_as_equal(is_equal)

            self.dataChanged.emit(self.__first_cell_index(), self.__last_cell_index(), (QtCore.Qt.BackgroundRole,))

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
        for row, column, cell in self.__get_cells_iterator():
            if not cell.config.verify_scheme(a_signal_type):
                bad_cells.append((f"{self.get_amplitude(row)} {self.__signal_type_units}",
                                 f"{self.get_frequency(column)} {MeasureDataModel.HZ_UNITS}"))
                if a_reset_bad_cells:
                    cell.config.reset_scheme(a_signal_type)
                    self.set_save_state(False)
        return bad_cells

    def __calculate_cells_parameters(self, a_displayed_data: CellData.GetDataType):
        cell_values = []
        for row, column, cell in self.__get_cells_iterator():
            if cell.has_value():
                setpoint = self.get_amplitude(row)
                cell.calculate_parameters(setpoint, a_displayed_data)
                if cell.is_calculated():
                    cell_values.append(abs(cell.get_value(a_displayed_data)))

        max_value = max(cell_values) if len(cell_values) else 0
        min_value = min(cell_values) if len(cell_values) else 0
        _range = max_value - min_value

        for row, column, cell in self.__get_cells_iterator():
            weight = 0
            if cell.is_calculated() and len(cell_values) > 1:
                value = abs(cell.get_value(a_displayed_data))

                if max_value != min_value:
                    weight = (value - min_value) / _range

            cell.set_weight(weight)

    def set_displayed_data(self, a_displayed_data: CellData.GetDataType):
        self.__displayed_data = a_displayed_data
        if self.__displayed_data != CellData.GetDataType.MEASURED:
            self.__calculate_cells_parameters(self.__displayed_data)

        self.dataChanged.emit(self.__first_cell_index(), self.__last_cell_index(), (QtCore.Qt.DisplayRole,))

    def rowCount(self, parent=QModelIndex()):
        return len(self.__cells)

    def columnCount(self, parent=QModelIndex()):
        return len(self.__cells[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

    def __get_cell_color(self, a_index: QtCore.QModelIndex):
        if self.__is_cell_header(a_index.row(), a_index.column()):
            color = MeasureDataModel.HEADER_COLOR
        elif self.__displayed_data == CellData.GetDataType.MEASURED:
            color = MeasureDataModel.TABLE_COLOR
            if self.is_cell_locked(a_index.row(), a_index.column()):
                color = MeasureDataModel.LOCK_COLOR
            if self.__show_equal_cells:
                if self.__cells[a_index.row()][a_index.column()].is_marked_as_equal():
                    color = MeasureDataModel.EQUAL_COLOR
        else:
            weight = self.__cells[a_index.row()][a_index.column()].get_weight()
            # Если использовать ARGB, то ломается прозрачность выделения ячеек
            tint_factor = 1 - weight
            g = int(MeasureDataModel.WEIGHT_COLOR_G + (255 - MeasureDataModel.WEIGHT_COLOR_G) * tint_factor)
            b = int(MeasureDataModel.WEIGHT_COLOR_B + (255 - MeasureDataModel.WEIGHT_COLOR_B) * tint_factor)
            color = QColor(MeasureDataModel.WEIGHT_COLOR_R, g, b)

        return color

    def get_cell_value(self, a_row: int, a_column: int) -> float:
        """
        Возвращает значение ячейки в зависимости от текущих self.__displayed_data. Если значение в ячейке
        отсутствует, возвращает 0. Не возвращает значения хэдеров
        :param a_row: Строка ячейки. a_row > 0
        :param a_column: Колонка ячейки. a_column > 0
        :return: Значение ячейки.
        """
        assert a_row < self.rowCount() and a_column < self.columnCount(), "Задан неверный индекс ячейки!"
        assert not self.__is_cell_header(a_row, a_column), "Этой функцией нельзя получить значения из хэдеров"

        cell = self.__cells[a_row][a_column]
        cell_value = 0.
        if self.__displayed_data == CellData.GetDataType.MEASURED:
            if cell.has_value():
                cell_value = cell.get_value(self.__displayed_data)
        else:
            if cell.is_calculated():
                cell_value = cell.get_value(self.__displayed_data)

        return cell_value

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

            if index.row() == MeasureDataModel.HEADER_ROW:
                displayed_data = CellData.GetDataType.MEASURED
                units = " " + MeasureDataModel.HZ_UNITS
            elif index.column() == MeasureDataModel.HEADER_COLUMN:
                displayed_data = CellData.GetDataType.MEASURED
                units = " " + self.__signal_type_units
            elif self.__displayed_data == CellData.GetDataType.MEASURED:
                displayed_data = self.__displayed_data
                units = " " + CellConfig.meter_to_units[cell_data.config.meter]
            else:
                displayed_data = self.__displayed_data
                units = ""

            if role == Qt.DisplayRole:
                value = utils.float_to_string(cell_data.get_value(displayed_data),
                                              a_precision=MeasureDataModel.DISPLAY_DATA_PRECISION)
            else:
                value = utils.float_to_string(cell_data.get_value(displayed_data),
                                              a_precision=MeasureDataModel.EDIT_DATA_PRECISION)

            str_value = f"{value}{units}"

            return str_value

    def reset_cell(self, a_row, a_column):
        self.__cells[a_row][a_column].reset()
        self.set_save_state(False)
        self.dataChanged.emit(self.index(a_row, a_column), self.index(a_row, a_column), (QtCore.Qt.DisplayRole,))

    def update_cell_with_value(self, a_row, a_column, a_value: float):
        self.__cells[a_row][a_column].append_value(a_value)
        self.set_save_state(False)
        self.dataChanged.emit(self.index(a_row, a_column), self.index(a_row, a_column), (QtCore.Qt.DisplayRole,))

    def finalize_cell(self, a_row, a_column):
        self.__cells[a_row][a_column].finalize()
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
                float_value = utils.parse_input(value, a_precision=MeasureDataModel.EDIT_DATA_PRECISION)
                if float_value != cell_data.get_value() or not cell_data.has_value():
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
