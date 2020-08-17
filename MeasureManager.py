from typing import Union, Dict, List, Tuple
from collections import OrderedDict
from enum import IntEnum
from array import array
import logging
import copy
import json
import os

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForView
from irspy.built_in_extensions import OrderedDictInsert
from irspy.clb.calibrator_constants import is_ac_signal
from irspy.settings_ini_parser import Settings
from irspy.qt import qt_utils
from irspy import utils

from edit_shared_measure_parameters_dialog import EditSharedMeasureParametersDialog, SharedMeasureParameters
from MeasureIterator import MeasureIteratorDirectByRows, MeasureIterator
from edit_measure_parameters_dialog import EditMeasureParametersDialog
from edit_cell_config_dialog import EditCellConfigDialog, CellConfig
from MeasureDataModel import MeasureDataModel, CellData
import multimeters


class SchemeInCellPainter(TransparentPainterForView):
    COIL_TO_ICON = {
        CellConfig.Coil.NONE: "",
        CellConfig.Coil.VAL_0_01_OHM: ":/scheme/icons/scheme/coil_001.png",
        CellConfig.Coil.VAL_1_OHM: ":/scheme/icons/scheme/coil_1.png",
        CellConfig.Coil.VAL_10_OHM: ":/scheme/icons/scheme/coil_10.png",
    }

    DIVIDER_TO_ICON = {
        CellConfig.Divider.NONE: "",
        CellConfig.Divider.DIV_650_V: ":/scheme/icons/scheme/div_650.png",
        CellConfig.Divider.DIV_500_V: ":/scheme/icons/scheme/div_500.png",
        CellConfig.Divider.DIV_350_V: ":/scheme/icons/scheme/div_350.png",
        CellConfig.Divider.DIV_200_V: ":/scheme/icons/scheme/div_200.png",
        CellConfig.Divider.DIV_55_V: ":/scheme/icons/scheme/div_55.png",
        CellConfig.Divider.DIV_40_V: ":/scheme/icons/scheme/div_40.png",
        CellConfig.Divider.MUL_30_mV: ":/scheme/icons/scheme/mul_30.png",
        CellConfig.Divider.MUL_10_mV: ":/scheme/icons/scheme/mul_10.png",
    }

    def __init__(self, a_parent=None, a_default_color="#f5f0f0"):
        super().__init__(a_parent, a_default_color)

    @staticmethod
    def decode_scheme(a_code: int) -> Tuple[CellConfig.Coil, CellConfig.Divider]:
        assert a_code <= 38, "Неверный код схемы"

        coil = CellConfig.Coil(a_code // 10)
        divider = CellConfig.Divider(a_code % 10)
        return coil, divider

    @staticmethod
    def get_button(a_left, a_top, a_width, a_height, a_icon):
        btn = QtWidgets.QStyleOptionButton()
        btn.rect = QtCore.QRect(a_left, a_top, a_width, a_height)
        btn.features |= QtWidgets.QStyleOptionButton.Flat
        btn.icon = a_icon
        btn.iconSize = QtCore.QSize(a_width, a_height)
        btn.state = QtWidgets.QStyle.State_Enabled
        return btn

    def paint(self, painter: QtGui.QPainter, option, index: QtCore.QModelIndex):
        super().paint(painter, option, index)

        code = index.data(QtCore.Qt.UserRole)
        if code > 0:
            coil, divider = self.decode_scheme(code)
            w = option.rect.height() / 2.5
            h = option.rect.height() / 2.5
            coil_x = option.rect.right() - w + 3
            coil_y = option.rect.top() - 1

            if coil != CellConfig.Coil.NONE:
                coil_icon = QtGui.QIcon(QtGui.QPixmap(self.COIL_TO_ICON[coil]))
                btn = self.get_button(coil_x, coil_y, w, h, coil_icon)
                QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_PushButton, btn, painter)

            if divider != CellConfig.Divider.NONE:
                divider_icon = QtGui.QIcon(QtGui.QPixmap(self.DIVIDER_TO_ICON[divider]))
                btn = self.get_button(coil_x - w, coil_y, w, h, divider_icon)
                QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_PushButton, btn, painter)


