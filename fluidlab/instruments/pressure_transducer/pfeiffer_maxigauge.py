"""pfeiffer_maxigauge
=====================

.. autoclass:: PfeifferMaxiGauge
   :members:
   :private-members:


"""

from __future__ import print_function, unicode_literals, division

from fluidlab.instruments.drivers import Driver
from fluidlab.instruments.interfaces.serial_inter import SerialInterface
from fluidlab.instruments.features import Value

# from time import sleep
import numpy as np
import six
from clint.textui import colored
from functools import reduce

__all__ = ["PfeifferMaxiGauge"]

codes = {
    "ETX": b"\x03",  # End of text (reset the interface)
    "CR": b"\x0D",  # Carriage return (go to beginning of line)
    "LF": b"\x0A",  # Line feed (advance by one line)
    "ENQ": b"\x05",  # Enquiry (request data transmission)
    "ACK": b"\x06",  # Acknowledge (positive report signal)
    "NAK": b"\x15",  # Negative acknowledge (negative report signal)
    "ESC": b"\x1B",
}  # Escape


class PfeifferMaxiGaugeException(Exception):
    pass


class PfeifferMaxiGaugeValue(Value):
    def __init__(self, name, doc="", mnemonic=b""):
        super(PfeifferMaxiGaugeValue, self).__init__(
            name,
            doc,
            command_set=None,
            command_get=None,
            check_instrument_value=False,
            pause_instrument=0.5,
            channel_argument=False,
        )
        self.mnemonic = mnemonic

    def set(self, value):
        self._driver.transmission(self.mnemonic, value)

    def get(self, parameter=b""):
        return self._driver.reception(self.mnemonic, parameter)


class PfeifferMaxiGaugePressureValue(PfeifferMaxiGaugeValue):
    def get(self, sensor):
        if isinstance(sensor, six.integer_types):
            sensor = str(sensor).encode("ascii")
        elif isinstance(sensor, (list, tuple, np.ndarray)):
            return [self.get(sen) for sen in sensor]
        msg = super(PfeifferMaxiGaugePressureValue, self).get(parameter=sensor)
        p = msg.split(b",")
        status = int(p[0])
        value = float(p[1])
        if status == 3:
            print(
                colored.red("Sensor error on channel " + sensor.decode("ascii"))
            )
        elif status == 4:
            print(
                colored.red("Sensor is off on channel " + sensor.decode("ascii"))
            )
        elif status == 5:
            print(colored.red("No sensor on channel " + sensor.decode("ascii")))
        elif status == 6:
            print(
                colored.red(
                    "Identification error on channel " + sensor.decode("ascii")
                )
            )
        return value


class PfeifferMaxiGaugeOnOffValue(PfeifferMaxiGaugeValue):
    def set(self, booleans):
        if len(booleans) != 6:
            raise ValueError("6 booleans are expected")
        msg = reduce(
            lambda a, b: a + b, [b",2" if b else b",1" for b in booleans]
        )
        try:
            super(PfeifferMaxiGaugeOnOffValue, self).set(msg)
        except PfeifferMaxiGaugeException:
            pass

    def get(self):
        msg = super(PfeifferMaxiGaugeOnOffValue, self).get(
            parameter=b",0,0,0,0,0,0"
        )
        return [s == b"1" for s in msg]


class PfeifferMaxiGauge(Driver):
    def __init__(self, serialPort, debug=False):
        interface = SerialInterface(
            serialPort,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )
        super(PfeifferMaxiGauge, self).__init__(interface)
        self.debug = debug
        self.clear_interface()
        print("Pfeiffer MaxiGauge:", self.program_version().decode("ascii"))
        long_description = {
            b"TPR/PCR": "Pirani Gauge or Pirani Capacitance Gauge",
            b"IKR9": "Cold cathode to 1e-9 mbar",
            b"IKR11": "Cold cathode to 1e-11 mbar",
            b"PKR": "FullRange CC",
            b"APR/CMR": "Linear sensor",
            b"IMR": "Pirani / High Pressure",
            b"PBR": "FullRange BA",
            b"no Sensor": "No sensor",
            b"no Ident": "No identification",
        }
        for i, sensor in enumerate(self.sensor_id()):
            try:
                desc = "(" + long_description[sensor] + ")"
            except KeyError:
                desc = ""
            print(i + 1, sensor.decode("ascii"), desc)

    def clear_interface(self):
        if self.debug:
            print("-> ETX")
        self.interface.write(codes["ETX"])

    def transmission(self, mnemonics, parameters=b""):
        """
        Transmission protocol:
        -> Mnemonics [and parameters] <CR>[<LF>]
        <- <ACK><CR><LF>
        """
        msg = self.interface.query(mnemonics + parameters + b"\r")
        if self.debug:
            print("->", mnemonics + parameters)
        ack_positif = codes["ACK"]
        ack_negatif = codes["NAK"]
        if msg == ack_positif:
            if self.debug:
                print("<- ACK")
        elif msg == ack_negatif:
            if self.debug:
                print("<- NAK")
            raise PfeifferMaxiGaugeException("Negative report signal received.")
        else:
            if self.debug:
                if len(msg) == 1:
                    print("<- " + ("0x%x" % ord(msg)))
                else:
                    print("<- " + msg)
            raise PfeifferMaxiGaugeException(
                'Unknown return value: "' + msg.decode("ascii") + '"'
            )

    def reception(self, mnemonics, parameters=b""):
        """
        Reception protocol:
        -> Mnemonics [and parameters] <CR>[<LF>]
        <- <ACK><CR><LF>
        -> <ENQ>
        <- Measurement values or parameters <CR><LF>
        """
        self.transmission(mnemonics, parameters)
        if self.debug:
            print("-> ENQ")
        data = self.interface.query(codes["ENQ"])
        if self.debug:
            print("<-", data)
        return data

    def error_status(self):
        msg = self.reception(b"ERR")
        p = msg.split(b",")
        status_1 = int(p[0])
        status_2 = int(p[1])
        if status_1 & 1:
            print("Watchdog has responded")
        elif status_1 & 2:
            print("Task fail error")
        elif status_1 & 4:
            print("IDCX idle error")
        elif status_1 & 8:
            print("Stack overflow error")
        elif status_1 & 16:
            print("EPROM error")
        elif status_1 & 32:
            print("RAM error")
        elif status_1 & 64:
            print("EEPROM error")
        elif status_1 & 128:
            print("Key error")
        elif status_1 & 4096:
            print("Syntax error")
        elif status_1 & 8192:
            print("Inadmissible parameter")
        elif status_1 & 16384:
            print("No hardware")
        elif status_1 & 32768:
            print("Fatal error")
        for i in range(6):
            if status_2 & (1 << i):
                print("Sensor {:d}: Measurement error".format(i + 1))
            if status_2 & (1 << (i + 9)):
                print("Sensor {:d}: Identification error".format(i + 1))
        if status_1 == 0 and status_2 == 0:
            print("No error")

    def program_version(self):
        return self.reception(b"PNR")

    def sensor_id(self):
        msg = self.reception(b"TID")
        data = msg.split(b",")
        return data


features = [
    PfeifferMaxiGaugeOnOffValue(
        "onoff", "Switch ON/OFF sensors", mnemonic=b"SEN"
    ),
    PfeifferMaxiGaugePressureValue(
        "pressure", "Pressure measurement", mnemonic=b"PR"
    ),
]

PfeifferMaxiGauge._build_class_with_features(features)

if __name__ == "__main__":
    gauge = PfeifferMaxiGauge("COM1", debug=False)
