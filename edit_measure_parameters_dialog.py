from collections import namedtuple
from enum import IntEnum
from typing import List
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from ui.py.edit_measure_parameters_dialog import Ui_Dialog as EditMeasureParametersForm
from irspy.settings_ini_parser import Settings

from irspy.clb import calibrator_constants as clb
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
    class Column(IntEnum):
        NUMBER = 0
        INDEX = 1
        MARK = 2
        NAME = 3
        GRAPH = 4
        TYPE = 5
        VALUE = 6

    def __init__(self, a_settings: Settings, a_parent=None):
        super().__init__(a_parent)

        self.ui = EditMeasureParametersForm()
        self.ui.setupUi(self)
        self.show()

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.flash_table.horizontalHeader().restoreState(self.settings.get_last_geometry(
            self.ui.flash_table.objectName()))
        self.ui.extra_variables_table.horizontalHeader().restoreState(self.settings.get_last_geometry(
            self.ui.extra_variables_table.objectName()))

        self.ui.accept_button.clicked.connect(self.accept)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditMeasureParametersDialog deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.flash_table.objectName(),
                                    self.ui.flash_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.ui.extra_variables_table.objectName(),
                                    self.ui.extra_variables_table.horizontalHeader().saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())

        a_event.accept()
