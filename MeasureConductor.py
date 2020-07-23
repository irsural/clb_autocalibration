from collections import namedtuple
from typing import Union, List
from time import perf_counter
from enum import IntEnum
import logging
import random

from PyQt5 import QtCore

from irspy.clb.network_variables import NetworkVariables, BufferedVariable, VariableInfo
from irspy.clb import assist_functions as clb_assists
from irspy.clb import calibrator_constants as clb
from CorrectionFlasher import CorrectionFlasher
from irspy.dlls.ftdi_control import FtdiControl
from irspy.settings_ini_parser import Settings
from irspy.clb.clb_dll import ClbDrv
from irspy import utils

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig
from MeasureIterator import MeasureIterator
from MeasureManager import MeasureManager
from SchemeControl import SchemeControl


ExtraVariable = namedtuple("ExtraVariable", ["buffered_variable", "work_value", "default_value"])


class MeasureConductor(QtCore.QObject):
    class Stage(IntEnum):
        REST = 0
        CONNECT_TO_CALIBRATOR = 1
        CONNECT_TO_METER = 2
        CONNECT_TO_SCHEME = 3
        GET_CONFIGS = 4
        RESET_CALIBRATOR_CONFIG = 5
        RESET_METER_CONFIG = 6
        RESET_SCHEME_CONFIG = 7
        SET_METER_CONFIG = 8
        SET_SCHEME_CONFIG = 9
        SET_CALIBRATOR_CONFIG = 10
        WAIT_CALIBRATOR_READY = 11
        MEASURE = 12
        START_FLASH = 13
        FLASH_TO_CALIBRATOR = 14
        NEXT_MEASURE = 15
        MEASURE_DONE = 16

    STAGE_IN_MESSAGE = {
        Stage.REST: "Измерение не проводится",
        Stage.CONNECT_TO_CALIBRATOR: "Подключение к калибратору",
        Stage.CONNECT_TO_METER: "Подключение к измерителю",
        Stage.CONNECT_TO_SCHEME: "Подключение к схеме",
        Stage.GET_CONFIGS: "Получение конфигурации",
        Stage.RESET_CALIBRATOR_CONFIG: "Сброс параметров калибратора",
        Stage.RESET_METER_CONFIG: "Сброс параметров измерителя",
        Stage.RESET_SCHEME_CONFIG: "Сброс параметров схемы",
        Stage.SET_METER_CONFIG: "Установка параметров измерителя",
        Stage.SET_SCHEME_CONFIG: "Установка параметров схемы",
        Stage.SET_CALIBRATOR_CONFIG: "Установка параметров калибратора",
        Stage.WAIT_CALIBRATOR_READY: "Ожидание выхода калибратора на режим",
        Stage.MEASURE: "Измерение",
        Stage.START_FLASH: "Начало прошивки",
        Stage.FLASH_TO_CALIBRATOR: "Прошивка калибратора.............................................................",
        Stage.NEXT_MEASURE: "Следующее измерение",
        Stage.MEASURE_DONE: "Измерение закончено",
    }

    NEXT_STAGE = {
        Stage.REST: Stage.REST,
        Stage.CONNECT_TO_CALIBRATOR: Stage.CONNECT_TO_METER,
        Stage.CONNECT_TO_METER: Stage.CONNECT_TO_SCHEME,
        Stage.CONNECT_TO_SCHEME: Stage.GET_CONFIGS,
        Stage.GET_CONFIGS: Stage.RESET_CALIBRATOR_CONFIG,
        Stage.RESET_CALIBRATOR_CONFIG: Stage.RESET_METER_CONFIG,
        Stage.RESET_METER_CONFIG: Stage.RESET_SCHEME_CONFIG,
        # Stage.RESET_SCHEME_CONFIG: Stage.SET_METER_CONFIG,
        # Stage.RESET_SCHEME_CONFIG: Stage.MEASURE_DONE,
        Stage.SET_METER_CONFIG: Stage.SET_SCHEME_CONFIG,
        Stage.SET_SCHEME_CONFIG: Stage.SET_CALIBRATOR_CONFIG,
        Stage.SET_CALIBRATOR_CONFIG: Stage.WAIT_CALIBRATOR_READY,
        Stage.WAIT_CALIBRATOR_READY: Stage.MEASURE,
        # Stage.MEASURE: Stage.START_FLASH,
        # Stage.MEASURE: Stage.NEXT_MEASURE,
        Stage.START_FLASH: Stage.FLASH_TO_CALIBRATOR,
        Stage.FLASH_TO_CALIBRATOR: Stage.NEXT_MEASURE,
        # Stage.NEXT_MEASURE: Stage.GET_CONFIGS,
        # Stage.NEXT_MEASURE: Stage.RESET_METER_CONFIG,
        Stage.MEASURE_DONE: Stage.REST,
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

        self.auto_flash_to_calibrator = False
        self.flash_current_measure = False

        self.calibrator_hold_ready_timer = utils.Timer(0)
        self.measure_duration_timer = utils.Timer(0)

        self.scheme_control = SchemeControl(self.ftdi_control)
        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

        self.start_time_point: Union[None, float] = None

        self.__started = False

        self.correction_flasher = CorrectionFlasher()
        self.correction_flasher_started = False

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

        self.auto_flash_to_calibrator = False
        self.flash_current_measure = False

        self.calibrator_hold_ready_timer.stop()
        self.measure_duration_timer.stop()
        self.extra_variables.clear()

        self.need_to_reset_scheme = True

        self.start_time_point = None

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
            self.__stage = MeasureConductor.Stage.RESET_METER_CONFIG

    def is_started(self):
        return self.__started

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

    def tick(self):
        self.scheme_control.tick()
        self.correction_flasher.tick()

        if self.correction_flasher_started != self.correction_flasher.is_started():
            self.correction_flasher_started = self.correction_flasher.is_started()

            if not self.correction_flasher_started:
                self.verify_flash_done.emit()

        if self.__prev_stage != self.__stage:
            self.__prev_stage = self.__stage
            logging.debug(MeasureConductor.STAGE_IN_MESSAGE[self.__stage])

        if self.__stage == MeasureConductor.Stage.REST:
            pass

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_CALIBRATOR:
            if self.calibrator.state == clb.State.DISCONNECTED: # ############################################################ if not self.calibr....
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.warning("Калибратор не подключен, измерение остановлено")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_METER:
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_SCHEME:
            if self.scheme_control.is_connected() or self.scheme_control.connect():
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.warning("Не удалось подключиться к схеме (FTDI), измерение остановлено")
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

            self.extra_variables.clear()
            for extra_parameter in self.current_config.extra_parameters:
                variable_info = VariableInfo(a_index=extra_parameter.index, a_bit_index=extra_parameter.bit_index,
                                             a_type=extra_parameter.type)

                buffered_variable = BufferedVariable(a_variable_info=variable_info, a_calibrator=self.calibrator,
                                                     a_buffer_delay_s=0)

                self.extra_variables.append(ExtraVariable(buffered_variable=buffered_variable,
                                                          work_value=extra_parameter.work_value,
                                                          default_value=extra_parameter.default_value))

            self.flash_current_measure = \
                self.auto_flash_to_calibrator and self.measure_iterator.is_the_last_cell_in_table()

            if self.current_config.verify_scheme(self.current_measure_parameters.signal_type):

                self.measure_manager.reset_measure(*self.current_cell_position)
                self.single_measure_started.emit()
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.critical("Ошибка в логике программы. Невалидная схема подключения ячейки")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.RESET_CALIBRATOR_CONFIG:
            # Чтобы не читать с калибратора с периодом основного тика программы
            if self.read_clb_variables_timer.check():
                self.read_clb_variables_timer.start()

                if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, False):
                    variables_ready = []
                    for variable in self.extra_variables:
                        ready = clb_assists.guaranteed_buffered_variable_set(variable.buffered_variable,
                                                                             variable.default_value)
                        variables_ready.append(ready)

                    if not all(variables_ready): # ################################################################################# if all....
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_METER_CONFIG:
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_SCHEME_CONFIG:

            if self.need_to_reset_scheme:
                if self.scheme_control.reset():
                    self.need_to_reset_scheme = False
                else:
                    logging.warning("Не удалось сбросить схему (FTDI), измерение остановлено")
                    self.stop()
                    # Иначе будет бесконечная рекурсия в автомате
                    self.__stage = MeasureConductor.Stage.MEASURE_DONE

            elif not self.scheme_control.ready():  # ################################################################################# elif self.scheme....
                self.need_to_reset_scheme = True

                if self.is_started():
                    self.__stage = MeasureConductor.Stage.SET_METER_CONFIG
                else:
                    self.__stage = MeasureConductor.Stage.MEASURE_DONE

        elif self.__stage == MeasureConductor.Stage.SET_METER_CONFIG:
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_SCHEME_CONFIG:
            if self.need_to_set_scheme:
                if self.scheme_control.set_up(a_coil=self.current_config.coil, a_divider=self.current_config.divider,
                                              a_meter=self.current_config.meter):
                    self.need_to_set_scheme = False
                else:
                    logging.warning("Не удалось сбросить схему (FTDI), измерение остановлено")
                    self.stop()
            else:
                if self.scheme_control.ready():
                    self.need_to_set_scheme = True
                    self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_CALIBRATOR_CONFIG:
            # Чтобы не читать с калибратора с периодом основного тика программы
            if self.read_clb_variables_timer.check():
                self.read_clb_variables_timer.start()

                variables_ready = []

                ready = self.set_signal_type(self.current_measure_parameters.signal_type)
                variables_ready.append(ready)

                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.reference_amplitude,
                                                                     self.current_amplitude)
                variables_ready.append(ready)

                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.frequency, self.current_frequency)
                variables_ready.append(ready)

                enable_correction = self.current_measure_parameters.enable_correction
                ready = clb_assists.guaranteed_buffered_variable_set(self.netvars.ui_correct_off, not enable_correction)
                variables_ready.append(ready)

                for variable in self.extra_variables:
                    ready = clb_assists.guaranteed_buffered_variable_set(variable.buffered_variable,
                                                                         variable.work_value)
                    variables_ready.append(ready)

                if not all(variables_ready): # ###################################################################################### if all....
                    if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, False): # ############################### True вместо False
                        # Сигнал включен, начинаем измерение
                        self.calibrator_hold_ready_timer.start(self.current_config.measure_delay)
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_CALIBRATOR_READY:
            if not self.calibrator_hold_ready_timer.check():
                if self.calibrator.state == clb.State.READY: # ################################################################# if not self.calib....
                    logging.info("Калибратор вышел из режима ГОТОВ. Таймер готовности запущен заново.")
                    self.calibrator_hold_ready_timer.start()
            else:
                self.measure_duration_timer.start(self.current_config.measure_time)
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE:
            if not self.measure_duration_timer.check():
                lower_bound = utils.increase_by_percent(self.current_amplitude, 2)
                upper_bound = utils.decrease_by_percent(self.current_amplitude, 2)

                value = random.uniform(lower_bound, upper_bound)
                time_of_measure = perf_counter()

                if self.start_time_point is None:
                    self.start_time_point = time_of_measure
                    time = 0
                else:
                    time = time_of_measure - self.start_time_point

                self.measure_manager.add_measured_value(*self.current_cell_position, value, time)
            else:
                self.measure_manager.finalize_measure(*self.current_cell_position)

                self.start_time_point = None
                # stop() чтобы таймеры возвращали верное значение time_passed()
                self.calibrator_hold_ready_timer.stop()
                self.measure_duration_timer.stop()
                self.single_measure_done.emit()

                if self.flash_current_measure:
                    self.__stage = MeasureConductor.Stage.START_FLASH
                else:
                    self.__stage = MeasureConductor.Stage.NEXT_MEASURE

        elif self.__stage == MeasureConductor.Stage.START_FLASH:
            # self.correction_flasher.start()
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

    def start_flash(self, a_measures_to_flash: List[str], a_flash_selected_cell: bool):
        self.get_data_to_flash_verify(a_measures_to_flash, a_flash_selected_cell)
        self.correction_flasher.start(CorrectionFlasher.Action.WRITE)

    def start_verify(self, a_measures_to_flash: List[str], a_flash_selected_cell: bool):
        self.get_data_to_flash_verify(a_measures_to_flash, a_flash_selected_cell)
        self.correction_flasher.start(CorrectionFlasher.Action.READ)

    def get_data_to_flash_verify(self, a_measures_to_flash: List[str], a_flash_selected_cell: bool):
        if len(a_measures_to_flash) > 1:
            assert not a_flash_selected_cell, "Нельзя прошивать диапазон ячейки для нескольких измерений"

    def stop_flash_verify(self):
        self.correction_flasher.stop()
