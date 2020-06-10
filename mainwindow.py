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
import irspy.dlls.ftdi_dll as ftdi_dll
import irspy.clb.clb_dll as clb_dll
import irspy.utils as utils
from enum import IntEnum


class MainWindow(QtWidgets.QMainWindow):
    clb_list_changed = QtCore.pyqtSignal([list])
    usb_status_changed = QtCore.pyqtSignal(clb.State)
    signal_enable_changed = QtCore.pyqtSignal(bool)

    class MeasureColumn(IntEnum):
        NAME = 0
        SETTINGS = 1
        ENABLE = 2

    def __init__(self):
        super().__init__()

        self.ui = MainForm()
        self.ui.setupUi(self)

        try:
            self.settings = Settings("./settings.ini", [
                Settings.VariableInfo(a_name="fixed_step_list", a_section="PARAMETERS",
                                      a_type=Settings.ValueType.LIST_FLOAT, a_default=[0.0001,0.01,0.1,1,10,20,100]),
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

            self.show()

            self.configuration_changed = False

            self.ui.enter_settings_action.triggered.connect(self.open_settings)
            self.ui.open_tstlan_action.triggered.connect(self.open_tstlan)
            self.ui.save_action.triggered.connect(self.save_configuration)
            self.ui.clb_list_combobox.currentTextChanged.connect(self.connect_to_clb)
            self.ui.add_measure_button.clicked.connect(self.add_measure_button_clicked)

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
        selected_row = qt_utils.get_selected_row(self.ui.measures_table)
        row_index = selected_row if selected_row is not None else self.ui.measures_table.rowCount()
        self.ui.measures_table.insertRow(row_index)
        self.ui.measures_table.setItem(row_index, MainWindow.MeasureColumn.NAME,
                                       QtWidgets.QTableWidgetItem("Новое измерение"))

        button = QtWidgets.QToolButton()
        self.ui.measures_table.setCellWidget(row_index, MainWindow.MeasureColumn.SETTINGS, qt_utils.wrap_in_layout(button))
        cb = QtWidgets.QCheckBox()
        self.ui.measures_table.setCellWidget(row_index, MainWindow.MeasureColumn.ENABLE, qt_utils.wrap_in_layout(cb))

        self.configuration_changed = True

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

    def save_configuration(self) -> bool:
        self.configuration_changed = False
        return True

    def closeEvent(self, a_event: QtGui.QCloseEvent):
        if self.configuration_changed:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Предупреждение")
            msgbox.setText("Текущая конфигурация не сохранена. Выберите действие")
            save_button = msgbox.addButton("Сохранить и выйти", QtWidgets.QMessageBox.YesRole)
            no_save_button = msgbox.addButton("Выйти без сохранения", QtWidgets.QMessageBox.AcceptRole)
            cancel_button = msgbox.addButton("Отмена", QtWidgets.QMessageBox.AcceptRole)
            msgbox.exec()

            if msgbox.clickedButton() == save_button:
                if self.save_configuration():
                    self.configuration_changed = False
                    a_event.ignore()
                    self.clb_signal_off_timer.start(self.SIGNAL_OFF_TIME_MS)
                else:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Не удалось сохранить конфигурацию")
                    a_event.ignore()

            elif msgbox.clickedButton() == no_save_button:
                self.configuration_changed = False
                a_event.ignore()
                self.clb_signal_off_timer.start(self.SIGNAL_OFF_TIME_MS)
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
