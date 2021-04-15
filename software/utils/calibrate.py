from drivers.motor_driver_interface import findSystemMotorDrivers, MotorDriver
from utils.align import findAlignedPosition
from utils import error_codes


def calibrate():
    rv = findSystemMotorDrivers()
    if rv['error code'] != error_codes.SUCCESS:
        return rv['error code']
    Test_MD = rv['test motor driver']
    Probe_MD = rv['probe motor driver']
    error_code = findAlignedPosition(Test_MD, Probe_MD)
    del Test_MD
    del Probe_MD
    return error_code