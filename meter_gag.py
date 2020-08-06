import random

from irspy import utils


class MeterGag:
    def __init__(self):
        self.lower_bound = 0
        self.upper_bound = 0

    def connect(self):
        return True

    def is_connected(self):
        return True

    def set_measured_amplitude(self, a_amplitude):
        self.lower_bound = utils.increase_by_percent(a_amplitude, 2)
        self.upper_bound = utils.decrease_by_percent(a_amplitude, 2)

    def get_measured_value(self):
        return random.uniform(self.lower_bound, self.upper_bound)
