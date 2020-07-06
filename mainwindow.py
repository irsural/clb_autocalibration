from enum import IntEnum
import logging

from PyQt5 import QtWidgets, QtCore, QtGui

from irspy.settings_ini_parser import Settings, BadIniException
from ui.py.mainwindow import Ui_MainWindow as MainForm
from source_mode_window import SourceModeWidget
from irspy.clb.network_variables import NetworkVariables
from settings_dialog import SettingsDialog
from tstlan_dialog import TstlanDialog
from irspy.qt import qt_utils
import irspy.clb.calibrator_constants as clb
from irspy.dlls.ftdi_dll import FtdiControl
from MeasureManager import MeasureManager
import irspy.dlls.ftdi_dll as ftdi_dll
import irspy.clb.clb_dll as clb_dll
import irspy.utils as utils


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

            self.set_up_logger()

            self.ftdi_driver = ftdi_dll.set_up_driver("../irspy/dlls/ftdi_dll.dll")
            self.ftdi = ftdi_dll.FtdiControl(self.ftdi_driver)

            self.clb_driver = clb_dll.set_up_driver("../irspy/clb/clb_driver_dll.dll")

            modbus_registers_count = 700
            self.usb_driver = clb_dll.UsbDrv(self.clb_driver, modbus_registers_count * 2)
            self.usb_state = clb_dll.UsbDrv.UsbState.DISABLED
            self.calibrator = clb_dll.ClbDrv(self.clb_driver)
            self.clb_state = clb.State.DISCONNECTED

            self.netvars = NetworkVariables(f"../irspy/clb/{clb.CLB_CONFIG_NAME}", self.calibrator)

            self.clb_signal_off_timer = QtCore.QTimer()
            # noinspection PyTypeChecker
            self.clb_signal_off_timer.timeout.connect(self.close)
            self.SIGNAL_OFF_TIME_MS = 200
            self.ignore_save = False

            self.current_configuration_path = ""

            self.show()

            self.measure_manager = MeasureManager(self.ui.measures_table, self.ui.measure_data_view, self.settings, self)
            self.open_configuration_by_name(self.settings.last_configuration_path)

            self.ui.lock_action.triggered.connect(self.lock_cell_button_clicked)
            self.ui.unlock_action.triggered.connect(self.unlock_cell_button_clicked)
            self.ui.show_equal_action.toggled.connect(self.show_equal_cell_configs_button_toggled)
            self.ui.add_row_button.clicked.connect(self.add_row_button_clicked)
            self.ui.remove_row_button.clicked.connect(self.remove_row_button_clicked)
            self.ui.add_column_button.clicked.connect(self.add_column_button_clicked)
            self.ui.remove_column_button.clicked.connect(self.remove_column_button_clicked)

            self.ui.measures_table.cellDoubleClicked.connect(self.measure_cell_double_clicked)
            self.ui.measures_table.cellChanged.connect(self.measure_cell_changed)
            self.ui.measure_data_view.clicked.connect(self.measure_data_cell_clicked)

            self.ui.enter_settings_action.triggered.connect(self.open_settings)
            self.ui.open_tstlan_action.triggered.connect(self.open_tstlan)
            self.ui.save_action.triggered.connect(self.save_configuration)
            self.ui.save_as_action.triggered.connect(self.save_configuration_as)
            self.ui.save_current_measure_button.clicked.connect(self.save_current_configuration)
            self.ui.open_cell_config_button.clicked.connect(self.open_cell_configuration)
            self.ui.open_action.triggered.connect(self.open_configuration)
            self.ui.clb_list_combobox.currentTextChanged.connect(self.connect_to_clb)
            self.ui.add_measure_button.clicked.connect(self.add_measure_button_clicked)
            self.ui.delete_measure_button.clicked.connect(self.remove_measure_button_clicked)

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
        self.ui.source_mode_layout.addWidget(source_mode_widget)
        return source_mode_widget

    def tick(self):
        self.usb_driver.tick()

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

    @utils.exception_decorator
    def add_measure_button_clicked(self, _):
        self.measure_manager.new_measure()

    @utils.exception_decorator
    def remove_measure_button_clicked(self, _):
        self.measure_manager.remove_measure(self.current_configuration_path)

    def measure_cell_double_clicked(self, a_row: int, a_column: int):
        self.measure_manager.rename_measure_started(a_row, a_column)

    def measure_cell_changed(self, a_row: int, a_column: int):
        self.measure_manager.rename_measure_finished(a_row, a_column, self.current_configuration_path)

    def measure_data_cell_clicked(self, index: QtCore.QModelIndex):
        if self.ui.show_equal_action.isChecked():
            self.measure_manager.set_cell_to_compare(index)

    def show_equal_cell_configs_button_toggled(self, a_enable: bool):
        self.measure_manager.show_equal_cell_configs(a_enable)

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

    def open_tstlan(self):
        try:
            tstlan_dialog = TstlanDialog(self.netvars, self.calibrator, self.settings, self)
            tstlan_dialog.exec()
        except Exception as err:
            logging.debug(utils.exception_handler(err))

    def open_settings(self):
        try:
            settings_dialog = SettingsDialog(self.settings, self)
            settings_dialog.exec()
        except Exception as err:
            logging.debug(utils.exception_handler(err))

    def open_cell_configuration(self):
        self.measure_manager.open_cell_configuration()

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
        else:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить конфигурации в каталоге {a_folder}",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
            result = False
        return result

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
        if self.measure_manager.load_from_file(a_folder):
            self.current_configuration_path = a_folder
            self.setWindowTitle(self.current_configuration_path)
        elif a_folder:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось нафти файлы конфигураций в каталоге {a_folder}",
                                           QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

    @staticmethod
    def close_configuration() -> CloseConfigOptions:
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle("Предупреждение")
        msgbox.setText("Текущая конфигурация не сохранена. Выберите действие")
        save_button = msgbox.addButton("Сохранить", QtWidgets.QMessageBox.YesRole)
        no_save_button = msgbox.addButton("Не сохранять", QtWidgets.QMessageBox.AcceptRole)
        cancel_button = msgbox.addButton("Отмена", QtWidgets.QMessageBox.AcceptRole)
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
        result = self.ftdi.write_gpio(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin._6, a_state)
        gpio_state = self.ftdi.read_gpio(FtdiControl.Channel.A, FtdiControl.Bus.D, FtdiControl.Pin._6)

    def reinit_button_clicked(self, _):
        self.ftdi.reinit()
