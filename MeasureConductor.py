from typing import Union
from enum import IntEnum
import logging
import random

from PyQt5 import QtCore

from irspy import utils

from MeasureIterator import MeasureIterator
from edit_measure_parameters_dialog import MeasureParameters
from edit_cell_config_dialog import CellConfig
from MeasureManager import MeasureManager


class MeasureConductor(QtCore.QObject):
    class Stage(IntEnum):
        REST = 0
        CONNECT_TO_METER = 1
        CONNECT_TO_SCHEME = 2
        CONNECT_TO_CALIBRATOR = 3
        GET_CONFIGS = 4
        SET_METER_CONFIG = 5
        SET_SCHEME_CONFIG = 6
        SET_CALIBRATOR_CONFIG = 7
        WAIT_CALIBRATOR_READY = 8
        MEASURE = 9
        MEASURE_DONE = 10
        RESET_METER_CONFIG = 11
        RESET_SCHEME_CONFIG = 12
        RESET_CALIBRATOR_CONFIG = 13
        FLASH_TO_CALIBRATOR = 14
        NEXT_MEASURE = 15

    NEXT_STAGE = {
        Stage.REST: Stage.REST,
        Stage.CONNECT_TO_METER: Stage.CONNECT_TO_SCHEME,
        Stage.CONNECT_TO_SCHEME: Stage.CONNECT_TO_CALIBRATOR,
        Stage.CONNECT_TO_CALIBRATOR: Stage.GET_CONFIGS,
        Stage.GET_CONFIGS: Stage.SET_METER_CONFIG,
        Stage.SET_METER_CONFIG: Stage.SET_SCHEME_CONFIG,
        Stage.SET_SCHEME_CONFIG: Stage.SET_CALIBRATOR_CONFIG,
        Stage.SET_CALIBRATOR_CONFIG: Stage.WAIT_CALIBRATOR_READY,
        Stage.WAIT_CALIBRATOR_READY: Stage.MEASURE,
        Stage.MEASURE: Stage.MEASURE_DONE,
        Stage.MEASURE_DONE: Stage.RESET_METER_CONFIG,
        Stage.RESET_METER_CONFIG: Stage.RESET_SCHEME_CONFIG,
        Stage.RESET_SCHEME_CONFIG: Stage.RESET_CALIBRATOR_CONFIG,
        Stage.RESET_CALIBRATOR_CONFIG: Stage.FLASH_TO_CALIBRATOR,
        Stage.FLASH_TO_CALIBRATOR: Stage.NEXT_MEASURE,
    }

    measure_done = QtCore.pyqtSignal()

    def __init__(self, a_measure_manager: MeasureManager, a_parent=None):
        super().__init__(a_parent)

        self.measure_manager = a_measure_manager
        self.measure_iterator: Union[None, MeasureIterator] = None

        self.current_cell_position: Union[None, MeasureIterator.CellPosition] = None
        self.current_measure_parameters: Union[None, MeasureParameters] = None
        self.current_config: Union[None, CellConfig] = None

        self.calibrator_hold_ready_timer = utils.Timer(0)
        self.measure_duration_timer = utils.Timer(0)

        self.__stage = MeasureConductor.Stage.REST

    def reset(self):
        self.measure_iterator = None
        self.current_cell_position = None
        self.current_measure_parameters = None
        self.current_config = None

    def start(self):
        """
        Начинает измерение с первой ячейки
        """
        self.measure_iterator = self.measure_manager.get_measure_iterator()
        self.__stage = MeasureConductor.Stage.CONNECT_TO_METER

    def continue_(self):
        """
        Начинает измерение с текущей ячейкт ячейки, если ячейка не заблокирована, ищет первую заблокированную ячейку
        начиная с текущей ячейки
        """
        self.measure_iterator = self.measure_manager.get_measure_iterator_from_current()
        if self.measure_iterator is not None:
            self.__stage = MeasureConductor.Stage.CONNECT_TO_METER

    def stop(self):
        self.reset()
        self.__stage = MeasureConductor.Stage.REST

    def tick(self):
        if self.__stage == MeasureConductor.Stage.REST:
            pass

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_METER:
            logging.debug("Подключение к измерителю")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_SCHEME:
            logging.debug("Подключение к схеме")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.CONNECT_TO_CALIBRATOR:
            logging.debug("Подключение к калибратору")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.GET_CONFIGS:
            logging.debug("Получение конфигурации")

            assert self.measure_iterator is not None, "Итератор не инициализирован!"

            self.current_cell_position = self.measure_iterator.get()
            self.measure_manager.set_active_cell(self.current_cell_position)

            self.current_measure_parameters = \
                self.measure_manager.get_measure_parameters(self.current_cell_position.measure_name)
            self.current_config = self.measure_manager.get_cell_config(*self.current_cell_position)

            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

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
                self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE_DONE:
            logging.debug("Измерение выполнено")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_METER_CONFIG:
            logging.debug("Сброс параметров измерителя")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_SCHEME_CONFIG:
            logging.debug("Сброс параметров схемы")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.RESET_CALIBRATOR_CONFIG:
            logging.debug("Сброс параметров калибратора")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

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
                logging.debug("Измерение выполнено")

                self.reset()
                self.measure_done.emit()
                self.__stage = MeasureConductor.Stage.REST
