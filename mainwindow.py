from logging.handlers import RotatingFileHandler
from os import system as os_system
from enum import IntEnum
import logging
import json

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget, TransparentPainterForView
from irspy.qt.custom_widgets.tstlan_dialog import TstlanDialog
from irspy.qt.custom_widgets.graph_dialog import GraphDialog
from irspy.clb.network_variables import NetworkVariables
from irspy.settings_ini_parser import BadIniException
from irspy.dlls.ftdi_control import FtdiControl
import irspy.clb.calibrator_constants as clb
import irspy.clb.clb_dll as clb_dll
from irspy.qt import qt_utils
import irspy.utils as utils

from MeasureManager import MeasureManager, SchemeInCellPainter
from correction_tables_dialog import CorrectionTablesDialog
from ui.py.mainwindow import Ui_MainWindow as MainForm
from MeasureConductor import MeasureConductor
from settings_dialog import SettingsDialog
from MeasureDataModel import CellData
from about_dialog import AboutDialog
from multimeters import MeterType
from SchemeControl import SchemeType
import settings


class MainWindow(QtWidgets.QMainWindow):
    clb_list_changed = QtCore.pyqtSignal([list])
    usb_status_changed = QtCore.pyqtSignal(clb.State)
    signal_enable_changed = QtCore.pyqtSignal(bool)

    class CloseConfigOptions(IntEnum):
        SAVE = 0
        DONT_SAVE = 1
        CANCEL = 2

    displayed_data_to_text = {
        CellData.GetDataType.MEASURED: "Измерено",
        CellData.GetDataType.DEVIATION: "Отклонение, %",
        CellData.GetDataType.DELTA_2: "Полудельта, %",
        CellData.GetDataType.SKO_PERCENTS: "СКО, %",
        CellData.GetDataType.STUDENT_95: "Доверительный интервал 0.95, %",
        CellData.GetDataType.STUDENT_99: "Доверительный интервал 0.99, %",
        CellData.GetDataType.STUDENT_999: "Доверительный интервал 0.999, %",
    }

    def __init__(self):
        super().__init__()

        self.ui = MainForm()
        self.ui.setupUi(self)

        try:
            self.settings = settings.get_clb_autocalibration_settings()
            ini_ok = True
        except BadIniException:
            ini_ok = False
            QtWidgets.QMessageBox.critical(self, "Ошибка", 'Файл конфигурации поврежден. Пожалуйста, '
                                                           'удалите файл "settings.ini" и запустите программу заново')
        if ini_ok:
            self.settings.restore_qwidget_state(self)
            self.settings.restore_qwidget_state(self.ui.mainwindow_splitter)
            self.settings.restore_qwidget_state(self.ui.mainwindow_splitter_2)
            self.settings.restore_qwidget_state(self.ui.measures_table)

            self.ui.measures_table.setItemDelegate(TransparentPainterForWidget(self.ui.measures_table, "#d4d4ff"))

            self.ui.progress_bar_widget.setHidden(True)

            for i in range(CellData.GetDataType.COUNT):
                self.ui.displayed_data_type_combobox.addItem(MainWindow.displayed_data_to_text[i])

            self.set_up_logger()

            self.ftdi_control = FtdiControl()

            self.clb_driver = clb_dll.clb_dll

            modbus_registers_count = 700
            self.usb_driver = clb_dll.UsbDrv(self.clb_driver, modbus_registers_count * 2)
            self.usb_state = clb_dll.UsbDrv.UsbState.DISABLED
            self.calibrator = clb_dll.ClbDrv(self.clb_driver)
            self.clb_state = clb.State.DISCONNECTED

            self.netvars = NetworkVariables(f"./{clb.CLB_CONFIG_NAME}", self.calibrator, a_variables_read_delay=0)

            self.clb_signal_off_timer = QtCore.QTimer()
            # noinspection PyTypeChecker
            self.clb_signal_off_timer.timeout.connect(self.close)
            self.SIGNAL_OFF_TIME_MS = 200
            self.ignore_save = False

            self.current_configuration_path = ""

            self.measure_progress_bar_value = 0

            self.tstlan_dialog = None
            self.graphs_dialog = None

            self.open_correction_tables = False

            self.show()

            self.measure_manager = MeasureManager(self.ui.measures_table, self.ui.measure_data_view, self.settings,
                                                  self)
            self.open_configuration_by_name(self.settings.last_configuration_path)

            self.measure_conductor = MeasureConductor(self.calibrator, self.netvars, self.measure_manager,
                                                      self.settings)
            self.measure_conductor.all_measures_done.connect(self.measure_done)
            self.measure_conductor.single_measure_started.connect(self.single_measure_started)
            self.measure_conductor.single_measure_done.connect(self.single_measure_done)
            self.measure_conductor.verify_flash_done.connect(self.verify_flash_done)

            self.connect_all()

            self.tick_timer = QtCore.QTimer(self)
            self.tick_timer.timeout.connect(self.tick)
            self.tick_timer.start(10)

        else:
            self.close()

    def connect_all(self):
        self.ui.lock_action.triggered.connect(self.lock_cell_button_clicked)
        self.ui.unlock_action.triggered.connect(self.unlock_cell_button_clicked)
        self.ui.lock_all_action.triggered.connect(self.lock_all_cells_button_clicked)
        self.ui.unlock_all_action.triggered.connect(self.unlock_all_cells_button_clicked)
        self.ui.show_equal_action.toggled.connect(self.show_equal_cell_configs_button_toggled)

        self.ui.switch_to_active_cell_action.setChecked(self.settings.switch_to_active_cell)
        self.ui.switch_to_active_cell_action.triggered.connect(self.switch_to_active_cell_action_toggled)

        self.ui.show_scheme_in_cell_action.setChecked(self.settings.show_scheme_in_cell)
        self.ui.show_scheme_in_cell_action.triggered.connect(self.show_scheme_in_cell_toggled)
        self.show_scheme_in_cell_toggled(self.settings.show_scheme_in_cell)

        self.ui.add_row_button.clicked.connect(self.add_row_button_clicked)
        self.ui.remove_row_button.clicked.connect(self.remove_row_button_clicked)
        self.ui.add_column_button.clicked.connect(self.add_column_button_clicked)
        self.ui.remove_column_button.clicked.connect(self.remove_column_button_clicked)
        self.ui.clear_table_button.clicked.connect(self.clear_table_button_clicked)

        self.ui.start_all_action.triggered.connect(self.start_all_measures_button_clicked)
        self.ui.continue_all_action.triggered.connect(self.continue_all_measures_button_clicked)
        self.ui.start_current_measure_button.clicked.connect(self.start_current_measure_button_clicked)
        self.ui.continue_current_measure_button.clicked.connect(self.continue_current_measure_button_clicked)
        self.ui.stop_all_action.triggered.connect(self.stop_measure_button_clicked)

        self.ui.flash_all_action.triggered.connect(self.flash_all_button_clicked)
        self.ui.verify_all_action.triggered.connect(self.verify_all_button_clicked)
        self.ui.read_correction_tables_action.triggered.connect(self.read_correction_tables_button_clicked)
        self.ui.stop_flash_verify_action.triggered.connect(self.stop_flash_verify_button_clicked)
        self.ui.get_correction_tables_from_file_action.triggered.connect(self.open_correction_tables_from_file)

        self.ui.measure_data_view.clicked.connect(self.measure_data_cell_clicked)
        self.ui.measure_data_view.customContextMenuRequested.connect(self.show_data_table_context_menu)

        self.ui.measures_table.customContextMenuRequested.connect(self.show_measures_table_context_menu)

        self.ui.enter_settings_action.triggered.connect(self.open_settings)
        self.ui.open_tstlan_action.triggered.connect(self.open_tstlan)
        self.ui.graphs_action.triggered.connect(self.open_graphs)
        self.ui.save_action.triggered.connect(self.save_configuration)
        self.ui.save_as_action.triggered.connect(self.save_configuration_as)
        self.ui.save_current_measure_button.clicked.connect(self.save_current_configuration)
        self.ui.open_cell_config_button.clicked.connect(self.open_cell_configuration)
        self.ui.open_action.triggered.connect(self.open_configuration)
        self.ui.new_configuration_action.triggered.connect(self.create_new_configuration)
        self.ui.clb_list_combobox.currentTextChanged.connect(self.connect_to_clb)
        self.ui.add_measure_button.clicked.connect(self.add_measure_button_clicked)
        self.ui.delete_measure_button.clicked.connect(self.remove_measure_button_clicked)
        self.ui.rename_measure_button.clicked.connect(self.rename_measure_button_clicked)
        self.ui.open_shared_measure_parameters_button.clicked.connect(self.open_shared_measure_parameters)
        self.ui.update_measure_status_button.clicked.connect(self.update_measure_status_button_clicked)

        self.ui.enable_all_button.clicked.connect(self.enable_all_button_clicked)

        self.ui.copy_cell_config_action.triggered.connect(self.copy_cell_config)
        self.ui.measure_data_view.addAction(self.ui.copy_cell_config_action)
        self.ui.paste_cell_config_action.triggered.connect(self.paste_cell_config)
        self.ui.measure_data_view.addAction(self.ui.paste_cell_config_action)

        self.ui.copy_cell_value_action.triggered.connect(self.copy_cell_value)
        self.ui.measure_data_view.addAction(self.ui.copy_cell_value_action)
        self.ui.paste_cell_value_action.triggered.connect(self.paste_cell_value)
        self.ui.measure_data_view.addAction(self.ui.paste_cell_value_action)

        self.ui.show_cell_graph_action.triggered.connect(self.open_cell_graph)
        self.ui.measure_data_view.addAction(self.ui.show_cell_graph_action)

        self.ui.flash_current_measure_action.triggered.connect(self.flash_table)
        self.ui.measure_data_view.addAction(self.ui.flash_current_measure_action)
        self.ui.verify_current_measure_action.triggered.connect(self.verify_table)
        self.ui.measure_data_view.addAction(self.ui.verify_current_measure_action)
        self.ui.verify_diapason_of_cell_action.triggered.connect(self.verify_diapason_of_cell)
        self.ui.measure_data_view.addAction(self.ui.verify_diapason_of_cell_action)
        self.ui.flash_diapason_of_cell_action.triggered.connect(self.flash_diapason_of_cell)
        self.ui.measure_data_view.addAction(self.ui.flash_diapason_of_cell_action)

        self.ui.meter_combobox.currentIndexChanged.connect(self.set_meter)
        self.ui.meter_settings_button.clicked.connect(self.open_meter_settings)

        self.ui.scheme_combobox.setCurrentIndex(self.settings.scheme_type)
        self.ui.scheme_combobox.currentIndexChanged.connect(self.set_scheme_type)
        self.set_scheme_type(self.ui.scheme_combobox.currentIndex())

        self.ui.displayed_data_type_combobox.currentIndexChanged.connect(self.set_displayed_data)
        self.ui.update_calculated_cells_data_button.clicked.connect(self.update_calculated_cells_data)

        self.ui.calculate_divider_coefficients.triggered.connect(self.calculate_divider_coefficients_button_clicked)
        self.ui.open_about_action.triggered.connect(self.open_about)

    def set_up_logger(self):
        log = qt_utils.QTextEditLogger(self.ui.log_text_edit)
        log.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

        file_log = RotatingFileHandler("autocalibration.log", maxBytes=10*1024*1024, backupCount=3)
        file_log.setLevel(logging.DEBUG)
        file_log.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'))

        logging.getLogger().addHandler(file_log)
        logging.getLogger().addHandler(log)
        logging.getLogger().setLevel(logging.DEBUG)

    def lock_interface(self, a_lock: bool):
        self.ui.new_configuration_action.setDisabled(a_lock)
        self.ui.open_action.setDisabled(a_lock)
        self.ui.save_action.setDisabled(a_lock)
        self.ui.save_as_action.setDisabled(a_lock)

        self.ui.start_all_action.setDisabled(a_lock)
        self.ui.continue_all_action.setDisabled(a_lock)

        self.ui.flash_all_action.setDisabled(a_lock)
        self.ui.verify_all_action.setDisabled(a_lock)
        self.ui.read_correction_tables_action.setDisabled(a_lock)
        self.ui.stop_flash_verify_action.setDisabled(a_lock)

        self.ui.lock_action.setDisabled(a_lock)
        self.ui.unlock_action.setDisabled(a_lock)
        self.ui.lock_all_action.setDisabled(a_lock)
        self.ui.unlock_all_action.setDisabled(a_lock)

        self.ui.save_current_measure_button.setDisabled(a_lock)

        self.ui.start_current_measure_button.setDisabled(a_lock)
        self.ui.continue_current_measure_button.setDisabled(a_lock)

        self.ui.add_row_button.setDisabled(a_lock)
        self.ui.remove_row_button.setDisabled(a_lock)
        self.ui.add_column_button.setDisabled(a_lock)
        self.ui.remove_column_button.setDisabled(a_lock)
        self.ui.clear_table_button.setDisabled(a_lock)

        self.ui.clb_list_combobox.setDisabled(a_lock)
        self.ui.meter_combobox.setDisabled(a_lock)
        self.ui.scheme_combobox.setDisabled(a_lock)

        self.ui.add_measure_button.setDisabled(a_lock)
        self.ui.delete_measure_button.setDisabled(a_lock)
        self.ui.rename_measure_button.setDisabled(a_lock)
        self.ui.update_measure_status_button.setDisabled(a_lock)
        self.ui.enable_all_button.setDisabled(a_lock)

        self.ui.paste_cell_value_action.setDisabled(a_lock)
        self.ui.paste_cell_config_action.setDisabled(a_lock)
        self.ui.flash_current_measure_action.setDisabled(a_lock)
        self.ui.verify_current_measure_action.setDisabled(a_lock)
        self.ui.flash_diapason_of_cell_action.setDisabled(a_lock)
        self.ui.verify_diapason_of_cell_action.setDisabled(a_lock)

        self.ui.progress_bar_widget.setHidden(not a_lock)

        self.measure_manager.lock_interface(a_lock)

    def gui_tick(self):
        self.progress_bars_handling()

        correction_enabled = not self.netvars.ui_correct_off.get()
        correction_enabled_ui = self.ui.correction_action.isChecked()
        if not correction_enabled == correction_enabled_ui:
            self.ui.correction_action.setChecked(correction_enabled)

    def tick(self):
        self.measure_conductor.tick()
        self.usb_driver.tick()
        self.gui_tick()

        if self.usb_driver.is_dev_list_changed():
            self.ui.clb_list_combobox.clear()
            for clb_name in self.usb_driver.get_dev_list():
                self.ui.clb_list_combobox.addItem(clb_name)

        if self.usb_driver.is_status_changed():
            self.usb_state = self.usb_driver.get_status()

        current_state = clb.State.DISCONNECTED
        if self.usb_state == clb_dll.UsbDrv.UsbState.CONNECTED:
            if self.calibrator.signal_enable_changed():
                self.signal_enable_changed.emit(self.calibrator.signal_enable)

            if not self.calibrator.signal_enable:
                current_state = clb.State.STOPPED
            elif not self.calibrator.is_signal_ready():
                current_state = clb.State.WAITING_SIGNAL
            else:
                current_state = clb.State.READY

        if self.clb_state != current_state:
            self.clb_state = current_state
            self.calibrator.state = current_state
            self.usb_status_changed.emit(self.clb_state)

    def connect_to_clb(self, a_clb_name):
        self.calibrator.connect(a_clb_name)

    def count_measure_length(self, a_iteration_type: MeasureManager.IterationType):
        measure_iterator = self.measure_manager.get_measure_iterator(a_iteration_type)
        seconds_count = 0
        if measure_iterator is not None:
            cell_position = measure_iterator.get()
            while cell_position is not None:
                cell_config = self.measure_manager.get_cell_config(*cell_position)
                seconds_count += cell_config.measure_delay
                seconds_count += cell_config.measure_time

                measure_iterator.next()
                cell_position = measure_iterator.get()

        return seconds_count

    def set_up_progress_bars_for_measure(self, a_measures_total_length):
        self.ui.measure_progress_bar.setMaximum(a_measures_total_length)

        self.ui.measure_progress_bar.setFormat("%v с. / %m с. (%p%)")
        self.ui.curent_cell_progress_bar.setFormat("%v с. / %m с. (%p%)")

    def start_measure(self, a_iteration_type: MeasureManager.IterationType):
        measure_iterator = self.measure_manager.get_measure_iterator(a_iteration_type)
        if measure_iterator is not None:
            # Это происходит, когда нет выделенных ячеек
            if measure_iterator.get() is not None:
                if self.save_configuration():
                    self.lock_interface(True)
                    self.set_up_progress_bars_for_measure(self.count_measure_length(a_iteration_type))

                    if a_iteration_type in (MeasureManager.IterationType.START_ALL,
                                            MeasureManager.IterationType.CONTINUE_ALL):
                        auto_flash_to_calibrator = True
                    else:
                        auto_flash_to_calibrator = False

                    self.measure_conductor.start(measure_iterator, auto_flash_to_calibrator)

    def progress_bars_handling(self):
        if self.measure_conductor.is_started():
            time_passed = self.measure_conductor.get_current_cell_time_passed()
            self.ui.curent_cell_progress_bar.setValue(time_passed)
            self.ui.measure_progress_bar.setValue(self.measure_progress_bar_value + time_passed)
        elif self.measure_conductor.is_correction_flash_verify_started():
            current, full = self.measure_conductor.get_flash_progress()
            self.ui.curent_cell_progress_bar.setValue(current)
            self.ui.measure_progress_bar.setValue(full)

    def single_measure_started(self):
        self.ui.curent_cell_progress_bar.setMaximum(self.measure_conductor.get_current_cell_time_duration())

    def single_measure_done(self):
        # "Переливаем" прогресс маленького прогресс бара в большой
        self.measure_progress_bar_value += self.ui.curent_cell_progress_bar.maximum()
        self.ui.curent_cell_progress_bar.setValue(0)
        if not self.save_current_configuration():
            logging.warning("Не удалось сохранить результат после завершения измерения ячейки")

    def measure_done(self):
        self.ui.curent_cell_progress_bar.setValue(0)
        self.ui.curent_cell_progress_bar.resetFormat()
        self.ui.measure_progress_bar.setValue(0)
        self.ui.measure_progress_bar.resetFormat()
        self.measure_progress_bar_value = 0
        self.lock_interface(False)

    def start_all_measures_button_clicked(self, _):
        self.start_measure(MeasureManager.IterationType.START_ALL)

    def continue_all_measures_button_clicked(self, _):
        self.start_measure(MeasureManager.IterationType.CONTINUE_ALL)

    def start_current_measure_button_clicked(self, _):
        self.start_measure(MeasureManager.IterationType.START_CURRENT)

    def continue_current_measure_button_clicked(self, _):
        self.start_measure(MeasureManager.IterationType.CONTINUE_CURRENT)

    def stop_measure_button_clicked(self, _):
        self.measure_conductor.stop()

    def copy_cell_config(self):
        self.measure_manager.copy_cell_config()

    def paste_cell_config(self):
        self.measure_manager.paste_cell_config()

    def copy_cell_value(self):
        self.measure_manager.copy_cell_value()

    def paste_cell_value(self):
        self.measure_manager.paste_cell_value()

    def lock_gui_while_flash(self):
        self.lock_interface(True)
        self.ui.stop_flash_verify_action.setDisabled(False)

        self.ui.measure_progress_bar.setMaximum(100)
        # self.ui.measure_progress_bar.setValue(0)
        self.ui.curent_cell_progress_bar.setMaximum(100)
        # self.ui.curent_cell_progress_bar.setValue(0)

    def flash_table(self):
        if self.calibrator.state == clb.State.STOPPED:
            current_measure = self.measure_manager.get_current_measure()
            if current_measure is not None:
                if self.measure_conductor.start_flash([current_measure]):
                    self.lock_gui_while_flash()
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def flash_diapason_of_cell(self):
        if self.calibrator.state == clb.State.STOPPED:
            current_measure = self.measure_manager.get_current_measure()
            if current_measure is not None:
                selected_cell = self.measure_manager.get_only_selected_cell()

                if selected_cell and selected_cell.row() != 0:
                    amplitude = self.measure_manager.get_amplitude(current_measure, selected_cell.row())
                    if self.measure_conductor.start_flash([current_measure], amplitude):
                        self.lock_gui_while_flash()
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def verify_table(self):
        if self.calibrator.state == clb.State.STOPPED:
            current_measure = self.measure_manager.get_current_measure()
            if current_measure is not None:
                if self.measure_conductor.start_verify([current_measure]):
                    self.lock_gui_while_flash()
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def verify_diapason_of_cell(self):
        if self.calibrator.state == clb.State.STOPPED:
            current_measure = self.measure_manager.get_current_measure()
            if current_measure is not None:
                selected_cell = self.measure_manager.get_only_selected_cell()

                if selected_cell and selected_cell.row() != 0:
                    amplitude = self.measure_manager.get_amplitude(current_measure, selected_cell.row())
                    if self.measure_conductor.start_verify([current_measure], amplitude):
                        self.lock_gui_while_flash()
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def flash_all_button_clicked(self):
        if self.calibrator.state == clb.State.STOPPED:
            enabled_measures = self.measure_manager.get_enabled_measures()
            if enabled_measures:
                if self.measure_conductor.start_flash(enabled_measures):
                    self.lock_gui_while_flash()
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def verify_all_button_clicked(self):
        if self.calibrator.state == clb.State.STOPPED:
            enabled_measures = self.measure_manager.get_enabled_measures()
            if enabled_measures:
                if self.measure_conductor.start_verify(enabled_measures):
                    self.lock_gui_while_flash()
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def read_correction_tables_button_clicked(self):
        if self.calibrator.state == clb.State.STOPPED:
            enabled_measures = self.measure_manager.get_enabled_measures()
            if enabled_measures:
                if self.measure_conductor.start_read_correction_to_tables(enabled_measures):
                    self.lock_gui_while_flash()
                    self.open_correction_tables = True
        else:
            logging.error("Калибратор не подключен, либо не находится в состоянии покоя")

    def stop_flash_verify_button_clicked(self):
        self.measure_conductor.stop_flash_verify()

    @utils.exception_decorator
    def verify_flash_done(self):
        self.lock_interface(False)

        self.ui.measure_progress_bar.setValue(0)
        self.ui.curent_cell_progress_bar.setValue(0)

        if self.open_correction_tables:
            self.open_correction_tables = False

            correction_tables = self.measure_conductor.get_correction_tables()
            if correction_tables:
                correct_tables_dialog = CorrectionTablesDialog(correction_tables, self.settings)
                correct_tables_dialog.exec()

    @utils.exception_decorator
    def open_correction_tables_from_file(self, _):
        tables_filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Открыть таблицы коррекции", "",
                                                                   "Таблицы коррекции (*.ct)")
        with open(tables_filename, "r") as tables_file:
            correction_tables = json.loads(tables_file.read())

        if correction_tables:
            correct_tables_dialog = CorrectionTablesDialog(correction_tables, self.settings)
            correct_tables_dialog.exec()

    def show_data_table_context_menu(self):
        menu = QtWidgets.QMenu(self)

        menu.addAction(self.ui.copy_cell_value_action)
        menu.addAction(self.ui.paste_cell_value_action)

        menu.addAction(self.ui.copy_cell_config_action)
        menu.addAction(self.ui.paste_cell_config_action)
        menu.insertSeparator(self.ui.copy_cell_config_action)

        menu.addAction(self.ui.show_cell_graph_action)
        menu.insertSeparator(self.ui.show_cell_graph_action)

        menu.addAction(self.ui.flash_current_measure_action)
        menu.addAction(self.ui.verify_current_measure_action)
        menu.insertSeparator(self.ui.flash_current_measure_action)

        menu.addAction(self.ui.flash_diapason_of_cell_action)
        menu.addAction(self.ui.verify_diapason_of_cell_action)
        menu.insertSeparator(self.ui.flash_diapason_of_cell_action)

        # add other required actions
        menu.popup(QtGui.QCursor.pos())

    def open_measure_folder(self):
        if self.current_configuration_path:
            path = self.current_configuration_path.replace("/", "\\")
            os_system(f'explorer.exe "{path}"')

    def show_measures_table_context_menu(self):
        menu = QtWidgets.QMenu(self)

        open_measure_folder_action = QtWidgets.QAction("Открыть каталог измерения", self)
        open_measure_folder_action.triggered.connect(self.open_measure_folder)
        menu.addAction(open_measure_folder_action)

        # add other required actions
        menu.popup(QtGui.QCursor.pos())

    @utils.exception_decorator
    def add_measure_button_clicked(self, _):
        self.measure_manager.new_measure()

    @utils.exception_decorator
    def remove_measure_button_clicked(self, _):
        self.measure_manager.remove_measure(self.current_configuration_path)

    def enable_all_button_clicked(self, _):
        self.measure_manager.enable_all_measures()

    @utils.exception_decorator
    def rename_measure_button_clicked(self, _):
        self.measure_manager.rename_current_measure(self.current_configuration_path)

    def update_measure_status_button_clicked(self, _):
        self.measure_manager.update_all_measures_status()

    def show_equal_cell_configs_button_toggled(self, a_enable: bool):
        self.measure_manager.show_equal_cell_configs(a_enable)

    def switch_to_active_cell_action_toggled(self, a_enable: bool):
        self.settings.switch_to_active_cell = int(a_enable)

    def show_scheme_in_cell_toggled(self, a_enable: bool):
        if a_enable:
            self.ui.measure_data_view.setItemDelegate(SchemeInCellPainter(self.ui.measure_data_view, "#d4d4ff"))
        else:
            self.ui.measure_data_view.setItemDelegate(TransparentPainterForView(self.ui.measure_data_view, "#d4d4ff"))

    def measure_data_cell_clicked(self, index: QtCore.QModelIndex):
        if self.ui.show_equal_action.isChecked():
            self.measure_manager.set_cell_to_compare(index)

    def lock_cell_button_clicked(self):
        self.measure_manager.lock_selected_cells(True)

    def unlock_cell_button_clicked(self):
        self.measure_manager.lock_selected_cells(False)

    def lock_all_cells_button_clicked(self):
        self.measure_manager.lock_all_cells(True)

    def unlock_all_cells_button_clicked(self):
        self.measure_manager.lock_all_cells(False)

    def add_row_button_clicked(self, _):
        self.measure_manager.add_row_to_current_measure()

    def remove_row_button_clicked(self, _):
        self.measure_manager.remove_row_from_current_measure()

    def add_column_button_clicked(self, _):
        self.measure_manager.add_column_to_current_measure()

    def remove_column_button_clicked(self, _):
        self.measure_manager.remove_column_from_current_measure()

    def clear_table_button_clicked(self, _):
        self.measure_manager.clear_table_content()

    @utils.exception_decorator
    def open_tstlan(self, _):
        # noinspection PyTypeChecker
        if self.tstlan_dialog is None:
            self.tstlan_dialog = TstlanDialog(self.netvars, self.calibrator, self.settings)
            self.tstlan_dialog.exec()
            self.tstlan_dialog = None
        else:
            self.tstlan_dialog.activateWindow()

    @utils.exception_decorator
    def open_graphs(self, _):
        if self.graphs_dialog is None:
            graphs_data = self.measure_manager.get_data_for_graphs()
            if graphs_data:
                self.graphs_dialog = GraphDialog(graphs_data, self.settings)
                self.graphs_dialog.exec()
                self.graphs_dialog = None
        else:
            self.graphs_dialog.activateWindow()

    @utils.exception_decorator
    def open_cell_graph(self, _):
        graphs_data = self.measure_manager.get_cell_measurement_graph()
        if graphs_data:
            graph_dialog = GraphDialog(graphs_data, self.settings)
            graph_dialog.exec()

    @utils.exception_decorator
    def open_settings(self, _):
        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()

    def open_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def open_shared_measure_parameters(self, _):
        self.measure_manager.open_shared_measure_parameters()

    def calculate_divider_coefficients_button_clicked(self, _):
        pass
        # self.measure_manager.auto_calculate_divider_coefficients()

    def open_cell_configuration(self):
        self.measure_manager.open_cell_configuration()

    def set_meter(self, a_index: int):
        self.measure_manager.set_meter(MeterType(a_index))

    def set_scheme_type(self, a_index: int):
        self.measure_manager.set_scheme(SchemeType(a_index), self.ftdi_control)
        self.settings.scheme_type = a_index

    def open_meter_settings(self):
        self.measure_manager.open_meter_settings()

    def set_displayed_data(self, a_displayed_data: int):
        self.measure_manager.set_displayed_data(CellData.GetDataType(a_displayed_data))

    def update_calculated_cells_data(self, _):
        displayed_data = self.ui.displayed_data_type_combobox.currentIndex()
        self.measure_manager.set_displayed_data(CellData.GetDataType(displayed_data))

    def save_configuration(self):
        result = True
        if self.current_configuration_path:
            if not self.measure_manager.is_saved():
                result = self.save_configuration_by_name(self.current_configuration_path)
        else:
            result = self.save_configuration_as()
        return result

    def save_configuration_as(self):
        result = True
        # noinspection PyTypeChecker
        config_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог конфигураций",
                                                                self.current_configuration_path)
        if config_dir:
            config_filename = f"{config_dir}"
            if self.save_configuration_by_name(config_filename):
                self.open_configuration_by_name(config_filename)
                pass
            else:
                result = False
        else:
            result = False
        return result

    def save_current_configuration(self):
        result = True
        if self.current_configuration_path:
            if not self.measure_manager.is_current_saved():
                if not self.measure_manager.save_current(self.current_configuration_path):
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось сохранить измерение",
                                                   QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
                    result = False
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Конфигурация не сохранена",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        return result

    def save_configuration_by_name(self, a_folder: str):
        result = True
        if self.measure_manager.save(a_folder):
            self.current_configuration_path = a_folder
            self.settings.last_configuration_path = a_folder
            self.setWindowTitle(self.current_configuration_path)
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфигурации в каталоге {a_folder}",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            result = False
        return result

    def reset_measure_manager(self):
        self.measure_manager = MeasureManager(self.ui.measures_table, self.ui.measure_data_view, self.settings, self)
        self.set_scheme_type(self.ui.scheme_combobox.currentIndex())

        self.measure_conductor = MeasureConductor(self.calibrator, self.netvars, self.measure_manager, self.settings)
        self.measure_conductor.all_measures_done.connect(self.measure_done)
        self.measure_conductor.single_measure_started.connect(self.single_measure_started)
        self.measure_conductor.single_measure_done.connect(self.single_measure_done)
        self.measure_conductor.verify_flash_done.connect(self.verify_flash_done)

    def create_new_configuration(self):
        cancel_open = False
        if self.current_configuration_path:
            if not self.measure_manager.is_saved():
                answer = self.close_configuration()
                if answer == MainWindow.CloseConfigOptions.SAVE:
                    if not self.save_configuration():
                        cancel_open = True
                elif answer == MainWindow.CloseConfigOptions.CANCEL:
                    cancel_open = True

        if not cancel_open:
            self.current_configuration_path = ""
            self.reset_measure_manager()

    def open_configuration(self):
        cancel_open = False
        if self.current_configuration_path:
            if not self.measure_manager.is_saved():
                answer = self.close_configuration()
                if answer == MainWindow.CloseConfigOptions.SAVE:
                    if not self.save_configuration():
                        cancel_open = True
                elif answer == MainWindow.CloseConfigOptions.CANCEL:
                    cancel_open = True

        if not cancel_open:
            config_filename = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите каталог конфигураций",
                                                                         self.settings.last_configuration_path)
            if config_filename:
                self.settings.last_configuration_path = config_filename
                self.open_configuration_by_name(config_filename)

    def open_configuration_by_name(self, a_folder: str):
        try:
            if self.measure_manager.load_from_file(a_folder):
                self.current_configuration_path = a_folder
                self.setWindowTitle(self.current_configuration_path)
            elif a_folder:
                QtWidgets.QMessageBox.critical(self, "Ошибка",
                                               f'Не удалось найти файлы конфигураций в каталоге "{a_folder}"',
                                               QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
        except FileNotFoundError:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f'Не удалось найти каталог "{a_folder}"',
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    @staticmethod
    def close_configuration() -> CloseConfigOptions:
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle("Предупреждение")
        msgbox.setText("Текущая конфигурация не сохранена. Выберите действие")
        save_button = msgbox.addButton("Сохранить", QtWidgets.QMessageBox.YesRole)
        no_save_button = msgbox.addButton("Не сохранять", QtWidgets.QMessageBox.AcceptRole)
        _ = msgbox.addButton("Отмена", QtWidgets.QMessageBox.AcceptRole)
        msgbox.exec()

        if msgbox.clickedButton() == save_button:
            return MainWindow.CloseConfigOptions.SAVE
        elif msgbox.clickedButton() == no_save_button:
            return MainWindow.CloseConfigOptions.DONT_SAVE
        else:
            return MainWindow.CloseConfigOptions.CANCEL

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        if not self.measure_manager.is_saved() and not self.ignore_save:
            answer = self.close_configuration()

            if answer == MainWindow.CloseConfigOptions.SAVE:
                if self.save_configuration_by_name(self.current_configuration_path):
                    a_event.ignore()
                    self.clb_signal_off_timer.start(self.SIGNAL_OFF_TIME_MS)
                else:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось сохранить конфигурацию")
                    a_event.ignore()

            elif answer == MainWindow.CloseConfigOptions.DONT_SAVE:
                self.ignore_save = True
                self.clb_signal_off_timer.start(self.SIGNAL_OFF_TIME_MS)
                a_event.ignore()
            else:
                a_event.ignore()

        else:
            if self.calibrator.signal_enable:
                self.calibrator.signal_enable = False
                self.clb_signal_off_timer.start(self.SIGNAL_OFF_TIME_MS)
                a_event.ignore()
            else:
                self.settings.save_qwidget_state(self.ui.mainwindow_splitter)
                self.settings.save_qwidget_state(self.ui.mainwindow_splitter_2)
                self.settings.save_qwidget_state(self.ui.measures_table)
                self.settings.save_qwidget_state(self)

                a_event.accept()
