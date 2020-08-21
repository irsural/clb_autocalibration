import logging

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from irspy.qt.object_fields_visualizer import ObjectFieldsVisualizer
from ui.py.settings_form import Ui_settings_dialog as SettingsForm
from irspy.settings_ini_parser import Settings
import irspy.clb.calibrator_constants as clb

import irspy.utils as utils


class SettingsDialog(QtWidgets.QDialog):
    class SettingPages:
        MARKS = 0
        FIXED_RANGE = 1

    fixed_range_changed = pyqtSignal()

    def __init__(self, a_settings: Settings, a_parent=None):
        super().__init__(a_parent)

        self.ui = SettingsForm()
        self.ui.setupUi(self)

        self.settings = a_settings
        self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))

        self.ui.save_and_exit_button.clicked.connect(self.save_and_exit)
        self.ui.save_button.clicked.connect(self.save)
        self.ui.cancel_button.clicked.connect(self.close)

        visualizer = ObjectFieldsVisualizer(self.settings, self)
        visualizer.add_setting("Точность числа при отображении", "display_data_precision")
        visualizer.add_setting("Точность числа при редактировании", "edit_data_precision")
        self.ui.measure_table_settings_layout.layout().addWidget(visualizer)

        self.open_first_tab()

    def __del__(self):
        print("settings deleted")

    def open_first_tab(self):
        self.ui.settings_menu_list.setCurrentRow(0)
        self.ui.settings_stackedwidget.setCurrentIndex(0)

    def save(self):
        return True

    def save_and_exit(self):
        if self.save():
            self.close()

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.objectName(), self.saveGeometry())
        a_event.accept()
