from collections import namedtuple
from enum import IntEnum
from typing import List, Union
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.clb import calibrator_constants as clb
from irspy.qt import qt_utils
import irspy.utils as utils

from ui.py.edit_measure_parameters_dialog import Ui_edit_measure_parameters_dialog as EditMeasureParametersForm


FlashTableRow = namedtuple("FlashTableRow", ["number", "eeprom_offset", "size", "start_value", "end_value"])


class MeasureParameters:

    def __init__(self, a_signal_type=clb.SignalType.ACI, a_flash_after_finish=False, a_enable_correction=False,
                 a_flash_table=None):
        self.signal_type = a_signal_type
        self.flash_after_finish = a_flash_after_finish
        self.enable_correction = a_enable_correction

        self.flash_table: List[FlashTableRow] = a_flash_table if a_flash_table is not None else []

    def __eq__(self, other):
        return other is not None and \
               self.signal_type == other.signal_type and \
               self.flash_after_finish == other.flash_after_finish and \
               self.enable_correction == other.enable_correction and \
               self.flash_table == other.flash_table

    def serialize_to_dict(self):
        data_dict = {
            "signal_type": self.signal_type,
            "flash_after_finish": self.flash_after_finish,
            "enable_correction": self.enable_correction,
            "flash_table": self.flash_table,
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_data_dict: dict):
        flash_table = [FlashTableRow(*flash_table_row) for flash_table_row in a_data_dict["flash_table"]]

        return cls(a_signal_type=clb.SignalType(int(a_data_dict["signal_type"])),
                   a_flash_after_finish=bool(a_data_dict["flash_after_finish"]),
                   a_enable_correction=bool(a_data_dict["enable_correction"]),
                   a_flash_table=flash_table)


class EditMeasureParametersDialog(QtWidgets.QDialog):
    class FlashColumn(IntEnum):
        NUMBER = 0
        EEPROM_OFFSET = 1
        SIZE = 2
        START_VALUE = 3
        END_VALUE = 4
        COUNT = 5

    def __init__(self, a_init_parameters: MeasureParameters, a_settings: QtSettings, a_lock_editing=False,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = EditMeasureParametersForm()
        self.ui.setupUi(self)
        self.show()

        if a_lock_editing:
            self.ui.accept_button.setDisabled(a_lock_editing)

        self.settings = a_settings
        self.settings.restore_dialog_size(self)
        self.settings.restore_qwidget_state(self.ui.flash_table)

        self.ui.flash_table.setItemDelegate(TransparentPainterForWidget(self.ui.flash_table, "#d4d4ff"))

        self.signal_type_to_radio = {
            clb.SignalType.ACI: self.ui.aci_radio,
            clb.SignalType.ACV: self.ui.acv_radio,
            clb.SignalType.DCI: self.ui.dci_radio,
            clb.SignalType.DCV: self.ui.dcv_radio
        }

        self.measure_parameters = None
        self.recover_parameters(a_init_parameters)

        self.ui.add_flash_table_row_button.clicked.connect(self.add_flash_table_button_clicked)
        self.ui.remove_flash_table_row_button.clicked.connect(self.remove_flash_table_button_clicked)

        self.ui.accept_button.clicked.connect(self.accept_parameters)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditMeasureParametersDialog deleted")

    def recover_parameters(self, a_measure_parameters: MeasureParameters):
        self.signal_type_to_radio[a_measure_parameters.signal_type].setChecked(True)
        self.ui.flash_after_finish_checkbox.setChecked(a_measure_parameters.flash_after_finish)
        self.ui.enable_correction_checkbox.setChecked(a_measure_parameters.enable_correction)

        for flash_row in a_measure_parameters.flash_table:
            qt_utils.qtablewidget_append_row(self.ui.flash_table, (
                str(flash_row.number), str(flash_row.eeprom_offset), str(flash_row.size),
                utils.float_to_string(flash_row.start_value), utils.float_to_string(flash_row.end_value)
            ))

    def exec_and_get(self) -> Union[MeasureParameters, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.measure_parameters
        else:
            return None

    def accept_parameters(self):
        flash_table = []
        try:
            for row in range(self.ui.flash_table.rowCount()):
                flash_table.append(FlashTableRow(
                    number=int(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.NUMBER).text()),
                    eeprom_offset=int(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.EEPROM_OFFSET).text()),
                    size=int(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.SIZE).text()),
                    start_value=utils.parse_input(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.START_VALUE).text()),
                    end_value=utils.parse_input(self.ui.flash_table.item(row, EditMeasureParametersDialog.FlashColumn.END_VALUE).text())
                ))

            table_valid = True
        except ValueError:
            table_valid = False

        if table_valid:
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
            self.measure_parameters.enable_correction = self.ui.enable_correction_checkbox.isChecked()

            self.measure_parameters.flash_table = flash_table

            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Таблица прошивки заполнена неверно",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def add_flash_table_button_clicked(self):
        qt_utils.qtablewidget_append_row(self.ui.flash_table,
                                         [""] * EditMeasureParametersDialog.FlashColumn.COUNT)

    def remove_flash_table_button_clicked(self):
        qt_utils.qtablewidget_delete_selected(self.ui.flash_table)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self.ui.flash_table)
        self.settings.restore_dialog_size(self)

        a_event.accept()
