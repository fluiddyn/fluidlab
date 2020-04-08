from .modbus_inter import get_modbus_interface


def test_false():
    inter = get_modbus_interface(port=0, module="false")
    repr(inter)
