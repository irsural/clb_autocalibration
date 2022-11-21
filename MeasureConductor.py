from typing import Union, List, Tuple, Dict
from collections import namedtuple
from time import perf_counter
from enum import IntEnum, auto
import logging

from PyQt5 import QtCore

from irspy.clb.network_variables import NetworkVariables, BufferedVariable, VariableInfo
from irspy.qt.qt_settings_ini_parser import QtSettings
from irspy.clb import assist_functions as clb_assists
from irspy.clb import calibrator_constants as clb
from CorrectionFlasher import CorrectionFlasher
from irspy.clb.clb_dll import ClbDrv
from irspy import metrology
from irspy import utils

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig
from MeasureIterator import MeasureIterator
from MeasureManager import MeasureManager
import allowed_schemes_lut as scheme_lut
import multimeters


ExtraVariable = namedtuple("ExtraVariable", ["buffered_variable", "work_value", "default_value"])


class MeasureConductor(QtCore.QObject):
    class Stage(IntEnum):
        REST = auto()
        CONNECT_TO_CALIBRATOR = auto()
        CONNECT_TO_METER = auto()
        CONNECT_TO_SCHEME = auto()
        GET_CONFIGS = auto()
        RESET_CALIBRATOR_CONFIG = auto()
        WAIT_CALIBRATOR_RESET = auto()
        RESET_METER_CONFIG = auto()
        RESET_SCHEME_CONFIG = auto()
        SET_METER_MEASURE_TYPE = auto()
        WAIT_METER_MEASURE_TYPE = auto()
        METER_TEST_MEASURE = auto()
        SET_METER_CONFIG = auto()
        WAIT_METER_CONFIG = auto()
        SET_SCHEME_CONFIG = auto()
        WAIT_SCHEME_SETTLE_DOWN = auto()
        SET_CALIBRATOR_CONFIG = auto()
        WAIT_CALIBRATOR_READY = auto()
        MEASURE = auto()
        END_MEASURE = auto()
        ERRORS_OUTPUT = auto()
        START_FLASH = auto()
        FLASH_TO_CALIBRATOR = auto()
        NEXT_MEASURE = auto()
        MEASURE_DONE = auto()

    STAGE_IN_MESSAGE = {
        Stage.REST: ("Измерение не проводится", logging.DEBUG),
        Stage.CONNECT_TO_CALIBRATOR: ("Подключение к калибратору", logging.DEBUG),
        Stage.CONNECT_TO_METER: ("Подключение к измерителю", logging.DEBUG),
        Stage.CONNECT_TO_SCHEME: ("Подключение к схеме", logging.DEBUG),
        Stage.GET_CONFIGS: ("Получение конфигурации", logging.DEBUG),
        Stage.RESET_CALIBRATOR_CONFIG: ("Сброс параметров калибратора", logging.DEBUG),

        Stage.WAIT_CALIBRATOR_RESET: ("Ждем сброс калибратора...", logging.INFO),

        Stage.RESET_METER_CONFIG: ("Сброс параметров измерителя", logging.DEBUG),
        Stage.RESET_SCHEME_CONFIG: ("Сброс параметров схемы", logging.DEBUG),

        Stage.SET_METER_MEASURE_TYPE: ("Установка рода тока и диапазона измерителя", logging.INFO),
        Stage.WAIT_METER_MEASURE_TYPE: ("Ожидание установки рода тока и диапазона измерителя", logging.DEBUG),
        Stage.METER_TEST_MEASURE: ("Выполняется тестовое измерение мультиметром...", logging.INFO),
        Stage.SET_METER_CONFIG: ("Установка параметров измерителя", logging.INFO),
        Stage.WAIT_METER_CONFIG: ("Ожидание установки параметров измерителя", logging.DEBUG),

        Stage.SET_SCHEME_CONFIG: ("Установка параметров схемы", logging.DEBUG),
        Stage.WAIT_SCHEME_SETTLE_DOWN: ("На всякий случай немного ждем схему...", logging.DEBUG),

        Stage.SET_CALIBRATOR_CONFIG: ("Установка параметров калибратора", logging.INFO),

        Stage.WAIT_CALIBRATOR_READY: ("Ожидание выхода калибратора на режим...", logging.DEBUG),
        Stage.MEASURE: ("Измерение...", logging.DEBUG),
        Stage.END_MEASURE: ("Конец измерения", logging.DEBUG),
        Stage.ERRORS_OUTPUT: ("Вывод ошибок", logging.DEBUG),
        Stage.START_FLASH: ("Начало прошивки", logging.DEBUG),

        Stage.FLASH_TO_CALIBRATOR: ("Прошивка калибратора...", logging.INFO),
        Stage.NEXT_MEASURE: ("Следующее измерение", logging.INFO),
        Stage.MEASURE_DONE: ("Измерение закончено", logging.INFO),
    }

    NEXT_STAGE = {
        Stage.REST: Stage.REST,
        Stage.CONNECT_TO_CALIBRATOR: Stage.CONNECT_TO_METER,
        Stage.CONNECT_TO_METER: Stage.CONNECT_TO_SCHEME,
        Stage.CONNECT_TO_SCHEME: Stage.GET_CONFIGS,
        Stage.GET_CONFIGS: Stage.RESET_CALIBRATOR_CONFIG,
        Stage.RESET_CALIBRATOR_CONFIG: Stage.WAIT_CALIBRATOR_RESET,
        Stage.WAIT_CALIBRATOR_RESET: Stage.RESET_METER_CONFIG,
        Stage.RESET_METER_CONFIG: Stage.RESET_SCHEME_CONFIG,
        # Stage.RESET_SCHEME_CONFIG: Stage.SET_METER_MEASURE_TYPE,
        # Stage.RESET_SCHEME_CONFIG: Stage.MEASURE_DONE,
        Stage.SET_METER_MEASURE_TYPE: Stage.WAIT_METER_MEASURE_TYPE,
        # Stage.WAIT_METER_MEASURE_TYPE: Stage.METER_TEST_MEASURE,
        # Stage.WAIT_METER_MEASURE_TYPE: Stage.SET_METER_CONFIG,
        Stage.METER_TEST_MEASURE: Stage.SET_METER_CONFIG,
        Stage.SET_METER_CONFIG: Stage.WAIT_METER_CONFIG,
        Stage.WAIT_METER_CONFIG: Stage.SET_SCHEME_CONFIG,
        Stage.SET_SCHEME_CONFIG: Stage.WAIT_SCHEME_SETTLE_DOWN,
        Stage.WAIT_SCHEME_SETTLE_DOWN: Stage.SET_CALIBRATOR_CONFIG,
        Stage.SET_CALIBRATOR_CONFIG: Stage.WAIT_CALIBRATOR_READY,
        Stage.WAIT_CALIBRATOR_READY: Stage.MEASURE,
        # Stage.MEASURE: Stage.ERRORS_OUTPUT,
        # Stage.MEASURE: Stage.END_MEASURE,
        # Stage.END_MEASURE: Stage.START_FLASH,
        # Stage.END_MEASURE: Stage.NEXT_MEASURE,
        Stage.ERRORS_OUTPUT: Stage.SET_CALIBRATOR_CONFIG,
        Stage.START_FLASH: Stage.FLASH_TO_CALIBRATOR,
        Stage.FLASH_TO_CALIBRATOR: Stage.NEXT_MEASURE,
        # Stage.NEXT_MEASURE: Stage.GET_CONFIGS,
        # Stage.NEXT_MEASURE: Stage.RESET_CALIBRATOR_CONFIG,
        Stage.MEASURE_DONE: Stage.REST,
    }

    SIGNAL_TO_MEASURE_TYPE = {
        (clb.SignalType.ACV, CellConfig.Meter.VOLTS): multimeters.MeasureType.tm_volt_ac,
        (clb.SignalType.ACI, CellConfig.Meter.VOLTS): multimeters.MeasureType.tm_volt_ac,
        (clb.SignalType.ACI, CellConfig.Meter.AMPERES): multimeters.MeasureType.tm_current_ac,
        (clb.SignalType.DCV, CellConfig.Meter.VOLTS): multimeters.MeasureType.tm_volt_dc,
        (clb.SignalType.DCI, CellConfig.Meter.VOLTS): multimeters.MeasureType.tm_volt_dc,
        (clb.SignalType.DCI, CellConfig.Meter.AMPERES): multimeters.MeasureType.tm_current_dc,
    }

    single_measure_started = QtCore.pyqtSignal()
    single_measure_done = QtCore.pyqtSignal()
    all_measures_done = QtCore.pyqtSignal(list)

    verify_flash_done = QtCore.pyqtSignal()

    def __init__(self, a_calibrator: ClbDrv, a_netvars: NetworkVariables, a_measure_manager: MeasureManager,
                 a_settings: QtSettings, a_parent=None):
        super().__init__(a_parent)

        self.calibrator = a_calibrator
        self.netvars = a_netvars
        self.settings = a_settings
        self.measure_manager = a_measure_manager

        self.measure_iterator: Union[None, MeasureIterator] = None
        self.current_cell_position: Union[None, MeasureIterator.CellPosition] = None
        self.current_measure_parameters: Union[None, MeasureParameters] = None
        self.current_config: Union[None, CellConfig] = None

        self.read_clb_variables_timer = utils.Timer(1)
        self.read_clb_variables_timer.start()
        self.extra_variables: List[ExtraVariable] = []

        self.current_amplitude = 0
        self.current_frequency = clb.MIN_FREQUENCY
        self.current_try = 0

        self.current_cell_is_the_last_in_table = False

        self.auto_flash_to_calibrator = False
        self.flash_current_measure = False

        self.calibrator_hold_ready_timer = utils.Timer(0)
        self.calibrator_not_ready_message_time = utils.Timer(20)
        self.measure_duration_timer = utils.Timer(0)

        self.scheme_control = None
        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

        self.start_time_point: Union[None, float] = None

        self.next_error_index = 0
        self.wait_error_clear_timer = utils.Timer(2)

        self.y_out = 0
        self.y_out_network_variable = self.netvars.fast_adc_slow
        self.y_out_network_variable_name = ""

        self.measure_errors = []

        self.out_filter_take_sample_timer = utils.Timer(0.1)
        self.calibrator_out_filter = metrology.MovingAverage(a_window_size=0)
        self.multimeter_out_filter = metrology.MovingAverage(a_window_size=0)

        self.calibrator_signal_off_timer = utils.Timer(2)
        self.wait_scheme_settle_down_timer = utils.Timer(1)

        self.__started = False

        self.correction_flasher = CorrectionFlasher()
        self.correction_flasher_started = False

        self.multimeter: Union[None, multimeters.MultimeterBase] = None
        self.first_multimeter_connect = True
        self.current_measure_type = None

        self.__stage = MeasureConductor.Stage.REST
        self.__prev_stage = self.__stage

    def __del__(self):
        print("MeasureConductor deleted")

    def reset(self):
        self.measure_iterator = None
        self.current_cell_position = None
        self.current_measure_parameters = None
        self.current_config = None
        self.__started = False
        self.current_amplitude = 0
        self.current_frequency = clb.MIN_FREQUENCY
        self.current_try = 0

        self.current_cell_is_the_last_in_table = False

        self.auto_flash_to_calibrator = False
        self.flash_current_measure = False

        self.calibrator_hold_ready_timer.stop()
        self.measure_duration_timer.stop()
        self.extra_variables.clear()

        if self.multimeter is not None:
            self.multimeter.disconnect()
        self.multimeter = None
        self.first_multimeter_connect = True
        self.current_measure_type = None

        self.scheme_control = self.measure_manager.get_scheme()
        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

        self.start_time_point = None

        self.calibrator_signal_off_timer.stop()
        self.wait_scheme_settle_down_timer.stop()

    def start(self, a_measure_iterator: MeasureIterator, a_auto_flash_to_calibrator):
        assert a_measure_iterator is not None, "Итератор не инициализирован!"
        self.reset()
        # Не сбрасывается в self.reset(), потому что в состоянии MEASURE_DONE сначала вызывается
        # reset(), а потом вызывается сигнал, в котором передаются ошибки
        self.measure_errors = []
        self.measure_iterator = a_measure_iterator
        self.auto_flash_to_calibrator = a_auto_flash_to_calibrator
        self.__started = True
        self.__stage = MeasureConductor.Stage.CONNECT_TO_CALIBRATOR

    def stop(self):
        if self.is_started():
            if self.current_cell_position is not None:
                measure_result = self.calculate_result()
                self.measure_manager.finalize_measure(*self.current_cell_position, measure_result)

            if self.correction_flasher.is_started():
                self.correction_flasher.stop()
            self.__started = False
            self.__stage = MeasureConductor.Stage.RESET_CALIBRATOR_CONFIG

    def is_started(self):
        return self.__started

    def is_correction_flash_verify_started(self):
        return self.correction_flasher.is_started()

    def get_flash_progress(self) -> Tuple[float, float]:
        return self.correction_flasher.get_progress()

    def get_current_cell_time_passed(self):
        if self.__started:
            return self.calibrator_hold_ready_timer.time_passed() + self.measure_duration_timer.time_passed()
        else:
            return 0

    def get_current_cell_time_duration(self):
        if self.__started:
            return self.current_config.measure_delay + self.current_config.measure_time
        else:
            return 1

    def __retry(self):
        self.current_try += 1
        logging.warning(f"Произошел сбой. Попытка:{self.current_try}/"
                        f"{self.current_config.additional_parameters.retry_count}")

        self.start_time_point = None
        # stop() чтобы таймеры возвращали верное значение time_passed()
        self.calibrator_hold_ready_timer.stop()
        self.measure_duration_timer.stop()

        self.next_error_index = 0
        self.netvars.error_index.set(self.next_error_index)

        self.wait_error_clear_timer.stop()
        self.__stage = MeasureConductor.Stage.ERRORS_OUTPUT

    @utils.exception_decorator
    def tick(self):
        self.correction_flasher.tick()

        if self.scheme_control is not None:
            self.scheme_control.tick()

        if self.multimeter is not None:
            self.multimeter.tick()

        if self.correction_flasher_started != self.correction_flasher.is_started():
            self.correction_flasher_started = self.correction_flasher.is_started()

            if not self.correction_flasher_started:
                if not self.is_started():
                    # Оповещает главное окно, когда прошивка запущена вручную
                    self.verify_flash_done.emit()

        if self.__prev_stage != self.__stage:
            self.__prev_stage = self.__stage
            if self.__stage in MeasureConductor.STAGE_IN_MESSAGE:
                msg, log_level = MeasureConductor.STAGE_IN_MESSAGE[self.__stage]
                logging.log(log_level, msg)

        if self.__stage == MeasureConductor.Stage.REST:
            pass

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_CALIBRATOR:
            if self.calibrator.state != clb.State.DISCONNECTED:
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.error("Калибратор не подключен, измерение остановлено")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_METER:
            self.multimeter = self.measure_manager.get_meter()

            # Паранойя, чтобы не началось измерение с неправильным типом измерителя
            self.multimeter.disconnect()

            if self.multimeter.connect(multimeters.MeasureType.tm_value):
                self.first_multimeter_connect = True
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.error("Не удалось подключиться к мультиметру. Измерение остановлено")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_SCHEME:
            self.scheme_control = self.measure_manager.get_scheme()

            if self.scheme_control.connect():
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.error("Не удалось подключиться к схеме (FTDI), измерение остановлено")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.GET_CONFIGS:
            assert self.measure_iterator is not None, "Итератор не инициализирован!"

            self.current_cell_position = self.measure_iterator.get()

            if self.settings.switch_to_active_cell:
                self.measure_manager.set_active_cell(self.current_cell_position)

            self.current_measure_parameters = \
                self.measure_manager.get_measure_parameters(self.current_cell_position.measure_name)
            self.current_config = self.measure_manager.get_cell_config(*self.current_cell_position)

            self.current_amplitude = self.measure_manager.get_amplitude(self.current_cell_position.measure_name,
                                                                        self.current_cell_position.row)
            self.current_frequency = self.measure_manager.get_frequency(self.current_cell_position.measure_name,
                                                                        self.current_cell_position.column)
            self.current_try = 0

            self.extra_variables.clear()
            for extra_parameter in self.current_config.extra_parameters:
                variable_info = VariableInfo(a_index=extra_parameter.index, a_bit_index=extra_parameter.bit_index,
                                             a_type=extra_parameter.type)

                buffered_variable = BufferedVariable(a_variable_info=variable_info, a_calibrator=self.calibrator,
                                                     a_buffer_delay_s=0)

                self.extra_variables.append(ExtraVariable(buffered_variable=buffered_variable,
                                                          work_value=extra_parameter.work_value,
                                                          default_value=extra_parameter.default_value))

            if clb.is_dc_signal[self.current_measure_parameters.signal_type]:
                self.y_out_network_variable = self.netvars.final_stabilizer_dac_dc_level
                self.y_out_network_variable_name = "final_stabilizer_dac_dc_level"
            else:
                self.y_out_network_variable = self.netvars.fast_adc_slow
                self.y_out_network_variable_name = "fast_adc_slow"
            self.measure_manager.set_clb_variable_name(*self.current_cell_position,
                                                       self.y_out_network_variable_name)

            self.current_cell_is_the_last_in_table = self.measure_iterator.is_the_last_cell_in_table()

            self.flash_current_measure = self.auto_flash_to_calibrator and \
                                         self.current_cell_is_the_last_in_table and \
                                         self.current_measure_parameters.flash_after_finish

            try:
                self.current_measure_type = MeasureConductor.SIGNAL_TO_MEASURE_TYPE[
                    (self.current_measure_parameters.signal_type, self.current_config.meter)]
            except KeyError:
                self.current_measure_type = None

            self.log_measure_info()

            if self.current_config.verify_scheme(self.current_measure_parameters.signal_type):
                if self.current_measure_type is not None:
                    max_amplitude = scheme_lut.get_max_amplitude(self.current_measure_parameters.signal_type,
                                                                 self.current_config.coil, self.current_config.divider,
                                                                 self.current_config.meter)

                    if abs(self.current_amplitude) <= max_amplitude:
                        self.measure_manager.reset_measure(*self.current_cell_position)
                        self.single_measure_started.emit()

                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
                    else:
                        logging.error(f'Амплитуда "{self.current_amplitude}" слишком высока для данной схемы '
                                      f'подключения. Максимальная амплитуда: "{max_amplitude}". Измерение остановлено')
                        self.stop()
                else:
                    logging.critical("Ошибка в логике программы. Не удалось определить тип измерения")
                    self.stop()
            else:
                logging.critical("Ошибка в логике программы. Невалидная схема подключения ячейки")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.RESET_CALIBRATOR_CONFIG:
            # Чтобы не читать с калибратора с периодом основного тика программы
            if self.read_clb_variables_timer.check():
                self.read_clb_variables_timer.start()

                if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, False):
                    if self.set_extra_variables(CellConfig.ExtraParameterState.DEFAULT_VALUE):
                        self.calibrator_signal_off_timer.start()
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_CALIBRATOR_RESET:
            if self.calibrator_signal_off_timer.check():
                self.calibrator_signal_off_timer.stop()

                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_METER_CONFIG:
            assert not (self.__started and self.multimeter is None), \
                "Измерение запущено, но мультиметр не инициализирован!"
            if self.multimeter is None or not self.multimeter.is_connected() or \
                    self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_SCHEME_CONFIG:
            if self.need_to_reset_scheme:
                if self.scheme_control.reset():
                    self.need_to_reset_scheme = False
                else:
                    logging.error("Не удалось сбросить схему (FTDI), измерение остановлено")
                    self.stop()
                    # Иначе будет бесконечная рекурсия в автомате
                    self.__stage = MeasureConductor.Stage.MEASURE_DONE

            elif self.scheme_control.ready():
                self.need_to_reset_scheme = True

                if self.is_started():
                    self.__stage = MeasureConductor.Stage.SET_METER_MEASURE_TYPE
                else:
                    self.__stage = MeasureConductor.Stage.MEASURE_DONE
