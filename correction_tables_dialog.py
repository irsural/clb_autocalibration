from typing import Dict, Tuple, List
from collections import OrderedDict
import logging
import json

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.qt_settings_ini_parser import QtSettings
import irspy.utils as utils

from ui.py.correction_tables_dialog import Ui_correction_tables_dialog as CorrectionTablesForm
from CorrectionTableModel import CorrectionTableModel


class CorrectionTablesDialog(QtWidgets.QDialog):
    save_tables_to_file = QtCore.pyqtSignal(dict)

    def __init__(self, a_correction_tables: Dict[str, List[Tuple[List, List, List]]], a_settings: QtSettings,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = CorrectionTablesForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
        self.ui.correction_tables_splitter.restoreState(self.settings.get_last_geometry(
            self.ui.correction_tables_splitter.objectName()))

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinMaxButtonsHint)

        self.correction_tables = a_correction_tables
        self.correction_table_models = OrderedDict()
        self.fill_correction_tables(a_correction_tables)

        self.ui.table_names_list.currentTextChanged.connect(self.change_table)
        self.ui.save_to_file_button.clicked.connect(self.save_tables_to_file_button_clicked)

        self.show()

    def fill_correction_tables(self, a_correction_tables: Dict[str, List[Tuple[List, List, List]]]):
        number = 0
        for idx, (name, data) in enumerate(a_correction_tables.items()):
            united_numbers = []
            united = {}

            prev_x_points = []
            y_united = []
            coefs_united = []

            # Объединяем коррекции, у которых совпадает имя и x_points в одну таблицу
            for sub_idx, (x_points, y_points, coefs) in enumerate(data):
                if x_points == prev_x_points:
                    united_numbers.append(number)

                    y_united += y_points
                    coefs_united += coefs
                else:
                    if united_numbers:
                        united[f"{united_numbers[0]}-{united_numbers[-1]}. {name}"] = (prev_x_points, y_united, coefs_united)

                    united_numbers = [number]

                    prev_x_points = list(x_points)
                    y_united = list(y_points)
                    coefs_united = list(coefs)

                number += 1

                if sub_idx == len(data) - 1:
                    united[f"[{united_numbers[0]}-{united_numbers[-1]}] {name}"] = (x_points, y_united, coefs_united)

            for united_name, (x_points, y_points, coefs_points) in united.items():
                self.ui.table_names_list.addItem(united_name)
                self.correction_table_models[united_name] = CorrectionTableModel(x_points, y_points, coefs_points)

    def change_table(self, a_name):
        self.ui.correction_table_view.setModel(self.correction_table_models[a_name])

    def save_tables_to_file_button_clicked(self, _):
        save_filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить таблицы коррекции", "",
                                                                 "Таблицы коррекции (*.ct)")
        with open(save_filename, "w") as tables_file:
            tables_file.write(json.dumps(self.correction_tables, ensure_ascii=False, indent=4))

    def __del__(self):
        print("CorrectionTables deleted")

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.ui.correction_tables_splitter.objectName(),
                                    self.ui.correction_tables_splitter.saveState())
        self.settings.save_geometry(self.objectName(), self.saveGeometry())
        a_event.accept()


