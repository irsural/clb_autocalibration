from collections import namedtuple
from enum import IntEnum
from typing import Union
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.settings_ini_parser import Settings

from ui.py.shared_measure_parameters import Ui_shared_measure_parameters as EditSharedMeasureParametersForm


DeviceCoefs = namedtuple("DeviceCoefs", "coil_001 coil_1 coil_10 mul_30 mul_10 div_650 div_500 div_350 div_200 "
                                        "div_55 div_40")


class SharedMeasureParameters:
    def __init__(self):
        self.device_coefs = DeviceCoefs(coil_001=0.01, coil_1=1, coil_10=10, mul_30=31, mul_10=81, div_650=65.5,
                                        div_500=50.5, div_350=35.5, div_200=20.5, div_55=5.5, div_40=4)

    def __eq__(self, other):
        return other is not None and \
               self.device_coefs == other.device_coefs

    def serialize_to_dict(self):
        data_dict = {
            "device_coefs": self.device_coefs
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_data_dict: dict):
        cell_config = cls()
        cell_config.device_coefs = [DeviceCoefs(*device_coefs) for device_coefs in a_data_dict["device_coefs"]]

        return cell_config


class EditSharedMeasureParametersDialog(QtWidgets.QDialog):

    def __init__(self, a_init_parameters: SharedMeasureParameters, a_settings: Settings, a_lock_editing=False,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = EditSharedMeasureParametersForm()
        self.ui.setupUi(self)
        self.show()

        if a_lock_editing:
            self.ui.accept_button.setDisabled(a_lock_editing)

        self.settings = a_settings

        try:
            size = self.settings.get_last_geometry(self.objectName()).split(";")
            self.resize(int(size[0]), int(size[1]))
        except ValueError:
            pass

        self.shared_parameters = None
        self.recover_parameters(a_init_parameters)

        self.ui.accept_button.clicked.connect(self.accept_parameters)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditSharedMeasureParametersDialog deleted")

    def recover_parameters(self, a_shared_parameters: SharedMeasureParameters):
        self.ui.coil_001_spinbox.setValue(a_shared_parameters.device_coefs.coil_001)
        self.ui.coil_1_spinbox.setValue(a_shared_parameters.device_coefs.coil_1)
        self.ui.coil_10_spinbox.setValue(a_shared_parameters.device_coefs.coil_10)

        self.ui.mul_30_spinbox.setValue(a_shared_parameters.device_coefs.mul_30)
        self.ui.mul_10_spinbox.setValue(a_shared_parameters.device_coefs.mul_10)

        self.ui.div_650_spinbox.setValue(a_shared_parameters.device_coefs.div_650)
        self.ui.div_500_spinbox.setValue(a_shared_parameters.device_coefs.div_500)
        self.ui.div_350_spinbox.setValue(a_shared_parameters.device_coefs.div_350)
        self.ui.div_200_spinbox.setValue(a_shared_parameters.device_coefs.div_200)
        self.ui.div_55_spinbox.setValue(a_shared_parameters.device_coefs.div_55)
        self.ui.div_40_spinbox.setValue(a_shared_parameters.device_coefs.div_40)

    def exec_and_get(self) -> Union[SharedMeasureParameters, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.shared_parameters
        else:
            return None

    def accept_parameters(self):
        self.shared_parameters = SharedMeasureParameters()

        # noinspection PyTypeChecker
        res = QtWidgets.QMessageBox.question(self, "Подтвердите действие",
                                             'После применения новых значений, коэффициенты всех ячеек, в которых '
                                             'используются делитель/усилитель или катушка и установлен параметр '
                                             '"Авто рассчет коэффициента" будут автоматически пересчитаны',
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                             QtWidgets.QMessageBox.Yes)

        if res == QtWidgets.QMessageBox.Yes:
            self.shared_parameters.device_coefs = DeviceCoefs(coil_001=self.ui.coil_001_spinbox.value(),
                                                              coil_1=self.ui.coil_1_spinbox.value(),
                                                              coil_10=self.ui.coil_10_spinbox.value(),
                                                              mul_30=self.ui.mul_30_spinbox.value(),
                                                              mul_10=self.ui.mul_10_spinbox.value(),
                                                              div_650=self.ui.div_650_spinbox.value(),
                                                              div_500=self.ui.div_500_spinbox.value(),
                                                              div_350=self.ui.div_350_spinbox.value(),
                                                              div_200=self.ui.div_200_spinbox.value(),
                                                              div_55=self.ui.div_55_spinbox.value(),
                                                              div_40=self.ui.div_40_spinbox.value())
            self.accept()

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        size = f"{self.size().width()};{self.size().height()}"
        self.settings.save_geometry(self.objectName(), bytes(size, encoding='cp1251'))

        a_event.accept()
