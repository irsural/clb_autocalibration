from collections import namedtuple
from typing import Union
from collections import OrderedDict
from enum import IntEnum
import logging

from PyQt5 import QtWidgets, QtCore, QtGui

from MeasureDataModel import MeasureDataModel
from irspy.qt import qt_utils


class MeasureManager(QtCore.QObject):
    class MeasureColumn(IntEnum):
        NAME = 0
        SETTINGS = 1
        ENABLE = 2

    def __init__(self, a_measures_table: QtWidgets.QTableWidget, a_data_view: QtWidgets.QTableView, a_parent=None):
        super().__init__(a_parent)

        self.measures_table = a_measures_table
        self.data_view = a_data_view
        self.data_view.verticalHeader().setHidden(True)

        self.measures = OrderedDict()
        self.current_data_model: Union[None, MeasureDataModel] = None

        self.changing_name = ""
        self.names_before_changing = []

        # self.measures_table.cellDoubleClicked.connect(self.measure_cell_double_clicked)
        # self.measures_table.cellChanged.connect(self.measure_name_changed)
        self.measures_table.currentItemChanged.connect(self.current_measure_changed)

    def __get_measures_list(self):
        return [self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                for row in range(self.measures_table.rowCount())]

    @staticmethod
    def __get_allowable_name(a_existing_names: list, a_name_template: str) -> str:
        new_name = a_name_template
        counter = 0
        while new_name in a_existing_names:
            counter += 1
            new_name = f"{a_name_template}_{counter}"
        return new_name

    def measure_cell_double_clicked(self, a_row: int, a_column: int):
        if a_column == MeasureManager.MeasureColumn.NAME:
            self.changing_name = self.measures_table.item(a_row, a_column).text()
            self.names_before_changing = self.__get_measures_list()

    def measure_name_changed(self, a_row: int, a_column: int):
        if a_column == MeasureManager.MeasureColumn.NAME:
            self.measures_table.blockSignals(True)

            new_name = self.measures_table.item(a_row, a_column).text()
            new_name = self.__get_allowable_name(self.names_before_changing, new_name)
            self.measures_table.item(a_row, a_column).setText(new_name)

            if self.changing_name != new_name:
                # try rename
                pass

            self.measures_table.blockSignals(False)

    def add_measure(self):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        row_index = selected_row if selected_row is not None else self.measures_table.rowCount()
        new_name = self.__get_allowable_name(self.__get_measures_list(), "Новое измерение")

        self.measures[new_name] = MeasureDataModel()

        self.measures_table.insertRow(row_index)
        self.measures_table.setItem(row_index, MeasureManager.MeasureColumn.NAME,
                                    QtWidgets.QTableWidgetItem(new_name))

        button = QtWidgets.QToolButton()
        button.setText("...")
        self.measures_table.setCellWidget(row_index, MeasureManager.MeasureColumn.SETTINGS,
                                          qt_utils.wrap_in_layout(button))

        cb = QtWidgets.QCheckBox()
        self.measures_table.setCellWidget(row_index, MeasureManager.MeasureColumn.ENABLE, qt_utils.wrap_in_layout(cb))

        self.set_measure_save_state(new_name, False)
        self.measures_table.setCurrentCell(row_index, MeasureManager.MeasureColumn.NAME)

    def remove_measure(self):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        if selected_row is not None:
            removed_name = self.measures_table.item(selected_row, MeasureManager.MeasureColumn.NAME).text()
            self.measures_table.removeRow(selected_row)

            del self.measures[removed_name]
            return removed_name
        else:
            return None

    def add_row_to_current_measure(self):
        if self.current_data_model is not None:
            selection = self.data_view.selectionModel().selectedIndexes()
            if selection:
                row_position = max(selection, key=lambda idx: idx.row())
                self.current_data_model.add_row(row_position.row())

    def remove_row_from_current_measure(self):
        if self.current_data_model is not None:
            # Множество для сортировки и удаления дубликатов
            removing_rows = list(set(index.row() for index in self.data_view.selectionModel().selectedIndexes()))
            for row in reversed(removing_rows):
                self.current_data_model.remove_row(row)

    def add_column_to_current_measure(self):
        if self.current_data_model is not None:
            selection = self.data_view.selectionModel().selectedIndexes()
            if selection:
                col_position = max(selection, key=lambda idx: idx.column())
                self.current_data_model.add_column(col_position.column())

    def remove_column_from_current_measure(self):
        if self.current_data_model is not None:
            # Множество для сортировки и удаления дубликатов
            removing_cols = list(set(index.column() for index in self.data_view.selectionModel().selectedIndexes()))
            for column in reversed(removing_cols):
                self.current_data_model.remove_column(column)

    def current_measure_changed(self, a_current: QtWidgets.QTableWidgetItem, _):
        if a_current is not None:
            self.current_data_model = self.measures[a_current.text()]
            self.data_view.setModel(self.current_data_model)
        else:
            self.current_data_model = None

    def set_measure_save_state(self, a_measure_name: str, a_saved: bool):
        for row in range(self.measures_table.rowCount()):
            measure_item = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME)
            if measure_item.text() == a_measure_name:
                if a_saved:
                    measure_item.setBackground(QtCore.Qt.white)
                else:
                    measure_item.setBackground(QtCore.Qt.yellow)

    def save(self):
        for measure in self.measures.keys():
            self.set_measure_save_state(measure, True)
