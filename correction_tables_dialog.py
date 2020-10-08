from typing import Dict, Tuple, List
from collections import OrderedDict
import logging
import json

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForView
from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.qt_settings_ini_parser import QtSettings
import irspy.utils as utils

from ui.py.correction_tables_dialog import Ui_correction_tables_dialog as CorrectionTablesForm
from CorrectionTableModel import CorrectionTableModel


class CorrectionTablesDialog(QtWidgets.QDialog):
    save_tables_to_file = QtCore.pyqtSignal(dict)

    def __init__(self, a_correction_tables: Dict[str, Tuple], a_settings: QtSettings,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = CorrectionTablesForm()
        self.ui.setupUi(self)

        self.ui.correction_table_view.setItemDelegate(TransparentPainterForView(self.ui.correction_table_view,
                                                                                "#d4d4ff"))
        self.ui.correction_table_view.customContextMenuRequested.connect(self.show_table_context_menu)

        self.ui.copy_cell_value_action.triggered.connect(self.copy_cell_value)
        self.ui.correction_table_view.addAction(self.ui.copy_cell_value_action)

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.correction_tables_splitter)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinMaxButtonsHint)

        self.correction_tables = a_correction_tables
        self.correction_table_models = OrderedDict()
        self.fill_correction_tables(a_correction_tables)

        self.ui.table_names_list.currentTextChanged.connect(self.change_table)
        self.ui.save_to_file_button.clicked.connect(self.save_tables_to_file_button_clicked)

        self.show()

    def fill_correction_tables(self, a_correction_tables: Dict[str, Tuple]):
        for table_name, (x_points, y_points, coefs_points) in a_correction_tables.items():
            self.ui.table_names_list.addItem(table_name)
            self.correction_table_models[table_name] = CorrectionTableModel(x_points, y_points, coefs_points)

    def show_table_context_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction(self.ui.copy_cell_value_action)
        menu.popup(QtGui.QCursor.pos())

    def copy_cell_value(self):
        data_model = self.ui.correction_table_view.model()

        if data_model is not None:
            selected_indices = sorted(self.ui.correction_table_view.selectionModel().selectedIndexes())
            if selected_indices:
                copy_str = ""
                prev_row = selected_indices[0].row()
                for num, cell_idx in enumerate(selected_indices):
                    if prev_row != cell_idx.row():
                        prev_row = cell_idx.row()
                        copy_str += "\n"
                    elif num != 0:
                        copy_str += "\t"

                    cell_value = data_model.get_cell_value(cell_idx.row(), cell_idx.column())
                    value_str = utils.float_to_string(cell_value, a_precision=15) if cell_value is not None else "0"
                    copy_str += f"{value_str}"

                QtWidgets.QApplication.clipboard().setText(copy_str)

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
        self.settings.save_qwidget_state(self)
        self.settings.save_qwidget_state(self.ui.correction_tables_splitter)
        a_event.accept()
