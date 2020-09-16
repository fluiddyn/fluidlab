"""lakeshore_224
================

.. autoclass:: Lakeshore224
   :members:
   :private-members:



"""

__all__ = ["Lakeshore224"]

from fluidlab.instruments.multiplexer import CurveFormat, CurveCoefficient
from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue, BoolValue, IntValue


def float_to_LS(number):
    if number < 1:
        result = f"{number:.5f}"
    elif number < 10:
        result = f"{number:.5f}"
    elif number < 100:
        result = f"{number:.4f}"
    elif number < 1000:
        result = f"{number:.3f}"
    elif number < 10000:
        result = f"{number:.2f}"
    elif number < 100000:
        result = f"{number:.1f}"
    else:
        result = f"{number:.0f}"
    assert len(result) == 7
    return result


class Lakeshore224(IEC60488):
    """Driver for the Lakeshore Model 224 Temperature Monitor"""

    def upload_curve(
        self,
        curve_number,
        curve_name,
        curve_sn,
        curve_format,
        limit_value,
        coefficient,
        sensor_values,
        temperature_values,
    ):
        """Upload a calibration curve.

        :param curve_number: Specifies which curve to configure. Valid entries: 21-59.
        :type curve_number: int
        :param curve_name: Specifies curve name. Limited to 15 characters.
        :type curve_name: str
        :param curve_sn: Specifies the curve serial number. Limited to 10 characters.
        :type curve_sn: str
        :param curve_format: Specifies the curve data format. Valid entries: 1 = mV/K, 2 = V/K,
                             3 = Ohm/K, 4 = log Ohm/K.
        :type curve_format: :class:`CurveFormat`
        :param limit_value: Specifies the curve temperature limit in kelvin.
        :type limit_value: float
        :param coefficient: Specifies the curve temperature coefficient. Valid entries: 1 = negative, 2 = positive.
        :type coefficient: :class:`CurveCoefficient`
        :param sensor_values: Specifies sensor units, to 6 digits.
        :type sensor_value: :class:`numpy.ndarray`
        :param temperature_values: Specifies the corresponding temperature in kelvin, to 6 digits
        :type temperature_values: :class:`numpy.ndarray`
        """

        # Check parameters
        curve_number = int(curve_number)
        if curve_number < 21 or curve_number > 59:
            raise ValueError("Valid curve numbers between 21 and 59.")
        curve_name = str(curve_name)
        if len(curve_name) > 15:
            raise ValueError("Valid curve names are limited to 15 characters.")
        curve_sn = str(curve_sn)
        if len(curve_sn) > 10:
            raise ValueError(
                "Valid curve serial numbers are limited to 10 characters."
            )
        curve_format = CurveFormat(curve_format)
        limit_value = float(limit_value)
        coefficient = CurveCoefficient(coefficient)

        # Curve Header Command
        self.interface.write(f"CRVDEL {curve_number:d}")
        self.interface.write(
            f"CRVHDR {curve_number:d},{curve_name:},{curve_sn:},{curve_format:d},{limit_value:.1f},{coefficient:d}"
        )
        index = 1
        for unit_value, temp_value in zip(sensor_values, temperature_values):
            if index > 200:
                print("Only the first 200 datapoints can be uploaded")
                break
            unit_str = float_to_LS(unit_value)
            temp_str = float_to_LS(temp_value)
            self.interface.write(
                f"CRVPT {curve_number:d},{index:d},{unit_str:},{temp_str}"
            )
            index = index + 1


features = [
    FloatValue(
        "temperature",
        doc="Reads temperature (in Kelvins)",
        command_get="KRDG? {channel:}",
        channel_argument=True,
    ),
    FloatValue(
        "sensor_value",
        doc="Reads sensor signal in sensor units",
        command_get="SRDG? {channel:}",
        channel_argument=True,
    ),
    IntValue(
        "curve_number",
        doc="Specifies the curve an input uses for temperature conversion",
        command_set="INCRV {channel:},{value:}",
        command_get="INCRV? {channel:}",
        channel_argument=True,
    )
]

Lakeshore224._build_class_with_features(features)

if __name__ == "__main__":
    with Lakeshore224("GPIB0::12::INSTR") as ls:
        T_Pt, T_Diode = ls.temperature.get(["A", "B"])
        print("T_Pt =", T_Pt, "K")
        print("T_Diode =", T_Diode, "K")
        R_Pt, V_Diode = ls.sensor_value.get(["A", "B"])
        print("R_Pt =", R_Pt, "Ohm")
        print("V_Diode =", V_Diode, "V")
