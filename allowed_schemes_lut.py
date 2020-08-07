from edit_cell_config_dialog import CellConfig
from irspy.clb.calibrator_constants import SignalType, is_voltage_signal
import logging


MAX_VOLTAGE_AMPLITUDES = {
    # Прямая схема подключения
    (CellConfig.Divider.NONE, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 630.,
    # Делить / усилитель
    (CellConfig.Divider.DIV_650_V, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 630.,
    (CellConfig.Divider.DIV_500_V, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 505.,
    (CellConfig.Divider.DIV_350_V, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 355.,
    (CellConfig.Divider.DIV_200_V, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 205.,
    (CellConfig.Divider.DIV_55_V, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 60.,
    (CellConfig.Divider.DIV_40_V, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 45.,
    (CellConfig.Divider.MUL_10_mV, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 0.11,
    (CellConfig.Divider.MUL_30_mV, CellConfig.Coil.NONE, CellConfig.Meter.VOLTS): 0.3,
}

MAX_CURRENT_AMPLITUDES = {
    # Прямая схема подключения
    (CellConfig.Divider.NONE, CellConfig.Coil.NONE, CellConfig.Meter.AMPERES): 11.,
    # Катушка
    (CellConfig.Divider.NONE, CellConfig.Coil.VAL_0_01_OHM, CellConfig.Meter.VOLTS): 11.,
    (CellConfig.Divider.NONE, CellConfig.Coil.VAL_1_OHM, CellConfig.Meter.VOLTS): 1.2,
    (CellConfig.Divider.NONE, CellConfig.Coil.VAL_10_OHM, CellConfig.Meter.VOLTS): 0.12,
    # Катушка + усилитель
    (CellConfig.Divider.MUL_10_mV, CellConfig.Coil.VAL_0_01_OHM, CellConfig.Meter.VOLTS): 11.,
    (CellConfig.Divider.MUL_30_mV, CellConfig.Coil.VAL_0_01_OHM, CellConfig.Meter.VOLTS): 3.3,
    (CellConfig.Divider.MUL_10_mV, CellConfig.Coil.VAL_1_OHM, CellConfig.Meter.VOLTS): 0.12,
    (CellConfig.Divider.MUL_30_mV, CellConfig.Coil.VAL_1_OHM, CellConfig.Meter.VOLTS): 0.033,
    (CellConfig.Divider.MUL_10_mV, CellConfig.Coil.VAL_10_OHM, CellConfig.Meter.VOLTS): 0.012,
    (CellConfig.Divider.MUL_30_mV, CellConfig.Coil.VAL_10_OHM, CellConfig.Meter.VOLTS): 0.0033,
}


def get_max_amplitude(a_signal_type: SignalType, a_coil: CellConfig.Coil, a_divider: CellConfig.Divider,
                      a_meter: CellConfig.Meter) -> float:
    max_amplitude_lut = MAX_VOLTAGE_AMPLITUDES if is_voltage_signal[a_signal_type] else MAX_CURRENT_AMPLITUDES
    try:
        max_amplitude = max_amplitude_lut[(a_divider, a_coil, a_meter)]
    except KeyError:
        logging.critical("Непредусмотренная схема подключения. Не удалось определить максимальную амплитуду")
        max_amplitude = 0

    return max_amplitude
