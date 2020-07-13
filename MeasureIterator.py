from collections import namedtuple
from typing import List, Tuple
import logging
import abc

from MeasureDataModel import MeasureDataModel


class MeasureIterator(abc.ABC):
    CellPosition = namedtuple("CellPosition", ["measure_name", "row", "column"])

    @abc.abstractmethod
    def next(self):
        pass

    @abc.abstractmethod
    def get(self):
        pass


class MeasureIteratorDirectByRows(MeasureIterator):
    """
    Ходит по заблокированным ячейкам слева направо и сверху вниз
    """
    FIRST_CELL_ROW = 1
    FIRST_CELL_COLUMN = 1

    def __init__(self, a_data_models: List[MeasureDataModel],
                 a_start_index: Tuple[int, int] = (FIRST_CELL_ROW, FIRST_CELL_COLUMN)):

        assert bool(a_data_models), "Нужна хотя бы одна модель данных"

        self.data_models = a_data_models
        self.current_data_model_idx = 0
        self.current_data_model = self.data_models[self.current_data_model_idx]

        self.current_row, self.current_column = a_start_index
        self.cells_are_over = False

        if not self.current_data_model.is_cell_locked(self.current_row, self.current_column):
            self.next()

    def __is_current_cell_the_last(self):
        return self.current_row + 1 == self.current_data_model.rowCount() and \
               self.current_column + 1 == self.current_data_model.columnCount()

    def __is_current_cell_the_last_in_row(self):
        return self.current_column + 1 == self.current_data_model.columnCount()

    def __is_current_model_the_last(self):
        return self.current_data_model == self.data_models[-1]

    def next(self):
        if self.__is_current_cell_the_last():
            if self.__is_current_model_the_last():
                self.cells_are_over = True
            else:
                self.current_data_model_idx += 1
                self.current_data_model = self.data_models[self.current_data_model_idx]
                self.current_row = MeasureIteratorDirectByRows.FIRST_CELL_ROW
                self.current_column = MeasureIteratorDirectByRows.FIRST_CELL_COLUMN
        else:
            if self.__is_current_cell_the_last_in_row():
                self.current_row += 1
                self.current_column = MeasureIteratorDirectByRows.FIRST_CELL_ROW
            else:
                self.current_column += 1

        if not self.cells_are_over:
            if not self.current_data_model.is_cell_locked(self.current_row, self.current_column):
                self.next()

    def get(self):
        return None if self.cells_are_over else \
            MeasureIterator.CellPosition(measure_name=self.current_data_model.get_name(),
                                         row=self.current_row, column=self.current_column)
