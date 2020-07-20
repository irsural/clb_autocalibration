from collections import namedtuple
from typing import Iterable, Dict, List, Tuple
from enum import IntEnum
import logging

from irspy.dlls.ftdi_control import FtdiControl, FtdiPin
from irspy import utils


from edit_cell_config_dialog import CellConfig

BistableRelay = namedtuple("BistableRelay", "set_pin reset_pin")


class SchemeControl:
    RESET_RELAYS_TIME_S = 0.1

    # Из "\\5-10\dev\Калибратор\Конструкция\Схема и плата\Тестовые платы\clb_autotest_analog\
    # Сборочная документация clb_autotest_analog Плата автотестирования калибратора Р0 И01\
    # Схема принципиальная clb_autotest_analog Р0 И01.PDF"

    class Circuit(IntEnum):
        K_V = 0
        K_C10A = 1
        K_C1A = 2
        K_C01A = 3
        K_BP = 4
        K_A = 5
        K_DIV650 = 6
        K_DIV500 = 7
        K_DIV350 = 8
        K_DIV200 = 9
        K_DIV55 = 10
        K_DIV40 = 11
        K_AMP30M = 12
        K_AMP10M = 13

    COIL_TO_CIRCUITS: Dict[CellConfig.Coil, List[Circuit]] = {
        CellConfig.Coil.NONE: [],
        CellConfig.Coil.VAL_10_OHM: [Circuit.K_C10A],
        CellConfig.Coil.VAL_1_OHM: [Circuit.K_C1A],
        CellConfig.Coil.VAL_0_01_OHM: [Circuit.K_C01A],
    }

    DIVIDER_TO_CIRCUITS: Dict[CellConfig.Divider, List[Circuit]] = {
        CellConfig.Divider.NONE: [],
        CellConfig.Divider.DIV_650_V: [Circuit.K_BP, Circuit.K_DIV650],
        CellConfig.Divider.DIV_500_V: [Circuit.K_BP, Circuit.K_DIV500],
        CellConfig.Divider.DIV_350_V: [Circuit.K_BP, Circuit.K_DIV350],
        CellConfig.Divider.DIV_200_V: [Circuit.K_BP, Circuit.K_DIV200],
        CellConfig.Divider.DIV_55_V: [Circuit.K_BP, Circuit.K_DIV55],
        CellConfig.Divider.DIV_40_V: [Circuit.K_BP, Circuit.K_DIV40],
        CellConfig.Divider.MUL_30_mV: [Circuit.K_BP, Circuit.K_AMP30M],
        CellConfig.Divider.MUL_10_mV: [Circuit.K_BP, Circuit.K_AMP10M],
    }

    METER_TO_CIRCUITS: Dict[CellConfig.Meter, List[Circuit]] = {
        CellConfig.Meter.AMPERES: [Circuit.K_A],
        CellConfig.Meter.VOLTS: [Circuit.K_V],
    }

    # noinspection PyProtectedMember
    CIRCUIT_TO_RELAYS: Dict[Circuit, Tuple[BistableRelay]] = {
        Circuit.K_V: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_C10A: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0))
        ),
        Circuit.K_C1A: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0))
        ),
        Circuit.K_C01A: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0))
        ),
        Circuit.K_BP: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_A: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_DIV650: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_DIV500: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_DIV350: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_DIV200: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_DIV55: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_DIV40: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_AMP30M: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
        Circuit.K_AMP10M: (
            BistableRelay(
                set_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0),
                reset_pin=FtdiPin(channel=FtdiControl.Channel.A, bus=FtdiControl.Bus.C, pin=FtdiControl.Pin._0)),
        ),
    }

    class RelayState(IntEnum):
        OFF = 0
        ON = 1

    def __init__(self, a_ftdi_control: FtdiControl):
        self.__ftdi_control = a_ftdi_control

        self.__coil = CellConfig.Coil.NONE
        self.__divider = CellConfig.Divider.NONE
        self.__meter = CellConfig.Meter.AMPERES

        self.__set_relays_timer = utils.Timer(SchemeControl.RESET_RELAYS_TIME_S)
        self.__unset_relays_timer = utils.Timer(SchemeControl.RESET_RELAYS_TIME_S)

        self.__ready = False

    def connect(self) -> bool:
        self.__ready = False
        return self.__ftdi_control.reinit()

    def is_connected(self) -> bool:
        return self.__ftdi_control.is_connected()

    def __set_relays(self, a_circuits: Iterable[Circuit], a_state: RelayState):
        """
        Устанавливает все реле во всех переданных цепях в состояние a_state
        :param a_circuits: Список цепей
        :param a_state: Состояние реле
        :return: None
        """
        for circuit in a_circuits:
            for relay in SchemeControl.CIRCUIT_TO_RELAYS[circuit]:
                logging.debug(f"set scheme: {circuit.name}, state: {a_state.name}, relay: {relay}")
                if a_state == SchemeControl.RelayState.ON:
                    self.__ftdi_control.set_pin(relay.set_pin, True)
                else:
                    self.__ftdi_control.set_pin(relay.reset_pin, True)

    def __unset_relays(self, a_circuits: Iterable[Circuit]):
        """
        Сбрасывает пины установки состояния всех реле во всех переданных цепях
        :param a_circuits: Список цепей
        :return: None
        """
        for circuit in a_circuits:
            for relay in SchemeControl.CIRCUIT_TO_RELAYS[circuit]:
                logging.debug(f"unset scheme: {circuit.name}, relay: {relay}")
                self.__ftdi_control.set_pin(relay.set_pin, False)
                self.__ftdi_control.set_pin(relay.reset_pin, False)

    def set_up(self, a_coil: CellConfig.Coil, a_divider: CellConfig.Divider, a_meter: CellConfig.Meter) -> bool:
        self.__coil = CellConfig.Coil.NONE
        self.__divider = CellConfig.Divider.NONE
        self.__meter = CellConfig.Meter.AMPERES
        self.__ready = False

        # Переводим реле на всех цепях в состояние OFF
        self.__set_relays(SchemeControl.CIRCUIT_TO_RELAYS.keys(), SchemeControl.RelayState.OFF)
        # Переводим реле на необходимых цепях в состояние ON
        self.__set_relays(SchemeControl.COIL_TO_CIRCUITS[a_coil], SchemeControl.RelayState.ON)
        self.__set_relays(SchemeControl.DIVIDER_TO_CIRCUITS[a_divider], SchemeControl.RelayState.ON)
        self.__set_relays(SchemeControl.METER_TO_CIRCUITS[a_meter], SchemeControl.RelayState.ON)

        self.__unset_relays_timer.stop()
        self.__set_relays_timer.start()

        result = self.__ftdi_control.write_changes()
        return result

    def reset(self) -> bool:
        self.__coil = CellConfig.Coil.NONE
        self.__divider = CellConfig.Divider.NONE
        self.__meter = CellConfig.Meter.AMPERES
        self.__ready = False

        # Переводим реле на всех цепях в состояние OFF
        self.__set_relays(SchemeControl.CIRCUIT_TO_RELAYS.keys(), SchemeControl.RelayState.OFF)

        self.__unset_relays_timer.stop()
        self.__set_relays_timer.start()

        result = self.__ftdi_control.write_changes()
        return result

    def get_coil(self):
        return self.__coil

    def get_meter(self):
        return self.__meter

    def get_divider(self):
        return self.__divider

    def tick(self):
        if self.__set_relays_timer.check():
            self.__set_relays_timer.stop()

            self.__unset_relays(SchemeControl.CIRCUIT_TO_RELAYS.keys())
            self.__ftdi_control.write_changes()

            self.__unset_relays_timer.start()

        if self.__unset_relays_timer.check():
            self.__unset_relays_timer.stop()

            self.__ready = True

    def ready(self) -> bool:
        return self.__ready
