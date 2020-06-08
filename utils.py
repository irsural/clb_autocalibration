from linecache import checkcache, getline
from configparser import ConfigParser
import traceback
import logging
from enum import IntEnum
from sys import exc_info
import math
import time
import re


check_input_re = re.compile(
    r"(?P<number>^[-+]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][-+]?\d+)?) *(?P<units>(?:мк|м|н)?[аАвВ]?) *$")

check_input_no_python_re = re.compile(r"^[-+]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][-+]?\d+)? *(?:мк|м|н)?[аАвВ]?$")

find_number_re = re.compile(r"[-+]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][-+]?\d+)?")

__units_to_factor = {
    "": 1,
    "в": 1,
    "а": 1,

    "м": 1e-3,
    "мв": 1e-3,
    "ма": 1e-3,

    "мк": 1e-6,
    "мкв": 1e-6,
    "мка": 1e-6,

    "н": 1e-9,
    "нв": 1e-9,
    "на": 1e-9,
}


class __UnitsPrefix(IntEnum):
    NANO = 0
    MICRO = 1
    MILLI = 2
    NO = 3


__enum_to_units = {
    __UnitsPrefix.NANO: "н",
    __UnitsPrefix.MICRO: "мк",
    __UnitsPrefix.MILLI: "м",
    __UnitsPrefix.NO: "",
}


def parse_input(a_input: str, a_reverse_check=False):
    if not a_input:
        return 0.
    input_re = check_input_re.match(a_input)
    if not input_re:
        raise ValueError("Wrong units input format: {0}".format(a_input))

    number = float(input_re.group('number').replace(",", "."))
    factor = __units_to_factor[input_re.group("units").lower()]
    result = round(number * factor, 9)

    # print(f"S->V. Input: {a_input}. Parsed: {number} {input_re.group('units').lower()}. Result: {result}")
    if a_reverse_check:
        if value_to_user_with_units("В", False)(result) != a_input:
            if value_to_user_with_units("А", False)(result) != a_input:
                str_no_units = value_to_user_with_units("", False)(result)
                if a_input != str_no_units:
                    print("S->V reverse check is failed: {0} != {1}".format(a_input, str_no_units))

    return result


def value_to_user_with_units(a_postfix: str, a_reverse_check=False):
    def value_to_user(a_value):
        prefix_type = __UnitsPrefix.NO

        abs_value = abs(a_value)
        if abs_value == 0:
            a_value = 0
            prefix_type = __UnitsPrefix.NO
        elif abs_value < 1e-9:
            a_value = 0
            prefix_type = __UnitsPrefix.NANO
        elif abs_value < 1e-6:
            a_value *= 1e9
            prefix_type = __UnitsPrefix.NANO
        elif abs_value < 1e-3:
            a_value *= 1e6
            prefix_type = __UnitsPrefix.MICRO
        elif abs_value < 1:
            a_value *= 1e3
            prefix_type = __UnitsPrefix.MILLI
        result = round(a_value, 9)
        result_str = float_to_string(result)
        result_with_units = "{0} {1}{2}".format(result_str, __enum_to_units[prefix_type], a_postfix)

        # print(f"V->S. Input: {a_value}. Output: {result_str}")
        if a_reverse_check:
            parsed = parse_input(result_with_units, False)
            if result != parsed:
                print("V->S reverse check is failed: {0} != {1}".format(result, parsed))

        return result_with_units
    return value_to_user


def float_to_string(a_number: float):
    return "{0:.9f}".format(a_number).rstrip('0').rstrip('.').replace(".", ",")


def absolute_error(a_reference: float, a_value: float):
    return a_reference - a_value


def relative_error(a_reference: float, a_value: float, a_normalize: float):
    assert a_normalize != 0, "Normalize value must not be zero"
    return (a_reference - a_value) / a_normalize * 100


def variation(a_lval: float, a_rval: float):
    return abs(a_lval - a_rval)


def absolute_error_limit(a_normalize_value: float, a_error_percent: float):
    return a_normalize_value * a_error_percent / 100


def bound(a_value, a_min, a_max):
    return max(min(a_value, a_max), a_min)


