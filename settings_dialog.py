import logging

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from irspy.qt.custom_widgets.EditListDialog import EditedListWithUnits
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

        self.edit_fixed_range_widget = EditedListWithUnits(self, "В", self.settings.fixed_step_list, clb.MIN_VOLTAGE,
                                                           clb.MAX_VOLTAGE,
                                                           a_optional_widget=QtWidgets.QLabel("Шаг", self))
        self.ui.fixed_range_groupbox.layout().addWidget(self.edit_fixed_range_widget)

        self.ui.exact_step_spinbox.setValue(self.settings.exact_step)
        self.ui.rough_step_spinbox.setValue(self.settings.rough_step)
        self.ui.common_step_spinbox.setValue(self.settings.common_step)

        self.open_first_tab()

    def __del__(self):
        print("settings deleted")

    def open_first_tab(self):
        self.ui.settings_menu_list.setCurrentRow(0)
        self.ui.settings_stackedwidget.setCurrentIndex(0)

    def save(self):
        fixed_step_list = self.edit_fixed_range_widget.sort_list()
        if self.settings.fixed_step_list != fixed_step_list:
            self.settings.fixed_step_list = fixed_step_list

        if self.settings.rough_step != self.ui.rough_step_spinbox.value():
            self.settings.rough_step = self.ui.rough_step_spinbox.value()

        if self.settings.common_step != self.ui.common_step_spinbox.value():
            self.settings.common_step = self.ui.common_step_spinbox.value()

        if self.settings.exact_step != self.ui.exact_step_spinbox.value():
            self.settings.exact_step = self.ui.exact_step_spinbox.value()

        return True

    def save_and_exit(self):
        if self.save():
            self.close()

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_geometry(self.objectName(), self.saveGeometry())
        a_event.accept()
