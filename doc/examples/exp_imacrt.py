from pymanip import Session

from fluidlab.instruments.multimeter.mgc3 import MGC3
from fluidlab.instruments.multimeter.mmr3 import MMR3

import time


# Function used to get and echo the MMR3 *IDN?
def idmmr3():
    with MMR3("192.168.1.18") as mmr3:
        idr3 = mmr3.query_identification()
        print("***********")
        print("IDMMR3: " + str(idr3))
        print("***********")
        time.sleep(1)
        pass
    if idr3 != "":
        return True
        pass
    else:
        return False
        pass
    pass


# Function used to get and echo the MGC3 *IDN?
def idmgc3():
    with MGC3("192.168.1.17") as mgc3:
        idg3 = mgc3.query_identification()
        print("IDMGC: " + str(idg3))
        print("***********")
        time.sleep(1)
        pass
    if idg3 != "":
        return True
        pass
    else:
        return False
        pass
    pass


# Function used to set up the MMR3
def setupmmr3():
    with MMR3("192.168.1.18") as mmr3:
        mmr3.r1_rangemode.set(0)
        mmr3.r1_rangemode_i.set(0)
        mmr3.r1_range_i.set(1)
        mmr3.r1_i.set(0.00001)
        time.sleep(1)
        pass
    pass


# Function used to set up the MGC3
def setupmgc3():
    with MGC3("192.168.1.17") as mgc3:
        mgc3.pid0_channel.set(0)
        mgc3.pid0_prop.set(0.5)
        mgc3.pid0_integral.set(0.01)
        mgc3.pid0_res.set(100)
        mgc3.pid0_maxpow.set(5)
        mgc3.pid0_setpoint.set(33)
        mgc3.pid0_onoff.set(1)
        time.sleep(1)
        pass
    pass


def setpoint():
    with MGC3("192.168.1.17") as mgc3:
        sp = mgc3.pid0_setpoint.get()
        return sp
        pass
    pass


# Function used to make a simple MMR3 measurement
def mesuremmr3():
    with MMR3("192.168.1.18") as mmr3:
        measr = mmr3.r1_convert.get()
        return measr
        pass
    pass


# Function used to make a simple MGC3 measurement
def mesuremgc3():
    with MGC3("192.168.1.17") as mgc3:
        measg = mgc3.pid0_meas.get()
        return measg
        pass
    pass


def main():
    # Vars
    basename = "demo"
    # Echo IDN
    chkr = idmmr3()
    chkg = idmgc3()
    # Make sure the instruments answer something
    if chkr and chkg:
        print("CONNECTION ESTABLISHED")
        print("MEASURING WILL START...")
        pass
    # If not, exit program
    else:
        print("CONNECTION FAILED!")
        print("ERR_OH_NO_IDN")
        print("STOPPING PROGRAM...")
        exit()
        pass
    # Start setup
    print("***********")
    print("SETTING UP MMR3")
    setupmmr3()
    print("***********")
    print("SETTING UP MGC3")
    setupmgc3()
    # Start Session
    # Where R1 = MMR3 meas and R2 = MGC3 meas
    with Session(basename, ("T", "SP")) as MI:
        print("**********")
        print("START PLOT")
        print("**********")
        while True:
            # Measurement
            T = mesuremmr3()
            SP = setpoint()
            # Graph gen
            MI.log_addline()
            MI.log_plot(1, ("T", "SP"))
            # Echo safety
            print(T)
            print(SP)
            # Sleep until next meas
            MI.sleep(1)
    pass


if __name__ == "__main__":
    main()
