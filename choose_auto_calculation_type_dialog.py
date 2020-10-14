from enum import IntEnum
import logging

from PyQt5 import QtGui, QtWidgets

from ui.py.choose_auto_calculation_type_dialog import Ui_choose_auto_calculation_type_dialog as DialogForm


class AutoCalculationTypeDialog(QtWidgets.QDialog):
    class Type(IntEnum):
        NONE = 0
        ADD = 1
        REPLACE = 2

    def __init__(self, a_parent=None):
        super().__init__(a_parent)

        self.ui = DialogForm()
        self.ui.setupUi(self)

        self.show()

        self.__type = AutoCalculationTypeDialog.Type.NONE

        self.ui.add_button.clicked.connect(self.choose_add_type)
        self.ui.replace_button.clicked.connect(self.choose_replace_type)
        self.ui.cancel_button.clicked.connect(self.reject)

    def exec_and_get(self):
        self.exec()
        return self.__type

    def choose_add_type(self):
        self.__type = AutoCalculationTypeDialog.Type.ADD
        self.accept()

    def choose_replace_type(self):
        self.__type = AutoCalculationTypeDialog.Type.REPLACE
        self.accept()

    def __del__(self):
        print("choose_auto_calculation_type_dialog deleted")
