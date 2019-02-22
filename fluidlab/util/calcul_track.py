from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt


def make_track_1period(z_max, z_min, v_up, v_down, acc, dacc, dt):
    """
    Track for the profilometers.

    Parameters
    ----------
    z_max : float
    Highest position in meters (normally 0.).

    z_min : float
    Lowest position in meters (i.e. -0.5).

    v_up : float
    Speed move up in m/s.

    v_down : float
    Speed move down in m/s.

    acc : float
    Acceleration in m2/s.

    dacc : float
    De-acceleration in m2/s.

    dt : float
    Time interval in s.
    """

    # Positions
    z_0 = z_max
    z_1 = z_max - (0.5 * acc * (v_down / acc) ** 2)
    z_2 = z_min + (0.5 * dacc * (v_down / dacc) ** 2)

    if z_2 > z_1:
        raise ValueError(
            "Acceleration too small or uniform velocity \n"
            "too large. Change input parameters!"
        )

    z_3 = z_min
    z_4 = z_min + (0.5 * acc * (v_up / acc) ** 2)
    z_5 = z_max - (0.5 * dacc * (v_up / dacc) ** 2)

    # Times
    # t_sleep = 5
    t_1 = v_down / acc
    t_2 = t_1 + (abs(z_2 - z_1) / v_down)
    t_3 = t_2 + v_down / dacc
    t_4 = t_3 + v_up / acc
    t_5 = t_4 + (abs(z_5 - z_4) / v_up)
    # t_6 = t_5 + t_sleep
    t_total = t_5 + v_up / dacc
    # t_total = t_6

    # Arrays
    nt = np.round(t_total / dt)
    times = dt * np.arange(nt)
    positions = np.zeros_like(times)
    speeds = np.zeros_like(times)

    # Move down (acceleration)
    cond = times <= t_1
    speeds[cond] = -acc * times[cond]
    positions[cond] = z_0 - 0.5 * acc * times[cond] ** 2

    # Move down (uniform)
    cond = (times > t_1) & (times <= t_2)
    speeds[cond] = -v_down
    positions[cond] = z_1 - (v_down * (times[cond] - t_1))

    # Move down (de-accelerating)
    cond = (times > t_2) & (times <= t_3)
    t = times[cond] - t_2
    speeds[cond] = -(v_down - dacc * t)
    positions[cond] = z_2 - v_down * t + 0.5 * dacc * t ** 2

    # Move up (acceleration)
    cond = (times > t_3) & (times <= t_4)
    t = times[cond] - t_3
    speeds[cond] = acc * t
    positions[cond] = z_3 + 0.5 * acc * t ** 2

    # Move up (uniform)
    cond = (times > t_4) & (times <= t_5)
    t = times[cond] - t_4
    speeds[cond] = v_up
    positions[cond] = z_4 + (v_up * t)

    # Move up (de-acceleration)
    cond = times > t_5
    t = times[cond] - t_5
    speeds[cond] = v_up - dacc * t
    positions[cond] = z_5 + v_up * t - 0.5 * dacc * t ** 2

    return times, positions, speeds, t_total


def make_track_sleep_1period(z_max, z_min, v_up, v_down, acc, dacc, dt, t_sleep):

    """ Track for the profilometers with a sleeping time """

    # Positions
    z_0 = z_max
    z_1 = z_max - (0.5 * acc * (v_down / acc) ** 2)
    z_2 = z_min + (0.5 * dacc * (v_down / dacc) ** 2)

    if z_2 > z_1:
        raise ValueError(
            "Acceleration too small or uniform velocity \n"
            "too large. Change input parameters!"
        )

    z_3 = z_min
    z_4 = z_min + (0.5 * acc * (v_up / acc) ** 2)
    z_5 = z_max - (0.5 * dacc * (v_up / dacc) ** 2)

    # Times
    t_1 = v_down / acc
    t_2 = t_1 + (abs(z_2 - z_1) / v_down)
    t_3 = t_2 + v_down / dacc
    t_4 = t_3 + v_up / acc
    t_5 = t_4 + (abs(z_5 - z_4) / v_up)
    t_6 = t_5 + v_up / dacc
    t_total = t_6 + t_sleep

    # Arrays
    nt = np.round(t_total / dt)
    times = dt * np.arange(nt)
    positions = np.zeros_like(times)
    speeds = np.zeros_like(times)

    # Move down (acceleration)
    cond = times <= t_1
    speeds[cond] = -acc * times[cond]
    positions[cond] = z_0 - 0.5 * acc * times[cond] ** 2

    # Move down (uniform)
    cond = (times > t_1) & (times <= t_2)
    speeds[cond] = -v_down
    positions[cond] = z_1 - (v_down * (times[cond] - t_1))

    # Move down (de-accelerating)
    cond = (times > t_2) & (times <= t_3)
    t = times[cond] - t_2
    speeds[cond] = -(v_down - dacc * t)
    positions[cond] = z_2 - v_down * t + 0.5 * dacc * t ** 2

    # Move up (acceleration)
    cond = (times > t_3) & (times <= t_4)
    t = times[cond] - t_3
    speeds[cond] = acc * t
    positions[cond] = z_3 + 0.5 * acc * t ** 2

    # Move up (uniform)
    cond = (times > t_4) & (times <= t_5)
    t = times[cond] - t_4
    speeds[cond] = v_up
    positions[cond] = z_4 + (v_up * t)

    # Move up (de-acceleration)
    cond = (times > t_5) & (times <= t_6)
    t = times[cond] - t_5
    speeds[cond] = v_up - dacc * t
    positions[cond] = z_5 + v_up * t - 0.5 * dacc * t ** 2

    # Sleep time
    cond = times > t_6
    t = times[cond] - t_6
    speeds[cond] = 0.0
    positions[cond] = z_0

    return times, positions, speeds, t_total


