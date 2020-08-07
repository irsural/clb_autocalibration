from logging.handlers import RotatingFileHandler
from os import system as os_system
from enum import IntEnum
import logging
import json

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget, TransparentPainterForView
from irspy.settings_ini_parser import Settings, BadIniException
from irspy.clb.network_variables import NetworkVariables
from irspy.dlls.ftdi_control import FtdiControl
import irspy.clb.calibrator_constants as clb
import irspy.clb.clb_dll as clb_dll
from irspy.qt import qt_utils
import irspy.utils as utils

from correction_tables_dialog import CorrectionTablesDialog
from ui.py.mainwindow import Ui_MainWindow as MainForm
from MeasureConductor import MeasureConductor
from settings_dialog import SettingsDialog
from MeasureManager import MeasureManager
from tstlan_dialog import TstlanDialog
from MeasureDataModel import CellData
from graph_dialog import GraphDialog
from multimeters import MeterType


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
            self.settings = Settings("./settings.ini", [
                Settings.VariableInfo(a_name="fixed_step_list", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.LIST_FLOAT,
                                      a_default=[0.0001, 0.01, 0.1, 1, 10, 20, 100]),
                Settings.VariableInfo(a_name="checkbox_states", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.LIST_INT),
                Settings.VariableInfo(a_name="fixed_step_idx", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT),
                Settings.VariableInfo(a_name="rough_step", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.FLOAT, a_default=0.5),
                Settings.VariableInfo(a_name="common_step", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.FLOAT, a_default=0.05),
                Settings.VariableInfo(a_name="exact_step", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.FLOAT, a_default=0.002),
                Settings.VariableInfo(a_name="tstlan_update_time", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.FLOAT, a_default=0.2),
                Settings.VariableInfo(a_name="tstlan_show_marks", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="tstlan_marks", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.LIST_INT),
                Settings.VariableInfo(a_name="tstlan_graphs", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.LIST_INT),
                Settings.VariableInfo(a_name="last_configuration_path", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.STRING),
                Settings.VariableInfo(a_name="meter_type", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="agilent_connect_type", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="agilent_gpib_index", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="agilent_gpib_address", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=22),
                Settings.VariableInfo(a_name="agilent_com_name", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.STRING, a_default="com4"),
                Settings.VariableInfo(a_name="agilent_ip_address", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.STRING, a_default="0.0.0.0"),
                Settings.VariableInfo(a_name="agilent_port", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="switch_to_active_cell", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="graph_parameters_splitter_size", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.INT, a_default=500),
            ])

            ini_ok = True
        except BadIniException:
            ini_ok = False
            QtWidgets.QMessageBox.critical(self, "Ошибка", 'Файл конфигурации поврежден. Пожалуйста, '
                                                           'удалите файл "settings.ini" и запустите программу заново')
        if ini_ok:
            self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
            self.ui.mainwindow_splitter.restoreState(self.settings.get_last_geometry(
                self.ui.mainwindow_splitter.objectName()))
            self.ui.mainwindow_splitter_2.restoreState(self.settings.get_last_geometry(
                self.ui.mainwindow_splitter_2.objectName()))
            self.ui.measures_table.horizontalHeader().restoreState(self.settings.get_last_header_state(
                self.ui.measures_table.objectName()))
            self.ui.measure_data_view.setItemDelegate(TransparentPainterForView(self.ui.measure_data_view, "#d4d4ff"))
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

            self.netvars = NetworkVariables(f"./{clb.CLB_CONFIG_NAME}", self.calibrator,
                                            a_variables_read_delay=0)

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

            self.measure_manager = MeasureManager(self.ui.measures_table,
                                                  self.ui.measure_data_view, self.settings, self)
            self.open_configuration_by_name(self.settings.last_configuration_path)

            self.measure_conductor = MeasureConductor(self.calibrator, self.netvars, self.ftdi_control,
                                                      self.measure_manager, self.settings)
            self.measure_conductor.all_measures_done.connect(self.measure_done)
            self.measure_conductor.single_measure_started.connect(self.single_measure_started)
            self.measure_conductor.single_measure_done.connect(self.single_measure_done)
            self.measure_conductor.verify_flash_done.connect(self.verify_flash_done)

            self.ui.lock_action.triggered.connect(self.lock_cell_button_clicked)
            self.ui.unlock_action.triggered.connect(self.unlock_cell_button_clicked)
            self.ui.lock_all_action.triggered.connect(self.lock_all_cells_button_clicked)
            self.ui.unlock_all_action.triggered.connect(self.unlock_all_cells_button_clicked)
            self.ui.show_equal_action.toggled.connect(self.show_equal_cell_configs_button_toggled)

            self.ui.switch_to_active_cell_action.setChecked(self.settings.switch_to_active_cell)
            self.ui.switch_to_active_cell_action.triggered.connect(self.switch_to_active_cell_action_toggled)

            self.ui.add_row_button.clicked.connect(self.add_row_button_clicked)
            self.ui.remove_row_button.clicked.connect(self.remove_row_button_clicked)
            self.ui.add_column_button.clicked.connect(self.add_column_button_clicked)
            self.ui.remove_column_button.clicked.connect(self.remove_column_button_clicked)

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

            self.ui.displayed_data_type_combobox.currentIndexChanged.connect(self.set_displayed_data)

            self.tick_timer = QtCore.QTimer(self)
            self.tick_timer.timeout.connect(self.tick)
            self.tick_timer.start(10)

        else:
            self.close()

    def set_up_logger(self):
        log = qt_utils.QTextEditLogger(self, self.ui.log_text_edit)
        log.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

        file_log = RotatingFileHandler("autocalibration.log", maxBytes=512*1024*1024, backupCount=3)
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

        self.ui.correction_action.setDisabled(a_lock)
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

        self.ui.clb_list_combobox.setDisabled(a_lock)
        self.ui.meter_combobox.setDisabled(a_lock)

        self.ui.add_measure_button.setDisabled(a_lock)
        self.ui.delete_measure_button.setDisabled(a_lock)
        self.ui.rename_measure_button.setDisabled(a_lock)
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
        self.save_current_configuration()

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

            # from collections import defaultdict
            # correction_tables = defaultdict(list, {'Калибровка U=': [([1.0, 2.0], [0.01, 0.04], [0.009975154248354, 0.009975154248354, 0.039970797689913, 0.039970797689913]), ([1.0, 2.0], [0.05, 0.4], [0.049927211508369006, 0.049927211508369006, 0.39995969607292703, 0.39995969607292703]), ([1.0, 2.0], [0.5, 4.0], [0.499422501526729, 0.499422501526729, 3.99942805992845, 3.99942805992845]), ([1.0, 2.0], [5.0, 40.0], [4.99410723585904, 4.99410723585904, 39.9947796930806, 39.9947796930806]), ([1.0, 2.0], [50.0, 200.0], [49.929965710001504, 49.929965710001504, 199.925356236382, 199.925356236382]), ([1.0, 2.0], [210.0, 600.0], [209.922540130437, 209.922540130437, 599.8432013468209, 599.8432013468209])], 'Калибровка I=': [([1.0, 2.0], [1e-05, 0.0001], [1.00327283641079e-05, 1.00328641408589e-05, 0.00010015972961021, 0.000100159933420841]), ([1.0, 2.0], [0.00011499999999999999, 0.001], [0.000115359308729811, 0.00011535984470438301, 0.00100146774030237, 0.0010014685727761802]), ([1.0, 2.0], [0.0011500000000000002, 0.01], [0.00115376444542256, 0.0011537689392614701, 0.0100147941816887, 0.010014775532116101]), ([1.0, 2.0], [0.0115, 0.1], [0.011526552203102, 0.011526584910971898, 0.10003368048541801, 0.10003377310587701]), ([1.0, 2.0], [0.115, 1.0], [0.11537375035214602, 0.11537474853705303, 1.00084928949008, 1.00085323469948]), ([1.0, 2.0], [1.1500000000000001, 10.0], [1.1837164792313097, 1.18368703441567, 10.3056051962545, 10.3055991072119])], 'Калибровка I~': [([40.0, 62.0, 105.0, 155.0, 405.0, 1005.0, 2000.0], [0.01, 0.035, 0.11], [0.010024623311651933, 0.009986813908168, 0.009977394580498, 0.009976973315591, 0.009978369264037, 0.009984158669325, 0.010001552990305, 0.034938082114077, 0.034928202835598, 0.034923328950179, 0.034922332504963, 0.034926247105708, 0.03494628677966, 0.035009413038922, 0.109810977344763, 0.109776049564884, 0.1101123547639906, 0.109755992391362, 0.109767206360684, 0.109829604417225, 0.11002905360721202]), ([40.0, 62.0, 105.0, 155.0, 405.0, 1005.0, 2000.0], [0.111, 0.35, 1.1], [0.110809125510565, 0.110774584094069, 0.110758165407581, 0.110753102906869, 0.110760765199417, 0.11079721471164, 0.110904281962654, 0.349457874237124, 0.349324818168857, 0.349258779826853, 0.349238269140621, 0.3500108635493698, 0.349342513676657, 0.34963444694719, 1.09899472748408, 1.000990293609996, 1.09772354794492, 1.09761974428777, 1.09761728142475, 1.09789822290319, 0.9987110201668582]), ([40.0, 51.0, 62.0, 105.0, 155.0, 270.0, 405.0, 1005.0, 2000.0], [1.101, 3.0, 11.0], [1.10032283882211, 1.09954667949391, 1.101, 1.101, 1.101, 1.101, 1.101, 1.101, 1.101, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0])], 'Калибровка U~': [([40.0, 405.0, 1005.0, 2000.0], [0.01, 0.035, 0.11], [0.0100029247564148, 0.010004022569512602, 0.0100092924151711, 0.0100248794391812, 0.0350100726684121, 0.0350135607215167, 0.0350314757912309, 0.0350861161298813, 0.11003536702437203, 0.11004306222317999, 0.11009411413007199, 0.110262204738018]), ([40.0, 405.0, 1005.0, 2000.0], [0.1101, 1.1], [0.11010863241753101, 0.11011332396601801, 0.11011698502153701, 0.11013607882270099, 1.10009134468776, 1.1001042156470102, 1.10015690654585, 1.10037547232962]), ([40.0, 405.0, 1005.0, 2000.0], [1.101, 11.0], [1.10051217185966, 1.10052093765244, 1.10057386098388, 1.10072789684985, 10.9949479016285, 10.994928028529701, 10.995235972542101, 10.9970302873191]), ([40.0, 405.0, 1005.0, 2000.0], [11.001, 110.0], [11.001935725372899, 11.0016749465013, 11.0020166913847, 11.0046770478365, 109.992142171693, 109.991246710281, 109.995711544914, 110.015757665742]), ([40.0, 405.0, 1005.0, 2000.0], [110.01, 250.0, 600.0], [110.027318391615, 110.02896730723398, 110.034971609218, 110.057689144301, 250.02470902624103, 250.028061604601, 250.043111533623, 250.09813645338096, 600.043738332903, 600.06316858885, 600.100835715896, 600.22667306978])]})

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

    def show_equal_cell_configs_button_toggled(self, a_enable: bool):
        self.measure_manager.show_equal_cell_configs(a_enable)

    def switch_to_active_cell_action_toggled(self, a_enable: bool):
        self.settings.switch_to_active_cell = int(a_enable)

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

    def open_cell_configuration(self):
        self.measure_manager.open_cell_configuration()

    def set_meter(self, a_index: int):
        self.measure_manager.set_meter(MeterType(a_index))

    def open_meter_settings(self):
        self.measure_manager.open_meter_settings()

    def set_displayed_data(self, a_displayed_data: int):
        self.measure_manager.set_displayed_data(CellData.GetDataType(a_displayed_data))

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

        self.measure_conductor = MeasureConductor(self.calibrator, self.netvars, self.ftdi_control,
                                                  self.measure_manager, self.settings)
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
                self.settings.save_geometry(self.ui.mainwindow_splitter.objectName(),
                                            self.ui.mainwindow_splitter.saveState())
                self.settings.save_geometry(self.ui.mainwindow_splitter_2.objectName(),
                                            self.ui.mainwindow_splitter_2.saveState())
                self.settings.save_geometry(self.ui.measures_table.objectName(),
                                            self.ui.measures_table.horizontalHeader().saveState())
                self.settings.save_geometry(self.objectName(), self.saveGeometry())
                a_event.accept()
