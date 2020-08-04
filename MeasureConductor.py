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
from irspy.dlls import multimeters
from irspy import utils

from edit_measure_parameters_dialog import MeasureParameters
from edit_agilent_config_dialog import AgilentConfig
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
        METER_TEST_MEASURE = 9
        SET_SCHEME_CONFIG = 10
        SET_CALIBRATOR_CONFIG = 11
        WAIT_CALIBRATOR_READY = 12
        MEASURE = 13
        ERRORS_OUTPUT = 14
        START_FLASH = 15
        FLASH_TO_CALIBRATOR = 16
        NEXT_MEASURE = 17
        MEASURE_DONE = 18

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
        Stage.METER_TEST_MEASURE: "Выполняется тестовое измерение...",
        Stage.SET_SCHEME_CONFIG: "Установка параметров схемы",
        Stage.SET_CALIBRATOR_CONFIG: "Установка параметров калибратора",
        Stage.WAIT_CALIBRATOR_READY: "Ожидание выхода калибратора на режим",
        Stage.MEASURE: "Измерение",
        Stage.ERRORS_OUTPUT: "Вывод ошибок",
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
        Stage.SET_METER_CONFIG: Stage.METER_TEST_MEASURE,
        Stage.METER_TEST_MEASURE: Stage.SET_SCHEME_CONFIG,
        Stage.SET_SCHEME_CONFIG: Stage.SET_CALIBRATOR_CONFIG,
        Stage.SET_CALIBRATOR_CONFIG: Stage.WAIT_CALIBRATOR_READY,
        Stage.WAIT_CALIBRATOR_READY: Stage.MEASURE,
        # Stage.MEASURE: Stage.START_FLASH,
        # Stage.MEASURE: Stage.NEXT_MEASURE,
        # Stage.MEASURE: Stage.ERRORS_OUTPUT,
        Stage.ERRORS_OUTPUT: Stage.SET_CALIBRATOR_CONFIG,
        Stage.START_FLASH: Stage.FLASH_TO_CALIBRATOR,
        Stage.FLASH_TO_CALIBRATOR: Stage.NEXT_MEASURE,
        # Stage.NEXT_MEASURE: Stage.GET_CONFIGS,
        # Stage.NEXT_MEASURE: Stage.RESET_CALIBRATOR_CONFIG,
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
        self.current_try = 0

        self.auto_flash_to_calibrator = False
        self.flash_current_measure = False

        self.calibrator_hold_ready_timer = utils.Timer(0)
        self.measure_duration_timer = utils.Timer(0)

        self.scheme_control = SchemeControl(self.ftdi_control)
        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

        self.start_time_point: Union[None, float] = None

        self.next_error_index = 0
        self.wait_error_clear_timer = utils.Timer(2)

        self.__started = False

        self.correction_flasher = CorrectionFlasher()
        self.correction_flasher_started = False

        self.multimeter = multimeters.Agilent3485A()

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

        self.auto_flash_to_calibrator = False
        self.flash_current_measure = False

        self.calibrator_hold_ready_timer.stop()
        self.measure_duration_timer.stop()
        self.extra_variables.clear()

        self.need_to_reset_scheme = True
        self.need_to_set_scheme = True

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
        if self.current_try < self.current_config.retry_count:
            logging.warning(f"Произошел сбой. Попытка:{self.current_try}/{self.current_config.retry_count}")

            self.start_time_point = None
            # stop() чтобы таймеры возвращали верное значение time_passed()
            self.calibrator_hold_ready_timer.stop()
            self.measure_duration_timer.stop()

            self.next_error_index = 0
            self.wait_error_clear_timer.stop()
            self.__stage = MeasureConductor.Stage.ERRORS_OUTPUT
        else:
            logging.warning(f"Произошел сбой. Попытка:{self.current_try}/{self.current_config.retry_count}. "
                            f"Попытки закончились. Измерение прервано.")
            self.stop()

    def tick(self):
        self.scheme_control.tick()
        self.correction_flasher.tick()

        if self.correction_flasher_started != self.correction_flasher.is_started():
            self.correction_flasher_started = self.correction_flasher.is_started()

            if not self.correction_flasher_started:
                if not self.is_started():
                    # Оповещает главное окно, когда прошивка запущена вручную
                    self.verify_flash_done.emit()

        if self.__prev_stage != self.__stage:
            self.__prev_stage = self.__stage
            logging.debug(MeasureConductor.STAGE_IN_MESSAGE[self.__stage])

        if self.__stage == MeasureConductor.Stage.REST:
            pass

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_CALIBRATOR:
            if self.calibrator.state != clb.State.DISCONNECTED: # ############################################################ if not self.calibr....
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

            self.flash_current_measure = self.auto_flash_to_calibrator and \
                                         self.measure_iterator.is_the_last_cell_in_table() and \
                                         self.current_measure_parameters.flash_after_finish

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

                    if all(variables_ready): # ################################################################################# if all....
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_METER_CONFIG:
            self.multimeter.disconnect()

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

            elif self.scheme_control.ready():  # ################################################################################# elif self.scheme....
                self.need_to_reset_scheme = True

                if self.is_started():
                    self.__stage = MeasureConductor.Stage.SET_METER_CONFIG
                else:
                    self.__stage = MeasureConductor.Stage.MEASURE_DONE

        elif self.__stage == MeasureConductor.Stage.SET_METER_CONFIG:
            meter_settings = self.measure_manager.get_meter_settings()
            success_connect = False
            if isinstance(meter_settings, AgilentConfig):
                if self.multimeter.connect(multimeters.MeasureType.tm_volt_dc,
                                           AgilentConfig.CONN_TYPE_TO_NAME[meter_settings.connect_type],
                                           meter_settings.gpib_index, meter_settings.gpib_address,
                                           meter_settings.com_name, meter_settings.ip_address, meter_settings.port):
                    success_connect = True
                else:
                    logging.error("Не удалось подключиться к мультиметру. Измерение остановлено")
            else:
                logging.critical("Не реализованный мультиметр. Измерение остановлено")

            if success_connect:
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                self.stop()

        elif self.__stage == MeasureConductor.Stage.METER_TEST_MEASURE:
            got_measure, value = self.multimeter.get_measured_value()
            if got_measure and value != 0:
                logging.info(f"Результат тестового измерения: {value}")
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

                for variable in self.extra_variables:
                    ready = clb_assists.guaranteed_buffered_variable_set(variable.buffered_variable,
                                                                         variable.work_value)
                    variables_ready.append(ready)

                if all(variables_ready): # ###################################################################################### if all....
                    if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, True): # ############################### True вместо False
                        # Сигнал включен, начинаем измерение
                        self.calibrator_hold_ready_timer.start(self.current_config.measure_delay)
                        self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_CALIBRATOR_READY:
            if self.calibrator.state == clb.State.STOPPED or self.netvars.error_occurred.get():
                self.__retry()

            elif not self.calibrator_hold_ready_timer.check():
                if self.calibrator.state != clb.State.READY: # ################################################################# if not self.calib....
                    # logging.info("Калибратор вышел из режима ГОТОВ. Таймер готовности запущен заново.")
                    self.calibrator_hold_ready_timer.start()
            else:
                self.measure_duration_timer.start(self.current_config.measure_time)
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE:
            if self.calibrator.state == clb.State.STOPPED or self.netvars.error_occurred.get():
                self.__retry()

            elif not self.measure_duration_timer.check():
                got_value, measured = self.multimeter.get_measured_value()
                if got_value:
                    logging.debug(f"Измерено: {measured}")
                    time_of_measure = perf_counter()

                    if self.start_time_point is None:
                        self.start_time_point = time_of_measure
                        time = 0
                    else:
                        time = time_of_measure - self.start_time_point

                    self.measure_manager.add_measured_value(*self.current_cell_position, measured, time)
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

        elif self.__stage == MeasureConductor.Stage.ERRORS_OUTPUT:
            if clb_assists.guaranteed_buffered_variable_set(self.netvars.signal_on, False):
                errors_output_done = False
                if not self.wait_error_clear_timer.started():
                    if self.netvars.error_count.get() > 0:
                        error_index = self.netvars.error_index.get()
                        error_count = self.netvars.error_count.get()

                        if self.next_error_index == error_index:
                            error_code = self.netvars.error_code.get()
                            logging.warning(f"Ошибка №{error_index + 1}: "
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
                    self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

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
