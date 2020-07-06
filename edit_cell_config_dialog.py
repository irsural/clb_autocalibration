from collections import namedtuple
from enum import IntEnum
from typing import List, Union
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.settings_ini_parser import Settings
from irspy.qt.custom_widgets.QTableDelegates import ComboboxCellDelegate

from ui.py.edit_cell_config_dialog import Ui_Dialog as EditCellConfigForm
from irspy.clb import calibrator_constants as clb
from irspy.qt import qt_utils
import irspy.utils as utils


class CellConfig:
    ExtraParameter = namedtuple("ExtraParameter", ["name", "index", "type", "work_value", "default_value"])

    def __init__(self):
        self.coefficient = 1
        self.measure_delay = 0
        self.measure_time = 0
        self.retry_count = 1

        self.consider_output_value = False
        self.enable_output_filtering = False
        self.filter_sampling_time = 0.1
        self.filter_samples_count = 100

        self.extra_parameters: List[CellConfig.ExtraParameter] = []


class EditCellConfigDialog(QtWidgets.QDialog):
    class ExtraParamsColumn(IntEnum):
        NAME = 0
        INDEX = 1
        TYPE = 2
        WORK_VALUE = 3
        DEFAULT_VALUE = 4
        COUNT = 5

    def __init__(self, a_init_config: CellConfig, a_signal_type: clb.SignalType, a_settings: Settings,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = EditCellConfigForm()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)
        self.show()

        self.__allowed_extra_param_types = ("double", "float", "bit", "u32", "i32", "u8", "i8", "u16", "i16",
                                            "bool", "u64", "i64")
        self.ui.extra_variables_table.setItemDelegateForColumn(EditCellConfigDialog.ExtraParamsColumn.TYPE,
                                                               ComboboxCellDelegate(self,
                                                                                    self.__allowed_extra_param_types))

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.extra_variables_table.horizontalHeader().restoreState(self.settings.get_last_geometry(
            self.ui.extra_variables_table.objectName()))

        self.signal_type_to_radio = {
            clb.SignalType.ACI: self.ui.aci_radio,
            clb.SignalType.ACV: self.ui.acv_radio,
            clb.SignalType.DCI: self.ui.dci_radio,
            clb.SignalType.DCV: self.ui.dcv_radio
        }

        self.cell_config = None
        self.signal_type = a_signal_type
        self.recover_config(a_init_config)

        self.ui.add_extra_param_button.clicked.connect(self.add_extra_param_button_clicked)
        self.ui.remove_extra_param_button.clicked.connect(self.remove_extra_param_button_clicked)

        self.ui.accept_button.clicked.connect(self.accept_config)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditCellConfigDialog deleted")

    def recover_config(self, a_cell_config: CellConfig):
        self.signal_type_to_radio[self.signal_type].setChecked(True)

        for extra_parameter in a_cell_config.extra_parameters:
            qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, (
                extra_parameter.name, utils.float_to_string(extra_parameter.index), extra_parameter.type,
                utils.float_to_string(extra_parameter.work_value), utils.float_to_string(extra_parameter.default_value)
            ))

    def exec_and_get(self) -> Union[CellConfig, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.cell_config
        else:
            return None

    def accept_config(self):
        extra_parameters = []
        try:
            for row in range(self.ui.extra_variables_table.rowCount()):
                extra_parameters.append(CellConfig.ExtraParameter(
                    name=self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.NAME).text(),
                    index=float(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.INDEX).text()),
                    type=self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.TYPE).text(),
                    work_value=float(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.WORK_VALUE).text()),
                    default_value=float(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.DEFAULT_VALUE).text())
                ))
            table_valid = True
        except ValueError:
            table_valid = False

        if table_valid:
            self.cell_config = CellConfig()

            self.cell_config.extra_parameters = extra_parameters

            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Таблица дополнительных параметров заполнена неверно",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def add_extra_param_button_clicked(self):
        init_row = [""] * EditCellConfigDialog.FlashColumn.COUNT
        init_row[EditCellConfigDialog.ExtraParamsColumn.TYPE] = self.__allowed_extra_param_types[0]

        qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, init_row)

    def remove_extra_param_button_clicked(self):
        qt_utils.qtablewidget_delete_selected(self.ui.extra_variables_table)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.extra_variables_table.objectName(),
                                    self.ui.extra_variables_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())

        a_event.accept()
