import logging

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QTimer


from ui.py.source_mode_form import Ui_Form as SourceModeForm
from network_variables import NetworkVariables
import calibrator_constants as clb
from settings_ini_parser import Settings
import qt_utils
import clb_dll
import utils


class SourceModeWidget(QtWidgets.QWidget):
    close_confirmed = pyqtSignal()

    def __init__(self, a_settings: Settings, a_calibrator: clb_dll.ClbDrv, a_network_variables: NetworkVariables,
                 a_parent=None):
        super().__init__(a_parent)

        self.ui = SourceModeForm()
        self.ui.setupUi(self)

        self.pause_icon = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/play.png"))
        self.play_icon = QtGui.QIcon(QtGui.QPixmap(":/icons/icons/pause.png"))
        self.ui.enable_button.setIconSize(QtCore.QSize(25, 25))

        self.settings = a_settings

        self.calibrator = a_calibrator
        self.clb_state = clb.State.DISCONNECTED
        self.signal_type = clb.SignalType.ACI
        self.mode = clb.Mode.SOURCE

        self.netvars = a_network_variables

        self.units = clb.signal_type_to_units[self.signal_type]
        self.value_to_user = utils.value_to_user_with_units(self.units)

        self.connect_signals()

        self.update_signal_enable_state(self.calibrator.signal_enable)

        self.signal_type_to_radio = {
            clb.SignalType.ACI: self.ui.aci_radio,
            clb.SignalType.ACV: self.ui.acv_radio,
            clb.SignalType.DCI: self.ui.dci_radio,
            clb.SignalType.DCV: self.ui.dcv_radio,
        }
        self.mode_to_radio = {
            clb.Mode.SOURCE: self.ui.source_mode_radio,
            clb.Mode.FIXED_RANGE: self.ui.fixed_mode_radio,
            clb.Mode.DETUNING: self.ui.detuning_radio,
        }

        self.clb_check_timer = QTimer()
        self.clb_check_timer.timeout.connect(self.sync_clb_parameters)
        self.clb_check_timer.start(10)

        self.update_netvars_timer = QTimer()
        self.update_netvars_timer.timeout.connect(self.update_netvars)
        self.update_netvars_timer.start(self.settings.tstlan_update_time * 1000)

        self.next_error_timer = QTimer()
        self.next_error_timer.timeout.connect(self.show_next_error)
        self.next_error_index = 0

        self.ui.errors_out_button.clicked.connect(self.start_errors_output)

    def __del__(self):
        print("source mode deleted")

    def connect_signals(self):
        self.ui.clb_list_combobox.currentTextChanged.connect(self.connect_to_clb)

        self.ui.enable_button.clicked.connect(self.enable_signal)

        self.ui.aci_radio.clicked.connect(self.aci_radio_checked)
        self.ui.acv_radio.clicked.connect(self.acv_radio_checked)
        self.ui.dci_radio.clicked.connect(self.dci_radio_checked)
        self.ui.dcv_radio.clicked.connect(self.dcv_radio_checked)

        self.ui.detuning_radio.clicked.connect(self.detuning_radio_checked)
        self.ui.fixed_mode_radio.clicked.connect(self.fixed_radio_checked)
        self.ui.source_mode_radio.clicked.connect(self.source_radio_checked)

        self.ui.amplitude_edit.textEdited.connect(self.amplitude_edit_text_changed)
        self.ui.apply_amplitude_button.clicked.connect(self.apply_amplitude_button_clicked)
        self.ui.amplitude_edit.returnPressed.connect(self.apply_amplitude_button_clicked)

        self.ui.frequency_edit.textEdited.connect(self.frequency_edit_text_changed)
        self.ui.apply_frequency_button.clicked.connect(self.apply_frequency_button_clicked)
        self.ui.frequency_edit.returnPressed.connect(self.apply_frequency_button_clicked)

    def update_clb_list(self, a_clb_list: list):
        self.ui.clb_list_combobox.clear()
        for clb_name in a_clb_list:
            self.ui.clb_list_combobox.addItem(clb_name)

    def update_clb_status(self, a_status: clb.State):
        self.clb_state = a_status
        self.ui.clb_state_label.setText(clb.enum_to_state[a_status])

    def connect_to_clb(self, a_clb_name):
        self.calibrator.connect(a_clb_name)

    def sync_clb_parameters(self):
        if self.calibrator.amplitude_changed():
            self.set_amplitude(self.calibrator.amplitude)

        if self.calibrator.frequency_changed():
            self.set_frequency(self.calibrator.frequency)

        if self.calibrator.signal_type_changed():
            self.signal_type = self.calibrator.signal_type
            self.signal_type_to_radio[self.signal_type].setChecked(True)
            self.update_signal_type(self.signal_type)

        if self.calibrator.mode_changed():
            self.mode = self.calibrator.mode
            self.mode_to_radio[self.mode].setChecked(True)

    def update_netvars(self):
        self.ui.fast_adc_label.setText(f"({utils.float_to_string(self.netvars.fast_adc_slow.get())})")

        firmware_type = "RELEASE" if self.netvars.release_firmware.get() else "DEBUG"
        self.ui.firmware_info_label.setText(f"{self.netvars.software_revision.get()} {firmware_type}")

        self.ui.errors_count_label.setText(str(self.netvars.error_count.get()))
        if self.netvars.error_count.get() > 0:
            self.ui.errors_label.setStyleSheet("QLabel { color : red; }")
        else:
            self.ui.errors_label.setStyleSheet("QLabel { color : black; }")

    def enable_signal(self, a_signal_enable):
        self.calibrator.signal_enable = a_signal_enable
        self.update_signal_enable_state(a_signal_enable)

    def signal_enable_changed(self, a_enable):
        if a_enable:
            self.update_signal_enable_state(True)
        else:
            self.update_signal_enable_state(False)

    def update_signal_enable_state(self, a_signal_enabled: bool):
        if a_signal_enabled:
            self.ui.enable_button.setIcon(self.play_icon)
            self.ui.enable_button.setText("Стоп")
        else:
            self.ui.enable_button.setIcon(self.pause_icon)
            self.ui.enable_button.setText("Старт")

        self.ui.enable_button.setChecked(a_signal_enabled)

        self.ui.dcv_radio.setDisabled(a_signal_enabled)
        self.ui.dci_radio.setDisabled(a_signal_enabled)
        self.ui.acv_radio.setDisabled(a_signal_enabled)
        self.ui.aci_radio.setDisabled(a_signal_enabled)

        self.ui.fixed_mode_radio.setDisabled(a_signal_enabled)
        self.ui.detuning_radio.setDisabled(a_signal_enabled)
        self.ui.source_mode_radio.setDisabled(a_signal_enabled)

    # noinspection PyTypeChecker
    def wheelEvent(self, event: QtGui.QWheelEvent):
        steps = qt_utils.get_wheel_steps(event)

        keys = event.modifiers()
        if keys & QtCore.Qt.ShiftModifier:
            self.tune_amplitude(self.settings.exact_step * steps)
        elif keys & QtCore.Qt.ControlModifier:
            self.tune_amplitude(self.settings.rough_step * steps)
        else:
            self.tune_amplitude(self.settings.common_step * steps)

        event.accept()

    def set_amplitude(self, a_amplitude: float):
        self.calibrator.amplitude = clb.bound_amplitude(a_amplitude, self.signal_type)
        self.ui.amplitude_edit.setText(self.value_to_user(self.calibrator.amplitude))
        self.amplitude_edit_text_changed()

    def tune_amplitude(self, a_step):
        self.set_amplitude(utils.relative_step_change(self.calibrator.amplitude, a_step,
                                                      clb.signal_type_to_min_step[self.signal_type],
                                                      a_normalize_value=self.calibrator.amplitude))

    def amplitude_edit_text_changed(self):
        try:
            parsed = utils.parse_input(self.ui.amplitude_edit.text())
        except ValueError:
            parsed = ""
        qt_utils.update_edit_color(self.calibrator.amplitude, parsed, self.ui.amplitude_edit)

    def apply_amplitude_button_clicked(self):
        try:
            new_amplitude = utils.parse_input(self.ui.amplitude_edit.text())
            self.set_amplitude(new_amplitude)
        except ValueError:
            # Отлавливает некорректный ввод
            pass

    def set_frequency(self, a_frequency):
        self.calibrator.frequency = a_frequency
        current_frequency = 0 if clb.is_dc_signal[self.signal_type] else self.calibrator.frequency
        self.ui.frequency_edit.setText(utils.float_to_string(current_frequency))

    def frequency_edit_text_changed(self):
        qt_utils.update_edit_color(self.calibrator.frequency, self.ui.frequency_edit.text().replace(",", "."),
                                   self.ui.frequency_edit)

    def apply_frequency_button_clicked(self):
        try:
            new_frequency = utils.parse_input(self.ui.frequency_edit.text())
            self.set_frequency(new_frequency)
            self.frequency_edit_text_changed()
        except ValueError:
            # Отлавливает некорректный ввод
            pass

    def start_errors_output(self):
        if self.netvars.error_count.get() > 0:
            self.next_error_index = 0
            self.next_error_timer.start(1200)

    def show_next_error(self):
        error_index = self.netvars.error_index.get()
        error_count = self.netvars.error_count.get()
        if error_index >= error_count:
            # На случай если во время вывода ошибок их состояние было изменено извне
            self.next_error_timer.stop()
        else:
            if self.next_error_index == error_index:
                error_code = self.netvars.error_code.get()
                logging.warning(f"Ошибка №{error_index + 1}: "
                                f"Код {error_code}. {clb.error_code_to_message[error_code]}.")

                next_error_index = error_index + 1
                if next_error_index >= error_count:
                    self.netvars.clear_error_occurred_status.set(1)
                    self.next_error_timer.stop()
                else:
                    self.next_error_index = next_error_index
                    self.netvars.error_index.set(next_error_index)

    def aci_radio_checked(self):
        self.update_signal_type(clb.SignalType.ACI)

    def acv_radio_checked(self):
        self.update_signal_type(clb.SignalType.ACV)

    def dci_radio_checked(self):
        self.update_signal_type(clb.SignalType.DCI)

    def dcv_radio_checked(self):
        self.update_signal_type(clb.SignalType.DCV)

    def source_radio_checked(self):
        self.update_mode(clb.Mode.SOURCE)

    def fixed_radio_checked(self):
        self.update_mode(clb.Mode.FIXED_RANGE)

    def detuning_radio_checked(self):
        self.update_mode(clb.Mode.DETUNING)

    def update_signal_type(self, a_signal_type: clb.SignalType):
        if not self.calibrator.signal_enable:
            self.calibrator.signal_type = a_signal_type
            self.signal_type = a_signal_type

            self.units = clb.signal_type_to_units[self.signal_type]
            self.value_to_user = utils.value_to_user_with_units(self.units)

            self.set_amplitude(self.calibrator.amplitude)
            self.set_frequency(self.calibrator.frequency)

    def update_mode(self, a_mode: clb.Mode):
        if not self.calibrator.signal_enable:
            self.calibrator.mode = a_mode
            self.mode = a_mode

    def closeEvent(self, a_event: QtGui.QCloseEvent) -> None:
        self.calibrator.signal_enable = False
