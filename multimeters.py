import logging
from enum import IntEnum
import random
import ctypes
import abc

from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.dlls import mxsrlib_dll
from irspy import utils

from edit_agilent_config_dialog import AgilentConfig, EditAgilentConfigDialog


# Из mxsrclib -> measmul.h
class MeasureType(IntEnum):
    tm_value = 1
    tm_volt_dc = 2,
    tm_volt_ac = 3,
    tm_current_dc = 4,
    tm_current_ac = 5,
    tm_resistance_2x = 6,
    tm_resistance_4x = 7,
    tm_frequency = 8,
    tm_phase = 9,
    tm_phase_average = 10,
    tm_time_interval = 11,
    tm_time_interval_average = 12,
    tm_distortion = 13,


class MultimeterBase(abc.ABC):
    # Из mxsrclib measdef.h
    class MeasureStatus(IntEnum):
        SUCCESS = 0
        BUSY = 1
        ERROR = 2

    def edit_settings(self, a_lock_changes: bool, a_parent):
        pass

    @abc.abstractmethod
    def connect(self, a_measure_type: MeasureType) -> bool:
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def is_connected(self) -> bool:
        pass

    @abc.abstractmethod
    def tick(self):
        pass

    @abc.abstractmethod
    def measure_status(self) -> MeasureStatus:
        pass

    @abc.abstractmethod
    def start_measure(self) -> bool:
        pass

    @abc.abstractmethod
    def get_measured_value(self) -> float:
        pass

    @abc.abstractmethod
    def get_measure_type(self) -> MeasureType:
        pass

    @abc.abstractmethod
    def set_range(self, a_measure_type: MeasureType, a_range: float) -> bool:
        pass

    @abc.abstractmethod
    def get_range(self) -> str:
        pass

    @abc.abstractmethod
    def set_config(self, a_config_str) -> bool:
        pass


class MeterType(IntEnum):
    AGILENT_3458A = 0
    GAG = 1


def create_multimeter(a_meter_type: MeterType, a_settings: QtSettings):
    if a_meter_type == MeterType.AGILENT_3458A:
        return Agilent3485A(a_settings)
    elif a_meter_type == MeterType.GAG:
        return MultimeterGag()
    else:
        return None


class Agilent3485A(MultimeterBase):

    MEASURE_TYPE_TO_SIGNAL_STR = {
        MeasureType.tm_volt_dc: "DCV",
        MeasureType.tm_volt_ac: "ACV",
        MeasureType.tm_current_dc: "DCI",
        MeasureType.tm_current_ac: "ACI",
    }

    def __init__(self, a_settings: QtSettings):
        assert mxsrlib_dll.mxsrclib_dll is not None, "mxsrclib_dll не инициализирована !!!"
        self.mxsrclib_dll = mxsrlib_dll.mxsrclib_dll

        self.settings = a_settings

        self.agilent_config = AgilentConfig()
        # Эти переменные должны быть добавлены в Settings в начале программы
        self.agilent_config.connect_type = self.settings.agilent_connect_type
        self.agilent_config.gpib_index = self.settings.agilent_gpib_index
        self.agilent_config.gpib_address = self.settings.agilent_gpib_address
        self.agilent_config.com_name = self.settings.agilent_com_name
        self.agilent_config.ip_address = self.settings.agilent_ip_address
        self.agilent_config.port = self.settings.agilent_port

        self.measure_type = None
        self.connected = False
        self.p_double = (ctypes.c_double * 1)()

        self.range = ""

    def edit_settings(self, a_lock_changes: bool, a_parent):
        edit_agilent_config_dialog = EditAgilentConfigDialog(self.agilent_config, self.settings, a_lock_changes,
                                                             a_parent)

        new_config = edit_agilent_config_dialog.exec_and_get()
        if new_config is not None and new_config != self.agilent_config:
            self.agilent_config = new_config
            self.settings.agilent_connect_type = self.agilent_config.connect_type
            self.settings.agilent_gpib_index = self.agilent_config.gpib_index
            self.settings.agilent_gpib_address = self.agilent_config.gpib_address
            self.settings.agilent_com_name = self.agilent_config.com_name
            self.settings.agilent_ip_address = self.agilent_config.ip_address
            self.settings.agilent_port = self.agilent_config.port

        edit_agilent_config_dialog.close()

    def connect(self, a_measure_type: MeasureType) -> bool:
        # ВНИМАНИЕ! Макрос IRS_LIB_DEBUG в irsconfig.h для mxsrclib_dll должен быть отключен!!! Иначе крашнется
        result = self.mxsrclib_dll.connect_to_agilent_3458a(
            ctypes.c_size_t(a_measure_type),
            ctypes.c_wchar_p(AgilentConfig.CONN_TYPE_TO_NAME[self.agilent_config.connect_type]),
            ctypes.c_int(self.agilent_config.gpib_index), ctypes.c_int(self.agilent_config.gpib_address),
            ctypes.c_wchar_p(self.agilent_config.com_name), ctypes.c_wchar_p(self.agilent_config.ip_address),
            ctypes.c_wchar_p(str(self.agilent_config.port)))

        if result:
            self.measure_type = a_measure_type
            self.connected = True

        return bool(result)

    def disconnect(self):
        self.measure_type = None
        self.connected = False
        self.p_double = (ctypes.c_double * 1)()
        self.mxsrclib_dll.disconnect_multimeter()

    def is_connected(self) -> bool:
        return self.connected

    def tick(self):
        self.mxsrclib_dll.multimeter_tick()

    def measure_status(self) -> MultimeterBase.MeasureStatus:
        status = MultimeterBase.MeasureStatus(self.mxsrclib_dll.multimeter_get_status())
        return status

    def start_measure(self) -> bool:
        assert self.measure_status() == MultimeterBase.MeasureStatus.SUCCESS, "Статус должен быть SUCCESS!!"
        assert self.measure_type is not None, "Мультиметр не инициализирован!"

        return bool(self.mxsrclib_dll.multimeter_start_measure(ctypes.c_size_t(self.measure_type), self.p_double))

    def get_measured_value(self) -> float:
        return self.p_double[0]

    def get_measure_type(self) -> MeasureType:
        return self.measure_type

    def set_range(self, a_measure_type: MeasureType, a_range: float) -> bool:
        try:
            measure_type_str = Agilent3485A.MEASURE_TYPE_TO_SIGNAL_STR[a_measure_type]
        except KeyError:
            return False
        else:
            self.range = f"{measure_type_str} {a_range}"

            return bool(self.mxsrclib_dll.multimeter_set_config(
                ctypes.c_char_p(bytes(self.range, encoding="cp1251")), ctypes.c_double(1.)))

    def get_range(self) -> str:
        return self.range

    def set_config(self, a_config_str: str):
        return bool(self.mxsrclib_dll.multimeter_set_config(
            ctypes.c_char_p(bytes(a_config_str, encoding="cp1251")), ctypes.c_double(2.)))


