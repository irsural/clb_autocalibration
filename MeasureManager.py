from collections import namedtuple
from typing import Union, Dict
from collections import OrderedDict
from enum import IntEnum
import json
import os
import logging

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.settings_ini_parser import Settings
from irspy.qt import qt_utils
from irspy import utils

from edit_measure_parameters_dialog import EditMeasureParametersDialog
from edit_cell_config_dialog import EditCellConfigDialog
from MeasureDataModel import MeasureDataModel


class MeasureManager(QtCore.QObject):
    class MeasureColumn(IntEnum):
        NAME = 0
        SETTINGS = 1
        ENABLE = 2

    MEASURE_FILE_EXTENSION = "measure"
    MEASURES_ORDER_FILENAME = "measures_order.json"

    def __init__(self, a_measures_table: QtWidgets.QTableWidget, a_data_view: QtWidgets.QTableView,
                 a_settings: Settings, a_parent=None):
        super().__init__(a_parent)

        self.settings = a_settings
        self.measures_table = a_measures_table
        self.data_view = a_data_view
        self.data_view.verticalHeader().setHidden(True)

        self.measures: Dict[str, MeasureDataModel] = OrderedDict()
        self.current_data_model: Union[None, MeasureDataModel] = None

        self.rename_in_process = False
        self.changing_name = ""
        self.names_before_changing = []

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

    def rename_measure_started(self, a_row: int, a_column: int):
        if a_column == MeasureManager.MeasureColumn.NAME:
            self.rename_in_process = True
            self.changing_name = self.measures_table.item(a_row, a_column).text()
            self.names_before_changing = self.__get_measures_list()

    def rename_measure_finished(self, a_row: int, a_column: int, a_measures_folder: str):
        if a_column == MeasureManager.MeasureColumn.NAME and self.rename_in_process:
            self.measures_table.blockSignals(True)

            new_name = self.measures_table.item(a_row, a_column).text()
            new_name = self.__get_allowable_name(self.names_before_changing, new_name)

            if self.changing_name != new_name:
                try:
                    if a_measures_folder:
                        old_filename = f"{a_measures_folder}/{self.changing_name}.{MeasureManager.MEASURE_FILE_EXTENSION}"
                        new_filename = f"{a_measures_folder}/{new_name}.{MeasureManager.MEASURE_FILE_EXTENSION}"
                        os.rename(old_filename, new_filename)

                        self.measures[new_name] = self.measures[self.changing_name]
                        self.measures[new_name].set_name(new_name)
                        del self.measures[self.changing_name]

                    self.measures_table.item(a_row, a_column).setText(new_name)

                    if a_measures_folder:
                        self.__save_measures_order_list(a_measures_folder)
                except OSError:
                    self.measures_table.item(a_row, a_column).setText(self.changing_name)

                    QtWidgets.QMessageBox.critical(None, "Ошибка", f'Не удалось переименовать измерение '
                                                                   f'"{self.changing_name}" в {new_name}"',
                                                   QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            self.rename_in_process = False
            self.measures_table.blockSignals(False)

    def new_measure(self, a_name="", a_measure_data_model: MeasureDataModel = None):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        row_index = selected_row + 1 if selected_row is not None else self.measures_table.rowCount()
        new_name = a_name if a_name else self.__get_allowable_name(self.__get_measures_list(), "Новое измерение")

        measure_data_model = a_measure_data_model if a_measure_data_model else MeasureDataModel(new_name)
        self.measures[new_name] = measure_data_model
        measure_data_model.data_save_state_changed.connect(self.set_measure_save_state)

        self.add_measure_in_table(row_index, new_name, measure_data_model.is_enabled())

        self.set_measure_save_state(new_name, measure_data_model.is_saved())
        self.measures_table.setCurrentCell(row_index, MeasureManager.MeasureColumn.NAME)

    def add_measure_in_table(self, a_row_index: int, a_name: str, a_enabled: bool):
        self.measures_table.insertRow(a_row_index)
        self.measures_table.setItem(a_row_index, MeasureManager.MeasureColumn.NAME,
                                    QtWidgets.QTableWidgetItem(a_name))

        button = QtWidgets.QToolButton()
        button.setText("...")
        self.measures_table.setCellWidget(a_row_index, MeasureManager.MeasureColumn.SETTINGS,
                                          qt_utils.wrap_in_layout(button))
        button.clicked.connect(self.edit_measure_parameters_button_clicked)

        cb = QtWidgets.QCheckBox()
        self.measures_table.setCellWidget(a_row_index, MeasureManager.MeasureColumn.ENABLE, qt_utils.wrap_in_layout(cb))
        cb.toggled.connect(self.enable_measure_checkbox_toggled)
        cb.setChecked(a_enabled)

    # noinspection PyTypeChecker
    def remove_measure(self, a_measure_folder: str):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        if selected_row is not None:
            removed_name = self.measures_table.item(selected_row, MeasureManager.MeasureColumn.NAME).text()
            cancel_remove = False
            if a_measure_folder:
                res = QtWidgets.QMessageBox.question(None, "Подтвердите действие",
                                                     f"Удалить измерение с именем {removed_name}? "
                                                     f"Данное действие нельзя отменить",
                                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                     QtWidgets.QMessageBox.No)
                if res == QtWidgets.QMessageBox.No:
                    cancel_remove = True

            if not cancel_remove:
                self.measures_table.removeRow(selected_row)
                del self.measures[removed_name]
                self.__save_measures_order_list(a_measure_folder)
                os.remove(f"{a_measure_folder}/{removed_name}.{MeasureManager.MEASURE_FILE_EXTENSION}")
                return removed_name
        else:
            return None

    def open_cell_configuration(self):
        if self.current_data_model is not None:
            selected_indexes = self.data_view.selectionModel().selectedIndexes()
            if len(selected_indexes) == 1:
                row, column = selected_indexes[0].row(), selected_indexes[0].column()
                cell_config = self.current_data_model.get_cell_config(row, column)
                if cell_config is not None:
                    signal_type = self.current_data_model.get_measure_parameters().signal_type

                    edit_cell_config_dialog = EditCellConfigDialog(cell_config, signal_type, self.settings)
                    new_cell_config = edit_cell_config_dialog.exec_and_get()
                    if new_cell_config is not None:
                        self.current_data_model.set_cell_config(row, column, new_cell_config)

                    edit_cell_config_dialog.close()

            elif len(selected_indexes) > 1:
                QtWidgets.QMessageBox.critical(None, "Ошибка", "Необходимо выбрать ровно одну ячейку",
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def lock_selected_cells(self, a_lock):
        if self.current_data_model is not None:
            for cell in self.data_view.selectionModel().selectedIndexes():
                self.current_data_model.lock_cell(cell.row(), cell.column(), a_lock)

    def show_equal_cell_configs(self, a_enable: bool):
        if self.current_data_model is not None:
            if a_enable:
                selected_indexes = self.data_view.selectedIndexes()
                if selected_indexes:
                    self.current_data_model.set_cell_to_compare(selected_indexes[0])
            else:
                self.current_data_model.reset_cell_to_compare()

    def set_cell_to_compare(self, a_index: QtCore.QModelIndex):
        if self.current_data_model is not None:
            self.current_data_model.set_cell_to_compare(a_index)

    def add_row_to_current_measure(self):
        if self.current_data_model is not None:
            selection = self.data_view.selectionModel().selectedIndexes()
            if selection:
                row = max(selection, key=lambda idx: idx.row()).row()
            else:
                row = self.current_data_model.rowCount()
            self.current_data_model.add_row(row)

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
                column = max(selection, key=lambda idx: idx.column()).column()
            else:
                column = self.current_data_model.columnCount()
            self.current_data_model.add_column(column)

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

    @utils.exception_decorator
    def edit_measure_parameters_button_clicked(self, _):
        button: QtWidgets.QPushButton = self.sender()
        for row in range(self.measures_table.rowCount()):
            cell_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.SETTINGS)
            row_button = qt_utils.unwrap_from_layout(cell_widget)
            if button == row_button:
                measure_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                measure_data_model = self.measures[measure_name]
                measure_parameters = measure_data_model.get_measure_parameters()

                edit_parameters_dialog = EditMeasureParametersDialog(measure_parameters, self.settings)
                new_parameters = edit_parameters_dialog.exec_and_get()
                if new_parameters is not None:
                    measure_data_model.set_measure_parameters(new_parameters)

                # Иначе не вызывается closeEvent()
                edit_parameters_dialog.close()
                return

        assert False, "Не найдена строка таблицы с виджетом-отправителем сигнала"

    @utils.exception_decorator
    def enable_measure_checkbox_toggled(self, _):
        checkbox: QtWidgets.QPushButton = self.sender()
        for row in range(self.measures_table.rowCount()):
            cell_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.ENABLE)
            row_checkbox = qt_utils.unwrap_from_layout(cell_widget)
            if checkbox == row_checkbox:
                measure_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                measure_data_model = self.measures[measure_name]
                measure_data_model.set_enabled(checkbox.isChecked())
                return

        assert False, "Не найдена строка таблицы с виджетом-отправителем сигнала"

    def is_saved(self):
        return all([data_model.is_saved() for data_model in self.measures.values()])

    def is_current_saved(self):
        saved = True if self.current_data_model is None else self.current_data_model.is_saved()
        return saved

    def save_current(self, a_folder):
        if self.current_data_model is not None:
            self.__save_measures_order_list(a_folder)
            measure_filename = f"{a_folder}/{self.current_data_model.get_name()}.{MeasureManager.MEASURE_FILE_EXTENSION}"
            try:
                with open(measure_filename, "w") as measure_file:
                    measure_file.write(self.current_data_model.serialize())

                self.current_data_model.set_save_state(True)
            except OSError:
                pass
            return self.is_current_saved()
        else:
            return True

    def __save_measures_order_list(self, a_folder):
        measure_order_filename = f"{a_folder}/{MeasureManager.MEASURES_ORDER_FILENAME}"

        with open(measure_order_filename, "w") as measure_order_file:
            measures_list = [f"{measure}.{MeasureManager.MEASURE_FILE_EXTENSION}"
                             for measure in self.__get_measures_list()]
            measures_order = json.dumps(measures_list, ensure_ascii=False)
            measure_order_file.write(measures_order)

    def save(self, a_folder: str):
        self.__save_measures_order_list(a_folder)
        for measure_name in self.measures.keys():
            measure_data_model = self.measures[measure_name]
            measure_filename = f"{a_folder}/{measure_name}.{MeasureManager.MEASURE_FILE_EXTENSION}"
            try:
                with open(measure_filename, "w") as measure_file:
                    measure_file.write(measure_data_model.serialize())

                measure_data_model.set_save_state(True)
            except OSError:
                pass
        return self.is_saved()

    def load_from_file(self, a_folder: str) -> bool:
        measures_order = []
        measure_order_filename = f"{a_folder}/{MeasureManager.MEASURES_ORDER_FILENAME}"
        if os.path.exists(measure_order_filename):
            with open(measure_order_filename, "r") as measure_order_file:
                measures_order = json.loads(measure_order_file.read())

        measure_files = [file for file in os.listdir(a_folder) if file.endswith(MeasureManager.MEASURE_FILE_EXTENSION)]

        if measure_files:
            if not measures_order:
                QtWidgets.QMessageBox.warning(None, "Предупреждение", "Файл с порядком измерений не найден, измерения "
                                                                      "будут отсортированы по имени",
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                measures_list = measure_files
            else:
                measures_list = measures_order

            self.measures_table.setRowCount(0)
            self.current_data_model = None
            self.measures.clear()

            for measure_file in measures_list:
                measure_full_path = f"{a_folder}/{measure_file}"
                if os.path.exists(measure_full_path):
                    measure_name = measure_file[:measure_file.find(MeasureManager.MEASURE_FILE_EXTENSION) - 1]
                    # deserialize
                    data_model = MeasureDataModel(measure_name)
                    data_model.set_save_state(True)
                    self.new_measure(measure_name, data_model)
                else:
                    QtWidgets.QMessageBox.warning(None, "Предупреждение", f"Файл измерения {measure_file} не найден!",
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            return True
        else:
            return False
