import enum
import threading
from lewis.devices import StateMachineDevice
from lewis.core import approaches
from lewis.core.logging import has_log
from .states import DefaultState
from collections import OrderedDict


class MeasurementMode(enum.Enum):
    VOLT_DC = 0
    VOLT_AC = 1
    CURR_DC = 2
    CURR_AC = 3
    RES_2WIRE = 4
    RES_4WIRE = 5



@has_log
class SimulatedB17Tmag(StateMachineDevice):

    def _initialize_data(self):
        self.re_initialise()

    def _get_state_handlers(self):
        return {'default': DefaultState()}

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([])

    def re_initialise(self):
        """
        Setting values device is initially set with when it is first turned on
        Values are set based on those set in the manual for Birmingham 17T magnet.
        """
        self.connected = True
        self.idn = "Simulated keithley 2000"
        self.mode = MeasurementMode.VOLT_DC
        self.reading = 0.