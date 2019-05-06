"""
Toolkit for various tasks (:mod:`fluidlab.util.util`)
=====================================================

"""


def make_ip_as_str(ip_modbus):
    list_ip = ip_modbus.split(".")
    ip_as_str = list_ip[0] + "_"
    for index in range(1, len(list_ip)):
        ip_as_str += list_ip[index] + "_"
    return ip_as_str


if __name__ == "__main__":
    ip_modbus = "192.168.28.11"
    ip_as_str = make_ip_as_str(ip_modbus)
