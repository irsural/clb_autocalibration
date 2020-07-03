from collections import namedtuple
from enum import IntEnum
from typing import List, Union
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.settings_ini_parser import Settings
from irspy.qt.custom_widgets.QTableDelegates import ComboboxCellDelegate

from ui.py.edit_measure_parameters_dialog import Ui_Dialog as EditMeasureParametersForm
from irspy.clb import calibrator_constants as clb
from irspy.qt import qt_utils
import irspy.utils as utils


class MeasureParameters:
    FlashTableRow = namedtuple("FlashTableRow", ["number", "index", "size", "value_number", "number_coef"])
    ExtraParameter = namedtuple("ExtraParameter", ["name", "index", "type", "work_value", "default_value"])

    def __init__(self):
        self.signal_type = clb.SignalType.ACI
        self.flash_after_finish = False

        self.flash_table: List[MeasureParameters.FlashTableRow] = []
        self.extra_parameters: List[MeasureParameters.ExtraParameter] = []


class EditMeasureParametersDialog(QtWidgets.QDialog):
    class FlashColumn(IntEnum):
        NUMBER = 0
        INDEX = 1
        SIZE = 2
        VALUE_NUMBER = 3
        NUMBER_COEF = 4
        COUNT = 5

    class ExtraParamsColumn(IntEnum):
        NAME = 0
        INDEX = 1
        TYPE = 2
        WORK_VALUE = 3
        DEFAULT_VALUE = 4
        COUNT = 5

    def __init__(self, a_init_parameters: MeasureParameters, a_settings: Settings, a_parent=None):
        super().__init__(a_parent)

        self.ui = EditMeasureParametersForm()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)
        self.show()

        self.__allowed_extra_param_types = ("double", "float", "bit", "u32", "i32", "u8", "i8", "u16", "i16",
                                            "bool", "u64", "i64")
        self.ui.extra_variables_table.setItemDelegateForColumn(EditMeasureParametersDialog.ExtraParamsColumn.TYPE,
                                                               ComboboxCellDelegate(self,
                                                                                    self.__allowed_extra_param_types))

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.flash_table.horizontalHeader().restoreState(self.settings.get_last_geometry(
            self.ui.flash_table.objectName()))
        self.ui.extra_variables_table.horizontalHeader().restoreState(self.settings.get_last_geometry(
            self.ui.extra_variables_table.objectName()))

        self.signal_type_to_radio = {
            clb.SignalType.ACI: self.ui.aci_radio,
            clb.SignalType.ACV: self.ui.acv_radio,
            clb.SignalType.DCI: self.ui.dci_radio,
            clb.SignalType.DCV: self.ui.dcv_radio
        }

        self.measure_parameters = None
        self.recover_parameters(a_init_parameters)

        self.ui.add_extra_param_button.clicked.connect(self.add_extra_param_button_clicked)
        self.ui.remove_extra_param_button.clicked.connect(self.remove_extra_param_button_clicked)
        self.ui.add_flash_table_row_button.clicked.connect(self.add_flash_table_button_clicked)
        self.ui.remove_flash_table_row_button.clicked.connect(self.remove_flash_table_button_clicked)

        self.ui.accept_button.clicked.connect(self.accept_parameters)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditMeasureParametersDialog deleted")

    def recover_parameters(self, a_measure_parameters: MeasureParameters):
        self.signal_type_to_radio[a_measure_parameters.signal_type].setChecked(True)
        self.ui.flash_after_finish_checkbox.setChecked(a_measure_parameters.flash_after_finish)

        for flash_row in a_measure_parameters.flash_table:
            qt_utils.qtablewidget_append_row(self.ui.flash_table, (
                str(flash_row.number), str(flash_row.index), str(flash_row.size),
                utils.float_to_string(flash_row.value_number), utils.float_to_string(flash_row.number_coef)
            ))

        for extra_parameter in a_measure_parameters.extra_parameters:
            qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, (
                extra_parameter.name, utils.float_to_string(extra_parameter.index), extra_parameter.type,
                utils.float_to_string(extra_parameter.work_value), utils.float_to_string(extra_parameter.default_value)
            ))

    def exec_and_get(self) -> Union[MeasureParameters, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.measure_parameters
        else:
            return None

    def accept_parameters(self):
        flash_table = []
        extra_parameters = []
        try:
            for row in range(self.ui.flash_table.rowCount()):
                flash_table.append(MeasureParameters.FlashTableRow(
                    number=int(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.NUMBER).text()),
                    index=int(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.INDEX).text()),
                    size=int(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.SIZE).text()),
                    value_number=float(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.VALUE_NUMBER).text()),
                    number_coef=float(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.NUMBER_COEF).text())
                ))

            for row in range(self.ui.extra_variables_table.rowCount()):
                extra_parameters.append(MeasureParameters.ExtraParameter(
                    name=self.ui.extra_variables_table.item(row, EditMeasureParametersDialog.ExtraParamsColumn.NAME).text(),
                    index=float(self.ui.extra_variables_table.item(row, EditMeasureParametersDialog.ExtraParamsColumn.INDEX).text()),
                    type=self.ui.extra_variables_table.item(row, EditMeasureParametersDialog.ExtraParamsColumn.TYPE).text(),
                    work_value=float(self.ui.extra_variables_table.item(row, EditMeasureParametersDialog.ExtraParamsColumn.WORK_VALUE).text()),
                    default_value=float(self.ui.extra_variables_table.item(row, EditMeasureParametersDialog.ExtraParamsColumn.DEFAULT_VALUE).text())
                ))
            tables_valid = True
        except ValueError:
            tables_valid = False

        if tables_valid:
            self.measure_parameters = MeasureParameters()

            if self.ui.aci_radio.isChecked():
                self.measure_parameters.signal_type = clb.SignalType.ACI
            elif self.ui.acv_radio.isChecked():
                self.measure_parameters.signal_type = clb.SignalType.ACV
            elif self.ui.dci_radio.isChecked():
                self.measure_parameters.signal_type = clb.SignalType.DCI
            else: # self.ui.dcv_radio.isChecked():
                self.measure_parameters.signal_type = clb.SignalType.DCV

            self.measure_parameters.flash_after_finish = self.ui.flash_after_finish_checkbox.isChecked()

            self.measure_parameters.flash_table = flash_table
            self.measure_parameters.extra_parameters = extra_parameters

            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Таблицы заполнены неверно", QtWidgets.QMessageBox.Ok,
                                           QtWidgets.QMessageBox.Ok)

    def add_extra_param_button_clicked(self):
        init_row = [""] * EditMeasureParametersDialog.FlashColumn.COUNT
        init_row[EditMeasureParametersDialog.ExtraParamsColumn.TYPE] = self.__allowed_extra_param_types[0]

        qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, init_row)

    def remove_extra_param_button_clicked(self):
        qt_utils.qtablewidget_delete_selected(self.ui.extra_variables_table)

    def add_flash_table_button_clicked(self):
        qt_utils.qtablewidget_append_row(self.ui.flash_table,
                                         [""] * EditMeasureParametersDialog.FlashColumn.COUNT)

    def remove_flash_table_button_clicked(self):
        qt_utils.qtablewidget_delete_selected(self.ui.flash_table)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.flash_table.objectName(),
                                    self.ui.flash_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.ui.extra_variables_table.objectName(),
                                    self.ui.extra_variables_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())

        a_event.accept()
