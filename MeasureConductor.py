from enum import IntEnum
import logging

from MeasureManager import MeasureManager


class MeasureConductor:
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

    def __init__(self, a_measure_manager: MeasureManager):
        self.measure_manager = a_measure_manager

        self.__stage = MeasureConductor.Stage.REST

    def start(self):
        self.__stage = MeasureConductor.Stage.CONNECT_TO_METER

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
            self.__stage = MeasureConductor.NEXT_STAGE[self.__stage]

        elif self.__stage == MeasureConductor.Stage.NEXT_MEASURE:
            if False:
                logging.debug("Следующее измерение")
                self.__stage = MeasureConductor.Stage.GET_CONFIGS
            else:
                logging.debug("Измерение выполнено")
                self.__stage = MeasureConductor.Stage.REST
