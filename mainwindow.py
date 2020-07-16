from os import system as os_system
from enum import IntEnum
import logging

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.qt.custom_widgets.QTableDelegates import TransparentPainterForWidget, TransparentPainterForView
from irspy.settings_ini_parser import Settings, BadIniException
from irspy.clb.network_variables import NetworkVariables
import irspy.clb.calibrator_constants as clb
from irspy.dlls.ftdi_control import FtdiControl
from irspy.metrology import ImpulseFilter
import irspy.clb.clb_dll as clb_dll
from irspy.dlls import mxsrlib_dll
from irspy.qt import qt_utils
import irspy.utils as utils

from ui.py.mainwindow import Ui_MainWindow as MainForm
from source_mode_window import SourceModeWidget
from MeasureConductor import MeasureConductor
from settings_dialog import SettingsDialog
from MeasureManager import MeasureManager
from tstlan_dialog import TstlanDialog


class MainWindow(QtWidgets.QMainWindow):
    clb_list_changed = QtCore.pyqtSignal([list])
    usb_status_changed = QtCore.pyqtSignal(clb.State)
    signal_enable_changed = QtCore.pyqtSignal(bool)

    class CloseConfigOptions(IntEnum):
        SAVE = 0
        DONT_SAVE = 1
        CANCEL = 2

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
            ])

            ini_ok = True
        except BadIniException:
            ini_ok = False
            QtWidgets.QMessageBox.critical(self, "Ошибка", 'Файл конфигурации поврежден. Пожалуйста, '
                                                           'удалите файл "settings.ini" и запустите программу заново')
        if ini_ok:
            self.restoreGeometry(self.settings.get_last_geometry(self.objectName()))
            self.ui.splitter.restoreState(self.settings.get_last_geometry(self.ui.splitter.objectName()))
            self.ui.splitter_2.restoreState(self.settings.get_last_geometry(self.ui.splitter_2.objectName()))
            self.ui.measures_table.horizontalHeader().restoreState(self.settings.get_last_header_state(
                self.ui.measures_table.objectName()))
            self.ui.measure_data_view.setItemDelegate(TransparentPainterForView(self.ui.measure_data_view, "#d4d4ff"))
            self.ui.measures_table.setItemDelegate(TransparentPainterForWidget(self.ui.measures_table, "#d4d4ff"))

            self.set_up_logger()

            self.mxsrclib_dll = mxsrlib_dll.set_up_mxsrclib_dll("../irspy/dlls/mxsrclib_dll.dll")
            ImpulseFilter.init_mxsrlib_dll(self.mxsrclib_dll)

            self.ftdi_control = FtdiControl(self.mxsrclib_dll)

            self.clb_driver = clb_dll.set_up_driver("../irspy/clb/clb_driver_dll.dll")

            modbus_registers_count = 700
            self.usb_driver = clb_dll.UsbDrv(self.clb_driver, modbus_registers_count * 2)
            self.usb_state = clb_dll.UsbDrv.UsbState.DISABLED
            self.calibrator = clb_dll.ClbDrv(self.clb_driver)
            self.clb_state = clb.State.DISCONNECTED

            self.netvars = NetworkVariables(f"../irspy/clb/{clb.CLB_CONFIG_NAME}", self.calibrator,
                                            a_variables_read_delay=0)

            self.clb_signal_off_timer = QtCore.QTimer()
            # noinspection PyTypeChecker
            self.clb_signal_off_timer.timeout.connect(self.close)
            self.SIGNAL_OFF_TIME_MS = 200
            self.ignore_save = False

            self.current_configuration_path = ""

            self.measure_progress_bar_value = 0

            self.show()

            self.measure_manager = MeasureManager(self.ui.measures_table,
                                                  self.ui.measure_data_view, self.settings, self)
            self.open_configuration_by_name(self.settings.last_configuration_path)

            self.measure_conductor = MeasureConductor(self.calibrator, self.netvars, self.ftdi_control,
                                                      self.measure_manager, self.settings)
            self.measure_conductor.all_measures_done.connect(self.measure_done)
            self.measure_conductor.single_measure_started.connect(self.single_measure_started)
            self.measure_conductor.single_measure_done.connect(self.single_measure_done)

            self.ui.lock_action.triggered.connect(self.lock_cell_button_clicked)
            self.ui.unlock_action.triggered.connect(self.unlock_cell_button_clicked)
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

            self.ui.measure_data_view.clicked.connect(self.measure_data_cell_clicked)
            self.ui.measure_data_view.customContextMenuRequested.connect(self.show_data_table_context_menu)

            self.ui.measures_table.customContextMenuRequested.connect(self.show_measures_table_context_menu)

            self.ui.enter_settings_action.triggered.connect(self.open_settings)
            self.ui.open_tstlan_action.triggered.connect(self.open_tstlan)
            # self.ui.correction_action.triggered.connect(self.toggle_correction)
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

            self.ui.show_cell_graph_action.triggered.connect(self.show_cell_graph)
            self.ui.measure_data_view.addAction(self.ui.show_cell_graph_action)

            self.ui.flash_current_measure_action.triggered.connect(self.flash_table)
            self.ui.measure_data_view.addAction(self.ui.flash_current_measure_action)
            self.ui.flash_diapason_of_cell_action.triggered.connect(self.flash_diapason_of_cell)
            self.ui.measure_data_view.addAction(self.ui.flash_diapason_of_cell_action)

            self.ui.meter_combobox.currentIndexChanged.connect(self.set_meter)
            self.ui.meter_settings_button.clicked.connect(self.open_meter_settings)

            self.tick_timer = QtCore.QTimer(self)
            self.tick_timer.timeout.connect(self.tick)
            self.tick_timer.start(10)

        else:
            self.close()

    def set_up_logger(self):
        log = qt_utils.QTextEditLogger(self, self.ui.log_text_edit)
        log.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

        logging.getLogger().addHandler(log)
        logging.getLogger().setLevel(logging.DEBUG)
        # logging.getLogger().setLevel(logging.INFO)
        # logging.getLogger().setLevel(logging.WARN)

    def set_up_source_mode_widget(self) -> SourceModeWidget:
        source_mode_widget = SourceModeWidget(self.settings, self.calibrator, self.netvars, self)
        self.clb_list_changed.connect(source_mode_widget.update_clb_list)
        self.usb_status_changed.connect(source_mode_widget.update_clb_status)
        self.signal_enable_changed.connect(source_mode_widget.signal_enable_changed)
        # self.ui.source_mode_layout.addWidget(source_mode_widget)
        return source_mode_widget

    def lock_interface(self, a_lock: bool):
        self.ui.open_action.setDisabled(a_lock)
        self.ui.save_action.setDisabled(a_lock)
        self.ui.save_as_action.setDisabled(a_lock)

        self.ui.start_all_action.setDisabled(a_lock)
        self.ui.continue_all_action.setDisabled(a_lock)

        self.ui.correction_action.setDisabled(a_lock)
        self.ui.flash_all_action.setDisabled(a_lock)
        self.ui.verify_action.setDisabled(a_lock)

        self.ui.lock_action.setDisabled(a_lock)
        self.ui.unlock_action.setDisabled(a_lock)

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
        self.ui.flash_diapason_of_cell_action.setDisabled(a_lock)

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

    def start_measure(self, a_iteration_type: MeasureManager.IterationType):
        measure_iterator = self.measure_manager.get_measure_iterator(a_iteration_type)
        if measure_iterator is not None:
            # Это происходит, когда нет выделенных ячеек
            if measure_iterator.get() is not None:
                if self.save_configuration():
                    self.lock_interface(True)
                    self.ui.measure_progress_bar.setMaximum(self.count_measure_length(a_iteration_type))

                    self.measure_conductor.start(measure_iterator)

    def progress_bars_handling(self):
        if self.measure_conductor.is_started():
            time_passed = self.measure_conductor.get_current_cell_time_passed()
            self.ui.curent_cell_progress_bar.setValue(time_passed)
            self.ui.measure_progress_bar.setValue(self.measure_progress_bar_value + time_passed)

    def single_measure_started(self):
        self.ui.curent_cell_progress_bar.setMaximum(self.measure_conductor.get_current_cell_time_duration())

    def single_measure_done(self):
        self.ui.curent_cell_progress_bar.setValue(0)
        self.measure_progress_bar_value = self.ui.measure_progress_bar.value()
        self.save_current_configuration()

    def measure_done(self):
        self.ui.curent_cell_progress_bar.setValue(0)
        self.ui.measure_progress_bar.setValue(0)
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

    def toggle_correction(self, _):
        logging.debug("Не реализовано")

    def copy_cell_config(self):
        self.measure_manager.copy_cell_config()

    def paste_cell_config(self):
        self.measure_manager.paste_cell_config()

    def copy_cell_value(self):
        self.measure_manager.copy_cell_value()

    def paste_cell_value(self):
        self.measure_manager.paste_cell_value()

    def show_cell_graph(self):
        logging.debug("Не реализовано")

    def flash_table(self):
        logging.debug("Не реализовано")

    def flash_diapason_of_cell(self):
        logging.debug("Не реализовано")

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
        menu.addAction(self.ui.flash_diapason_of_cell_action)
        menu.insertSeparator(self.ui.flash_current_measure_action)

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
        tstlan_dialog: QtWidgets.QDialog = self.findChild(QtWidgets.QDialog, "tstlan_dialog")
        if not tstlan_dialog:
            tstlan_dialog = TstlanDialog(self.netvars, self.calibrator, self.settings, self)
            tstlan_dialog.exec()
        else:
            tstlan_dialog.activateWindow()

    @utils.exception_decorator
    def open_settings(self, _):
        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()

    def open_cell_configuration(self):
        self.measure_manager.open_cell_configuration()

    def set_meter(self, a_index: int):
        self.measure_manager.set_meter(MeasureManager.MeterType(a_index))

    def open_meter_settings(self):
        self.measure_manager.open_meter_settings()

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
                # self.open_configuration_by_name(config_filename)
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

        self.measure_conductor = MeasureConductor(self.calibrator, self.ftdi_control, self.measure_manager,
                                                  self.settings)
        self.measure_conductor.all_measures_done.connect(self.measure_done)
        self.measure_conductor.single_measure_done.connect(self.single_measure_done)

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
                self.settings.save_geometry(self.ui.splitter.objectName(), self.ui.splitter.saveState())
                self.settings.save_geometry(self.ui.splitter_2.objectName(), self.ui.splitter_2.saveState())
                self.settings.save_geometry(self.ui.measures_table.objectName(),
                                            self.ui.measures_table.horizontalHeader().saveState())
                self.settings.save_geometry(self.objectName(), self.saveGeometry())
                a_event.accept()

    def pa6_button_clicked(self, a_state):
        result = self.ftdi_control.write_gpio(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin._6, a_state)
        gpio_state = self.ftdi_control.read_gpio(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin._6)