class MeasureManager(QtCore.QObject):
    class MeasureColumn(IntEnum):
        NAME = 0
        SETTINGS = 1
        ENABLE = 2

    class IterationType(IntEnum):
        START_ALL = 0
        CONTINUE_ALL = 1
        START_CURRENT = 2
        CONTINUE_CURRENT = 3

    class GraphType(IntEnum):
        NONE = 0
        Z_X = 1
        Z_Y = 2

    MEASURE_FILE_EXTENSION = "measure"
    MEASURES_ORDER_FILENAME = "measures_order.json"
    SHARED_PARAMETERS_FILENAME = "shared_measure_parameters.json"

    SAVED_COLOR = QtCore.Qt.white
    UNSAVED_COLOR = QtGui.QColor(255, 235, 179)

    new_value_measured = QtCore.pyqtSignal(float, float)

    def __init__(self, a_measures_table: QtWidgets.QTableWidget, a_data_view: QtWidgets.QTableView,
                 a_settings: Settings, a_parent=None):
        # a_parent специально не передается в super, потому что иначе MeasureManager не удаляется в MainWindow при
        # пересоздании
        super().__init__(None)

        self.settings = a_settings
        self.__parent = a_parent
        self.measures_table = a_measures_table
        self.measures_table.setRowCount(0)

        self.measures_table.horizontalHeader().resizeSection(MeasureManager.MeasureColumn.SETTINGS, 70)
        self.measures_table.horizontalHeader().resizeSection(MeasureManager.MeasureColumn.ENABLE, 50)

        self.measures_table.horizontalHeader().setSectionResizeMode(MeasureManager.MeasureColumn.NAME,
                                                                    QtWidgets.QHeaderView.Stretch)
        self.measures_table.horizontalHeader().setSectionResizeMode(MeasureManager.MeasureColumn.ENABLE,
                                                                    QtWidgets.QHeaderView.Fixed)
        self.measures_table.horizontalHeader().setSectionResizeMode(MeasureManager.MeasureColumn.SETTINGS,
                                                                    QtWidgets.QHeaderView.Fixed)

        self.data_view = a_data_view
        self.data_view.setModel(None)

        self.measures: Dict[str, MeasureDataModel] = OrderedDictInsert()
        self.current_data_model: Union[None, MeasureDataModel] = None

        self.shared_measure_parameters: Union[None, SharedMeasureParameters] = None
        self.shared_measure_parameters_changed: bool = False

        self.show_equal_cells = False
        self.copied_cell_config: Union[None, CellConfig] = None

        self.interface_is_locked = False

        self.meter: Union[None, multimeters.MultimeterBase] = None
        self.set_meter(multimeters.MeterType.AGILENT_3458A)

        self.displayed_data: CellData.GetDataType = CellData.GetDataType.MEASURED

        self.measures_table.currentItemChanged.connect(self.current_measure_changed)

    def __del__(self):
        print("MeasureManager deleted")

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

    def get_only_selected_cell(self) -> Union[None, QtCore.QModelIndex]:
        selected_indexes = self.data_view.selectionModel().selectedIndexes()
        if len(selected_indexes) == 1:
            return selected_indexes[0]
        elif len(selected_indexes) > 1:
            QtWidgets.QMessageBox.critical(None, "Ошибка", "Необходимо выбрать ровно одну ячейку",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            return None

    @staticmethod
    def __get_full_path_to_measure(a_folder: str, a_measure_name: str):
        return f"{a_folder}/{a_measure_name}.{MeasureManager.MEASURE_FILE_EXTENSION}"

    def __rename_measure(self, a_measure_row, a_old_name, a_new_name, a_folder):
        if a_folder:
            old_full_path = self.__get_full_path_to_measure(a_folder, a_old_name)
            new_full_path = self.__get_full_path_to_measure(a_folder, a_new_name)
            os.rename(old_full_path, new_full_path)

        data_model = self.measures[a_old_name]
        del self.measures[a_old_name]
        self.measures.insert(a_measure_row, a_new_name, data_model)

        measure_item = self.measures_table.item(a_measure_row, MeasureManager.MeasureColumn.NAME)
        measure_item.setText(a_new_name)
        # Обязательно вызывать после изменения текста в таблице
        data_model.set_name(a_new_name)
        self.current_measure_changed(measure_item, None)

        if a_folder:
            if not self.save_current(a_folder):
                QtWidgets.QMessageBox.critical(None, "Ошибка", f'При переименовании измерения возникла ошибка!!'
                                                               f'Необходимо вручную изменить имя в файле измерения '
                                                               f'"имя_измерения.measure"',
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def rename_current_measure(self, a_folder):
        if self.current_data_model:
            selected_indexes = self.measures_table.selectedIndexes()
            if selected_indexes:
                # Разрешено выделение только по строкам, так что у всех ячеек будет одинаковая строка
                row = selected_indexes[0].row()

                names_before_changing = self.__get_measures_list()
                changing_name = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME).text()

                # noinspection PyTypeChecker
                new_name, accept = QtWidgets.QInputDialog.getText(self.__parent, "Переименование измерения",
                                                                  "Введите новое имя измерения\t\t\t",
                                                                  text=changing_name)

                if accept and changing_name != new_name:
                    new_name = self.__get_allowable_name(names_before_changing, new_name)

                    try:
                        self.__rename_measure(row, changing_name, new_name, a_folder)
                    except OSError:
                        QtWidgets.QMessageBox.critical(None, "Ошибка", f'Не удалось переименовать измерение '
                                                                       f'"{changing_name}" в "{new_name}"',
                                                       QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def new_measure(self, a_name="", a_measure_data_model: MeasureDataModel = None):
        selected_row = qt_utils.get_selected_row(self.measures_table)
        row_index = selected_row + 1 if selected_row is not None else self.measures_table.rowCount()
        new_name = a_name if a_name else self.__get_allowable_name(self.__get_measures_list(), "Новое измерение")

        measure_data_model = a_measure_data_model if a_measure_data_model else \
            MeasureDataModel(new_name, self.shared_measure_parameters)

        self.measures.insert(row_index, new_name, measure_data_model)
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

    def get_cell_config(self, a_measure_name: str, a_row: int, a_column: int) -> CellConfig:
        assert a_measure_name in self.measures, f"Не найдено измерение с именем {a_measure_name}"
        return self.measures[a_measure_name].get_cell_config(a_row, a_column)

    def get_measure_parameters(self, a_measure_name: str):
        assert a_measure_name in self.measures, f"Не найдено измерение с именем {a_measure_name}"
        return self.measures[a_measure_name].get_measure_parameters()

    def get_amplitude(self, a_measure_name: str, a_row: int) -> float:
        return self.measures[a_measure_name].get_amplitude(a_row)

    def get_frequency(self, a_measure_name: str, a_column: int) -> float:
        return self.measures[a_measure_name].get_frequency(a_column)

    def get_table_values(self, a_measure_name) -> List[List[Union[None, float]]]:
        data_model = self.measures[a_measure_name]
        table = []
        for row in range(data_model.rowCount()):
            table_row = []
            for column in range(data_model.columnCount()):
                cell_value = data_model.get_cell_value(row, column, CellData.GetDataType.MEASURED)
                table_row.append(cell_value)
            table.append(table_row)
        return table

    def open_cell_configuration(self):
        selected_index = self.get_only_selected_cell()
        if selected_index:
            row, column = selected_index.row(), selected_index.column()
            cell_config = self.current_data_model.get_cell_config(row, column)
            if cell_config is not None:
                measure_name = self.current_data_model.get_name()
                signal_type = self.current_data_model.get_measure_parameters().signal_type
                frequency = self.current_data_model.get_frequency(column) if is_ac_signal[signal_type] else 0

                edit_cell_config_dialog = EditCellConfigDialog(cell_config, self.shared_measure_parameters,
                                                               frequency, signal_type, self.settings,
                                                               self.interface_is_locked, self.__parent)

                new_cell_config = edit_cell_config_dialog.exec_and_get()
                if new_cell_config is not None and new_cell_config != cell_config:
                    self.measures[measure_name].set_cell_config(row, column, new_cell_config)

                edit_cell_config_dialog.close()

    @utils.exception_decorator
    def open_shared_measure_parameters(self):
        shared_parameter_dialog = EditSharedMeasureParametersDialog(self.shared_measure_parameters, self.settings,
                                                                    self.interface_is_locked, self.__parent)
        new_shared_parameters = shared_parameter_dialog.exec_and_get()
        if new_shared_parameters is not None and new_shared_parameters != self.shared_measure_parameters:
            self.shared_measure_parameters_changed = True
            self.shared_measure_parameters = new_shared_parameters
            self.__calculate_coefficients_for_all_auto_cells()
        shared_parameter_dialog.close()

    def __calculate_coefficients_for_all_auto_cells(self):
        if self.current_data_model is not None:
            for data_model in self.measures.values():
                data_model.update_shared_parameters(self.shared_measure_parameters)

    def lock_selected_cells(self, a_lock):
        if self.current_data_model is not None:
            for cell in self.data_view.selectionModel().selectedIndexes():
                self.current_data_model.lock_cell(cell.row(), cell.column(), a_lock)

    def lock_all_cells(self, a_lock):
        if self.current_data_model is not None:
            for data_model in self.measures.values():
                data_model.lock_all_cells(a_lock)

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
            # Множество для удаления дубликатов
            removing_rows = list(set(index.row() for index in self.data_view.selectionModel().selectedIndexes()))
            removing_rows.sort()
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
            # Множество для удаления дубликатов
            removing_cols = list(set(index.column() for index in self.data_view.selectionModel().selectedIndexes()))
            removing_cols.sort()
            for column in reversed(removing_cols):
                self.current_data_model.remove_column(column)

    def clear_table_content(self):
        if self.current_data_model is not None:
            # noinspection PyTypeChecker
            res = QtWidgets.QMessageBox.question(None, "Подтвердите действие",
                                                 f"Очистить содержимое таблицы? Заголовки таблицы не изменятся.",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 QtWidgets.QMessageBox.No)
            if res == QtWidgets.QMessageBox.Yes:
                self.current_data_model.reset_all_cells()
                self.current_data_model.set_save_state(False)

    def copy_cell_config(self):
        if self.current_data_model is not None:
            index = self.get_only_selected_cell()
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
            selected_indices = sorted(self.data_view.selectionModel().selectedIndexes())
            if selected_indices:
                copy_str = ""
                prev_row = selected_indices[0].row()
                for num, cell_idx in enumerate(selected_indices):
                    if prev_row != cell_idx.row():
                        prev_row = cell_idx.row()
                        copy_str += "\n"
                    elif num != 0:
                        copy_str += "\t"

                    cell_value = self.current_data_model.get_cell_value(cell_idx.row(), cell_idx.column())
                    value_str = utils.float_to_string(cell_value, a_precision=15) if cell_value is not None else "0"
                    copy_str += f"{value_str}"

                QtWidgets.QApplication.clipboard().setText(copy_str)

    def paste_cell_value(self):
        if self.current_data_model is not None:
            for index in self.data_view.selectedIndexes():
                value = QtWidgets.QApplication.clipboard().text()
                self.current_data_model.setData(index, value)

    def __lock_measure_table(self, a_lock: bool):
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

    def lock_interface(self, a_lock: bool):
        for row in range(self.measures_table.rowCount()):
            enabled_widget = self.measures_table.cellWidget(row, MeasureManager.MeasureColumn.ENABLE)
            enabled_button = qt_utils.unwrap_from_layout(enabled_widget)
            enabled_button.setDisabled(a_lock)

        self.interface_is_locked = a_lock

        lock_table = self.displayed_data != CellData.GetDataType.MEASURED or a_lock
        self.__lock_measure_table(lock_table)

    def get_current_measure(self):
        if self.current_data_model:
            return self.current_data_model.get_name()
        else:
            return None

    def get_enabled_measures(self) -> List[str]:
        return [name for name in self.measures.keys() if self.measures[name].is_enabled()]

    def get_measure_iterator(self, a_iteration_type: IterationType):
        pass_through_measures = a_iteration_type in (MeasureManager.IterationType.START_ALL,
                                                     MeasureManager.IterationType.CONTINUE_ALL)

        if a_iteration_type in (MeasureManager.IterationType.START_ALL, MeasureManager.IterationType.START_CURRENT):
            return self.__get_measure_iterator(pass_through_measures)
        else:
            return self.__get_measure_iterator_from_current(pass_through_measures)

    def __get_measure_iterator(self, a_pass_through_measures: bool):
        iterator = None
        if self.current_data_model:
            measure_models_list = [data_model for data_model in self.measures.values() if data_model.is_enabled()] \
                if a_pass_through_measures else [self.current_data_model]

            if measure_models_list:
                iterator = MeasureIteratorDirectByRows(measure_models_list)

        return iterator

    def __get_measure_iterator_from_current(self, a_pass_through_measures: bool):
        iterator = None
        if self.current_data_model:
            selected_cells_idx = self.get_only_selected_cell()
            if selected_cells_idx:

                measure_models_list = []
                if a_pass_through_measures:
                    start_add = False
                    for data_model in self.measures.values():
                        if self.current_data_model == data_model:
                            start_add = True
                        if start_add and data_model.is_enabled():
                            measure_models_list.append(data_model)
                else:
                    measure_models_list.append(self.current_data_model)

                if measure_models_list:
                    iterator = MeasureIteratorDirectByRows(measure_models_list,
                                                           (selected_cells_idx.row(), selected_cells_idx.column()))
        return iterator

    def set_active_cell(self, a_cell_pos: MeasureIterator.CellPosition):
        name_item = None
        for row in range(self.measures_table.rowCount()):
            name_item = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME)
            if a_cell_pos.measure_name == name_item.text():
                break

        assert name_item is not None, f"Не найдено измерение с именем {a_cell_pos.measure_name}"

        self.measures_table.setCurrentItem(name_item)
        assert self.current_data_model is not None, f"current_data_model не должна быть None"

        self.data_view.setCurrentIndex(self.current_data_model.index(a_cell_pos.row, a_cell_pos.column))

    def reset_measure(self, a_name: str, a_row, a_column):
        self.measures[a_name].reset_cell(a_row, a_column)

    def add_measured_value(self, a_name: str, a_row, a_column, a_value: float, a_time: float):
        self.measures[a_name].update_cell_with_value(a_row, a_column, a_value, a_time)
        # Используется для обновления графиков
        self.new_value_measured.emit(a_value, a_time)

    def finalize_measure(self, a_name: str, a_row, a_column):
        self.measures[a_name].finalize_cell(a_row, a_column)

    def current_measure_changed(self, a_current: QtWidgets.QTableWidgetItem, _):
        if a_current is not None:
            measure_name = self.measures_table.item(a_current.row(), MeasureManager.MeasureColumn.NAME).text()
            self.current_data_model = self.measures[measure_name]
            self.data_view.setModel(self.current_data_model)
            self.show_equal_cell_configs(self.show_equal_cells)
            self.current_data_model.set_displayed_data(self.displayed_data)
        else:
            self.current_data_model = None

    def set_measure_save_state(self, a_measure_name: str, a_saved: bool):
        for row in range(self.measures_table.rowCount()):
            name_item, param_item, enable_item = self.measures_table.item(row, MeasureManager.MeasureColumn.NAME), \
                                                 self.measures_table.item(row, MeasureManager.MeasureColumn.SETTINGS), \
                                                 self.measures_table.item(row, MeasureManager.MeasureColumn.ENABLE),
            if name_item.text() == a_measure_name:
                color = MeasureManager.SAVED_COLOR if a_saved else MeasureManager.UNSAVED_COLOR
                name_item.setBackground(color)
                param_item.setBackground(color)
                enable_item.setBackground(color)
                break
        else:
            assert False, f"Не найдено измерение с именем {a_measure_name}"

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
                                                                     self.interface_is_locked, self.__parent)
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

    def set_meter(self, a_meter_type: multimeters.MeterType):
        self.meter = multimeters.create_multimeter(a_meter_type, self.settings)
        assert self.meter is not None, f"Не реализованный измеритель '{a_meter_type}'"

    def open_meter_settings(self):
        assert self.meter is not None, f"Не инициализированный измеритель"
        self.meter.edit_settings(self.interface_is_locked, self.__parent)

    def get_meter(self) -> multimeters.MultimeterBase:
        return self.meter

    def set_displayed_data(self, a_displayed_data: CellData.GetDataType):
        self.displayed_data = a_displayed_data
        if self.current_data_model:
            lock_table = self.displayed_data != CellData.GetDataType.MEASURED or self.interface_is_locked
            self.__lock_measure_table(lock_table)

            self.current_data_model.set_displayed_data(a_displayed_data)

    def __extract_z_x_graph(self, a_row: int) -> Tuple[List, List]:
        x = []
        y = []
        amplitude = self.current_data_model.get_amplitude(a_row)
        for column in range(1, self.current_data_model.columnCount()):
            x_val = self.current_data_model.get_frequency(column)
            y_val = self.current_data_model.get_cell_value(a_row, column)

            if amplitude and x_val and y_val is not None:
                x.append(x_val)
                normalized_y = y_val / amplitude
                y.append(normalized_y)

        return x, y

    def __extract_z_y_graph(self, a_column: int) -> Tuple[List, List]:
        x = []
        y = []
        for row in range(1, self.current_data_model.rowCount()):
            x_val = self.current_data_model.get_amplitude(row)
            y_val = self.current_data_model.get_cell_value(row, a_column)

            if x_val and y_val is not None:
                x.append(x_val)
                normalized_y = y_val / x_val
                y.append(normalized_y)

        return x, y

    def get_data_for_graphs(self) -> Dict[str, Tuple[List, List]]:
        data = OrderedDict()
        if self.current_data_model:
            # Получаем все выделенные уникальные строки и колонки, за исключением хэдеров
            selected_rows = list(set(index.row() for index in self.data_view.selectionModel().selectedIndexes()
                                     if index.row() != 0))
            selected_rows.sort()
            selected_columns = list(set(index.column() for index in self.data_view.selectionModel().selectedIndexes()
                                        if index.column() != 0))
            selected_columns.sort()

            if selected_rows and selected_columns:

                graphs_type = MeasureManager.GraphType.NONE

                if len(selected_rows) > 1 and len(selected_columns) > 1 or \
                        len(selected_rows) == len(selected_columns) == 1:
                    msgbox = QtWidgets.QMessageBox()
                    msgbox.setWindowTitle("Выберите действие")
                    msgbox.setText("Обнаружено выделение строк и столбцов. Выберите тип графика.")
                    z_x_button = msgbox.addButton("Z(X)", QtWidgets.QMessageBox.YesRole)
                    z_y_button = msgbox.addButton("Z(Y)", QtWidgets.QMessageBox.AcceptRole)
                    _ = msgbox.addButton("Отмена", QtWidgets.QMessageBox.AcceptRole)
                    msgbox.exec()

                    if msgbox.clickedButton() == z_x_button:
                        graphs_type = MeasureManager.GraphType.Z_X
                    elif msgbox.clickedButton() == z_y_button:
                        graphs_type = MeasureManager.GraphType.Z_Y
                elif len(selected_rows) > 1:
                    graphs_type = MeasureManager.GraphType.Z_X
                elif len(selected_columns) > 1:
                    graphs_type = MeasureManager.GraphType.Z_Y

                if graphs_type == MeasureManager.GraphType.Z_X:
                    for row in selected_rows:
                        graph_name = self.current_data_model.get_amplitude_with_units(row)
                        graph_data = self.__extract_z_x_graph(row)
                        if graph_data[0]:
                            data[graph_name] = graph_data
                elif graphs_type == MeasureManager.GraphType.Z_Y:
                    for column in selected_columns:
                        graph_name = self.current_data_model.get_frequency_with_units(column)
                        graph_data = self.__extract_z_y_graph(column)
                        if graph_data[0]:
                            data[graph_name] = graph_data

            else:
                QtWidgets.QMessageBox.information(None, "Информация",
                                                  f"Для построения графиков необходимо выделить соответствующие ячейки",
                                                  QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        return data

    def get_cell_measurement_graph(self) -> Dict[str, Tuple[array, array]]:
        graphs = OrderedDict()
        if self.current_data_model:
            cell = self.get_only_selected_cell()
            if cell:
                measurement_graph = self.current_data_model.get_cell_measured_values(cell.row(), cell.column())
                times = measurement_graph[0]
                if times:
                    graph_values_name = f"Ячейка {self.current_data_model.get_amplitude_with_units(cell.row())}; " \
                                        f"{self.current_data_model.get_frequency_with_units(cell.column())}"

                    measure_result = self.current_data_model.get_cell_value(cell.row(), cell.column(),
                                                                            CellData.GetDataType.MEASURED)
                    result_graph = ([times[0], times[-1]], [measure_result, measure_result])

                    graphs[graph_values_name] = measurement_graph
                    graphs["Результат"] = result_graph

        return graphs

    def is_saved(self):
        return all([data_model.is_saved() for data_model in self.measures.values()]) and \
               not self.shared_measure_parameters_changed

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

    def __save_shared_measure_parameters(self, a_folder):
        shared_parameters_filename = f"{a_folder}/{MeasureManager.SHARED_PARAMETERS_FILENAME}"

        with open(shared_parameters_filename, "w") as shared_parameters_file:
            shared_parameters = json.dumps(self.shared_measure_parameters.serialize_to_dict(),
                                           ensure_ascii=False, indent=4)
            shared_parameters_file.write(shared_parameters)
            self.shared_measure_parameters_changed = False

    def save_current(self, a_folder):
        if self.current_data_model is not None:
            self.__save_measures_order_list(a_folder)
            self.__save_shared_measure_parameters(a_folder)
            measure_filename = self.__get_full_path_to_measure(a_folder, self.current_data_model.get_name())
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
        self.__save_shared_measure_parameters(a_folder)
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

            shared_parameters_filename = f"{a_folder}/{MeasureManager.SHARED_PARAMETERS_FILENAME}"
            if os.path.exists(shared_parameters_filename):
                with open(shared_parameters_filename, 'r') as shared_parameters_file:
                    shared_parameters_dict = json.loads(shared_parameters_file.read())
                    self.shared_measure_parameters = SharedMeasureParameters.from_dict(shared_parameters_dict)
            else:
                self.shared_measure_parameters = SharedMeasureParameters()
                QtWidgets.QMessageBox.warning(None, "Предупреждение", f"Файл общих параметров измерения не найден! "
                                                                      f"Будут использованы параметры по-умолчанию",
                                              QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                # Сразу сохраняем если отсутствуют
                self.shared_measure_parameters_changed = True
                self.__save_shared_measure_parameters(a_folder)

            for measure_filename in measures_list:
                measure_full_path = f"{a_folder}/{measure_filename}"
                if os.path.exists(measure_full_path):
                    with open(measure_full_path, 'r') as measure_file:
                        data_dict = json.loads(measure_file.read())

                        measure_name = measure_filename[:measure_filename.find(MeasureManager.MEASURE_FILE_EXTENSION) - 1]
                        data_model = MeasureDataModel.from_dict(measure_name, self.shared_measure_parameters, data_dict)
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
