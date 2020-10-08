from collections import namedtuple, OrderedDict
from enum import IntEnum
from typing import Union, List, Dict, Tuple
import logging

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.qt_settings_ini_parser import QtSettings

from ui.py.edit_shared_measure_parameters_dialog import Ui_shared_measure_parameters_dialog as EditSharedMeasureParametersForm
from DeviceCoefficientsModel import DeviceCoefficientsModel


DeviceCoefs = namedtuple("DeviceCoefs", "coil_001 coil_1 coil_10 mul_30 mul_10 div_650 div_500 div_350 div_200 "
                                        "div_55 div_40")


class Device(IntEnum):
    COIL_0_01_OHM = 0
    COIL_1_OHM = 1
    COIL_10_OHM = 2
    MUL_30_mV = 3
    MUL_10_mV = 4
    DIV_650_V = 5
    DIV_500_V = 6
    DIV_350_V = 7
    DIV_200_V = 8
    DIV_55_V = 9
    DIV_40_V = 10
    COUNT = 11


DEVICE_TO_NAME = {
    Device.COIL_0_01_OHM: "Катушка 0,01 Ом",
    Device.COIL_1_OHM: "Катушка 1 Ом",
    Device.COIL_10_OHM: "Катушка 10 Ом",
    Device.MUL_30_mV: "Усилитель 30 мВ",
    Device.MUL_10_mV: "Усилитель 10 мВ",
    Device.DIV_650_V: "Делитель 650 В",
    Device.DIV_500_V: "Делитель 500 В",
    Device.DIV_350_V: "Делитель 350 В",
    Device.DIV_200_V: "Делитель 200 В",
    Device.DIV_55_V: "Делитель 55 В",
    Device.DIV_40_V: "Делитель 40 В",
}

DEVICE_TO_DEFAULT_COEFS = {
    # Значения: Кортеж(Список частот, список коэффициентов)
    Device.COIL_0_01_OHM: ([0], [0.01]),
    Device.COIL_1_OHM: ([0], [1]),
    Device.COIL_10_OHM: ([0], [10]),
    Device.MUL_30_mV: ([0], [31]),
    Device.MUL_10_mV: ([0], [81]),
    Device.DIV_650_V: ([0], [65.5]),
    Device.DIV_500_V: ([0], [50.5]),
    Device.DIV_350_V: ([0], [35.5]),
    Device.DIV_200_V: ([0], [20.5]),
    Device.DIV_55_V: ([0], [5.5]),
    Device.DIV_40_V: ([0], [4]),
}


class SharedMeasureParameters:
    def __init__(self):
        devices = [Device(device) for device in range(Device.COUNT)]
        default_frequencies = [value[0] for value in DEVICE_TO_DEFAULT_COEFS.values()]
        default_coefficients = [value[1] for value in DEVICE_TO_DEFAULT_COEFS.values()]

        self.device_coefs: Dict[Device, Tuple[List[float], List[float]]] = OrderedDict()
        for device, frequencies, coefficients in zip(devices, default_frequencies, default_coefficients):
            self.device_coefs[device] = (frequencies, coefficients)

    def __eq__(self, other):
        if isinstance(other, SharedMeasureParameters):
            return self.device_coefs == other.device_coefs
        else:
            return NotImplemented


    def serialize_to_dict(self):
        data_dict = {
            "device_coefs": self.device_coefs
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_data_dict: dict):
        shared_parameters = cls()

        shared_parameters.device_coefs = OrderedDict()

        for device, (frequencies, coefficients) in a_data_dict["device_coefs"].items():
            shared_parameters.device_coefs[Device(int(device))] = (frequencies, coefficients)

        return shared_parameters


