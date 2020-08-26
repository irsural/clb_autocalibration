from collections import namedtuple, OrderedDict
from typing import List, Union
from enum import IntEnum
import logging
import copy

from PyQt5 import QtGui, QtWidgets, QtCore

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget
from irspy.qt.custom_widgets.QTableDelegates import ComboboxCellDelegate
from irspy.qt.object_fields_visualizer import ObjectFieldsVisualizer
from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.clb import calibrator_constants as clb
from irspy.metrology import Pchip
from irspy.qt import qt_utils
import irspy.utils as utils

from ui.py.edit_cell_config_dialog import Ui_edit_cell_config_dialog as EditCellConfigForm
from edit_shared_measure_parameters_dialog import SharedMeasureParameters, Device, DEVICE_TO_DEFAULT_COEFS


class CellConfig:
    class Coil(IntEnum):
        NONE = 0
        VAL_0_01_OHM = 1
        VAL_1_OHM = 2
        VAL_10_OHM = 3

    COIL_TO_NAME = {
        Coil.NONE: "",
        Coil.VAL_0_01_OHM: "Катушка [0,01 Ом]",
        Coil.VAL_1_OHM: "Катушка [1 Ом]",
        Coil.VAL_10_OHM: "Катушка [10 Ом]",
    }

    class Divider(IntEnum):
        NONE = 0
        DIV_650_V = 1
        DIV_500_V = 2
        DIV_350_V = 3
        DIV_200_V = 4
        DIV_55_V = 5
        DIV_40_V = 6
        MUL_30_mV = 7
        MUL_10_mV = 8

    DIVIDER_TO_NAME = {
        Divider.NONE: "",
        Divider.DIV_650_V: "Делитель [650 В]",
        Divider.DIV_500_V: "Делитель [500 В]",
        Divider.DIV_350_V: "Делитель [350 В]",
        Divider.DIV_200_V: "Делитель [200 В]",
        Divider.DIV_55_V: "Делитель [55 В]",
        Divider.DIV_40_V: "Делитель [40 В]",
        Divider.MUL_30_mV: "Усилитель [30 мВ]",
        Divider.MUL_10_mV: "Усилитель [10 мВ]",
    }

    class Meter(IntEnum):
        AMPERES = 0
        VOLTS = 1

    METER_TO_NAME = {
        Meter.AMPERES: "Амперметр",
        Meter.VOLTS: "Вольтметр",
    }

    ALLOWED_COILS = {
        clb.SignalType.ACI: (Coil.NONE, Coil.VAL_0_01_OHM, Coil.VAL_1_OHM, Coil.VAL_10_OHM),
        clb.SignalType.DCI: (Coil.NONE, Coil.VAL_0_01_OHM, Coil.VAL_1_OHM, Coil.VAL_10_OHM),
        clb.SignalType.ACV: (Coil.NONE,),
        clb.SignalType.DCV: (Coil.NONE,),
    }

    ALLOWED_DIVIDERS = {
        clb.SignalType.ACI: (Divider.NONE,),
        clb.SignalType.DCI: (Divider.NONE,),
        clb.SignalType.ACV: (Divider.NONE, Divider.MUL_10_mV, Divider.MUL_30_mV, Divider.DIV_650_V, Divider.DIV_500_V,
                             Divider.DIV_350_V, Divider.DIV_200_V, Divider.DIV_55_V, Divider.DIV_40_V),
        clb.SignalType.DCV: (Divider.NONE, Divider.MUL_10_mV, Divider.MUL_30_mV, Divider.DIV_650_V, Divider.DIV_500_V,
                             Divider.DIV_350_V, Divider.DIV_200_V, Divider.DIV_55_V, Divider.DIV_40_V),
    }

    ALLOWED_DIVIDERS_WITH_COIL = {
        clb.SignalType.ACI: (Divider.NONE, Divider.MUL_10_mV, Divider.MUL_30_mV, ),
        clb.SignalType.DCI: (Divider.NONE, Divider.MUL_10_mV, Divider.MUL_30_mV, ),
        clb.SignalType.ACV: (Divider.NONE,),
        clb.SignalType.DCV: (Divider.NONE,),
    }

    ALLOWED_METERS = {
        clb.SignalType.ACI: (Meter.AMPERES,),
        clb.SignalType.DCI: (Meter.AMPERES,),
        clb.SignalType.ACV: (Meter.VOLTS,),
        clb.SignalType.DCV: (Meter.VOLTS,),
    }

    ALLOWED_METERS_WITH_COIL = {
        clb.SignalType.ACI: (Meter.VOLTS,),
        clb.SignalType.DCI: (Meter.VOLTS,),
        clb.SignalType.ACV: (Meter.VOLTS,),
        clb.SignalType.DCV: (Meter.VOLTS,),
    }

    meter_to_units = {
        Meter.AMPERES: "А",
        Meter.VOLTS: "В",
    }

    COIL_TO_DEVICE = {
        Coil.VAL_0_01_OHM: Device.COIL_0_01_OHM,
        Coil.VAL_1_OHM: Device.COIL_1_OHM,
        Coil.VAL_10_OHM: Device.COIL_10_OHM,
    }

    DIVIDER_TO_DEVICE = {
        Divider.MUL_30_mV: Device.MUL_30_mV,
        Divider.MUL_10_mV: Device.MUL_10_mV,
        Divider.DIV_650_V: Device.DIV_650_V,
        Divider.DIV_500_V: Device.DIV_500_V,
        Divider.DIV_350_V: Device.DIV_350_V,
        Divider.DIV_200_V: Device.DIV_200_V,
        Divider.DIV_55_V: Device.DIV_55_V,
        Divider.DIV_40_V: Device.DIV_40_V,
    }

    ExtraParameter = namedtuple("ExtraParameter", ["name", "index", "bit_index", "type", "work_value", "default_value"])

    class ExtraParameterState(IntEnum):
        WORK_VALUE = 0
        DEFAULT_VALUE = 1

    class AdditionalParameters:
        # Эта структура специально сделана классом, чтобы можно было передать ее в ObjectFieldsVisualizer

        def __init__(self):
            self.deviation_threshold = 0.02
            self.confidence_interval_threshold = 0.02

            self.retry_count = 3

            self.manual_range_enabled = False
            self.manual_range_value = 1.
            self.dont_set_meter_config = False

            self.enable_output_filtering = True
            self.filter_sampling_time = 0.1
            self.filter_samples_count = 100

        def __eq__(self, other):
            return other is not None and \
                utils.are_float_equal(self.deviation_threshold, other.deviation_threshold) and \
                utils.are_float_equal(self.confidence_interval_threshold, other.confidence_interval_threshold) and \
                self.retry_count == other.retry_count and \
                self.manual_range_enabled == other.manual_range_enabled and \
                self.manual_range_value == other.manual_range_value and \
                self.dont_set_meter_config == other.dont_set_meter_config and \
                self.enable_output_filtering == other.enable_output_filtering and \
                self.filter_sampling_time == other.filter_sampling_time and \
                self.filter_samples_count == other.filter_samples_count

        def serialize_to_dict(self):
            data_dict = {
                "deviation_threshold": self.deviation_threshold,
                "confidence_interval_threshold": self.confidence_interval_threshold,

                "retry_count": self.retry_count,

                "manual_range_enabled": self.manual_range_enabled,
                "manual_range_value": self.manual_range_value,
                "dont_set_meter_config": self.dont_set_meter_config,

                "enable_output_filtering": self.enable_output_filtering,
                "filter_sampling_time": self.filter_sampling_time,
                "filter_samples_count": self.filter_samples_count,
            }
            return data_dict

        @classmethod
        def from_dict(cls, a_data_dict: dict):
            additional_parameters = cls()

            additional_parameters.deviation_threshold = float(a_data_dict["deviation_threshold"])
            additional_parameters.confidence_interval_threshold = float(a_data_dict["confidence_interval_threshold"])

            additional_parameters.retry_count = int(a_data_dict["retry_count"])

            additional_parameters.manual_range_enabled = bool(a_data_dict["manual_range_enabled"])
            additional_parameters.manual_range_value = float(a_data_dict["manual_range_value"])
            additional_parameters.dont_set_meter_config = bool(a_data_dict["dont_set_meter_config"])

            additional_parameters.enable_output_filtering = bool(a_data_dict["enable_output_filtering"])
            additional_parameters.filter_sampling_time = float(a_data_dict["filter_sampling_time"])
            additional_parameters.filter_samples_count = int(a_data_dict["filter_samples_count"])

            return additional_parameters

    def __init__(self):
        self.coefficient = 1.
        self.measure_delay = 100
        self.measure_time = 300

        self.auto_calc_coefficient = True

        self.meter_config_string = "NPLC 100;LFILTER ON;SETACV SYNC"

        self.consider_output_value = True

        self.coil = CellConfig.Coil.NONE
        self.divider = CellConfig.Divider.NONE
        self.meter = CellConfig.Meter.AMPERES

        # Это дополнительные сетевые переменные
        self.extra_parameters: List[CellConfig.ExtraParameter] = []
        # А это просто переменные
        self.additional_parameters = CellConfig.AdditionalParameters()

    def serialize_to_dict(self):
        data_dict = {
            "coefficient": self.coefficient,
            "measure_delay": self.measure_delay,
            "measure_time": self.measure_time,

            "auto_calc_coefficient": self.auto_calc_coefficient,
            "meter_config_string": self.meter_config_string,

            "consider_output_value": self.consider_output_value,

            "coil": int(self.coil),
            "divider": int(self.divider),
            "meter": int(self.meter),

            "extra_parameters": self.extra_parameters,
            "additional_parameters": self.additional_parameters.serialize_to_dict(),
        }
        return data_dict

    @classmethod
    def from_dict(cls, a_data_dict: dict):
        cell_config = cls()

        cell_config.coefficient = float(a_data_dict["coefficient"])
        cell_config.measure_delay = int(a_data_dict["measure_delay"])
        cell_config.measure_time = int(a_data_dict["measure_time"])

        cell_config.auto_calc_coefficient = bool(a_data_dict["auto_calc_coefficient"])
        cell_config.meter_config_string = a_data_dict["meter_config_string"]

        cell_config.consider_output_value = bool(a_data_dict["consider_output_value"])

        cell_config.coil = CellConfig.Coil(int(a_data_dict["coil"]))
        cell_config.divider = CellConfig.Divider(int(a_data_dict["divider"]))
        cell_config.meter = CellConfig.Meter(int(a_data_dict["meter"]))

        cell_config.extra_parameters = [CellConfig.ExtraParameter(*extra_parameter)
                                        for extra_parameter in a_data_dict["extra_parameters"]]

        cell_config.additional_parameters = CellConfig.AdditionalParameters.from_dict(
            a_data_dict["additional_parameters"])

        return cell_config

    def verify_scheme(self, a_signal_type: clb.SignalType):
        is_coil_used = self.coil != CellConfig.Coil.NONE
        allowed_dividers = CellConfig.ALLOWED_DIVIDERS_WITH_COIL if is_coil_used else CellConfig.ALLOWED_DIVIDERS
        allowed_meters = CellConfig.ALLOWED_METERS_WITH_COIL if is_coil_used else CellConfig.ALLOWED_METERS
        scheme_is_ok = self.coil in CellConfig.ALLOWED_COILS[a_signal_type] and \
                       self.divider in allowed_dividers[a_signal_type] and \
                       self.meter in allowed_meters[a_signal_type]
        return scheme_is_ok

    def reset_scheme(self, a_signal_type: clb.SignalType):
        self.coil = CellConfig.Coil.NONE
        self.divider = CellConfig.Divider.NONE
        self.meter = CellConfig.Meter.VOLTS if clb.is_voltage_signal[a_signal_type] else CellConfig.Meter.AMPERES

    @utils.exception_decorator
    def update_coefficient(self, a_frequency: float, a_shared_parameters: SharedMeasureParameters) -> bool:
        result = False

        if self.auto_calc_coefficient:
            coefficient = self.calculate_coefficient(self.coil, self.divider, a_frequency, a_shared_parameters)
            if not utils.are_float_equal(self.coefficient, coefficient):
                self.coefficient = coefficient
                result = True

        return result

    @staticmethod
    def calculate_coefficient(a_coil: Coil, a_divider: Divider, a_frequency: float,
                              a_shared_parameters: SharedMeasureParameters) -> float:
        coil_coef = 1.
        if a_coil != CellConfig.Coil.NONE:
            a_device = CellConfig.COIL_TO_DEVICE[a_coil]
            coil_coef = CellConfig.get_device_coefficient_by_frequency(a_device, a_frequency, a_shared_parameters)

        divider_coef = 1.
        if a_divider != CellConfig.Divider.NONE:
            a_device = CellConfig.DIVIDER_TO_DEVICE[a_divider]
            divider_coef = CellConfig.get_device_coefficient_by_frequency(a_device, a_frequency, a_shared_parameters)

        # I = (1/R * 1/K) * Uк,
        # где I - заданный в калибратор ток, R - сопр. катушки, K - коэф. делителя, Uк - конечное напряжение
        # Здесь возвращаем коэффициент преобразования 1/R * 1/K
        return 1 / coil_coef / divider_coef

    @staticmethod
    def get_device_coefficient_by_frequency(a_device: Device, a_frequency: float,
                                            a_shared_parameters: SharedMeasureParameters) -> float:
        """
        Для нулевой частоты (постоянный сигнал) всегда берется коэффициент с частотой 0, если он отсутствует,
        берется коэффициент по-умолчанию
        Для ненулевой частоты (переменный сигнал) сигнал интерполируется, если частот не хватает для интерполяции, то
        берется коэффициент для 0 частоты. Если коэффициент для 0 частоты не задан, то берется коэффициент по умолчанию
        При вычислении интерполяции, коэффициент для 0 частоты не учитывается.
        """
        frequencies, coefficients = a_shared_parameters.device_coefs[a_device]

        try:
            frequency_idx = frequencies.index(a_frequency)
            coefficient = coefficients[frequency_idx]
        except ValueError:
            freq_coefs = {freq: coef for freq, coef in zip(frequencies, coefficients)}
            freq_coefs_sorted = OrderedDict(sorted(freq_coefs.items()))

            if 0 in freq_coefs_sorted:
                # 0 частоту не включаем в интерполяцию
                del freq_coefs_sorted[0]

            if a_frequency == 0 or len(freq_coefs_sorted) < 2:
                logging.error(f'Частота {a_frequency}, коэффициент для частоты 0 Гц не задан, либо количество точек '
                              f'для интерполяции слишком мало, будет использован коэффициент по-умолчанию. '
                              f'(При интерполяции точка с частотой 0 не учитывается!)')
                frequencies, coefficients = DEVICE_TO_DEFAULT_COEFS[a_device]
                frequency_idx = frequencies.index(0.)
                coefficient = coefficients[frequency_idx]
                logging.error(f'Коэффициент по-умолчанию: {coefficient}')
            else:
                pchip = Pchip()
                pchip.set_points(list(freq_coefs_sorted.keys()), list(freq_coefs_sorted.values()))
                coefficient = pchip.interpolate(a_frequency)

        return coefficient

    def __eq__(self, other):
        return other is not None and \
            utils.are_float_equal(self.coefficient, other.coefficient) and \
            self.measure_delay == other.measure_delay and \
            self.measure_time == other.measure_time and \
            self.auto_calc_coefficient == other.auto_calc_coefficient and \
            self.consider_output_value == other.consider_output_value and \
            self.meter_config_string == other.meter_config_string and \
            self.coil == other.coil and \
            self.divider == other.divider and \
            self.meter == other.meter and \
            self.extra_parameters == other.extra_parameters and \
            self.additional_parameters == other.additional_parameters


