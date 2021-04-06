#%%

# Section 1

from motor_driver_interface import MotorDriver

probe_COM = r'COM15'
test_COM = r'COM21'

Test = MotorDriver(test_COM)
Probe = MotorDriver(probe_COM)

#%%

# Section 2

Test.startTurnMotor('theta', 4494000, 'cw')
Probe.startTurnMotor('theta', 4494000, 'ccw')
Test.waitForDone()
Probe.waitForDone()
Test.turnMotor('phi', 9142000, 'cw')


# Theta motor: roughly 4499000
# Phi motor: roughly 9142000