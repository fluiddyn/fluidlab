#!/usr/bin/env python
"""fluid_stop_pumps.py: Quickly stop the pumps!"""

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()

    from fluiddyn.lab.pumps import MasterFlexPumps
    pumps = MasterFlexPumps(nb_pumps=2)
