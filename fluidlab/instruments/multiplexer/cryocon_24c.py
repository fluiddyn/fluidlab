"""Driver for the CryoCon 24C Temperature controller
====================================================

.. autoclass:: Cryocon24c
   :members:
   :private-members:

"""

__all__ = ["Cryocon24c"]

from time import sleep
from progressbar import ProgressBar

from fluidlab.interfaces import PhysicalInterfaceType
from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, StringValue, IntValue, WriteCommand
from fluidlab.instruments.multiplexer import CurveFormat, CurveCoefficient

    
class CryoconFloatValue(FloatValue):
    """This subclass converts Cryocon undefined value, '.......'
    to NaN instead of raising ValueError exception.
    """
    def _convert_from_str(self, value):
        value = value.strip()
        if value == '.......':
            return float("nan")
        try:
            return super()._convert_from_str(value)
        except ValueError:
            return float("nan")
        
class Cryocon24c(IEC60488):
    default_physical_interface = PhysicalInterfaceType.Ethernet
    default_inter_params = {"port": 5000}
    
    SensorTypes = {"DIODE", "PTC100", "PTC1K", "PTC10K", "NTC10uA", "ACR"}
    Units = {"OHMS", "VOLT", "LOGOHM"}
        
    def upload_curve(
        self,
        curve_number,
        curve_name,
        sensor_type,
        curve_format,
        coefficient,
        sensor_values,
        temperature_values,
    ):
        """Uploads calibration curve to CryoCon.
        
        :param curve_number: Index number of the curve to upload. Must be between 1 and 8.
        :type curve_number: int
        :param curve_name: Name of the curve. Up to 15 ASCII characters.
        :type curve_name: str
        :param sensor_type: One of "DIODE", "PTC100", "PTC1K", "PTC10K", "NTC10uA", "ACR" (see table.)
        :type sensor_type: str
        :param curve_format: One of "OHMS", "VOLT", "LOGOHM"
        :type curve_format: str
        :param coefficient: 1.0 for PTC sensors, -1.0 for NTC sensors.
        :type coefficient: float
        :param sensor_values: table of sensor values
        :type: :class:`numpy.ndarray`
        :param temperature_values: table of temperature values
        :type: :class:`numpy.ndarray`
        
        Complete list of sensor types
        
        Sensor Type Max Voltage/Resistance Bias Type Excitation current Typical User
        =========== ====================== ========= ================== ==================================================
        DIODE       2.25 V                 CI        10 µA DC           Si or GaAs diode.
        ACR         10 Ohm to 2.0 MOhm     CV        150 mA - 50 nA AC  NTC resistors including Ruthenium Oxide and Cernox
        PTC100      0.5 - 750 Ohm          CI        1.0 mA DC          100 Ohm Platinum, Rhodium-Iron
        PTC1K       5 - 7.5 kOhm           CI        100 µA DC          1 kOhm Platinum
        PTC10K      50 Ohm - 75 kOhm       CI        10 µA DC           10 kOhm Platinum
        NTC10UA     240 kOhm               CI        10 µA DC           R400 Ruthenium Oxide
        TC70        +/- 70 mV              None      0                  All thermocouples types.
        None        0                      None      0                  Disable Input Channel.
        
        * CI: Bridge maintains a constant current through the sensor
        * CV: Bridge maintains a constant voltage-drop across the sensor.
        
        """
        if len(curve_name) > 15:
            raise ValueError("Curve name may not have more than 15 characters")
            
        if curve_number < 1 or curve_number > 8:
            raise ValueError("User installed sensors have index values from 61 to 68 corresponding to user curves 1 through 8.")
        if sensor_type not in Cryocon24c.SensorTypes:
            raise ValueError("Not a valid sensor type.")
        if coefficient is CurveCoefficient.POSITIVE:
            coefficient = 1.0
        elif coefficient is CurveCoefficient.NEGATIVE:
            coefficient = -1.0
        elif coefficient in [-1.0, 1.0]:
            coefficient = float(coefficient)
        else:
            raise ValueError("Wrong coefficient value. Should be NEGATIVE or POSITIVE.")
    
        if curve_format is CurveFormat.MILLIVOLT_PER_KELVIN:
            raise ValueError("Unsupported curve format. Must be VOLTS, OHMS or LOGOHM")
        elif curve_format is CurveFormat.VOLT_PER_KELVIN:
            curve_format = "VOLTS"
        elif curve_format is CurveFormat.OHM_PER_KELVIN:
            curve_format = "OHMS"
        elif curve_format is CurveFormat.LOGOHM_PER_KELVIN:
            curve_format = "LOGOHM"
        elif curve_format.upper() in Cryocon24c.Units:
            curve_format = curve_format.upper()
        else:
            raise ValueError("Wrong curve format. Must be VOLTS, OHMS or LOGOHM")
            
        print(f"Uploading User Curve {curve_number:} (index = {curve_number+60:})")
        pb = ProgressBar(min_value=0, max_value=sensor_values.size+5, initial_value=0)
        pbi = 0
        
        # Sensing CALCUR command
        self.interface.write(f"CALCUR {curve_number:}")
        sleep(0.5)
        pbi += 1
        pb.update(pbi)
        
        # Sending header
        self.interface.write(curve_name)
        sleep(0.5)
        pbi += 1
        pb.update(pbi)
        
        self.interface.write(sensor_type)
        sleep(0.5)
        pbi += 1
        pb.update(pbi)
        
        self.interface.write(f"{coefficient:.1f}")
        sleep(0.5)
        pbi += 1
        pb.update(pbi)
        
        self.interface.write(curve_format)
        sleep(0.5)
        pbi += 1
        pb.update(pbi)
        
        # Sending table
        index = 1
        for unit_value, temp_value in zip(sensor_values, temperature_values):
            if index > 200:
                print("Only the first 200 datapoints can be uploaded")
                break
            self.interface.write(
                f"{unit_value:.6f} {temp_value:.6f}"
            )
            index = index + 1
            sleep(0.5)
            pbi += 1
            pb.update(pbi)
        self.interface.write(";")
     
