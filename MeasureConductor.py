from enum import IntEnum
import logging

from MeasureManager import MeasureManager


class MeasureConductor:
    class Stage(IntEnum):
        CONNECT_TO_METER = 0
        CONNECT_TO_SCHEME = 1
        CONNECT_TO_CALIBRATOR = 2
        GET_CONFIGS = 3
        SET_METER_CONFIG = 4
        SET_SCHEME_CONFIG = 5
        SET_CALIBRATOR_CONFIG = 6
        WAIT_CALIBRATOR_READY = 7
        MEASURE = 8
        MEASURE_DONE = 9
        RESET_METER_CONFIG = 10
        RESET_SCHEME_CONFIG = 11
        RESET_CALIBRATOR_CONFIG = 12
        FLASH_TO_CALIBRATOR = 13
        DONE = 14

    NEXT_STAGE = {
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
        Stage.DONE: Stage.DONE,
    }

    def __init__(self, a_measure_manager: MeasureManager):
        self.measure_manager = a_measure_manager

        self.__stage = MeasureConductor.Stage.DONE

    def start(self):
        self.__stage = MeasureConductor.Stage.CONNECT_TO_METER

    def tick(self):
        if self.__stage == MeasureConductor.Stage.CONNECT_TO_METER:
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
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_METER_CONFIG:
            logging.debug("Установка параметров измерителя")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_SCHEME_CONFIG:
            logging.debug("Установка параметров схемы")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.SET_CALIBRATOR_CONFIG:
            logging.debug("Установка параметров калибратора")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.WAIT_CALIBRATOR_READY:
            logging.debug("Ожидание выхода калибратора на режим")
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.MEASURE:
            logging.debug("Измерение")
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
            if False:
                self.__stage = MeasureConductor.Stage.GET_CONFIGS
            else:
                self.__stage = MeasureConductor.Stage.DONE

        elif self.__stage == MeasureConductor.Stage.DONE:
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]
