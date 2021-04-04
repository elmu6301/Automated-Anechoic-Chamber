from motor_driver_interface_v2 import findSystemMotorDrivers, MotorDriver
from find_aligned_position import findAlignedPosition
from error_codes import *

def calibrate():
    rv = findSystemMotorDrivers()
    if rv['error code'] != ERROR_CODE__SUCCESS:
        return rv['error code']
    Test_MD = rv['test motor driver']
    Probe_MD = rv['probe motor driver']
    error_code = findAlignedPosition(Test_MD, Probe_MD)
    del Test_MD
    del Probe_MD
    return error_code