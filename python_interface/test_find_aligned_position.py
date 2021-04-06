from motor_driver_interface_v2 import MotorDriver
from find_aligned_position import findAlignedPosition

PROBE_COM = r'COM21'
TEST_COM  = r'COM15'
Probe_MD  = MotorDriver(PROBE_COM, debug=False)
Test_MD   = MotorDriver(TEST_COM, debug=False)

findAlignedPosition(Test_MD, Probe_MD)