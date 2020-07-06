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
    class Coil(IntEnum):
        NONE = 0
        VAL_0_01_OHM = 1
        VAL_1_OHM = 2
        VAL_10_OHM = 3

    class Divider(IntEnum):
        NONE = 0
        DIV_650_V = 1
        DIV_500_V = 2
        DIV_350_V = 3
        DIV_200_V = 4
        DIV_55_V = 5
        DIV_40_V = 6
        MUL_30_mV = 7
        MUL_10_mV = 8

    class Meter(IntEnum):
        AMPERES = 0
        VOLTS = 1

    ExtraParameter = namedtuple("ExtraParameter", ["name", "index", "type", "work_value", "default_value"])

    def __init__(self):
        self.coefficient = 1
        self.measure_delay = 100
        self.measure_time = 300
        self.retry_count = 1

        self.consider_output_value = False
        self.enable_output_filtering = False
        self.filter_sampling_time = 0.1
        self.filter_samples_count = 100

        self.coil = CellConfig.Coil.NONE
        self.divider = CellConfig.Divider.NONE
        self.meter = CellConfig.Meter.AMPERES

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

        self.coil_to_radio = {
            CellConfig.Coil.NONE: self.ui.coil_no_radio,
            CellConfig.Coil.VAL_0_01_OHM: self.ui.coil_001_radio,
            CellConfig.Coil.VAL_1_OHM: self.ui.coil_1_radio,
            CellConfig.Coil.VAL_10_OHM: self.ui.coil_10_radio,
        }
        self.radio_to_coil = {v: k for k, v in self.coil_to_radio.items()}

        self.divider_to_radio = {
            CellConfig.Divider.NONE: self.ui.divider_no_radio,
            CellConfig.Divider.DIV_650_V: self.ui.divider_650_radio,
            CellConfig.Divider.DIV_500_V: self.ui.divider_500_radio,
            CellConfig.Divider.DIV_350_V: self.ui.divider_350_radio,
            CellConfig.Divider.DIV_200_V: self.ui.divider_200_radio,
            CellConfig.Divider.DIV_55_V: self.ui.divider_55_radio,
            CellConfig.Divider.DIV_40_V: self.ui.divider_40_radio,
            CellConfig.Divider.MUL_30_mV: self.ui.amplifier_30_radio,
            CellConfig.Divider.MUL_10_mV: self.ui.amplifier_10_radio,
        }
        self.radio_to_divider = {v: k for k, v in self.divider_to_radio.items()}

        self.meter_to_radio = {
            CellConfig.Meter.AMPERES: self.ui.ammeter_radio,
            CellConfig.Meter.VOLTS: self.ui.voltmeter_radio
        }
        self.radio_to_meter = {v: k for k, v in self.meter_to_radio.items()}

        self.cell_config = None
        self.signal_type = a_signal_type
        self.recover_config(a_init_config)

        self.ui.add_extra_param_button.clicked.connect(self.add_extra_param_button_clicked)
        self.ui.remove_extra_param_button.clicked.connect(self.remove_extra_param_button_clicked)

        self.ui.coefficient_edit.textEdited.connect(self.coefficient_edited)
        self.ui.coefficient_edit.editingFinished.connect(self.editing_finished)

        self.ui.accept_button.clicked.connect(self.accept_config)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditCellConfigDialog deleted")

    def coefficient_edited(self):
        edit = self.sender()
        assert isinstance(edit, QtWidgets.QLineEdit), "edit_text_edited must be connected to QLineEdit event!"
        self.update_edit_color(edit)

    def update_edit_color(self, a_edit: QtWidgets.QLineEdit):
        try:
            utils.parse_input(a_edit.text())
            # По каким то причинам это меняет размер шрифта
            a_edit.setStyleSheet(qt_utils.QSTYLE_COLOR_WHITE + "font-size: 17px;")
        except ValueError:
            a_edit.setStyleSheet(qt_utils.QSTYLE_COLOR_RED + "font-size: 17px;")

    def editing_finished(self):
        edit = self.sender()
        assert isinstance(edit, QtWidgets.QLineEdit), "editinig_finished must be connected to QLineEdit event!"
        self.normalize_edit_value(edit)

    def normalize_edit_value(self, edit: QtWidgets.QLineEdit):
        try:
            value = utils.parse_input(edit.text())
            edit.setText(utils.float_to_string(value))
        except ValueError:
            edit.setText("0")
        self.update_edit_color(edit)

    def recover_config(self, a_cell_config: CellConfig):
        self.signal_type_to_radio[self.signal_type].setChecked(True)

        self.ui.measure_delay_spinbox.setValue(a_cell_config.measure_delay)
        self.ui.measure_time_spinbox.setValue(a_cell_config.measure_time)
        self.ui.retry_count_spinbox.setValue(a_cell_config.retry_count)
        self.ui.coefficient_edit.setText(utils.float_to_string(a_cell_config.coefficient))

        self.ui.consider_output_value_checkbox.setChecked(a_cell_config.consider_output_value)
        self.ui.enable_output_filtering_checkbox.setChecked(a_cell_config.enable_output_filtering)
        self.ui.sampling_time_spinbox.setValue(a_cell_config.filter_sampling_time)
        self.ui.filter_points_count_spinbox.setValue(a_cell_config.filter_samples_count)

        self.coil_to_radio[a_cell_config.coil].setChecked(True)
        self.divider_to_radio[a_cell_config.divider].setChecked(True)
        self.meter_to_radio[a_cell_config.meter].setChecked(True)

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

            self.cell_config.measure_delay = self.ui.measure_delay_spinbox.value()
            self.cell_config.measure_time = self.ui.measure_time_spinbox.value()
            self.cell_config.retry_count = self.ui.retry_count_spinbox.value()
            self.cell_config.coefficient = utils.parse_input(self.ui.coefficient_edit.text())

            self.cell_config.consider_output_value = self.ui.consider_output_value_checkbox.isChecked()
            self.cell_config.enable_output_filtering = self.ui.enable_output_filtering_checkbox.isChecked()
            self.cell_config.filter_sampling_time = self.ui.sampling_time_spinbox.value()
            self.cell_config.filter_samples_count = self.ui.filter_points_count_spinbox.value()

            for coil_radio in self.radio_to_coil.keys():
                if coil_radio.isChecked():
                    self.cell_config.coil = self.radio_to_coil[coil_radio]

            for divider_radio in self.radio_to_divider.keys():
                if divider_radio.isChecked():
                    self.cell_config.divider = self.radio_to_divider[divider_radio]

            for meter_radio in self.radio_to_meter.keys():
                if meter_radio.isChecked():
                    self.cell_config.meter = self.radio_to_meter[meter_radio]

            self.cell_config.extra_parameters = extra_parameters

            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Таблица дополнительных параметров заполнена неверно",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def add_extra_param_button_clicked(self):
        init_row = [""] * EditCellConfigDialog.ExtraParamsColumn.COUNT
        init_row[EditCellConfigDialog.ExtraParamsColumn.TYPE] = self.__allowed_extra_param_types[0]

        qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, init_row)

    def remove_extra_param_button_clicked(self):
        qt_utils.qtablewidget_delete_selected(self.ui.extra_variables_table)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.extra_variables_table.objectName(),
                                    self.ui.extra_variables_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())

        a_event.accept()
