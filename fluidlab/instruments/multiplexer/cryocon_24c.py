"""

Driver for the CryoCon 24C Temperature controller

"""

__all__ = ["Cryocon24c"]

from fluidlab.interfaces import PhysicalInterfaceType
from fluidlab.instruments.iec60488 import IEC60488
from fluidlab.instruments.features import FloatValue

class Cryocon24c(IEC60488):
    default_physical_interface = PhysicalInterfaceType.Ethernet
    default_inter_params = {'port': 5000}

    

features = [
    FloatValue("temperature",
        doc="Reads temperature",
        command_get="input? {channel:}",
        channel_argument=True,
    ),
]

Cryocon24c._build_class_with_features(features)
    
if __name__ == '__main__':
    with Cryocon24c('192.168.0.2') as cc:
        Ta = cc.temperature.get('A')
        print('Ta =', Ta)