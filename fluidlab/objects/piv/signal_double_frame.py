from __future__ import print_function

from math import ceil
import numpy as np


def make_signal_double_frame(
    time_between_pairs, time_expo, delta_t, nb_nodes=256
):

    """

    Computes the signal to trigger out the cameras for a PIV double frame 2d

    Parameters
    ----------
    time_between_pairs : float
    Period in s.

    time_expo : float
    Exposure time in s.

    delta_t : float
    Time between the two frames in s.

    n : int
    Number of time nodes

    Returns
    -------

    times :
      Array of times

    volts :
      Array of volts

    time_expo :
      Final exposure time in s.

    delta_t:
      Final time between two frames in s.

    time_between_nodes:
      Time between the time nodes.

    """
    assert nb_nodes > 8

    # Compute time interval
    time_between_nodes = (time_expo + delta_t) / (nb_nodes - 1)

    # Check potential errors
    if delta_t - time_expo < 0:
        raise ValueError(
            "No double frame possible. \n" "Choose lower exposure time"
        )

    n_e = int(ceil(time_expo / time_between_nodes))
    time_expo = n_e * time_between_nodes

    # Check if n_d (number of nodes delta_t - time_expo) is an integer
    t_0 = delta_t - time_expo
    n_d = int(ceil(t_0 / time_between_nodes))
    t_0 = n_d * time_between_nodes

    delta_t = t_0 + time_expo

    # Arrays
    times = time_between_nodes * np.arange(nb_nodes)
    volts = np.zeros_like(times)

    # Trigger on. Frame 1
    cond = times < time_expo
    volts[cond] = 5.0

    # Trigger off.
    cond = (times >= time_expo) & (times < delta_t)
    volts[cond] = 0.0

    # Trigger on. Frame 2
    cond = (times >= delta_t) & (times < delta_t + time_expo)
    volts[cond] = 5.0

    # Trigger off
    volts[-1] = 0.0

    return times, volts, time_expo, delta_t, time_between_nodes


if __name__ == "__main__":

    time_between_pairs = 5.0
    time_expo = 0.1
    delta_t = 0.5
    n = 256

    (
        times1,
        volts1,
        time_expo,
        delta_t,
        time_between_nodes,
    ) = make_signal_double_frame(time_between_pairs, time_expo, delta_t, n)

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel("time (s)")
    ax.set_ylabel("volts (V)")
    ax.plot(times1, volts1)

    plt.show()