class EditCellConfigDialog(QtWidgets.QDialog):
    class ExtraParamsColumn(IntEnum):
        NAME = 0
        INDEX = 1
        BIT_INDEX = 2
        TYPE = 3
        WORK_VALUE = 4
        DEFAULT_VALUE = 5
        COUNT = 6

    # a_shared_parameters и a_frequency нужны для автоматического рассчета коэффициента
    def __init__(self, a_init_config: CellConfig, a_shared_parameters: SharedMeasureParameters, a_frequency: float,
                 a_signal_type: clb.SignalType, a_settings: QtSettings, a_lock_editing=False, a_parent=None):
        super().__init__(a_parent)

        self.ui = EditCellConfigForm()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)
        self.show()

        if a_lock_editing:
            self.ui.accept_button.setDisabled(a_lock_editing)

        self.__allowed_extra_param_types = ("double", "float", "bit", "u32", "i32", "u8", "i8", "u16", "i16",
                                            "bool", "u64", "i64")
        self.ui.extra_variables_table.setItemDelegate(TransparentPainterForWidget(self.ui.extra_variables_table,
                                                                                  "#d4d4ff"))
        self.ui.extra_variables_table.setItemDelegateForColumn(EditCellConfigDialog.ExtraParamsColumn.TYPE,
                                                               ComboboxCellDelegate(self,
                                                                                    self.__allowed_extra_param_types))

        self.settings = a_settings
        self.settings.restore_dialog_size(self)
        self.settings.restore_qwidget_state(self.ui.extra_variables_table)

        self.signal_type_to_radio = {
            clb.SignalType.ACI: self.ui.aci_radio,
            clb.SignalType.ACV: self.ui.acv_radio,
            clb.SignalType.DCI: self.ui.dci_radio,
            clb.SignalType.DCV: self.ui.dcv_radio
        }

        self.coil_to_radio = {
            CellConfig.Coil.NONE: self.ui.coil_no_radio,
            CellConfig.Coil.VAL_0_01_OHM: self.ui.coil_001_radio,
            CellConfig.Coil.VAL_1_OHM: self.ui.coil_1_radio,
            CellConfig.Coil.VAL_10_OHM: self.ui.coil_10_radio,
        }
        self.radio_to_coil = {v: k for k, v in self.coil_to_radio.items()}

        self.divider_to_radio = {
            CellConfig.Divider.NONE: self.ui.divider_no_radio,
            CellConfig.Divider.DIV_650_V: self.ui.divider_650_radio,
            CellConfig.Divider.DIV_500_V: self.ui.divider_500_radio,
            CellConfig.Divider.DIV_350_V: self.ui.divider_350_radio,
            CellConfig.Divider.DIV_200_V: self.ui.divider_200_radio,
            CellConfig.Divider.DIV_55_V: self.ui.divider_55_radio,
            CellConfig.Divider.DIV_40_V: self.ui.divider_40_radio,
            CellConfig.Divider.MUL_30_mV: self.ui.amplifier_30_radio,
            CellConfig.Divider.MUL_10_mV: self.ui.amplifier_10_radio,
        }
        self.radio_to_divider = {v: k for k, v in self.divider_to_radio.items()}

        self.meter_to_radio = {
            CellConfig.Meter.AMPERES: self.ui.ammeter_radio,
            CellConfig.Meter.VOLTS: self.ui.voltmeter_radio
        }
        self.radio_to_meter = {v: k for k, v in self.meter_to_radio.items()}

        self.shared_parameters = a_shared_parameters
        self.frequency = a_frequency
        self.init_coefficient = a_init_config.coefficient
        self.cell_config = None
        self.signal_type = a_signal_type
        self.recover_config(a_init_config)

        self.additional_parameters = copy.deepcopy(a_init_config.additional_parameters)
        visualizer = ObjectFieldsVisualizer(self.additional_parameters, self)
        visualizer.add_setting("Порог отклонения", "deviation_threshold")
        visualizer.add_setting("Порог болтанки (95%)", "confidence_interval_threshold")
        visualizer.add_setting("Количество попыток", "retry_count")
        visualizer.add_setting("Вкл. ручной диапазон измерителя", "manual_range_enabled")
        visualizer.add_setting("Ручной диапазон", "manual_range_value")
        visualizer.add_setting("Не выставлять парам-ры измерителя", "dont_set_meter_config")
        visualizer.add_setting("Фильтрация выходного значения", "enable_output_filtering")
        visualizer.add_setting("Время дискретизации (фильтр)", "filter_sampling_time")
        visualizer.add_setting("Количество точек (фильтр)", "filter_samples_count")
        self.ui.additional_parameters_layout.addWidget(visualizer)

        self.lock_scheme_radios()
        self.scheme_changed()

        for radio in self.radio_to_coil:
            radio.toggled.connect(self.scheme_changed)
            radio.toggled.connect(self.calculate_auto_coefficient)

        for radio in self.radio_to_divider:
            radio.toggled.connect(self.scheme_changed)
            radio.toggled.connect(self.calculate_auto_coefficient)

        self.ui.auto_coefficient_checkbox.toggled.connect(self.auto_coefficient_checkbox_toggled)

        self.ui.add_extra_param_button.clicked.connect(self.add_extra_param_button_clicked)
        self.ui.remove_extra_param_button.clicked.connect(self.remove_extra_param_button_clicked)

        self.ui.coefficient_edit.textEdited.connect(self.coefficient_edited)
        self.ui.coefficient_edit.editingFinished.connect(self.editing_finished)

        self.ui.accept_button.clicked.connect(self.accept_config)
        self.ui.cancel_button.clicked.connect(self.reject)

    def __del__(self):
        print("EditCellConfigDialog deleted")

    def coefficient_edited(self):
        edit = self.sender()
        assert isinstance(edit, QtWidgets.QLineEdit), "edit_text_edited must be connected to QLineEdit event!"
        self.update_edit_color(edit)

    @staticmethod
    def update_edit_color(a_edit: QtWidgets.QLineEdit):
        try:
            utils.parse_input(a_edit.text())

            a_edit.setStyleSheet(qt_utils.QSTYLE_COLOR_WHITE)
        except ValueError:
            a_edit.setStyleSheet(qt_utils.QSTYLE_COLOR_RED)

    def editing_finished(self):
        edit = self.sender()
        assert isinstance(edit, QtWidgets.QLineEdit), "editinig_finished must be connected to QLineEdit event!"
        self.normalize_edit_value(edit)

    def normalize_edit_value(self, edit: QtWidgets.QLineEdit):
        try:
            value = utils.parse_input(edit.text(), a_precision=20)
            edit.setText(utils.float_to_string(value, a_precision=20))
        except ValueError:
            edit.setText("0")
        self.update_edit_color(edit)

    def recover_config(self, a_cell_config: CellConfig):
        self.signal_type_to_radio[self.signal_type].setChecked(True)

        self.ui.measure_delay_spinbox.setValue(a_cell_config.measure_delay)
        self.ui.measure_time_spinbox.setValue(a_cell_config.measure_time)
        self.ui.coefficient_edit.setText(utils.float_to_string(a_cell_config.coefficient, a_precision=20))

        self.ui.coefficient_edit.setReadOnly(a_cell_config.auto_calc_coefficient)
        self.ui.auto_coefficient_checkbox.setChecked(a_cell_config.auto_calc_coefficient)

        self.ui.meter_config_edit.setText(a_cell_config.meter_config_string)

        self.ui.consider_output_value_checkbox.setChecked(a_cell_config.consider_output_value)

        self.coil_to_radio[a_cell_config.coil].setChecked(True)
        self.divider_to_radio[a_cell_config.divider].setChecked(True)
        self.meter_to_radio[a_cell_config.meter].setChecked(True)

        for extra_parameter in a_cell_config.extra_parameters:
            qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, (
                extra_parameter.name, str(extra_parameter.index), str(extra_parameter.bit_index), extra_parameter.type,
                utils.float_to_string(extra_parameter.work_value), utils.float_to_string(extra_parameter.default_value)
            ))

    def auto_coefficient_checkbox_toggled(self, a_enable):
        if a_enable:
            coil, divider, _ = self.__get_scheme()
            coefficient = CellConfig.calculate_coefficient(coil, divider, self.frequency, self.shared_parameters)
        else:
            coefficient = self.init_coefficient

        self.ui.coefficient_edit.setText(utils.float_to_string(coefficient, a_precision=20))
        self.ui.coefficient_edit.setReadOnly(a_enable)

    def lock_scheme_radios(self):
        for radio, coil in self.radio_to_coil.items():
            enable_cb = coil in CellConfig.ALLOWED_COILS[self.signal_type]
            if not enable_cb and radio.isChecked():
                self.ui.coil_no_radio.setChecked(True)
            radio.setEnabled(enable_cb)

        is_coil_using = not self.ui.coil_no_radio.isChecked()
        allowed_dividers = CellConfig.ALLOWED_DIVIDERS_WITH_COIL if is_coil_using else CellConfig.ALLOWED_DIVIDERS

        for radio, divider in self.radio_to_divider.items():
            enable_cb = divider in allowed_dividers[self.signal_type]
            if not enable_cb and radio.isChecked():
                self.ui.divider_no_radio.setChecked(True)
            radio.setEnabled(enable_cb)

    def scheme_changed(self):
        meter = CellConfig.Meter.VOLTS if clb.is_voltage_signal[self.signal_type] else CellConfig.Meter.AMPERES

        is_coil_using = not self.ui.coil_no_radio.isChecked()
        if is_coil_using:
            meter = CellConfig.Meter.VOLTS

        self.meter_to_radio[meter].setChecked(True)
        self.lock_scheme_radios()

    def calculate_auto_coefficient(self):
        # Пересчитывает коэффициент, если включен авто рассчет
        self.auto_coefficient_checkbox_toggled(self.ui.auto_coefficient_checkbox.isChecked())

    def exec_and_get(self) -> Union[CellConfig, None]:
        if self.exec() == QtWidgets.QDialog.Accepted:
            return self.cell_config
        else:
            return None

    def accept_config(self):
        extra_parameters = []
        try:
            for row in range(self.ui.extra_variables_table.rowCount()):
                extra_parameters.append(CellConfig.ExtraParameter(
                    name=self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.NAME).text(),
                    index=int(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.INDEX).text()),
                    bit_index=int(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.BIT_INDEX).text()),
                    type=self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.TYPE).text(),
                    work_value=utils.parse_input(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.WORK_VALUE).text()),
                    default_value=utils.parse_input(self.ui.extra_variables_table.item(row, EditCellConfigDialog.ExtraParamsColumn.DEFAULT_VALUE).text())
                ))
            data_valid = True
        except ValueError:
            data_valid = False

        coefficient = utils.parse_input(self.ui.coefficient_edit.text(), a_precision=20)
        if coefficient == 0:
            data_valid = False

        if data_valid:
            self.cell_config = CellConfig()

            self.cell_config.measure_delay = self.ui.measure_delay_spinbox.value()
            self.cell_config.measure_time = self.ui.measure_time_spinbox.value()
            self.cell_config.coefficient = coefficient

            self.cell_config.auto_calc_coefficient = self.ui.auto_coefficient_checkbox.isChecked()

            self.cell_config.consider_output_value = self.ui.consider_output_value_checkbox.isChecked()

            self.cell_config.meter_config_string = self.ui.meter_config_edit.text()

            self.cell_config.coil, self.cell_config.divider, self.cell_config.meter = self.__get_scheme()

            self.cell_config.extra_parameters = extra_parameters

            self.cell_config.additional_parameters = self.additional_parameters

            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", "Таблица дополнительных параметров заполнена неверно,"
                                                           "либо коэффициент равен нулю",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    def __get_scheme(self):
        coil = CellConfig.Coil.NONE
        divider = CellConfig.Divider.NONE
        meter = CellConfig.Meter.VOLTS

        for coil_radio in self.radio_to_coil.keys():
            if coil_radio.isChecked():
                coil = self.radio_to_coil[coil_radio]

        for divider_radio in self.radio_to_divider.keys():
            if divider_radio.isChecked():
                divider = self.radio_to_divider[divider_radio]

        for meter_radio in self.radio_to_meter.keys():
            if meter_radio.isChecked():
                meter = self.radio_to_meter[meter_radio]

        return coil, divider, meter

    def add_extra_param_button_clicked(self):
        init_row = [""] * EditCellConfigDialog.ExtraParamsColumn.COUNT
        init_row[EditCellConfigDialog.ExtraParamsColumn.TYPE] = self.__allowed_extra_param_types[0]

        qt_utils.qtablewidget_append_row(self.ui.extra_variables_table, init_row)

    def remove_extra_param_button_clicked(self):
        qt_utils.qtablewidget_delete_selected(self.ui.extra_variables_table)

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.settings.save_qwidget_state(self.ui.extra_variables_table)
        self.settings.save_dialog_size(self)

        a_event.accept()