####################################################################################################
        elif self.__stage == MeasureConductor.Stage.SET_METER_MEASURE_TYPE:
            if self.multimeter.is_connected():
                assert self.current_config.coefficient != 0, \
                    "Коэффициент преобразования не может быть равен нулю!"

                if self.current_config.additional_parameters.manual_range_enabled:
                    range_ = self.current_config.additional_parameters.manual_range_value
                else:
                    range_ = abs(self.current_amplitude) / self.current_config.coefficient

                if self.multimeter.set_range(self.current_measure_type, range_):
                    self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
                else:
                    logging.error(f"Не удалось установить тип измерения и диапазон мультиметра."
                                  f"Измерение остановлено")
                    self.stop()
            else:
                logging.error(f"Мультиметр не подключен на этапе {self.__stage.name}! "
                              f"Измерение остановлено")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.WAIT_METER_MEASURE_TYPE:
            if self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                if self.first_multimeter_connect:
                    if self.multimeter.start_measure():
                        self.first_multimeter_connect = False
                        self.__stage = MeasureConductor.Stage.METER_TEST_MEASURE
                    else:
                        logging.error("Не удалось начать тестовое измерение. Измерение остановлено")
                        self.stop()
                else:
                    self.__stage = MeasureConductor.Stage.SET_METER_CONFIG

        elif self.__stage == MeasureConductor.Stage.METER_TEST_MEASURE:
            if self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                value = self.multimeter.get_measured_value()
                logging.debug(f"Результат тестового измерения: {value}")

                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_METER_CONFIG:
            self.multimeter.set_config(self.current_config.meter_config_string)

            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_METER_CONFIG:
            if self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                logging.info(f"Конфигурация мультиметра: {self.multimeter.get_range()};"
                             f"{self.current_config.meter_config_string}")

                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
