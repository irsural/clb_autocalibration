from typing import Dict, Tuple, List
from collections import OrderedDict
from enum import IntEnum
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.settings_ini_parser import Settings
import irspy.utils as utils

from ui.py.correction_tables_dialog import Ui_correction_tables_dialog as CorrectionTablesForm
from CorrectionTableModel import CorrectionTableModel


class CorrectionTablesDialog(QtWidgets.QDialog):

    def __init__(self, a_correction_tables: Dict[str, List[Tuple[List, List, List]]], a_settings: Settings,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = CorrectionTablesForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.correction_tables_splitter.restoreState(self.settings.get_last_geometry(
            self.ui.correction_tables_splitter.objectName()))

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinMaxButtonsHint)

        self.correction_table_models = OrderedDict()
        self.fill_correction_tables(a_correction_tables)

        self.ui.table_names_list.currentTextChanged.connect(self.change_table)

        self.show()

    def fill_correction_tables(self, a_correction_tables: Dict[str, List[Tuple[List, List, List]]]):
        for name, data in a_correction_tables.items():
            self.ui.table_names_list.addItem(name)

            x_points = []
            y_points = []
            coef_points = []

            for x_p, y_p, coefs in data:
                x_points = x_p
                y_points += y_p
                coef_points += coefs

            self.correction_table_models[name] = CorrectionTableModel(x_points, y_points, coef_points)

    def change_table(self, a_name):
        self.ui.correction_table_view.setModel(self.correction_table_models[a_name])

    def __del__(self):
        print("CorrectionTables deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.correction_tables_splitter.objectName(),
                                    self.ui.correction_tables_splitter.saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())
        a_event.accept()


