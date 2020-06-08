import logging

from PyQt5 import QtWidgets, QtCore, QtGui

from settings_ini_parser import Settings, BadIniException
from ui.py.mainwindow import Ui_MainWindow as MainForm
from source_mode_window import SourceModeWidget
from network_variables import NetworkVariables
from settings_dialog import SettingsDialog
from tstlan_dialog import TstlanDialog
from qt_utils import QTextEditLogger
import calibrator_constants as clb
import constants as cfg
import clb_dll
import utils


class MainWindow(QtWidgets.QMainWindow):
    clb_list_changed = QtCore.pyqtSignal([list])
    usb_status_changed = QtCore.pyqtSignal(clb.State)
    signal_enable_changed = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.ui = MainForm()
        self.ui.setupUi(self)

        try:
            self.settings = Settings("./settings.ini", [
                Settings.VariableInfo(a_name="fixed_step_list", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_FLOAT, a_default=[0.0001,0.01,0.1,1,10,20,100]),
                Settings.VariableInfo(a_name="checkbox_states", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
                Settings.VariableInfo(a_name="fixed_step_idx", a_section="PARAMETERS", a_type=Settings.ValueType.INT),
                Settings.VariableInfo(a_name="rough_step", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.5),
                Settings.VariableInfo(a_name="common_step", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.05),
                Settings.VariableInfo(a_name="exact_step", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.002),
                Settings.VariableInfo(a_name="tstlan_update_time", a_section="PARAMETERS", a_type=Settings.ValueType.FLOAT, a_default=0.2),
                Settings.VariableInfo(a_name="tstlan_show_marks", a_section="PARAMETERS", a_type=Settings.ValueType.INT, a_default=0),
                Settings.VariableInfo(a_name="tstlan_marks", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
                Settings.VariableInfo(a_name="tstlan_graphs", a_section="PARAMETERS", a_type=Settings.ValueType.LIST_INT),
            ])

            ini_ok = True
        except BadIniException:
            ini_ok = False
            QtWidgets.QMessageBox.critical(self, "Ошибка", 'Файл конфигурации поврежден. Пожалуйста, '
                                                           'удалите файл "settings.ini" и запустите программу заново')
        if ini_ok:
            self.restoreGeometry(self.settings.get_last_geometry(self.__class__.__name__))
            self.ui.splitter.restoreState(self.settings.get_last_geometry(self.ui.splitter.__class__.__name__ + "1"))

            self.set_up_logger()

            self.clb_driver = clb_dll.set_up_driver(clb_dll.debug_dll_path)

            modbus_registers_count = 700
            self.usb_driver = clb_dll.UsbDrv(self.clb_driver, modbus_registers_count * 2)
            self.usb_state = clb_dll.UsbDrv.UsbState.DISABLED
            self.calibrator = clb_dll.ClbDrv(self.clb_driver)
            self.clb_state = clb.State.DISCONNECTED

            self.netvars = NetworkVariables(cfg.CLB_CONFIG_PATH, self.calibrator)

            self.clb_signal_off_timer = QtCore.QTimer()
            # noinspection PyTypeChecker
            self.clb_signal_off_timer.timeout.connect(self.close)
            self.SIGNAL_OFF_TIME_MS = 200

            self.ui.enter_settings_action.triggered.connect(self.open_settings)

            self.source_mode_widget = self.set_up_source_mode_widget()
            self.show()

            self.source_mode_widget.ui.open_tstlan_button.clicked.connect(self.open_tstlan)

            self.tick_timer = QtCore.QTimer(self)
            self.tick_timer.timeout.connect(self.tick)
            self.tick_timer.start(10)
        else:
            self.close()

    def set_up_logger(self):
        log = QTextEditLogger(self, self.ui.log_text_edit)
        log.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))

        logging.getLogger().addHandler(log)
        # logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.INFO)
        # logging.getLogger().setLevel(logging.WARN)

    def set_up_source_mode_widget(self) -> SourceModeWidget:
        source_mode_widget = SourceModeWidget(self.settings, self.calibrator, self.netvars, self)
        self.clb_list_changed.connect(source_mode_widget.update_clb_list)
        self.usb_status_changed.connect(source_mode_widget.update_clb_status)
        self.signal_enable_changed.connect(source_mode_widget.signal_enable_changed)
        self.ui.source_mode_layout.addWidget(source_mode_widget)
        return source_mode_widget

    def tick(self):
        self.usb_tick()

    def usb_tick(self):
        self.usb_driver.tick()

        if self.usb_driver.is_dev_list_changed():
            self.clb_list_changed.emit(self.usb_driver.get_dev_list())

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

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        if self.calibrator.signal_enable:
            self.calibrator.signal_enable = False
            self.clb_signal_off_timer.start(self.SIGNAL_OFF_TIME_MS)
            a_event.ignore()
        else:
            self.settings.save_geometry(self.ui.splitter.__class__.__name__ + "1", self.ui.splitter.saveState())
            self.settings.save_geometry(self.__class__.__name__, self.saveGeometry())
            a_event.accept()
