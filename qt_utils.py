from math import isclose
import logging

from PyQt5 import QtCore, QtWidgets, QtGui

import constants


QSTYLE_COLOR_WHITE = "background-color: rgb(255, 255, 255);"
QSTYLE_COLOR_YELLOW = "background-color: rgb(250, 250, 170);"
QSTYLE_COLOR_RED = "background-color: rgb(245, 206, 203);"


def update_edit_color(a_actual_value, a_current_value, a_edit: QtWidgets.QLineEdit):
    try:
        if isclose(a_actual_value, float(a_current_value), rel_tol=constants.FLOAT_EPSILON):
            a_edit.setStyleSheet(QSTYLE_COLOR_WHITE)
        else:
            a_edit.setStyleSheet(QSTYLE_COLOR_YELLOW)
    except ValueError:
        a_edit.setStyleSheet(QSTYLE_COLOR_RED)


def get_wheel_steps(event: QtGui.QWheelEvent):
    degrees_num = event.angleDelta() / 8
    steps_num = degrees_num / 15
    return steps_num.y()


def qtablewidget_append_row(a_table: QtWidgets.QTableWidget, a_row_data: tuple):
    row_num = a_table.rowCount()
    a_table.insertRow(row_num)
    for col, data in enumerate(a_row_data):
        a_table.setItem(row_num, col, QtWidgets.QTableWidgetItem(str(data)))


def qtablewidget_clear(a_table: QtWidgets.QTableWidget):
    """
    В отличии от QTableWidget.clear не удаляет заголовки таблицы и
    В отличии от QTableWidget.clearContents удаляет строки, вместо простого их очищения
    :param a_table: QTableWidget
    :return:
    """
    for row in reversed(range(a_table.rowCount())):
        a_table.removeRow(row)


def qtablewidget_delete_selected(a_table: QtWidgets.QTableWidget):
    rows = a_table.selectionModel().selectedRows()
    if rows:
        for idx_model in reversed(rows):
            a_table.removeRow(idx_model.row())


class TableHeaderContextMenu:
    def __init__(self, a_parent: QtWidgets.QWidget, a_table: QtWidgets.QTableView, a_hide_first_column: bool = False):
        table_header = a_table.horizontalHeader()
        table_header.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.table = a_table
        self.hide_first_col = a_hide_first_column
        self.menu = QtWidgets.QMenu(a_parent)
        self.lambda_connections = []
        for column in range(a_table.model().columnCount()):
            if column == 0 and a_hide_first_column:
                continue
            header_name = a_table.model().headerData(column, QtCore.Qt.Horizontal)
            menu_checkbox = QtWidgets.QAction(header_name, self.menu)
            menu_checkbox.setCheckable(True)
            if not a_table.isColumnHidden(column):
                menu_checkbox.setChecked(True)
            self.menu.addAction(menu_checkbox)

            self.lambda_connections.append((menu_checkbox.triggered, menu_checkbox.triggered.connect(
                lambda state, col=column: a_table.setColumnHidden(col, not state))))

        self.lambda_connections.append((table_header.customContextMenuRequested,
                                        table_header.customContextMenuRequested.connect(self.show_context_menu)))

    def show_context_menu(self, a_position):
        self.menu.popup(self.table.horizontalHeader().viewport().mapToGlobal(a_position))
        for column, action in enumerate(self.menu.actions()):
            col_idx = column + 1 if self.hide_first_col else column
            action.setChecked(not self.table.isColumnHidden(col_idx))

    def delete_connections(self):
        # Нужно потому что лямбда соединения сами не удаляются
        for signal, connection in self.lambda_connections:
            signal.disconnect(connection)


class QTextEditLogger(logging.Handler):
    def __init__(self, parent, a_plain_text_edit):
        super().__init__()
        self.widget = a_plain_text_edit
        # self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