class EditSharedMeasureParametersDialog(QtWidgets.QDialog):

    def __init__(self, a_init_parameters: SharedMeasureParameters, a_settings: QtSettings, a_lock_editing=False,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = EditSharedMeasureParametersForm()
        self.ui.setupUi(self)
        self.show()

        if a_lock_editing:
            self.ui.accept_button.setDisabled(a_lock_editing)

        self.settings = a_settings
        self.settings.restore_qwidget_state(self)
        self.settings.restore_qwidget_state(self.ui.shared_parameters_splitter)
        self.settings.restore_qwidget_state(self.ui.device_coefs_view)

        self.shared_parameters: Union[None, SharedMeasureParameters] = None
        self.init_shared_parameters = a_init_parameters

        self.ui.device_coefs_view.setModel(None)
        self.device_coefs_models: Dict[str, DeviceCoefficientsModel] = OrderedDict()

        self.recover_parameters(a_init_parameters)

        self.ui.devices_list.currentTextChanged.connect(self.device_changed)

        self.ui.add_coefficient_button.clicked.connect(self.add_coefficient_button_clicked)
        self.ui.remove_coefficient_button.clicked.connect(self.remove_coefficient_button_clicked)

        self.ui.accept_button.clicked.connect(self.accept_parameters)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditSharedMeasureParametersDialog deleted")

    def recover_parameters(self, a_shared_parameters: SharedMeasureParameters):
        for device, (frequencies, coefficients) in a_shared_parameters.device_coefs.items():
            device_name = DEVICE_TO_NAME[device]
            self.ui.devices_list.addItem(device_name)
            self.device_coefs_models[device_name] = DeviceCoefficientsModel(frequencies, coefficients)

        if self.ui.devices_list.count():
            self.ui.devices_list.setCurrentRow(0)
            current_device_name = self.ui.devices_list.currentItem().text()

            self.ui.device_coefs_view.setModel(self.device_coefs_models[current_device_name])

    def device_changed(self, a_device_name: str):
        self.ui.device_coefs_view.setModel(self.device_coefs_models[a_device_name])

    def add_coefficient_button_clicked(self, _):
        current_model = self.device_coefs_models[self.ui.devices_list.currentItem().text()]

        selection = self.ui.device_coefs_view.selectionModel().selectedIndexes()
        if selection:
            row = max(selection, key=lambda idx: idx.row()).row() + 1
        else:
            row = current_model.rowCount()

        current_model.add_coefficient(row)

    def remove_coefficient_button_clicked(self, _):
        current_model = self.device_coefs_models[self.ui.devices_list.currentItem().text()]
        # Множество для удаления дубликатов
        removing_rows = list(set(index.row() for index in self.ui.device_coefs_view.selectionModel().selectedIndexes()))
        removing_rows.sort()
        for row in reversed(removing_rows):
            current_model.remove_coefficient(row)

    def exec_and_get(self) -> Union[SharedMeasureParameters, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.shared_parameters
        else:
            return None

    def accept_parameters(self):
        self.shared_parameters = SharedMeasureParameters()

        new_device_coefs = OrderedDict()
        for device, (device_name, coefs_model) in enumerate(self.device_coefs_models.items()):
            assert DEVICE_TO_NAME[device] == device_name, "Ошибка в порядке ключей словаря"

            new_device_coefs[device] = (list(coefs_model.get_frequencies()), list(coefs_model.get_coefficients()))

        self.shared_parameters.device_coefs = new_device_coefs

        if self.init_shared_parameters != self.shared_parameters:
            # noinspection PyTypeChecker
            res = QtWidgets.QMessageBox.question(self, "Подтвердите действие",
                                                 'После применения новых значений, коэффициенты всех ячеек, в которых '
                                                 'используются делитель/усилитель или катушка и установлен параметр '
                                                 '"Авто рассчет коэффициента" будут автоматически пересчитаны.\n'
                                                 'ВНИМАНИЕ! Убедитесь, что заголовки всех таблиц заполнены, иначе '
                                                 'коэффициент может быть рассчитан неверно.',
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                 QtWidgets.QMessageBox.Yes)
            if res == QtWidgets.QMessageBox.Yes:
                self.accept()
        else:
            self.reject()

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self.ui.device_coefs_view)
        self.settings.save_qwidget_state(self.ui.shared_parameters_splitter)
        self.settings.save_qwidget_state(self)

        a_event.accept()