class MultimeterGag(MultimeterBase):

    def __init__(self):
        self.measure_type = None
        self.lower_bound = 0.
        self.upper_bound = 0.

        self.measure_value_timer = utils.Timer(2)
        self.measure_value_timer.start()
        self.range = ""

    def edit_settings(self, a_lock_changes: bool, a_parent):
        pass

    def connect(self, a_measure_type: MeasureType) -> bool:
        self.measure_type = a_measure_type
        return True

    def disconnect(self):
        self.lower_bound = 0.
        self.upper_bound = 0.

    def is_connected(self) -> bool:
        return True

    def tick(self):
        pass

    def measure_status(self) -> MultimeterBase.MeasureStatus:
        if self.measure_value_timer.check():
            self.measure_value_timer.stop()
            return MultimeterBase.MeasureStatus.SUCCESS
        else:
            return MultimeterBase.MeasureStatus.BUSY

    def start_measure(self) -> bool:
        self.measure_value_timer.start()
        return True

    def get_measured_value(self) -> float:
        return random.uniform(self.lower_bound, self.upper_bound)

    def get_measure_type(self) -> MeasureType:
        return self.measure_type

    def set_range(self, a_measure_type: MeasureType, a_range: float) -> bool:
        deviation = 0.04
        self.lower_bound = utils.decrease_by_percent(a_range, deviation)
        self.upper_bound = utils.increase_by_percent(a_range, deviation)
        self.range = f"{self.lower_bound}-{self.upper_bound}+-{deviation}"
        return True

    def get_range(self) -> str:
        return self.range

    def set_config(self, a_config_str) -> bool:
        return True


if __name__ == "__main__":
    from irspy.qt.qt_settings_ini_parser import QtSettings
    import time
    import os

    settings_file = "./tmp_settings.ini"
    settings = QtSettings(settings_file, [
        QtSettings.VariableInfo(a_name="agilent_connect_type", a_section="PARAMETERS",
                                a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="agilent_gpib_index", a_section="PARAMETERS",
                                a_type=QtSettings.ValueType.INT, a_default=0),
        QtSettings.VariableInfo(a_name="agilent_gpib_address", a_section="PARAMETERS",
                                a_type=QtSettings.ValueType.INT, a_default=22),
        QtSettings.VariableInfo(a_name="agilent_com_name", a_section="PARAMETERS",
                                a_type=QtSettings.ValueType.STRING, a_default="com4"),
        QtSettings.VariableInfo(a_name="agilent_ip_address", a_section="PARAMETERS",
                                a_type=QtSettings.ValueType.STRING, a_default="0.0.0.0"),
        QtSettings.VariableInfo(a_name="agilent_port", a_section="PARAMETERS",
                                a_type=QtSettings.ValueType.INT, a_default=0),
    ])

    m = Agilent3485A(settings)
    m.connect(MeasureType.tm_value)

    def send_command(command, *args):
        start = time.time()
        command(*args)
        while m.measure_status() != MultimeterBase.MeasureStatus.SUCCESS:
            m.tick()
        print(f"'{command.__name__}' executed for {time.time() - start} sec")

    send_command(m.set_range, MeasureType.tm_current_ac, 1)
    # send_command(m.set_range, MeasureType.tm_volt_ac, 1)
    send_command(m.set_config, "SETACV SYNC;NPLC 100")

    m.disconnect()
    os.remove(settings_file)

