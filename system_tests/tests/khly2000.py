import math
import unittest

from utils.test_modes import TestModes
from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.testing import get_running_lewis_and_ioc, assert_log_messages, skip_if_recsim, unstable_test, parameterized_list
from parameterized import parameterized


DEVICE_PREFIX = "KHLY2000_01"

EMULATOR_DEVICE = "khly2000"

IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("KHLY2000"),
        "emulator": EMULATOR_DEVICE,
    },
]


TEST_MODES = [TestModes.DEVSIM, TestModes.RECSIM]


MEASUREMENT_MODES = [
    "DC Voltage",
    "AC Voltage",
    "DC Current",
    "AC Current",
    "Resistance (2 wire)",
    "Resistance (4 wire)",
]


class Khly2000Tests(unittest.TestCase):

    def setUp(self):
        self.lewis, self.ioc = get_running_lewis_and_ioc(EMULATOR_DEVICE, DEVICE_PREFIX)
        self.ca = ChannelAccess(default_timeout=15, default_wait_time=0.0, device_prefix=DEVICE_PREFIX)
        self.ca.assert_that_pv_exists("DISABLE", timeout=30)

    @skip_if_recsim("IDN not implemented in recsim")
    def test_idn(self):
        self.ca.assert_that_pv_is("IDN", "Simulated keithley 2000")

    @parameterized.expand(parameterized_list(MEASUREMENT_MODES))
    def test_switch_modes(self, _, mode):
        self.ca.assert_setting_setpoint_sets_readback(mode, "MODE")

    def _set_reading(self, value):
        self.ioc.set_simulated_value("SIM:READING", value)
        self.lewis.backdoor_set_on_device("reading", value)

    def test_WHEN_in_voltage_mode_THEN_voltage_pv_reflects_reading_and_other_pvs_are_nan(self):
        self._set_reading(50)
        self.ca.set_pv_value("MODE:SP", "DC Voltage")
        self.ca.assert_that_pv_is("VOLT", 50)
        self.ca.assert_that_pv_value_causes_func_to_return_true("CURR", math.isnan)
        self.ca.assert_that_pv_value_causes_func_to_return_true("RES", math.isnan)

    def test_WHEN_in_current_mode_THEN_current_pv_reflects_reading_and_other_pvs_are_nan(self):
        self._set_reading(60)
        self.ca.set_pv_value("MODE:SP", "DC Current")
        self.ca.assert_that_pv_value_causes_func_to_return_true("VOLT", math.isnan)
        self.ca.assert_that_pv_is("CURR", 60)
        self.ca.assert_that_pv_value_causes_func_to_return_true("RES", math.isnan)

    def test_WHEN_in_res_mode_THEN_res_pv_reflects_reading_and_other_pvs_are_nan(self):
        self._set_reading(70)
        self.ca.set_pv_value("MODE:SP", "Resistance (2 wire)")
        self.ca.assert_that_pv_value_causes_func_to_return_true("VOLT", math.isnan)
        self.ca.assert_that_pv_value_causes_func_to_return_true("CURR", math.isnan)
        self.ca.assert_that_pv_is("RES", 70)
