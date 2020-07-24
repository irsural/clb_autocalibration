from collections import namedtuple
from typing import List, Tuple, Union
from enum import IntEnum
import logging

from irspy.dlls import mxsrlib_dll

from edit_measure_parameters_dialog import FlashTableRow


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

    FlashData = namedtuple("FlashData", "eeprom_offset x_points y_points coef_points")

    def __init__(self):
        super().__init__()

        self.__started = False

        self.__flash_data: List[CorrectionFlasher.FlashData] = []

        self.__action = CorrectionFlasher.Action.NONE

        self.__stage = CorrectionFlasher.Stage.REST
        self.__prev_stage = CorrectionFlasher.Stage.REST

    def start(self, a_data_to_flash: List[Tuple], a_amplitude_of_cell_to_flash, a_action_type: Action) -> bool:
        data_ok = True
        if a_amplitude_of_cell_to_flash is not None:
            assert len(a_data_to_flash) == 1, "Для прошивки одного диапазона должна быть передана только одна таблица"
            data_ok = self.shrink_data_table(a_data_to_flash[0], a_amplitude_of_cell_to_flash)

        if data_ok and self.process_data_to_flash(a_data_to_flash):
            self.__action = a_action_type
            self.__stage = CorrectionFlasher.Stage.START
            self.__started = True
        else:
            logging.warning("Прошивка/верификация отменена.")

        return self.is_started()

    def stop(self):
        self.__action = CorrectionFlasher.Action.NONE
        self.__stage = CorrectionFlasher.Stage.RESET_EEPROM
        self.__flash_data.clear()
        self.__started = False

    def is_started(self):
        return self.__started

    @staticmethod
    def shrink_data_table(a_data_to_flash: Tuple, a_amplitude: float) -> bool:
        """
        Оставляет в таблице данных строки, соттветствующие диапазону, в который входит a_amplitude
        :param a_data_to_flash: Кортеж [Таблица прошивки, Таблица данных]
        :param a_amplitude: Амплитуда
        :return True, Если удалось найти строки в таблице для заданного диапазона, иначе False
        """
        flash_table: List[FlashTableRow] = a_data_to_flash[0]
        data_table: List[List] = a_data_to_flash[1]

        success = False

        start_amplitude = None
        end_amplitude = None
        for flash_row in flash_table:
            if flash_row.start_value <= a_amplitude <= flash_row.end_value:
                start_amplitude = flash_row.start_value
                end_amplitude = flash_row.end_value
                break

        if start_amplitude is not None:
            amplitudes = [(row_idx, data_row[0]) for row_idx, data_row in enumerate(data_table) if row_idx != 0]
            if all([amplitude is not None for _, amplitude in amplitudes]):
                rows_to_drop = []
                for row, amplitude in amplitudes:
                    if not start_amplitude <= amplitude <= end_amplitude:
                        rows_to_drop.append(row)
                # Удаляем с конца, чтобы не нарушить индексацию в списке
                for row in reversed(rows_to_drop):
                    data_table.pop(row)

                success = True
                assert len(data_table) > 1, "Должна остаться хотя бы одна строка с данными!"
            else:
                logging.warning("В таблице обнаружены ячейки без значений.")
        else:
            logging.warning("Выбранная ячейка не входит ни в один диапазон.")

        return success

    def process_data_to_flash(self, a_data_to_flash: List[Tuple]) -> bool:
        success = True
        self.__flash_data.clear()

        for data_to_flash in a_data_to_flash:
            flash_table: List[FlashTableRow] = data_to_flash[0]
            data_table: List[List] = data_to_flash[1]

            have_empty_cells = self.__empty_cells_in_table(data_table)

            if not have_empty_cells:
                flash_data = self.__get_flash_data(flash_table, data_table)
                if flash_data:
                    self.__flash_data += flash_data
                else:
                    logging.warning("Некоторые строки таблицы не входят ни в один из заданных диапазонов, "
                                    "либо входят в несколько диапазонов одновременно")
                    success = False
                    break
            else:
                logging.warning("В одной из таблиц обнаружены ячейки без значений, либо содержащие значение 0.")
                success = False
                break

        return success

    @staticmethod
    def __empty_cells_in_table(a_data_table: List[List[Union[None, float]]]):
        have_empty_cells = False
        for row_idx, data_row in enumerate(a_data_table):
            for col_idx, value in enumerate(data_row):
                if not (row_idx == 0 and col_idx == 0):
                    if value is None or value == 0:
                        have_empty_cells = True
                        break
        return have_empty_cells

    @staticmethod
    def __get_flash_data(a_flash_table: List[FlashTableRow], a_data_table: List[List[Union[None, float]]]) -> List[FlashData]:
        flash_data = []
        amplitudes = [(row_idx, data_row[0]) for row_idx, data_row in enumerate(a_data_table) if row_idx != 0]

        for flash_row in a_flash_table:
            x_points = []
            y_points = [value for col_idx, value in enumerate(a_data_table[0]) if col_idx != 0]
            coef_points = []

            for row_idx, amplitude in amplitudes:

                if flash_row.start_value <= amplitude <= flash_row.end_value:
                    x_points.append(amplitude)

                    for col_idx, cell_value in enumerate(a_data_table[row_idx]):
                        if col_idx != 0:
                            # coef_points.append(cell_value)
                            coef_points.append(cell_value / amplitude)
            if x_points:
                flash_data.append(CorrectionFlasher.FlashData(eeprom_offset=flash_row.eeprom_offset, x_points=x_points,
                                                              y_points=y_points, coef_points=coef_points))

        x_count = sum([len(f_data.x_points) for f_data in flash_data])
        if x_count != len(a_data_table) - 1:
            # Это значит, что некоторые амлитуды не вощли ни в один диапазон
            flash_data.clear()

        return flash_data

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
