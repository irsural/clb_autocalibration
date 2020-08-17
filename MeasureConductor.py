from typing import Union, List, Tuple
from collections import namedtuple
from time import perf_counter
from enum import IntEnum
import logging

from PyQt5 import QtCore

from irspy.clb.network_variables import NetworkVariables, BufferedVariable, VariableInfo
from irspy.clb import assist_functions as clb_assists
from irspy.clb import calibrator_constants as clb
from CorrectionFlasher import CorrectionFlasher
from irspy.dlls.ftdi_control import FtdiControl
from irspy.settings_ini_parser import Settings
from irspy.clb.clb_dll import ClbDrv
from irspy import metrology
from irspy import utils

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig
from MeasureIterator import MeasureIterator
from MeasureManager import MeasureManager
import allowed_schemes_lut as scheme_lut
from SchemeControl import SchemeControl, SchemeControlGag
import multimeters


ExtraVariable = namedtuple("ExtraVariable", ["buffered_variable", "work_value", "default_value"])


class MeasureConductor(QtCore.QObject):
    class Stage(IntEnum):
        REST = 0
        CONNECT_TO_CALIBRATOR = 1
        CONNECT_TO_METER = 2
        CONNECT_TO_SCHEME = 3
        GET_CONFIGS = 4
        RESET_CALIBRATOR_CONFIG = 5
        WAIT_CALIBRATOR_RESET = 6
        RESET_METER_CONFIG = 7
        RESET_SCHEME_CONFIG = 8
        SET_METER_CONFIG = 9
        METER_TEST_MEASURE = 10
        SET_METER_RANGE = 11
        SET_SCHEME_CONFIG = 12
        WAIT_SCHEME_SETTLE_DOWN = 13
        SET_CALIBRATOR_CONFIG = 14
        WAIT_CALIBRATOR_READY = 15
        MEASURE = 16
        END_MEASURE = 17
        ERRORS_OUTPUT = 18
        START_FLASH = 19
        FLASH_TO_CALIBRATOR = 20
        NEXT_MEASURE = 21
        MEASURE_DONE = 22

    STAGE_IN_MESSAGE = {
        # Stage.REST: "Измерение не проводится",
        # Stage.CONNECT_TO_CALIBRATOR: "Подключение к калибратору",
        # Stage.CONNECT_TO_METER: "Подключение к измерителю",
        # Stage.CONNECT_TO_SCHEME: "Подключение к схеме",
        # Stage.GET_CONFIGS: "Получение конфигурации",
        # Stage.RESET_CALIBRATOR_CONFIG: "Сброс параметров калибратора",
        Stage.WAIT_CALIBRATOR_RESET: "Ждем сброс калибратора...",
        # Stage.RESET_METER_CONFIG: "Сброс параметров измерителя",
        # Stage.RESET_SCHEME_CONFIG: "Сброс параметров схемы",
        # Stage.SET_METER_CONFIG: "Установка параметров измерителя",
        Stage.METER_TEST_MEASURE: "Выполняется тестовое измерение мультиметром...",
        # Stage.SET_METER_RANGE: "Установка диапазона мультиметра",
        # Stage.SET_SCHEME_CONFIG: "Установка параметров схемы",
        # Stage.WAIT_SCHEME_SETTLE_DOWN: "На всякий случай немного ждем схему...",
        Stage.SET_CALIBRATOR_CONFIG: "Установка параметров калибратора",
        # Stage.WAIT_CALIBRATOR_READY: "Ожидание выхода калибратора на режим...",
        # Stage.MEASURE: "Измерение...",
        # Stage.END_MEASURE: "Конец измерения",
        # Stage.ERRORS_OUTPUT: "Вывод ошибок",
        # Stage.START_FLASH: "Начало прошивки",
        Stage.FLASH_TO_CALIBRATOR: "Прошивка калибратора...",
        Stage.NEXT_MEASURE: "Следующее измерение",
        Stage.MEASURE_DONE: "Измерение закончено",
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
        # Stage.RESET_SCHEME_CONFIG: Stage.SET_METER_CONFIG,
        # Stage.RESET_SCHEME_CONFIG: Stage.MEASURE_DONE,
        # Stage.SET_METER_CONFIG: Stage.METER_TEST_MEASURE,
        # Stage.SET_METER_CONFIG: Stage.SET_METER_RANGE,
        Stage.METER_TEST_MEASURE: Stage.SET_METER_RANGE,
        Stage.SET_METER_RANGE: Stage.SET_SCHEME_CONFIG,
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
    all_measures_done = QtCore.pyqtSignal()

    verify_flash_done = QtCore.pyqtSignal()

    def __init__(self, a_calibrator: ClbDrv, a_netvars: NetworkVariables, a_ftdi_control: FtdiControl,
                 a_measure_manager: MeasureManager, a_settings: Settings, a_parent=None):
        super().__init__(a_parent)

        self.calibrator = a_calibrator
        self.ftdi_control = a_ftdi_control
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
        self.calibrator_not_ready_message_time = utils.Timer(10)
        self.measure_duration_timer = utils.Timer(0)

        self.scheme_control_real = SchemeControl(self.ftdi_control)
        self.scheme_control_gag = SchemeControlGag()
        self.scheme_control = self.scheme_control_real
        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

        self.start_time_point: Union[None, float] = None

        self.next_error_index = 0
        self.wait_error_clear_timer = utils.Timer(2)

        self.y_out = 0
        self.y_out_filter = metrology.ParamFilter()
        self.y_out_network_variable = self.netvars.fast_adc_slow

        self.calibrator_signal_off_timer = utils.Timer(2)
        self.wait_scheme_settle_down_timer = utils.Timer(1)

        self.__started = False

        self.correction_flasher = CorrectionFlasher()
        self.correction_flasher_started = False

        self.multimeter: Union[None, multimeters.MultimeterBase] = None
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

        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

        self.current_measure_type = None

        self.start_time_point = None

        self.calibrator_signal_off_timer.stop()
        self.wait_scheme_settle_down_timer.stop()

    def start(self, a_measure_iterator: MeasureIterator, a_auto_flash_to_calibrator):
        assert a_measure_iterator is not None, "Итератор не инициализирован!"
        self.reset()
        self.measure_iterator = a_measure_iterator
        self.auto_flash_to_calibrator = a_auto_flash_to_calibrator
        self.__started = True
        self.__stage = MeasureConductor.Stage.CONNECT_TO_CALIBRATOR

    def stop(self):
        if self.is_started():
            if self.current_cell_position is not None:
                self.measure_manager.finalize_measure(*self.current_cell_position)

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

    def set_signal_type(self, a_signal_type: clb.SignalType) -> bool:
        current_enabled = clb.signal_type_to_current_enabled[a_signal_type]
        dc_enabled = clb.signal_type_to_dc_enabled[a_signal_type]

        current_ok = clb_assists.guaranteed_buffered_variable_set(self.netvars.current_enabled, current_enabled)
        dc_ok = clb_assists.guaranteed_buffered_variable_set(self.netvars.dc_enabled, dc_enabled)

        return current_ok and dc_ok

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
        self.scheme_control.tick()
        self.correction_flasher.tick()

        if self.multimeter is not None:
            self.multimeter.tick()

        if self.calibrator.state != clb.State.DISCONNECTED:
            self.y_out_filter.add(self.y_out_network_variable.get())
            self.y_out_filter.tick()

        if self.correction_flasher_started != self.correction_flasher.is_started():
            self.correction_flasher_started = self.correction_flasher.is_started()

            if not self.correction_flasher_started:
                if not self.is_started():
                    # Оповещает главное окно, когда прошивка запущена вручную
                    self.verify_flash_done.emit()

        if self.__prev_stage != self.__stage:
            self.__prev_stage = self.__stage
            if self.__stage in MeasureConductor.STAGE_IN_MESSAGE:
                logging.debug(MeasureConductor.STAGE_IN_MESSAGE[self.__stage])

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

            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_SCHEME:
            if isinstance(self.multimeter, multimeters.MultimeterGag):
                self.scheme_control = self.scheme_control_gag
            else:
                self.scheme_control = self.scheme_control_real

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

            self.y_out_network_variable = self.netvars.final_stabilizer_dac_dc_level if \
                clb.is_dc_signal[self.current_measure_parameters.signal_type] else self.netvars.fast_adc_slow

            self.y_out_filter.stop()
            self.y_out_filter.set_sampling_time(self.current_config.additional_parameters.filter_sampling_time)
            self.y_out_filter.resize(self.current_config.additional_parameters.filter_samples_count)

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

                    if self.current_amplitude <= max_amplitude:
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
            # self.multimeter is None, когда измерение останавливается до CONNECT_TO_METER
            if self.multimeter is not None:
                if self.current_measure_type != self.multimeter.get_measure_type():
                    self.multimeter.disconnect()
            else:
                assert not self.__started, "Мультиметр не инициализирован, но измерение не остановлено!"

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
                    self.__stage = MeasureConductor.Stage.SET_METER_CONFIG
                else:
                    self.__stage = MeasureConductor.Stage.MEASURE_DONE

        elif self.__stage == MeasureConductor.Stage.SET_METER_CONFIG:
            if self.multimeter.is_connected():
                self.__stage = MeasureConductor.Stage.SET_METER_RANGE
            else:
                if self.multimeter.connect(self.current_measure_type):
                    if self.multimeter.start_measure():
                        self.__stage = MeasureConductor.Stage.METER_TEST_MEASURE
                    else:
                        logging.error("Не удалось начать тестовое измерение. Измерение остановлено")
                        self.stop()
                else:
                    logging.error("Не удалось подключиться к мультиметру. Измерение остановлено")
                    self.stop()

        elif self.__stage == MeasureConductor.Stage.METER_TEST_MEASURE:
            if self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                value = self.multimeter.get_measured_value()
                logging.debug(f"Результат тестового измерения: {value}")

                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_METER_RANGE:
            assert self.current_config.coefficient != 0, "Коэффициент преобразования не может быть равен нулю!"

            if self.current_config.additional_parameters.manual_range_enabled:
                range_ = self.current_config.additional_parameters.manual_range_value
            else:
                range_ = self.current_amplitude / self.current_config.coefficient

            self.multimeter.set_range(range_)
            logging.info(f"Диапазон: {range_}")

            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_SCHEME_CONFIG:
            if self.need_to_set_scheme:
                if self.scheme_control.set_up(a_coil=self.current_config.coil, a_divider=self.current_config.divider,
                                              a_meter=self.current_config.meter):
                    self.need_to_set_scheme = False
                else:
                    logging.error("Не удалось установить схему (FTDI), измерение остановлено")
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

                ready = self.set_signal_type(self.current_measure_parameters.signal_type)
                variables_ready.append(ready)

                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.reference_amplitude,
                                                                     self.current_amplitude)
                variables_ready.append(ready)

                if clb.is_ac_signal[self.current_measure_parameters.signal_type]:
                    ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.frequency, self.current_frequency)
                    variables_ready.append(ready)

                enable_correction = self.current_measure_parameters.enable_correction
                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.ui_correct_off, not enable_correction)
                variables_ready.append(ready)

                # На Agilent лучше не подавать инверсный сигнал
                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.reverse, False)
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
                measure_duration = self.current_config.measure_time if self.current_config.measure_time != 0 else 999999
                self.measure_duration_timer.start(measure_duration)

                self.multimeter.start_measure()

                self.y_out = self.y_out_network_variable.get()

                if self.current_config.consider_output_value and \
                        self.current_config.additional_parameters.enable_output_filtering:
                    self.y_out_filter.restart()

                logging.info(f"Измерение... ({self.current_config.measure_time} с)")
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE:
            if self.calibrator.state == clb.State.STOPPED or self.netvars.error_occurred.get():
                self.__retry()

            elif not self.measure_duration_timer.check():
                if self.multimeter.measure_status() == multimeters.MultimeterBase.MeasureStatus.SUCCESS:
                    measured = self.multimeter.get_measured_value()
                    time_of_measure = perf_counter()

                    if self.start_time_point is None:
                        self.start_time_point = time_of_measure
                        time = 0
                    else:
                        time = time_of_measure - self.start_time_point

                    self.add_new_measured_value(measured, time)

                    self.multimeter.start_measure()

                    # Лайфхак(говнокод), так будет сделано ровно одно измерение
                    if self.current_config.measure_time == 0:
                        self.measure_duration_timer.start(1e-6)
            else:
                self.measure_manager.finalize_measure(*self.current_cell_position)

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
            self.all_measures_done.emit()
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
            f"Сигнал: {clb.enum_to_signal_type_short[signal_type]} ({clb.enum_to_signal_type[signal_type]}). "
            f"Амплитуда: {utils.float_to_string(self.current_amplitude)} "
            f"{clb.signal_type_to_units[signal_type]}. {frequency_str}. "
            f"Катушка: {self.current_config.coil.name}, "
            f"делитель: {self.current_config.divider.name}, "
            f"измеритель: {self.current_config.meter.name}"
        )

    def add_new_measured_value(self, a_measured_value: float, a_time: float):
        self.y_out_filter.stop()
        if self.current_config.consider_output_value and self.current_config.additional_parameters.enable_output_filtering:
            out_on_device = self.y_out_filter.get_value()
        else:
            out_on_device = self.y_out

        out_measured = a_measured_value * self.current_config.coefficient

        if self.current_config.consider_output_value:
            if out_on_device != 0:
                out_measured = out_measured / out_on_device * self.current_amplitude
            else:
                logging.warning("Ошибка, выходное значение с устройства равно нулю и не будет учтено")

        self.measure_manager.add_measured_value(*self.current_cell_position, out_measured, a_time)

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

    def get_correction_tables(self):
        return self.correction_flasher.get_read_data()

    def get_data_to_flash_verify(self, a_measures_to_flash: List[str], amplitude_of_cell_to_flash):
        if len(a_measures_to_flash) > 1:
            assert amplitude_of_cell_to_flash is None, "Нельзя прошивать диапазон ячейки для нескольких измерений"

        data_to_flash = []
        for measure_name in a_measures_to_flash:
            measure_params = self.measure_manager.get_measure_parameters(measure_name)
            if measure_params.flash_after_finish:
                data_to_flash.append((measure_params.flash_table, self.measure_manager.get_table_values(measure_name)))
            else:
                logging.warning(f'Измерение "{measure_name}" не предназначено для прошивки и '
                                f'прошито/верифицировано не будет')
        return data_to_flash

    def stop_flash_verify(self):
        self.correction_flasher.stop()
