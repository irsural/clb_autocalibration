from typing import Union
from enum import IntEnum
import logging
import random

from PyQt5 import QtCore

from irspy.clb import calibrator_constants as clb
from irspy.dlls.ftdi_control import FtdiControl
from irspy.settings_ini_parser import Settings
from irspy.clb.network_variables import NetworkVariables, BufferedVariable, VariableInfo
from irspy.clb import assist_functions as clb_assists
from irspy.clb.clb_dll import ClbDrv
from irspy import utils

from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig
from MeasureIterator import MeasureIterator
from MeasureManager import MeasureManager


class MeasureConductor(QtCore.QObject):
    class Stage(IntEnum):
        REST = 0
        CONNECT_TO_CALIBRATOR = 1
        CONNECT_TO_METER = 2
        CONNECT_TO_SCHEME = 3
        GET_CONFIGS = 4
        RESET_METER_CONFIG = 5
        RESET_SCHEME_CONFIG = 6
        RESET_CALIBRATOR_CONFIG = 7
        SET_METER_CONFIG = 8
        SET_SCHEME_CONFIG = 9
        SET_CALIBRATOR_CONFIG = 10
        WAIT_CALIBRATOR_READY = 11
        MEASURE = 12
        FLASH_TO_CALIBRATOR = 13
        NEXT_MEASURE = 14
        MEASURE_DONE = 15

    NEXT_STAGE = {
        Stage.REST: Stage.REST,
        Stage.CONNECT_TO_CALIBRATOR: Stage.CONNECT_TO_METER,
        Stage.CONNECT_TO_METER: Stage.CONNECT_TO_SCHEME,
        Stage.CONNECT_TO_SCHEME: Stage.GET_CONFIGS,
        Stage.GET_CONFIGS: Stage.RESET_METER_CONFIG,
        Stage.RESET_METER_CONFIG: Stage.RESET_SCHEME_CONFIG,
        Stage.RESET_SCHEME_CONFIG: Stage.RESET_CALIBRATOR_CONFIG,
        # Stage.RESET_CALIBRATOR_CONFIG: Stage.SET_METER_CONFIG,
        # Stage.RESET_CALIBRATOR_CONFIG: Stage.MEASURE_DONE,
        Stage.SET_METER_CONFIG: Stage.SET_SCHEME_CONFIG,
        Stage.SET_SCHEME_CONFIG: Stage.SET_CALIBRATOR_CONFIG,
        Stage.SET_CALIBRATOR_CONFIG: Stage.WAIT_CALIBRATOR_READY,
        Stage.WAIT_CALIBRATOR_READY: Stage.MEASURE,
        # Stage.MEASURE: Stage.FLASH_TO_CALIBRATOR,
        # Stage.MEASURE: Stage.NEXT_MEASURE,
        Stage.FLASH_TO_CALIBRATOR: Stage.NEXT_MEASURE,
        # Stage.NEXT_MEASURE: Stage.GET_CONFIGS,
        # Stage.NEXT_MEASURE: Stage.RESET_METER_CONFIG,
        Stage.MEASURE_DONE: Stage.REST,
    }

    single_measure_started = QtCore.pyqtSignal()
    single_measure_done = QtCore.pyqtSignal()
    all_measures_done = QtCore.pyqtSignal()

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

        self.extra_variables = []

        self.calibrator_hold_ready_timer = utils.Timer(0)
        self.measure_duration_timer = utils.Timer(0)

        self.__started = False

        self.__stage = MeasureConductor.Stage.REST

    def __del__(self):
        print("MeasureConductor deleted")

    def reset(self):
        self.measure_iterator = None
        self.current_cell_position = None
        self.current_measure_parameters = None
        self.current_config = None
        self.__started = False
        self.calibrator_hold_ready_timer.stop()
        self.measure_duration_timer.stop()
        self.extra_variables.clear()

    def start(self, a_measure_iterator: MeasureIterator):
        assert a_measure_iterator is not None, "Итератор не инициализирован!"
        self.measure_iterator = a_measure_iterator
        self.__started = True
        self.__stage = MeasureConductor.Stage.CONNECT_TO_CALIBRATOR

    def stop(self):
        if self.is_started():
            if self.current_cell_position is not None:
                self.measure_manager.finalize_measure(*self.current_cell_position)
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

    def tick(self):
        if self.__stage == MeasureConductor.Stage.REST:
            pass

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_CALIBRATOR:
            if self.calibrator.state == clb.State.DISCONNECTED: # #################################################################################
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.warning("Калибратор не подключен, измерение остановлено")

                self.stop()

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_METER:
            logging.debug("Подключение к измерителю")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_SCHEME:
            if not self.ftdi_control.reinit(): # #################################################################################
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
            else:
                logging.warning("Не удалось подключиться к схеме (FTDI), измерение остановлено")
                self.stop()

        elif self.__stage == MeasureConductor.Stage.GET_CONFIGS:
            logging.debug("Получение конфигурации")

            assert self.measure_iterator is not None, "Итератор не инициализирован!"

            self.current_cell_position = self.measure_iterator.get()

            if self.settings.switch_to_active_cell:
                self.measure_manager.set_active_cell(self.current_cell_position)

            self.current_measure_parameters = \
                self.measure_manager.get_measure_parameters(self.current_cell_position.measure_name)
            self.current_config = self.measure_manager.get_cell_config(*self.current_cell_position)

            self.measure_manager.reset_measure(*self.current_cell_position)
            self.single_measure_started.emit()

            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_METER_CONFIG:
            logging.debug("Сброс параметров измерителя")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_SCHEME_CONFIG:
            logging.debug("Сброс параметров схемы")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_CALIBRATOR_CONFIG:
            logging.debug("Сброс параметров калибратора")

            # if clb_assists.guaranteed_buffered_variable_set()

            if self.is_started():
                self.__stage = MeasureConductor.Stage.SET_METER_CONFIG
            else:
                self.__stage = MeasureConductor.Stage.MEASURE_DONE

        elif self.__stage == MeasureConductor.Stage.SET_METER_CONFIG:
            logging.debug("Установка параметров измерителя")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_SCHEME_CONFIG:
            logging.debug("Установка параметров схемы")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_CALIBRATOR_CONFIG:
            logging.debug("Установка параметров калибратора")

            self.calibrator_hold_ready_timer.start(self.current_config.measure_delay)

            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_CALIBRATOR_READY:
            if self.calibrator_hold_ready_timer.check():
                self.measure_duration_timer.start(self.current_config.measure_time)

                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE:
            if not self.measure_duration_timer.check():
                self.measure_manager.add_measured_value(*self.current_cell_position, random.random())
            else:
                self.measure_manager.finalize_measure(*self.current_cell_position)

                # stop() чтобы таймеры возвращали верное значение time_passed()
                self.calibrator_hold_ready_timer.stop()
                self.measure_duration_timer.stop()
                self.single_measure_done.emit()

                if self.current_measure_parameters.flash_after_finish:
                    self.__stage = MeasureConductor.Stage.FLASH_TO_CALIBRATOR
                else:
                    self.__stage = MeasureConductor.Stage.NEXT_MEASURE

        elif self.__stage == MeasureConductor.Stage.FLASH_TO_CALIBRATOR:
            logging.debug("Прошивка калибратора")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.NEXT_MEASURE:
            self.measure_iterator.next()
            cell_position = self.measure_iterator.get()

            if cell_position is not None:
                logging.debug("Следующее измерение")
                self.__stage = MeasureConductor.Stage.GET_CONFIGS
            else:
                self.__started = False
                self.__stage = MeasureConductor.Stage.RESET_METER_CONFIG

        elif self.__stage == MeasureConductor.Stage.MEASURE_DONE:
            logging.debug("Измерение закончено")
            self.reset()
            self.all_measures_done.emit()
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