def relative_step_change(a_value: float, a_step: float, a_min_step: float, a_normalize_value=None):
    value_sign = 1 if a_step >= 0 else -1
    if a_value == 0:
        return a_min_step * value_sign

    if not a_normalize_value:
        a_normalize_value = a_value

    absolute_step = abs(a_normalize_value * a_step)
    exp = int(math.floor(math.log10(absolute_step)))

    absolute_step /= pow(10., exp)

    def get_new_step(x, y):
        return x if absolute_step < math.sqrt(x * y) else y

    if absolute_step <= 2:
        new_step = 1. if absolute_step < math.sqrt(1 * 2) else 2
        test_step = get_new_step(1, 2)
    elif absolute_step < 5:
        new_step = 2. if absolute_step < math.sqrt(2 * 5) else 5
        test_step = get_new_step(2, 5)
    else:
        new_step = 5. if absolute_step < math.sqrt(5 * 10) else 10
        test_step = get_new_step(5, 10)

    assert new_step == test_step, "new: {0}, test: {1}. don't work".format(new_step, test_step)

    new_step *= pow(10., exp)
    new_step /= 100
    new_step = max(new_step, a_min_step)

    a_value += new_step * value_sign
    # Если это преобразование убрать, то шаг будет равномерным на любой амплитуде
    finish_value = math.ceil(a_value / new_step) * new_step if value_sign > 0 \
        else math.floor(a_value / new_step) * new_step

    return finish_value


def increase_by_percent(a_value, a_percent, a_normalize_value=None):
    normalize = a_normalize_value if a_normalize_value else a_value
    return a_value + abs(normalize) * a_percent / 100


def decrease_by_percent(a_value, a_percent, a_normalize_value=None):
    normalize = a_normalize_value if a_normalize_value else a_value
    return a_value - abs(normalize) * a_percent / 100


def save_settings(a_path: str, a_config: ConfigParser):
    with open(a_path, 'w') as config_file:
        a_config.write(config_file)


def calc_smooth_approach(a_from, a_to, a_count, a_dt, sigma=0.01):
    """
    Вычисляет экспоненциальное изменение величины во времени от a_from до a_to с ассимптотическим подходом к a_to
    :param a_from: Стартовое значение
    :param a_to: Конечное значение
    :param a_count: Количество точек между a_from и a_to
    :param a_dt: Дискрет времени, с которым должна изменяться величина
    :param sigma: Кэффициент плавного подхода. Чем меньше, там плавнее будет подход к a_to и тем резче будет
                  скачок в начале
    :return: Список точек, размером a_count
    """
    dt_stop = a_dt * a_count
    dt_stop_s = dt_stop / 1000
    a_k = -1 / dt_stop_s * math.log(sigma)

    delta = abs(a_from - a_to)
    slope = delta / (1 - math.e ** (-a_k * dt_stop_s))

    points = []
    for t in range(a_dt, dt_stop + a_dt, a_dt):

        point = a_from + slope * (1 - math.e**(-a_k * t / 1000)) if a_from < a_to else \
            a_from + slope * (math.e ** (-a_k * t / 1000) - 1)

        points.append(round(point, 9))

    return points


def exception_handler(a_exception):
    e_type, e_obj, e_tb = exc_info()
    frame = e_tb.tb_frame
    lineno = e_tb.tb_lineno
    filename = frame.f_code.co_filename
    checkcache(filename)
    line = getline(filename, lineno, frame.f_globals)
    return "Exception{0} in {1}\n"\
           "Line {2}: '{3}'\n"\
           "Message: {4}".format(type(a_exception), filename, lineno, line.strip(), a_exception)


def get_decorator(errors=(Exception, ), default_value=None, log_out_foo=print):
    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors:
                log_out_foo(traceback.format_exc())
                return default_value
        return new_func
    return decorator


exception_decorator = get_decorator(log_out_foo=logging.debug)
exception_decorator_print = get_decorator(log_out_foo=print)
assertion_decorator = get_decorator(errors=(AssertionError, ), log_out_foo=logging.debug)


def get_array_min_diff(a_array: list):
    unique_array = list(dict.fromkeys(a_array))
    min_diff = unique_array[-1] - unique_array[0]
    for i in range(len(unique_array) - 1):
        diff = unique_array[i + 1] - unique_array[i]
        min_diff = diff if diff < min_diff else min_diff
    return round(min_diff, 9)


class Timer:
    def __init__(self, a_interval_s: float):
        self.interval_s = a_interval_s
        self.start_time = 0
        self.stop_time = 0
        self.__started = False

    def start(self, a_interval_s=None):
        self.__started = True
        self.start_time = time.time()
        if a_interval_s is not None:
            self.interval_s = a_interval_s
        self.stop_time = self.start_time + self.interval_s

    def stop(self):
        self.start_time = 0
        self.stop_time = 0
        self.__started = False

    def check(self):
        if not self.__started:
            return False
        return time.time() > self.stop_time

    def started(self):
        return self.__started
