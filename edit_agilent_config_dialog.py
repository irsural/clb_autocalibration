import re
from enum import IntEnum
from typing import Union
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.settings_ini_parser import Settings

from ui.py.edit_agilent_config_dialog import Ui_edit_agilent_config_dialog as EditAgilentConfigForm


class AgilentConfig:
    class ConnectType(IntEnum):
        AGILENT_USB = 0
        NI_USB = 1
        PROLOGIX_COM = 2
        PROLOGIX_ETHERNET = 3

    def __init__(self):
        self.connect_type = AgilentConfig.ConnectType.AGILENT_USB
        self.gpib_index = 0
        self.gpib_address = 22
        self.com_name = "com4"
        self.ip_address = "0.0.0.0"
        self.port = 0

    def __eq__(self, other):
        return other is not None and \
               self.connect_type == other.connect_type and \
               self.gpib_index == other.gpib_index and \
               self.gpib_address == other.gpib_address and \
               self.com_name == other.com_name and \
               self.ip_address == other.ip_address and \
               self.port == other.port


class EditAgilentConfigDialog(QtWidgets.QDialog):

    def __init__(self, a_init_parameters: AgilentConfig, a_settings: Settings, a_lock_editing=False,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = EditAgilentConfigForm()
        self.ui.setupUi(self)
        self.show()

        if a_lock_editing:
            self.ui.accept_button.setDisabled(a_lock_editing)

        self.settings = a_settings

        self.ip_address_regex = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
        self.com_regex = re.compile(r"(?i)com\d")

        self.agilent_config = None
        self.recover_parameters(a_init_parameters)

        self.ui.accept_button.clicked.connect(self.accept_parameters)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditAgilentConfigDialog deleted")

    def recover_parameters(self, a_agilent_config: AgilentConfig):
        self.ui.connect_type_combobox.setCurrentIndex(a_agilent_config.connect_type)
        self.ui.gpib_index_spinbox.setValue(a_agilent_config.gpib_index)
        self.ui.gpib_address_spinbox.setValue(a_agilent_config.gpib_address)
        self.ui.com_name_edit.setText(a_agilent_config.com_name)
        self.ui.ip_address_edit.setText(a_agilent_config.ip_address)
        self.ui.port_spinbox.setValue(a_agilent_config.port)

    def exec_and_get(self) -> Union[AgilentConfig, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.agilent_config
        else:
            return None

    def accept_parameters(self):
        self.agilent_config = AgilentConfig()

        if self.com_regex.fullmatch(self.ui.com_name_edit.text()) is not None:
            if self.ip_address_regex.fullmatch(self.ui.ip_address_edit.text()) is not None:
                self.agilent_config.connect_type = self.ui.connect_type_combobox.currentIndex()
                self.agilent_config.gpib_index = self.ui.gpib_index_spinbox.value()
                self.agilent_config.gpib_address = self.ui.gpib_address_spinbox.value()
                self.agilent_config.com_name = self.ui.com_name_edit.text()
                self.agilent_config.ip_address = self.ui.ip_address_edit.text()
                self.agilent_config.port = self.ui.port_spinbox.value()
                self.accept()

            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка", "Неверный формат IP адреса",
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Неверный формат COM name",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        a_event.accept()
