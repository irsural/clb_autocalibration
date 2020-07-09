from collections import OrderedDict
from typing import Union, Dict
from enum import IntEnum
import logging
import copy
import json
import os

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.settings_ini_parser import Settings
from irspy.qt import qt_utils
from irspy import utils

from edit_measure_parameters_dialog import EditMeasureParametersDialog
from edit_cell_config_dialog import EditCellConfigDialog, CellConfig
from MeasureDataModel import MeasureDataModel


class MeasureManager(QtCore.QObject):
    class MeasureColumn(IntEnum):
        NAME = 0
        SETTINGS = 1
        ENABLE = 2

    MEASURE_FILE_EXTENSION = "measure"
    MEASURES_ORDER_FILENAME = "measures_order.json"

    SAVED_COLOR = QtCore.Qt.white
    UNSAVED_COLOR = QtGui.QColor(255, 235, 179)

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

        self.show_equal_cells = False
        self.copied_cell_config: Union[None, CellConfig] = None

        self.interface_is_locked = False

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

    def __get_only_selected_cell(self) -> Union[None, QtCore.QModelIndex]:
        selected_indexes = self.data_view.selectionModel().selectedIndexes()
        if len(selected_indexes) == 1:
            return selected_indexes[0]
        elif len(selected_indexes) > 1:
            QtWidgets.QMessageBox.critical(None, "Ошибка", "Необходимо выбрать ровно одну ячейку",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            return None

    def rename_measure_started(self, a_row: int, a_column: int):
        if a_column == MeasureManager.MeasureColumn.NAME:
            self.rename_in_process = True
            self.changing_name = self.measures_table.item(a_row, a_column).text()
            self.names_before_changing = self.__get_measures_list()

    def rename_measure_finished(self, a_row: int, a_column: int, a_measures_folder: str):
        if a_column == MeasureManager.MeasureColumn.NfAME and self.rename_in_process:
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
        self.measures_table.setItem(a_row_index, MeasureManager.MeasureColumn.SETTINGS,
                                    QtWidgets.QTableWidgetItem())
        self.measures_table.setItem(a_row_index, MeasureManager.MeasureColumn.ENABLE,
                                    QtWidgets.QTableWidgetItem())

        button = QtWidgets.QToolButton()
        button.setText("...")
        self.measures_table.setCellWidget(a_row_index, MeasureManager.MeasureColumn.SETTINGS,
                                          qt_utils.wrap_in_layout(button))
        button.clicked.connect(self.edit_measure_parameters_button_clicked)

        cb = QtWidgets.QCheckBox()
        self.measures_table.setCellWidget(a_row_index, MeasureManager.MeasureColumn.ENABLE, qt_utils.wrap_in_layout(cb))
        cb.setChecked(a_enabled)
        cb.toggled.connect(self.enable_measure_checkbox_toggled)

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
                measure_filename = f"{a_measure_folder}/{removed_name}.{MeasureManager.MEASURE_FILE_EXTENSION}"
                if os.path.exists(measure_filename):
                    os.remove(measure_filename)
                return removed_name
        else:
            return None

    def enable_all_measures(self):
        enable_checkboxes = []
        for row in range(self.measures_table.rowCount()):
            cell_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.ENABLE)
            enable_checkbox = qt_utils.unwrap_from_layout(cell_widget)
            enable_checkboxes.append(enable_checkbox)

        enable = not all([cb.isChecked() for cb in enable_checkboxes])
        for cb in enable_checkboxes:
            cb.setChecked(enable)

    def open_cell_configuration(self):
        selected_index = self.__get_only_selected_cell()
        if selected_index:
            row, column = selected_index.row(), selected_index.column()
            cell_config = self.current_data_model.get_cell_config(row, column)
            if cell_config is not None:
                signal_type = self.current_data_model.get_measure_parameters().signal_type

                edit_cell_config_dialog = EditCellConfigDialog(cell_config, signal_type, self.settings,
                                                               self.interface_is_locked)
                new_cell_config = edit_cell_config_dialog.exec_and_get()
                if new_cell_config is not None and new_cell_config != cell_config:
                    self.current_data_model.set_cell_config(row, column, new_cell_config)

                edit_cell_config_dialog.close()

    def lock_selected_cells(self, a_lock):
        if self.current_data_model is not None:
            for cell in self.data_view.selectionModel().selectedIndexes():
                self.current_data_model.lock_cell(cell.row(), cell.column(), a_lock)

    def show_equal_cell_configs(self, a_enable: bool):
        self.show_equal_cells = a_enable

        if self.current_data_model is not None:
            self.current_data_model.show_equal_cell_configs(a_enable)
            if a_enable:
                selected_indexes = self.data_view.selectedIndexes()
                if selected_indexes:
                    self.current_data_model.set_cell_to_compare(selected_indexes[0])

    def set_cell_to_compare(self, a_index: QtCore.QModelIndex):
        if self.current_data_model is not None:
            self.current_data_model.set_cell_to_compare(a_index)

    def add_row_to_current_measure(self):
        if self.current_data_model is not None:
            selection = self.data_view.selectionModel().selectedIndexes()
            if selection:
                row = max(selection, key=lambda idx: idx.row()).row() + 1
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
                column = max(selection, key=lambda idx: idx.column()).column() + 1
            else:
                column = self.current_data_model.columnCount()
            self.current_data_model.add_column(column)

    def remove_column_from_current_measure(self):
        if self.current_data_model is not None:
            # Множество для сортировки и удаления дубликатов
            removing_cols = list(set(index.column() for index in self.data_view.selectionModel().selectedIndexes()))
            for column in reversed(removing_cols):
                self.current_data_model.remove_column(column)

    def copy_cell_config(self):
        if self.current_data_model is not None:
            index = self.__get_only_selected_cell()
            if index:
                self.copied_cell_config = self.current_data_model.get_cell_config(index.row(), index.column())

    def paste_cell_config(self):
        if self.current_data_model is not None and self.copied_cell_config is not None:
            current_signal_type = self.current_data_model.get_measure_parameters().signal_type
            always_paste = False
            for index in self.data_view.selectedIndexes():
                if self.copied_cell_config != self.current_data_model.get_cell_config(index.row(), index.column()):
                    scheme_is_ok = self.copied_cell_config.verify_scheme(current_signal_type)
                    exec_paste = True
                    if not scheme_is_ok and not always_paste:
                        amplitude = self.current_data_model.get_amplitude_with_units(index.row())
                        frequency = self.current_data_model.get_frequency_with_units(index.column())

                        msgbox = QtWidgets.QMessageBox()
                        msgbox.setWindowTitle("Предупреждение")
                        msgbox.setText(f'Схема подключения ячейки "{amplitude}; {frequency}" не подходит для текущего '
                                       f'типа сигнала.Если вы согласитесь продолжить, то схема ячейки будет сброшена.\n'
                                       f'Вставить конфигурацию ячейки?')
                        always_yes_button = msgbox.addButton("Всегда да", QtWidgets.QMessageBox.YesRole)
                        yes_button = msgbox.addButton("Да", QtWidgets.QMessageBox.AcceptRole)
                        no_button = msgbox.addButton("Нет", QtWidgets.QMessageBox.AcceptRole)
                        msgbox.exec()

                        if msgbox.clickedButton() == always_yes_button:
                            always_paste = True
                        elif msgbox.clickedButton() == no_button:
                            exec_paste = False

                    if exec_paste or always_paste:
                        if not scheme_is_ok:
                            new_cell_config = copy.deepcopy(self.copied_cell_config)
                            new_cell_config.reset_scheme(current_signal_type)
                        else:
                            new_cell_config = self.copied_cell_config

                        self.current_data_model.set_cell_config(index.row(), index.column(), new_cell_config)

    def copy_cell_value(self):
        if self.current_data_model is not None:
            selected_index = self.__get_only_selected_cell()
            if selected_index:
                value: str = self.current_data_model.data(selected_index)
                if value:
                    value_without_units = value.split(" ")[0]
                    QtWidgets.QApplication.clipboard().setText(value_without_units)

    def paste_cell_value(self):
        if self.current_data_model is not None:
            for index in self.data_view.selectedIndexes():
                value = QtWidgets.QApplication.clipboard().text()
                self.current_data_model.setData(index, value)

    def lock_interface(self, a_lock: bool):
        for row in range(self.measures_table.rowCount()):
            enabled_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.ENABLE)
            enabled_button = qt_utils.unwrap_from_layout(enabled_widget)
            enabled_button.setDisabled(a_lock)

            if a_lock:
                self.data_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            else:
                # noinspection PyTypeChecker
                self.data_view.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked |
                                               QtWidgets.QAbstractItemView.EditKeyPressed |
                                               QtWidgets.QAbstractItemView.AnyKeyPressed)
            # Чтобы сбросился фокус с ячейки, если в ней открыт эдитор
            self.data_view.setDisabled(True)
            self.data_view.setDisabled(False)

            self.interface_is_locked = a_lock

    def current_measure_changed(self, a_current: QtWidgets.QTableWidgetItem, _):
        if a_current is not None:
            measure_name = self.measures_table.item(a_current.row(), MeasureManager.MeasureColumn.NAME).text()
            self.current_data_model = self.measures[measure_name]
            self.data_view.setModel(self.current_data_model)
            self.show_equal_cell_configs(self.show_equal_cells)
        else:
            self.current_data_model = None

    def set_measure_save_state(self, a_measure_name: str, a_saved: bool):
        for row in range(self.measures_table.rowCount()):
            name_item, param_item, enable_item = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME),\
                                                 self.measures_table.item(row, MeasureManager.MeasureColumn.SETTINGS),\
                                                 self.measures_table.item(row, MeasureManager.MeasureColumn.ENABLE),
            if name_item.text() == a_measure_name:
                color = MeasureManager.SAVED_COLOR if a_saved else MeasureManager.UNSAVED_COLOR
                name_item.setBackground(color)
                param_item.setBackground(color)
                enable_item.setBackground(color)

    @utils.exception_decorator
    def edit_measure_parameters_button_clicked(self, _):
        # noinspection PyTypeChecker
        button: QtWidgets.QPushButton = self.sender()
        for row in range(self.measures_table.rowCount()):
            cell_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.SETTINGS)
            row_button = qt_utils.unwrap_from_layout(cell_widget)
            if button == row_button:
                measure_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()
                measure_data_model = self.measures[measure_name]
                measure_parameters = measure_data_model.get_measure_parameters()

                edit_parameters_dialog = EditMeasureParametersDialog(measure_parameters, self.settings,
                                                                     self.interface_is_locked)
                new_parameters = edit_parameters_dialog.exec_and_get()
                if new_parameters is not None and new_parameters != measure_parameters:
                    bad_cells = measure_data_model.verify_cell_configs(new_parameters.signal_type)
                    if bad_cells:
                        bad_cells_text = "\n".join([f"{ampli}; {freq}" for ampli, freq in bad_cells])
                        QtWidgets.QMessageBox.warning(None, "Предупреждение",
                                                      f"Схема подключения следующих ячеек не подходит для выбранного "
                                                      f"типа сигнала и БУДЕТ СБРОШЕНА:\n\n{bad_cells_text}.",
                                                      QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    measure_data_model.set_measure_parameters(new_parameters)
                # Иначе не вызывается closeEvent()
                edit_parameters_dialog.close()
                return

        assert False, "Не найдена строка таблицы с виджетом-отправителем сигнала"

    @utils.exception_decorator
    def enable_measure_checkbox_toggled(self, _):
        # noinspection PyTypeChecker
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

    def __save_measures_order_list(self, a_folder):
        measure_order_filename = f"{a_folder}/{MeasureManager.MEASURES_ORDER_FILENAME}"

        with open(measure_order_filename, "w") as measure_order_file:
            measures_list = [f"{measure}.{MeasureManager.MEASURE_FILE_EXTENSION}"
                             for measure in self.__get_measures_list()]
            measures_order = json.dumps(measures_list, ensure_ascii=False, indent=4)
            measure_order_file.write(measures_order)

    def save_current(self, a_folder):
        if self.current_data_model is not None:
            self.__save_measures_order_list(a_folder)
            measure_filename = f"{a_folder}/{self.current_data_model.get_name()}.{MeasureManager.MEASURE_FILE_EXTENSION}"
            try:
                with open(measure_filename, "w") as measure_file:
                    measure_file.write(json.dumps(self.current_data_model.serialize_to_dict(), ensure_ascii=False,
                                                  indent=4))

                self.current_data_model.set_save_state(True)
            except OSError:
                pass
            return self.is_current_saved()
        else:
            return True

    def save(self, a_folder: str):
        self.__save_measures_order_list(a_folder)
        for measure_name in self.measures.keys():
            measure_data_model = self.measures[measure_name]
            measure_filename = f"{a_folder}/{measure_name}.{MeasureManager.MEASURE_FILE_EXTENSION}"
            try:
                with open(measure_filename, "w") as measure_file:
                    measure_file.write(json.dumps(measure_data_model.serialize_to_dict(), ensure_ascii=False, indent=4))

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

            for measure_filename in measures_list:
                measure_full_path = f"{a_folder}/{measure_filename}"
                if os.path.exists(measure_full_path):
                    with open(measure_full_path, 'r') as measure_file:
                        data_dict = json.loads(measure_file.read())

                        measure_name = measure_filename[:measure_filename.find(MeasureManager.MEASURE_FILE_EXTENSION) - 1]
                        data_model = MeasureDataModel.from_dict(measure_name, data_dict)
                        self.new_measure(measure_name, data_model)
                else:
                    QtWidgets.QMessageBox.warning(None, "Предупреждение",
                                                  f"Файл измерения {measure_filename} не найден!",
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            if self.measures_table.rowCount() > 0:
                self.measures_table.setCurrentCell(0, 0)

            return True
        else:
            return False
