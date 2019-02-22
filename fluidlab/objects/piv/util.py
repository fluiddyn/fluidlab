import time
import os
from glob import glob

import h5py

from fluiddyn.util import time_as_str

serial_numbers = {"horiz": 470012356, "vert": 470012767}

path_save = os.path.join(os.path.expanduser("~"), ".fluidcoriolis")


def is_new_file(str_name):
    str_name = os.path.expanduser(str_name)
    files_start = glob(str_name)
    while True:
        files = glob(str_name)
        if len(files) > len(files_start):
            return max(files, key=os.path.getctime)

        time.sleep(0.1)


def wait_for_file(str_file, nb_period_to_wait):

    str_file = os.path.join(path_save, str_file)

    print("Waiting for a new file:\n" + str_file)
    path = is_new_file(str_file)

    with open(path, "r") as f:
        txt = f.read()
        period = float(txt.split("\n")[-2].split(" ")[-1])

        if nb_period_to_wait != 0:
            print(
                "Waiting {:.2f} period(s) (= {:.2f} s)".format(
                    float(nb_period_to_wait), nb_period_to_wait * period
                )
            )
            time.sleep(nb_period_to_wait * period)


def save_exp(
    t,
    volt,
    time_between_frames=None,
    time_expo=None,
    tup=None,
    time_between_pairs=None,
    rootname="pivscan",
):
    date = time_as_str()
    name = rootname + "_" + date + ".h5"
    path = os.path.join(path_save, name)
    with h5py.File(path, "w") as f:
        f["t"] = t
        f["volt_angle"] = volt
        f["t_start"] = time.ctime(int(time.time()))
        if time_between_pairs:
            f["time_between_pairs"] = time_between_pairs
        if time_between_frames:
            f["time_between_frames"] = time_between_frames
        if tup:
            f["tup"] = tup
        if time_expo:
            f["time_expo"] = time_expo