def make_track_sleep_1period_tbottom(
    z_max, z_min, v_up, v_down, acc, dacc, dt, t_bottom, t_period=None
):
    """ 
    Track for the profilometers with a sleeping time at the end AND
    sleeping time at the bottom (to measure the signal at the bottom).
    """

    # Positions
    z_0 = z_max
    z_1 = z_max - (0.5 * acc * (v_down / acc) ** 2)
    z_2 = z_min + (0.5 * dacc * (v_down / dacc) ** 2)

    z_3 = z_min
    z_4 = z_min + (0.5 * acc * (v_up / acc) ** 2)
    z_5 = z_max - (0.5 * dacc * (v_up / dacc) ** 2)

    if not z_0 > z_1 > z_2 > z_3:
        print("not z_0 > z_1 > z_2 > z_3")
        print("z_0, z_1, z_2, z_3 =", z_0, z_1, z_2, z_3)
        raise ValueError(
            "Acceleration too small or uniform velocity \n"
            "too large. Change input parameters!"
        )

    if not z_3 < z_4 < z_5 < z_0:
        print("not z_3 < z_4 < z_5 < z_0")
        print("z_3, z_4, z_5, z_0 =", z_3, z_4, z_5, z_0)
        raise ValueError(
            "Acceleration too small or uniform velocity \n"
            "too large. Change input parameters!"
        )

    # Times
    t_1 = v_down / acc
    t_2 = t_1 + (abs(z_2 - z_1) / v_down)
    t_3 = t_2 + v_down / dacc
    t_4 = t_3 + t_bottom
    t_5 = t_4 + v_up / acc
    t_6 = t_5 + (abs(z_5 - z_4) / v_up)
    t_7 = t_6 + v_up / dacc

    if t_period is None:
        t_period = t_7
    elif t_period < t_7:
        raise ValueError("t_period < t_7")

    # Arrays
    nt = np.round(t_period / dt)
    t_total = nt * dt

    times = dt * np.arange(nt)
    positions = np.zeros_like(times)
    speeds = np.zeros_like(times)

    # Move down (acceleration)
    cond = times <= t_1
    speeds[cond] = -acc * times[cond]
    positions[cond] = z_0 - 0.5 * acc * times[cond] ** 2

    # Move down (uniform)
    cond = (times > t_1) & (times <= t_2)
    speeds[cond] = -v_down
    positions[cond] = z_1 - (v_down * (times[cond] - t_1))

    # Move down (de-accelerating)
    cond = (times > t_2) & (times <= t_3)
    t = times[cond] - t_2
    speeds[cond] = -(v_down - dacc * t)
    positions[cond] = z_2 - v_down * t + 0.5 * dacc * t ** 2

    # Sleep t_bottom
    cond = (times > t_3) & (times <= t_4)
    t = times[cond] - t_3
    speeds[cond] = 0.0
    positions[cond] = z_3

    # Move up (acceleration)
    cond = (times > t_4) & (times <= t_5)
    t = times[cond] - t_4
    speeds[cond] = acc * t
    positions[cond] = z_3 + 0.5 * acc * t ** 2

    # # Move up (uniform)
    cond = (times > t_5) & (times <= t_6)
    t = times[cond] - t_5
    speeds[cond] = v_up
    positions[cond] = z_4 + (v_up * t)

    # # Move up (de-acceleration)
    cond = (times > t_6) & (times <= t_7)
    t = times[cond] - t_6
    speeds[cond] = v_up - dacc * t
    positions[cond] = z_5 + v_up * t - 0.5 * dacc * t ** 2

    # # Sleep time
    cond = times > t_7
    t = times[cond] - t_6
    speeds[cond] = 0.0
    positions[cond] = z_0

    return times, positions, speeds, t_total


def concatenate(times1, positions1, speeds1, nb_periods):

    times = times1
    positions = positions1
    speeds = speeds1

    dt = times1[1] - times1[0]
    period = times1[-1] + dt

    for i in range(1, nb_periods):
        times = np.append(times, times1 + i * period)
        positions = np.append(positions, positions1)
        speeds = np.append(speeds, speeds1)

    return times, positions, speeds


if __name__ == "__main__":

    z_max = 0.78
    z_min = 0.02

    coef = 2

    v_up = 0.1 / coef
    v_down = 0.07 / coef

    acc = 0.05 / coef  # Fix acceleration
    dacc = 0.05 / coef  # Fix acceleration

    dt = 0.25 * coef
    t_exp = 100.0
    t_bottom = 10.0 * coef
    t_period = 60.0 * coef

    times1, positions1, speeds1, t_total = make_track_sleep_1period_tbottom(
        z_max, z_min, v_up, v_down, acc, dacc, dt, t_bottom, t_period
    )

    nb_periods = int(round(t_exp / t_total, 0))

    times, speeds, positions = concatenate(
        times1, speeds1, positions1, nb_periods
    )

    fig = plt.figure()
    ax = fig.gca()
    ax.set_xlabel("time (s)")
    ax.set_ylabel("position (m)")
    ax.plot(times1, positions1, "x")

    plt.show()