features = [
    CryoconFloatValue(
        "temperature",
        doc="Reads temperature",
        command_get="input? {channel:}",
        channel_argument=True,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
    ),
    StringValue(
        "unit",
        doc="Set the temperature units on input channel. Choices are k (Kelvin), c (Celsius), f (Fahrenheit), s (native sensor)",
        command_get="input {channel:}:units?",
        command_set="input {channel:}:units {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
        possible_values={"k", "c", "f", "s"},
    ),
    StringValue(
        "name",
        doc="Instrument name",
        command_get="input {channel:}:name?",
        command_set="input {channel:}:name {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
    ),
    StringValue(
        "ohm",
        doc="Reports the reading on the selected input channel in sensor units.",
        command_get="input {channel:}:senpr?",
        command_set=None,
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
    ),
    StringValue(
        "volt",
        doc="Reports the reading on the selected input channel in sensor units.",
        command_get="input {channel:}:senpr?",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
    ),
    FloatValue(
        "power",
        doc="Queries the sensor power dissipation in watts.",
        command_get="input {channel:}:senspwr?",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
    ),
    IntValue(
        "curve_number",
        doc="Specifies the curve an input uses for temperature conversion",
        command_set="input {channel:}:sensor {value:}",
        command_get="input {channel:}:sensor?",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={"A", "B", "C", "D"},
        default_channel="A",
        possible_values={61, 62, 63, 64, 65, 66, 67, 68},
    ),
    StringValue(
        "curve_name",
        doc="Sets and queries the name string of the user-installed sensor at index <index>.",
        command_get="SENSorix {channel:}:name?",
        command_set='SENSorix {channel:}:name "{value:}"',
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={61, 62, 63, 64, 65, 66, 67, 68},
        default_channel=61,
    ),
    IntValue(
        "curve_n_entry",
        doc="Queries the number of entries of the user-installed calibration curve at <index>.",
        command_get="SENSorix {channel:}:NENTry?",
        channel_argument=True,
        possible_channels={61, 62, 63, 64, 65, 66, 67, 68},
        default_channel=61,
    ),
    StringValue(
        "curve_units",
        doc="Sets or queries the units of a user installed calibration curve at <index>.",
        command_get="SENSorix {channel:}:UNITs?",
        command_set="SENSorix {channel:}:UNITs {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={61, 62, 63, 64, 65, 66, 67, 68},
        default_channel=61,
        possible_values={"VOLTS", "OHMS", "LOGOHM"},
    ),
    StringValue(
        "curve_type",
        doc="Sets or queries the type of sensor at <index>.",
        command_get="SENSorix {channel:}:TYPe?",
        command_set="SENSorix {channel:}:TYPe {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={61, 62, 63, 64, 65, 66, 67, 68},
        default_channel=61,
    ),
    FloatValue(
        "curve_multiplier",
        doc="Sets or queries the multiplier field of a user installed calibration curve at <index>.",
        command_get="SENSorix {channel:}:MULTiply?",
        command_set="SENSorix {channel:}:MULTiply {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={61, 62, 63, 64, 65, 66, 67, 68},
        default_channel=61,
        possible_values={1.0, -1.0},
    ),
    WriteCommand(
        "loop_stop",
        doc="Disengage all control loops.",
        command_str="stop",
    ),
    WriteCommand(
        "loop_start",
        doc="Engage all control loops.",
        command_str="control",
    ),
    StringValue(
        "loop_source",
        doc="Sets and queries the selected control loop's controlling input channel, which may be any one of the four input channels.",
        command_get="loop {channel:}:SOURce?",
        command_set="loop {channel:}:SOURce {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
        possible_values={"A", "B", "C", "D"},
    ),
    FloatValue(
        "loop_setpoint",
        doc="""Sets and queries the selected control loop's setpoint. This is a numeric value that has units
determined by the display units of the controlling input channel.""",
        command_get="loop {channel:}:SETPt?",
        command_set="loop {channel:}:SETPt {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
    ),
    StringValue(
        "loop_type",
        doc="Sets and queries the selected control loop's control type. Allowed values are Off, PID, Man, Table, RampP, RampT.",
        command_get="loop {channel:}:TYPe?",
        command_set="loop {channel:}:TYPe {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
        possible_values={"Off", "PID", "Man", "Table", "RampP", "RampT"},
    ),
    StringValue(
        "loop_range",
        doc="""Sets or queries the control loop's output range.
Range determines the maximum output power available and is different for a 50 Ohm load resistance than for a 25 Ohm load.
Values of heater range for Loop 1 are: Hi, Mid and Low. These corresponds to the output power levels in this table:

Range 50 Ohm Load 25 Ohm Load
===== =========== ===========
Hi    50W         25W
Mid   5W          2.5W
Low   0.5W        0.25W

The values for loop 2 is 10W into a 50 Ohm load.
""",
        command_get="loop {channel:}:RANGe?",
        command_set="loop {channel:}:RANGe {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
        possible_values={"Hi", "Mid", "Low"},
    ),
    IntValue(
        "loop_pid_P",
        doc="Sets or queries the selected control loop's proportional gain term. Values between 0 (off) and 1000.",
        command_get="loop {channel:}:PGAin?",
        command_set="loop {channel:}:PGain {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
    ),
    IntValue(
        "loop_pid_I",
        doc="Sets or queries the selected control loop's integrator gain, in units of seconds, between 0 (off) through 1000.",
        command_get="loop {channel:}:IGAin?",
        command_set="loop {channel:}:IGain {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
    ),
    IntValue(
        "loop_pid_d",
        doc="Sets or queries the selected control loop's differentiator gain term, in inverse of seconds, between 0 (off) to 1000.",
        command_get="loop {channel:}:DGain?",
        command_set="loop {channel:}:DGAin {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
    ),
    FloatValue(
        "loop_output_power",
        doc="Queries the output power of the selected control loop. This is a numeric field in percent of full scale.",
        command_get="loop {channel:}:OUTPwr?",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1, 2, 3, 4},
        default_channel=1,
    ),
    IntValue(
        "loop_load",
        doc="Sets or queries the load resistance setting of the primary heater (loop 1).",
        command_get="loop {channel:}:LOAD?",
        command_set="loop {channel:}:LOAD {value:}",
        channel_argument=True,
        pause_instrument=0.5,
        check_instrument_value=False,
        possible_channels={1},
        default_channel=1,
        possible_values={25, 50},
    ),
]

Cryocon24c._build_class_with_features(features)


def loop_output_power_to_power(loop_channel, loop_output_power, loop_range="Low", heater_resistance=50.0):
    """Converts the loop output power, which is a percentage of the power full scale to actual power (in watts).

    For loop 1, there are three range values, "High" (1 A), "Mid" (0.333 A), "Low" (0.100 A). The load parameter (25 Ohm or 50 Ohm)
    controls the compliance voltage (25 V or 50 V respectively).

    For loop 2 (secondary loop), maximum output current is 450 mA, and compliance 25 V.

    Both have 1.0ppm full scale (20 bits).
    """

    if loop_channel == 1:
        maximum_current = {
            "High": 1.0,
            "Mid": 0.333,
            "Low": 0.1,
        }[loop_range]
    elif loop_channel == 2:
        maximum_current = 0.45

    return heater_resistance * (loop_output_power / 100) * maximum_current ** 2
        

if __name__ == "__main__":
    with Cryocon24c("192.168.0.2") as cc:
        Ta = cc.temperature.get("A")
        print("Ta =", Ta)
