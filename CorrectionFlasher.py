from collections import namedtuple, defaultdict
from typing import List, Tuple, Union, Dict
from array import array
from enum import IntEnum
import logging

from irspy.dlls import mxsrlib_dll
from irspy import utils

from edit_measure_parameters_dialog import FlashTableRow


class CorrectionFlasher:
    class Action(IntEnum):
        NONE = 0
        READ = 1
        WRITE = 2

    class Stage(IntEnum):
        REST = 0
        SET_UP_FUNNEL = 1
        CONNECT_TO_FUNNEL = 2
        READ_WRITE_START = 3
        WAIT_EEPROM_READ_METADATA = 4
        WAIT_EEPROM_READ_DATA = 5
        VERIFY_DATA = 6
        WRITE_TO_EEPROM = 7
        WAIT_WRITE = 8
        RESET_EEPROM = 9
        NEXT_DIAPASON = 10
        DONE = 11

    NEXT_STAGE = {
        Stage.REST: Stage.REST,
        # Stage.RESET_EEPROM: Stage.SET_UP_FUNNEL,
        # Stage.RESET_EEPROM: Stage.DONE,
        Stage.SET_UP_FUNNEL: Stage.CONNECT_TO_FUNNEL,
        Stage.CONNECT_TO_FUNNEL: Stage.READ_WRITE_START,
        # Stage.READ_WRITE_START: Stage.WAIT_EEPROM_READ_METADATA,
        # Stage.READ_WRITE_START: Stage.WAIT_EEPROM_READ_DATA,
        # Stage.READ_WRITE_START: Stage.WRITE_TO_EEPROM,
        Stage.WAIT_EEPROM_READ_METADATA: Stage.SET_UP_FUNNEL,
        Stage.WAIT_EEPROM_READ_DATA: Stage.VERIFY_DATA,
        Stage.VERIFY_DATA: Stage.NEXT_DIAPASON,
        Stage.WRITE_TO_EEPROM: Stage.WAIT_WRITE,
        Stage.WAIT_WRITE: Stage.NEXT_DIAPASON,
        Stage.NEXT_DIAPASON: Stage.RESET_EEPROM,
        Stage.DONE: Stage.REST
    }

    STAGE_IN_MESSAGE = {
        # Stage.REST: "Прошивка / верефикация не проводится",
        # Stage.SET_UP_FUNNEL: "Создание воронки",
        # Stage.CONNECT_TO_FUNNEL: "Подключение к eeprom",
        # Stage.READ_WRITE_START: "Установка параметров в eeprom",
        # Stage.WAIT_EEPROM_READ_METADATA: "Чтение метаданных...",
        Stage.WAIT_EEPROM_READ_DATA: "Чтение данных...",
        # Stage.VERIFY_DATA: "Проверка данных",
        # Stage.WRITE_TO_EEPROM: "Запись в eeprom",
        Stage.WAIT_WRITE: "Ожидание записи...",
        # Stage.RESET_EEPROM: "Сброс eeprom",
        # Stage.NEXT_DIAPASON: "Следующий диапазон",
        Stage.DONE: "Прошивка / верификация завершена",
    }

    FUNNEL_MXDATA_OFFSET = 1044
    FlashData = namedtuple("FlashData", "diapason_name eeprom_offset free_space x_points y_points coef_points")

    def __init__(self):
        super().__init__()

        self.__started = False

        self.__flash_data: List[CorrectionFlasher.FlashData] = []
        self.__current_flash_data_idx = 0
        self.__current_flash_data = None

        self.__action = CorrectionFlasher.Action.NONE
        self.__mxdata = None

        self.__funnel_client = mxsrlib_dll.FunnelClient()
        self.__correct_map = mxsrlib_dll.CorrectMap()

        self.__metadata_are_read = False

        self.__progress = 0

        self.__save_instead_of_verify = False
        self.__read_data: Dict[str, List[Tuple[List, List, List]]] = defaultdict(list)

        self.__stage = CorrectionFlasher.Stage.REST
        self.__prev_stage = CorrectionFlasher.Stage.REST

    def reset(self):
        self.__current_flash_data_idx = 0
        self.__current_flash_data = None
        self.__action = CorrectionFlasher.Action.NONE
        self.__mxdata = None
        self.__stage = CorrectionFlasher.Stage.RESET_EEPROM
        self.__metadata_are_read = False
        self.__progress = 0
        self.__save_instead_of_verify = False
        self.__read_data = defaultdict(list)

    def start(self, a_data_to_flash: List[Tuple], a_amplitude_of_cell_to_flash, a_action_type: Action,
              a_clb_mxdata: int) -> bool:
        data_ok = True
        if a_amplitude_of_cell_to_flash is not None:
            assert len(a_data_to_flash) == 1, "Для прошивки одного диапазона должна быть передана только одна таблица"
            data_ok = self.shrink_data_table(a_data_to_flash[0], a_amplitude_of_cell_to_flash)

        if data_ok and self.process_data_to_flash(a_data_to_flash):
            self.reset()
            self.__action = a_action_type
            self.__mxdata = a_clb_mxdata
            self.__started = True
        else:
            logging.warning("Прошивка/верификация отменена.")

        return self.is_started()

    def start_read_by_flash_data(self, a_flash_data: List[FlashData], a_clb_mxdata: int):
        """
        Отличается от self.start() тем, что проверки входных данных не происходит и на вход подается сразу FlashData
        """
        if a_flash_data:
            self.reset()
            self.__flash_data = a_flash_data
            self.__action = CorrectionFlasher.Action.READ
            self.__mxdata = a_clb_mxdata
            self.__save_instead_of_verify = True
            self.__started = True
        return self.is_started()

    def get_read_data(self) -> Dict[str, List[Tuple[List, List, List]]]:
        return self.__read_data

    def stop(self):
        self.reset()
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
                    flash_data_ok = [self.__get_flash_data_size(len(f_data.x_points), len(f_data.y_points)) <=
                                     f_data.free_space for f_data in flash_data]
                    if all(flash_data_ok):
                        self.__flash_data += flash_data
                    else:
                        logging.warning("Размер некоторых данных превышает заданный размер памяти.")
                        success = False
                        break
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
    def __get_flash_data(a_flash_table: List[FlashTableRow],
                         a_data_table: List[List[Union[None, float]]]) -> List[FlashData]:
        flash_data = []
        amplitudes = [(row_idx, data_row[0]) for row_idx, data_row in enumerate(a_data_table) if row_idx != 0]

        for flash_row in a_flash_table:
            x_points = array('d')
            x_points.fromlist([value for col_idx, value in enumerate(a_data_table[0]) if col_idx != 0])
            y_points = array('d')
            coef_points = array('d')

            for row_idx, amplitude in amplitudes:

                if flash_row.start_value <= amplitude <= flash_row.end_value:
                    y_points.append(amplitude)

                    for col_idx, cell_value in enumerate(a_data_table[row_idx]):
                        if col_idx != 0:
                            # coef_points.append(cell_value)
                            coef_points.append(cell_value / amplitude)
            if y_points:
                diapason_name = f"{flash_row.start_value} - {flash_row.end_value}"
                flash_data.append(CorrectionFlasher.FlashData(diapason_name=diapason_name,
                                                              eeprom_offset=flash_row.eeprom_offset,
                                                              free_space=flash_row.size, x_points=x_points,
                                                              y_points=y_points, coef_points=coef_points))

        y_count = sum([len(f_data.y_points) for f_data in flash_data])
        if y_count != len(a_data_table) - 1:
            # Это значит, что некоторые амлитуды не вощли ни в один диапазон
            flash_data.clear()

        return flash_data

    @staticmethod
    def __get_flash_metadata_size() -> int:
        # uint32_t
        size_of_ident = 4
        size_of_size_x = 4
        size_of_size_y = 4

        return size_of_ident + size_of_size_x + size_of_size_y

    def __get_flash_data_size(self, a_x_points_count, a_y_points_count) -> int:
        metadata_size = self.__get_flash_metadata_size()

        # double
        x_elem_size = 8
        y_elem_size = 8
        coef_elem_size = 8

        coefs_count = a_x_points_count * a_y_points_count

        need_space = metadata_size + x_elem_size * a_x_points_count + \
            y_elem_size * a_y_points_count + coef_elem_size * coefs_count

        return need_space

    def tick(self):
        if self.__prev_stage != self.__stage:
            self.__prev_stage = self.__stage
            try:
                logging.debug(CorrectionFlasher.STAGE_IN_MESSAGE[self.__stage])
            except KeyError:
                pass

        if self.__stage == CorrectionFlasher.Stage.REST:
            pass

        elif self.__stage == CorrectionFlasher.Stage.RESET_EEPROM:
            self.__funnel_client.destroy()
            self.__metadata_are_read = False

            if self.__started:
                self.__stage = CorrectionFlasher.Stage.SET_UP_FUNNEL
            else:
                self.__stage = CorrectionFlasher.Stage.DONE

        elif self.__stage == CorrectionFlasher.Stage.SET_UP_FUNNEL:
            self.__current_flash_data = self.__flash_data[self.__current_flash_data_idx]
            if self.__action == CorrectionFlasher.Action.READ:
                if not self.__metadata_are_read:
                    # Чтение начинаем с чтения метаданных, чтобы не читать с запасом
                    data_size = self.__get_flash_metadata_size()
                else:
                    self.__correct_map.create()
                    self.__correct_map.connect(self.__funnel_client.get_address())
                    x_count = self.__correct_map.get_x_points_count()
                    y_count = self.__correct_map.get_y_points_count()
                    data_size = self.__get_flash_data_size(x_count, y_count)
            else:
                data_size = self.__get_flash_data_size(len(self.__current_flash_data.x_points),
                                                       len(self.__current_flash_data.y_points))

            self.__funnel_client.create(self.__mxdata, CorrectionFlasher.FUNNEL_MXDATA_OFFSET,
                                        self.__current_flash_data.eeprom_offset, data_size)

            self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.CONNECT_TO_FUNNEL:
            self.__funnel_client.tick()
            if self.__funnel_client.connected():
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.READ_WRITE_START:
            if self.__action == CorrectionFlasher.Action.READ:
                self.__funnel_client.reset_stat_read_complete()

                if not self.__metadata_are_read:
                    self.__stage = CorrectionFlasher.Stage.WAIT_EEPROM_READ_METADATA
                else:
                    logging.debug(f"Верификация диапазона: {self.__current_flash_data.diapason_name}")
                    self.__stage = CorrectionFlasher.Stage.WAIT_EEPROM_READ_DATA
            else:
                logging.debug(f"Прошивка диапазона: {self.__current_flash_data.diapason_name}")
                self.__stage = CorrectionFlasher.Stage.WRITE_TO_EEPROM

        elif self.__stage == CorrectionFlasher.Stage.WAIT_EEPROM_READ_METADATA:
            if not self.__funnel_client.is_read_complete():
                self.__funnel_client.tick()
            else:
                self.__metadata_are_read = True
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.WAIT_EEPROM_READ_DATA:
            if not self.__funnel_client.is_read_complete():
                self.__funnel_client.tick()

                data_size = self.__funnel_client.data_size()
                self.__progress = (data_size - self.__funnel_client.get_read_size()) / data_size * 100
                self.__progress = utils.bound(self.__progress, 0., 100.)
            else:
                self.__progress = 100
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.VERIFY_DATA:
            self.__correct_map.connect(self.__funnel_client.get_address())
            x_points = self.__correct_map.x_points
            y_points = self.__correct_map.y_points
            coefs_points = self.__correct_map.coef_points

            if self.__save_instead_of_verify:
                real_coefs = []
                for num, coef in enumerate(self.__correct_map.coef_points):
                    y = self.__correct_map.y_points[num // (len(self.__correct_map.x_points))]
                    real_coefs.append(y * coef)

                self.__read_data[self.__current_flash_data.diapason_name].append(
                    (self.__correct_map.x_points, self.__correct_map.y_points, real_coefs)
                )
                logging.info(f"Измерение {self.__current_flash_data.diapason_name}. Данные считаны.")
            else:
                if x_points == list(self.__current_flash_data.x_points) and \
                        y_points == list(self.__current_flash_data.y_points) and \
                        coefs_points == list(self.__current_flash_data.coef_points):
                    logging.info("Данные в калибраторе соответствуют данным в таблице")
                else:
                    logging.warning("ВНИМАНИЕ! Данные в калибраторе отличаются от данных в таблице")

            self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.WRITE_TO_EEPROM:
            self.__correct_map.create()
            self.__correct_map.connect(self.__funnel_client.get_address())
            self.__correct_map.set_x_points_count(len(self.__current_flash_data.x_points))
            self.__correct_map.set_y_points_count(len(self.__current_flash_data.y_points))
            self.__correct_map.connect(self.__funnel_client.get_address())

            self.__correct_map.x_points = self.__current_flash_data.x_points
            self.__correct_map.y_points = self.__current_flash_data.y_points
            self.__correct_map.coef_points = self.__current_flash_data.coef_points

            self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.WAIT_WRITE:
            write_remain_bytes = self.__funnel_client.get_write_size()
            if write_remain_bytes > 0:
                self.__funnel_client.tick()

                data_size = self.__funnel_client.data_size()
                self.__progress = (data_size - write_remain_bytes) / data_size * 100
            else:
                self.__progress = 100
                self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.NEXT_DIAPASON:
            self.__progress = 0
            if self.__current_flash_data_idx + 1 != len(self.__flash_data):
                self.__current_flash_data_idx += 1
                self.__current_flash_data = self.__flash_data[self.__current_flash_data_idx]
            else:
                self.__action = CorrectionFlasher.Action.NONE
                self.__started = False

            self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

        elif self.__stage == CorrectionFlasher.Stage.DONE:
            self.__stage = CorrectionFlasher.NEXT_STAGE[self.__stage]

    def get_progress(self) -> Tuple[float, float]:
        full_progress = (self.__current_flash_data_idx * 100 + self.__progress) / len(self.__flash_data)
        return self.__progress, full_progress
