from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply

from ..device import MeasurementMode

MODE_TO_STR = {
    "VOLT:DC": MeasurementMode.VOLT_DC,
    "VOLT:AC": MeasurementMode.VOLT_AC,
    "CURR:DC": MeasurementMode.CURR_DC,
    "CURR:AC": MeasurementMode.CURR_AC,
    "RES": MeasurementMode.RES_2WIRE,
    "FRES": MeasurementMode.RES_4WIRE,
}


@has_log
class Khly2000StreamInterface(StreamInterface):
    commands = {
        # Get commands
        CmdBuilder("getIdn").escape("*IDN?").eos().build(),
        CmdBuilder("getReading").escape(":READ?").eos().build(),
        CmdBuilder("getMode").escape(":CONF?").eos().build(),
        CmdBuilder("setMode").escape(":CONF:").string().eos().build(),
    }
    
    in_terminator = "\r\n"
    out_terminator = "\r\n"

    @conditional_reply("connected")
    def getIdn(self):
        """
        Gets the current FIELD value from the device. The FIELD type returned is Tesla.
        """
        return self.device.idn

    @conditional_reply("connected")
    def setMode(self, mode):
        self.device.mode = MODE_TO_STR[mode]

    @conditional_reply("connected")
    def getMode(self):
        for key, e in MODE_TO_STR.items():
            if self.device.mode == e:
                # Note: read device *does* send the quotes around this value
                return f'"{key}"'
        else:
            raise ValueError("Device is in unknown mode")

    @conditional_reply("connected")
    def getReading(self):
        return self.device.reading
