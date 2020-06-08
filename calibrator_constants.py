import enum

from utils import bound


MAX_CURRENT = 11
MIN_CURRENT = -11

MAX_VOLTAGE = 630
MIN_VOLTAGE = -630

MIN_ALTERNATIVE = 0

MAX_FREQUENCY = 2000
MIN_FREQUENCY = 35

FREQUENCY_MIN_STEP = 1

SHORT_CIRCUIT_PASSWORD = 4242
MANUAL_MODE_ENABLE_PASSWORD = 8925
SHUTDOWN_EXECUTE_PASSWORD = 5298


class Polatiry(enum.IntEnum):
    POS = 0
    NEG = 1


int_to_polarity = {
    Polatiry.POS: "+",
    Polatiry.NEG: "-"
}


class SignalType(enum.IntEnum):
    ACI = 0
    ACV = 1
    DCI = 2
    DCV = 3


class Mode(enum.IntEnum):
    SOURCE = 0
    FIXED_RANGE = 1
    DETUNING = 2


class State(enum.IntEnum):
    DISCONNECTED = 0
    STOPPED = 1
    WAITING_SIGNAL = 2
    READY = 3


enum_to_state = {
    State.DISCONNECTED: "Соединение отсутствует",
    State.STOPPED: "Остановлен",
    State.WAITING_SIGNAL: "Установка сигнала...",
    State.READY: "Готов"
}

enum_to_mode = {
    Mode.SOURCE: "Источник",
    Mode.FIXED_RANGE: "Фиксированный",
    Mode.DETUNING: "Расстройка",
}

enum_to_signal_type = {
    SignalType.ACI: "Переменный ток",
    SignalType.ACV: "Переменное напряжение",
    SignalType.DCI: "Постоянный ток",
    SignalType.DCV: "Постоянное напряжение"
}

enum_to_signal_type_short = {
    SignalType.ACI: "I~",
    SignalType.ACV: "U~",
    SignalType.DCI: "I=",
    SignalType.DCV: "U="
}

signal_type_to_units = {
    SignalType.ACI: "А",
    SignalType.DCI: "А",
    SignalType.ACV: "В",
    SignalType.DCV: "В"
}

is_dc_signal = {
    SignalType.ACI: False,
    SignalType.ACV: False,
    SignalType.DCI: True,
    SignalType.DCV: True
}

is_ac_signal = {
    SignalType.ACI: True,
    SignalType.ACV: True,
    SignalType.DCI: False,
    SignalType.DCV: False
}

is_voltage_signal = {
    SignalType.ACI: False,
    SignalType.DCI: False,
    SignalType.ACV: True,
    SignalType.DCV: True
}

signal_type_to_min_step = {
    SignalType.ACI: 2e-6,
    SignalType.ACV: 2e-6,
    SignalType.DCI: 2e-9,
    SignalType.DCV: 2e-7,
}

error_code_to_message = {
    257: "Перегрев аналоговой платы",
    258: "Перегрев платы питания",
    259: "Перегрев транзистора постоянного тока 10 А",
    260: "Перегрев элемента Пельтье №1",
    261: "Перегрев элемента Пельтье №2",
    262: "Перегрев элемента Пельтье №3",
    263: "Перегрев элемента Пельтье №4",
    4104: "Нестабильное напряжение на стабилизаторе 12 В",
    4105: "Нестабильное напряжение на стабилизаторе 9 В",
    4106: "Нестабильное напряжение на стабилизаторе 5 В",
    4107: "Нестабильное напряжение на стабилизаторе +2,5 В",
    4108: "Нестабильное напряжение на стабилизаторе -2,5 В",
    4109: "Нестабильное напряжение на источнике питания вентиляторов",
    4110: "Стабилизатор 4 В не вышел на режим",
    4111: "Стабилизатор 45 В не вышел на режим",
    4112: "Стабилизатор 650 В не вышел на режим",
    4113: "Не удалось выйти на режим",
    4114: "Не удалось выйти на режим, слишком большое сопротивление",
    4115: "Превышение тока",
    4116: "Не удалось выделить память",
    4117: "Сторожевой таймер перезагрузил установку",
    4118: "Ошибка при чтении основных настроек",
    4119: "Слишком много ошибок",
    4120: "Сброс EEPROM Пельтье 4",
    4121: "Слишком низкое сопротивление нагрузки. Прибор не может выйти на режим",
    4122: "Обнаружено короткое замыкание",
    129: "SD карта не обнаружена. Калибровка прибора нарушена",
    140: "Не удалось смонтировать файловую систему. Калибровка прибора нарушена",
}


def bound_amplitude(a_amplitude: float, a_signal_type: SignalType):
    min_value = MIN_VOLTAGE
    max_value = MAX_VOLTAGE
    if not is_voltage_signal[a_signal_type]:
        min_value = MIN_CURRENT
        max_value = MAX_CURRENT
    if is_ac_signal[a_signal_type]:
        min_value = MIN_ALTERNATIVE
    return round(bound(a_amplitude, min_value, max_value), 9)


def bound_frequency(a_frequency: float, a_signal_type: SignalType):
    min_frequency = MIN_FREQUENCY if is_ac_signal[a_signal_type] else 0
    max_frequency = MAX_FREQUENCY if is_ac_signal[a_signal_type] else 0
    return round(bound(a_frequency, min_frequency, max_frequency), 9)
