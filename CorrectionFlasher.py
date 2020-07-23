from enum import IntEnum
import logging

from irspy.dlls import mxsrlib_dll


class CorrectionFlasher():
    class Action(IntEnum):
        NONE = 0
        READ = 1
        WRITE = 2

    class Stage(IntEnum):
        REST = 0
        START = 1
        GET_DIAPASON = 2
        CHECK_INPUT_DATA = 3
        CONNECT_TO_EEPROM = 4
        SET_EEPROM_PARAMS = 5
        WAIT_EEPROM_READ = 6
        VERIFY_DATA = 7
        WRITE_TO_EEPROM = 8
        WAIT_WRITE = 9
        RESET_EEPROM = 10
        NEXT_DIAPASON = 11
        DONE = 12

    NEXT_STAGE = {
        Stage.REST: Stage.REST,
        Stage.START: Stage.GET_DIAPASON,
        Stage.GET_DIAPASON: Stage.CHECK_INPUT_DATA,
        # Stage.CHECK_INPUT_DATA: Stage.CONNECT_TO_EEPROM,
        # Stage.CHECK_INPUT_DATA: Stage.DONE,
        Stage.CONNECT_TO_EEPROM: Stage.SET_EEPROM_PARAMS,
        # Stage.SET_EEPROM_PARAMS: Stage.WAIT_EEPROM_READ,
        # Stage.SET_EEPROM_PARAMS: Stage.WRITE_TO_EEPROM,
        Stage.WAIT_EEPROM_READ: Stage.VERIFY_DATA,
        Stage.VERIFY_DATA: Stage.RESET_EEPROM,
        Stage.WRITE_TO_EEPROM: Stage.WAIT_WRITE,
        Stage.WAIT_WRITE: Stage.RESET_EEPROM,
        Stage.RESET_EEPROM: Stage.NEXT_DIAPASON,
        # Stage.NEXT_DIAPASON: Stage.GET_DIAPASON,
        # Stage.NEXT_DIAPASON: Stage.DONE,
        Stage.DONE: Stage.REST
    }

    STAGE_IN_MESSAGE = {
        Stage.REST: "Прошивка / верефикация не проводится",
        Stage.START: "Старт прошивки / верификации",
        Stage.GET_DIAPASON: "Определение диапазона",
        Stage.CHECK_INPUT_DATA: "Проверка входных данных",
        Stage.CONNECT_TO_EEPROM: "Подключение к eeprom",
        Stage.SET_EEPROM_PARAMS: "Установка параметров в eeprom",
        Stage.WAIT_EEPROM_READ: "Чтение eeprom...",
        Stage.VERIFY_DATA: "Проверка данных",
        Stage.WRITE_TO_EEPROM: "Запись в eeprom",
        Stage.WAIT_WRITE: "Ожидание записи...",
        Stage.RESET_EEPROM: "Сброс eeprom",
        Stage.NEXT_DIAPASON: "Следующий диапазон",
        Stage.DONE: "Прошивка / верификация завершена",
    }

    def __init__(self):
        super().__init__()

        self.__started = False

        self.__action = CorrectionFlasher.Action.NONE

        self.__stage = CorrectionFlasher.Stage.REST
        self.__prev_stage = CorrectionFlasher.Stage.REST

    def start_flash(self):
        self.__action = CorrectionFlasher.Action.WRITE
        self.__stage = CorrectionFlasher.Stage.START
        self.__started = True

    def start_verify(self):
        self.__action = CorrectionFlasher.Action.READ
        self.__stage = CorrectionFlasher.Stage.START
        self.__started = True

    def stop(self):
        self.__action = CorrectionFlasher.Action.NONE
        self.__stage = CorrectionFlasher.Stage.RESET_EEPROM
        self.__started = False

    def is_started(self):
        return self.__started

    def tick(self):
        if self.__prev_stage != self.__stage:
            self.__prev_stage = self.__stage

            logging.debug(CorrectionFlasher.STAGE_IN_MESSAGE[self.__stage])

            if self.__stage == CorrectionFlasher.Stage.REST:
                pass

            elif self.__stage == CorrectionFlasher.Stage.START:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.GET_DIAPASON:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.CHECK_INPUT_DATA:

                if True:
                    self.__stage = CorrectionFlasher.Stage.CONNECT_TO_EEPROM
                else:
                    self.__stage = CorrectionFlasher.Stage.DONE

            elif self.__stage == CorrectionFlasher.Stage.CONNECT_TO_EEPROM:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.SET_EEPROM_PARAMS:

                if self.__action == CorrectionFlasher.Action.READ:
                    self.__stage = CorrectionFlasher.Stage.WAIT_EEPROM_READ
                else:
                    self.__stage = CorrectionFlasher.Stage.WRITE_TO_EEPROM

            elif self.__stage == CorrectionFlasher.Stage.WAIT_EEPROM_READ:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.VERIFY_DATA:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.WRITE_TO_EEPROM:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.WAIT_WRITE:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.RESET_EEPROM:
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

            elif self.__stage == CorrectionFlasher.Stage.NEXT_DIAPASON:

                if False:
                    self.__stage = CorrectionFlasher.Stage.GET_DIAPASON
                else:
                    self.__stage = CorrectionFlasher.Stage.DONE

            elif self.__stage == CorrectionFlasher.Stage.DONE:

                self.__action = CorrectionFlasher.Action.NONE
                self.__started = False

                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]