####################################################################################################
        elif self.__stage == MeasureConductor.Stage.SET_SCHEME_CONFIG:
            if self.need_to_set_scheme:
                if self.scheme_control.set_up(a_coil=self.current_config.coil, a_divider=self.current_config.divider,
                                              a_meter=self.current_config.meter):
                    self.need_to_set_scheme = False
                else:
                    logging.error("Не удалось установить схему, измерение остановлено")
                    self.stop()
            else:
                if self.scheme_control.ready():
                    self.need_to_set_scheme = True
                    self.wait_scheme_settle_down_timer.start()
                    self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_SCHEME_SETTLE_DOWN:
            if self.wait_scheme_settle_down_timer.check():
                self.wait_scheme_settle_down_timer.stop()
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_CALIBRATOR_CONFIG:
            if self.netvars.error_occurred.get():
                self.__retry()

            # Чтобы не читать с калибратора с периодом основного тика программы
            if self.read_clb_variables_timer.check():
                self.read_clb_variables_timer.start()

                variables_ready = []

                ready = clb_assists.guaranteed_set_signal_type(self.netvars,
                                                               self.current_measure_parameters.signal_type)
                variables_ready.append(ready)

                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.reference_amplitude,
                                                                     abs(self.current_amplitude))
                variables_ready.append(ready)

                if clb.is_ac_signal[self.current_measure_parameters.signal_type]:
                    ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.frequency, self.current_frequency)
                    variables_ready.append(ready)

                enable_correction = self.current_measure_parameters.enable_correction
                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.ui_correct_off, not enable_correction)
                variables_ready.append(ready)

                # На Agilent лучше не подавать инверсный сигнал
                if clb.is_dc_signal[self.current_measure_parameters.signal_type]:
                    if self.current_amplitude >= 0:
                        ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.reverse, False)
                    else:
                        ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.reverse, True)

                variables_ready.append(ready)

                ready = self.set_extra_variables(CellConfig.ExtraParameterState.WORK_VALUE)
                variables_ready.append(ready)

                if all(variables_ready):
                    if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, True):
                        logging.info(f"Ожидание выхода калибратора на режим... ({self.current_config.measure_delay} с)")
                        # Сигнал включен, начинаем измерение
                        self.calibrator_hold_ready_timer.start(self.current_config.measure_delay)
                        self.calibrator_not_ready_message_time.start()
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_CALIBRATOR_READY:
            if self.calibrator.state == clb.State.STOPPED or self.netvars.error_occurred.get():
                self.__retry()

            elif not self.calibrator_hold_ready_timer.check():
                if self.calibrator.state != clb.State.READY:
                    self.calibrator_hold_ready_timer.start()

                    if self.calibrator_not_ready_message_time.check():
                        self.calibrator_not_ready_message_time.start()
                        logging.warning("Калибратор вышел из режима ГОТОВ!")
            else:
                self.measure_duration_timer.start(self.current_config.measure_time)

                self.out_filter_take_sample_timer.start(self.current_config.additional_parameters.filter_sampling_time)
                self.calibrator_out_filter.reset()
                self.multimeter_out_filter.reset()

                self.multimeter.start_measure()

                logging.info(f"Измерение... ({self.current_config.measure_time} с)")
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE:
            if self.calibrator.state == clb.State.STOPPED or self.netvars.error_occurred.get():
                self.__retry()

            else:
                time_of_measure = perf_counter()
                if self.start_time_point is None:
                    self.start_time_point = time_of_measure
                    time = 0
                else:
                    time = time_of_measure - self.start_time_point

                if self.out_filter_take_sample_timer.check():
                    self.out_filter_take_sample_timer.start()

                    clb_value = self.y_out_network_variable.get()
                    if clb_value == 0:
                        logging.warning(f"С калибратора было считано значение "
                                        f"{self.y_out_network_variable_name} = 0. "
                                        f"Это значение не будет учтено")
                        self.measure_errors.append("С калибратора считано значение 0")
                    else:
                        self.add_new_clb_value(clb_value, time)

                if self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                    measured = self.multimeter.get_measured_value()

                    self.add_new_measured_value(measured, time)

                    if not self.measure_duration_timer.check():
                        self.multimeter.start_measure()
                    else:
                        measure_result = self.calculate_result()
                        self.measure_manager.finalize_measure(*self.current_cell_position, measure_result)

                        if self.current_cell_is_the_last_in_table:
                            self.measure_manager.update_measure_status(self.current_cell_position.measure_name)

                        self.start_time_point = None
                        # stop() чтобы таймеры возвращали верное значение time_passed()
                        self.calibrator_hold_ready_timer.stop()
                        self.measure_duration_timer.stop()
                        self.single_measure_done.emit()

                        self.__stage = MeasureConductor.Stage.END_MEASURE

        elif self.__stage == MeasureConductor.Stage.ERRORS_OUTPUT:
            if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, False):
                errors_output_done = False
                if not self.wait_error_clear_timer.started():
                    if self.netvars.error_count.get() > 0:
                        error_index = self.netvars.error_index.get()
                        error_count = self.netvars.error_count.get()

                        if self.next_error_index == error_index:
                            error_code = self.netvars.error_code.get()
                            logging.error(f"Ошибка №{error_index + 1}: "
                                          f"Код {error_code}. {clb.error_code_to_message[error_code]}.")

                            next_error_index = error_index + 1
                            if next_error_index < error_count:
                                self.next_error_index = next_error_index
                                self.netvars.error_index.set(next_error_index)
                            else:
                                errors_output_done = True
                    else:
                        errors_output_done = True

                if errors_output_done:
                    self.next_error_index = 0
                    self.netvars.clear_error_occurred_status.set(1)
                    self.wait_error_clear_timer.start()

                if self.wait_error_clear_timer.check():
                    if self.current_try >= self.current_config.additional_parameters.retry_count:
                        logging.error(f"Попытки закончились. Измерение прервано.")
                        self.stop()
                    else:
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.END_MEASURE:
            if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, False):
                if self.set_extra_variables(CellConfig.ExtraParameterState.DEFAULT_VALUE):
                    if self.flash_current_measure:
                        self.__stage = MeasureConductor.Stage.START_FLASH
                    else:
                        self.__stage = MeasureConductor.Stage.NEXT_MEASURE

        elif self.__stage == MeasureConductor.Stage.START_FLASH:
            if not self.start_flash([self.current_cell_position.measure_name]):
                logging.warning("ВНИМАНИЕ! Прошивка не была произведена из-за неверных данных")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.FLASH_TO_CALIBRATOR:
            if not self.correction_flasher.is_started():
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.NEXT_MEASURE:
            self.measure_iterator.next()
            cell_position = self.measure_iterator.get()

            if cell_position is not None:
                self.__stage = MeasureConductor.Stage.GET_CONFIGS
            else:
                self.__started = False
                self.__stage = MeasureConductor.Stage.RESET_CALIBRATOR_CONFIG

        elif self.__stage == MeasureConductor.Stage.MEASURE_DONE:
            self.reset()
            self.all_measures_done.emit(self.measure_errors)
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

    def set_extra_variables(self, a_state: CellConfig.ExtraParameterState):
        variables_ready = []
        for variable in self.extra_variables:
            value = variable.default_value if a_state == CellConfig.ExtraParameterState.DEFAULT_VALUE else \
                variable.work_value
            ready = clb_assists.guaranteed_buffered_variable_set(variable.buffered_variable, value)
            variables_ready.append(ready)
        return all(variables_ready)

    def log_measure_info(self):
        signal_type = self.current_measure_parameters.signal_type
        frequency = utils.float_to_string(self.current_frequency)
        frequency_str = f"Частота: {frequency} Гц" if clb.is_ac_signal[signal_type] else f"Y: {frequency}"

        logging.info(
            f"Параметры текущего измерения ({self.current_cell_position.measure_name}). "
            f"Сигнал: {clb.signal_type_to_text_short[signal_type]} ({clb.signal_type_to_text[signal_type]}). "
            f"Амплитуда: {utils.float_to_string(self.current_amplitude)} "
            f"{clb.signal_type_to_units[signal_type]}. {frequency_str}. "
            f"Катушка: {self.current_config.coil.name}, "
            f"делитель: {self.current_config.divider.name}, "
            f"измеритель: {self.current_config.meter.name}"
        )

    def add_new_measured_value(self, a_measured_value: float, a_time: float):
        out_measured = a_measured_value * self.current_config.coefficient
        self.multimeter_out_filter.add(out_measured)
        self.measure_manager.add_measured_value(*self.current_cell_position, out_measured, a_time)

    def add_new_clb_value(self, a_clb_value: float, a_time: float):
        self.calibrator_out_filter.add(a_clb_value)
        self.measure_manager.add_clb_value(*self.current_cell_position, a_clb_value, a_time)

    def calculate_result(self):
        calibrator_out = self.calibrator_out_filter.get()
        multimeter_out = self.multimeter_out_filter.get()
        result = multimeter_out

        if self.current_config.consider_output_value:
            if calibrator_out == 0:
                logging.warning("Ошибка, выходное значение с устройства равно нулю и не будет учтено")
            elif multimeter_out == 0:
                logging.warning("Ошибка, с мультиметра не было считано ни одного значения")
            else:
                result = multimeter_out / calibrator_out * self.current_amplitude

                logging.info(f"Результат измерения = multimeter_out / "
                             f"{self.y_out_network_variable_name} * setpoint = "
                             f"{multimeter_out:.9f} / "
                             f"{calibrator_out:.9f} * {self.current_amplitude:.9f} = {result:.9f}")

        return result

    def start_flash(self, a_measures_to_flash: List[str], amplitude_of_cell_to_flash=None):
        data_to_flash = self.get_data_to_flash_verify(a_measures_to_flash, amplitude_of_cell_to_flash)
        if data_to_flash:
            return self.correction_flasher.start(data_to_flash, amplitude_of_cell_to_flash,
                                                 CorrectionFlasher.Action.WRITE, self.calibrator.get_mxdata_address())
        else:
            return False

    def start_verify(self, a_measures_to_flash: List[str], amplitude_of_cell_to_flash=None):
        data_to_flash = self.get_data_to_flash_verify(a_measures_to_flash, amplitude_of_cell_to_flash)
        if data_to_flash:
            return self.correction_flasher.start(data_to_flash, amplitude_of_cell_to_flash,
                                                 CorrectionFlasher.Action.READ, self.calibrator.get_mxdata_address())
        else:
            return False

    def start_read_correction_to_tables(self, a_measures_to_flash: List[str]):
        flash_data_list = []
        for measure_name in a_measures_to_flash:
            measure_params = self.measure_manager.get_measure_parameters(measure_name)
            if measure_params.flash_after_finish:
                for flash_table_row in measure_params.flash_table:
                    flash_data_list.append(CorrectionFlasher.FlashData(diapason_name=measure_name,
                                                                       eeprom_offset=flash_table_row.eeprom_offset,
                                                                       free_space=0, x_points=[], y_points=[],
                                                                       coef_points=[]))
            else:
                logging.warning(f'Измерение "{measure_name}" не предназначено для прошивки и считано не будет')

        return self.correction_flasher.start_read_by_flash_data(flash_data_list, self.calibrator.get_mxdata_address())

    def get_correction_tables(self) -> Dict[str, Tuple]:
        read_data: Dict[str, List[Tuple[List, List, List]]] = self.correction_flasher.get_read_data()

        number = 0
        correction_tables = {}
        for idx, (name, data) in enumerate(read_data.items()):
            logging.debug(name)
            united_numbers = []

            prev_x_points = []
            y_united = []
            coefs_united = []

            # Объединяем коррекции, у которых совпадает имя и x_points в одну таблицу
            for sub_idx, (x_points, y_points, coefs) in enumerate(data):
                if x_points == prev_x_points:
                    united_numbers.append(number)

                    y_united += y_points
                    coefs_united += coefs
                else:
                    if united_numbers:
                        table_name = f"[{united_numbers[0]}-{united_numbers[-1]}]. {name}"
                        correction_tables[table_name] = (prev_x_points, y_united, coefs_united)

                    united_numbers = [number]

                    prev_x_points = list(x_points)
                    y_united = list(y_points)
                    coefs_united = list(coefs)

                number += 1

                if sub_idx == len(data) - 1:
                    correction_tables[f"[{united_numbers[0]}-{united_numbers[-1]}]. {name}"] = \
                        (x_points, y_united, coefs_united)

        return correction_tables

    def get_data_to_flash_verify(self, a_measures_to_flash: List[str], amplitude_of_cell_to_flash):
        if len(a_measures_to_flash) > 1:
            assert amplitude_of_cell_to_flash is None, "Нельзя прошивать диапазон ячейки для нескольких измерений"

        data_to_flash = []
        for measure_name in a_measures_to_flash:
            measure_params = self.measure_manager.get_measure_parameters(measure_name)
            if measure_params.flash_after_finish:
                table_data: List[List[Union[None, float]]] = self.measure_manager.get_table_values(measure_name)

                if table_data:
                    if clb.is_dc_signal[measure_params.signal_type] and len(table_data[0]) == 2:
                        # Особый случай, потому что на постоянных сигналах должно быть 2 одинаковых столбца и измерять
                        # достаточно только один, а прошивать нужно оба
                        for row in table_data:
                            row.append(row[1])
                        # Заголовок столбца может быть любой, главно чтобы отличался от столбца-предка
                        table_data[0][2] = table_data[0][1] + 1

                data_to_flash.append((measure_params.flash_table, table_data))
            else:
                logging.warning(f'Измерение "{measure_name}" не предназначено для прошивки и '
                                f'прошито/верифицировано не будет')
        return data_to_flash

    def stop_flash_verify(self):
        self.correction_flasher.stop()
