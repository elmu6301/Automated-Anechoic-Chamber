#%%
# -*- coding: utf-8 -*-

# Connect to device


def degreesToSteps(degrees):
    return int(9144000*(degrees/360))

from motor_driver_interface_v2 import MotorDriver

COM = r'COM21'

MD = MotorDriver(COM, debug=False)



#%%

# Motor control

import time
t_0 = time.time()
MD.turnMotor('theta', degreesToSteps(10), 'cw')
MD.turnMotor('theta', degreesToSteps(10), 'ccw')
print(time.time()-t_0)

MD.turnMotor('theta', 10000, 'ccw')
MD.turnMotor('theta', degreesToSteps(180), 'ccw')
MD.turnMotor('phi', 100000, 'ccw')
MD.turnMotor('phi', degreesToSteps(1), 'ccw')
MD.alignMotor('theta')
MD.alignMotor('phi')


#%%

MD.startTurnMotor('theta', 4500000, 'cw')
MD.startTurnMotor('phi', 9187000, 'cw')
MD.waitForDone()
MD.waitForDone()

# Theta motor: roughly 4499000
# Phi motor: roughly 9142000

phi_angle = 9187000

#%%

import time
for i in range(50):
    MD.turnMotor('theta', 1000, 'cw')
    time.sleep(.25)
    MD.turnMotor('theta', 1000, 'ccw')
    time.sleep(.25)

MD.turnMotor('theta', 4494400, 'cw')
MD.turnMotor('phi', 9142000, 'cw')
#%%

angle = 0
MD.turnMotor('theta', 100, 'cw')
angle += 100
MD.turnMotor('theta', 100, 'ccw')
angle -= 100

# Alignment checker control

MD.writeLaser(True)
MD.writeLaser(False)
print(MD.readSensor())

import numpy as np
vals = []
for i in range(1000):
    vals.append(MD.readSensor())
print(np.mean(vals))
print(np.std(vals))
print(np.max(vals))
print(np.min(vals))

#%%

# Check status

MD.getId()
MD.getAssertInfo()
MD.invokeBsl()
MD.getFreq('theta')
MD.getFreq('phi')
MD.setFreq('theta', 6553)
MD.setFreq('phi', 12345)
MD.setAlignedOrientation(321, 123)
MD.getOrientation('theta', 'aligned')
MD.getOrientation('phi', 'aligned')
MD.getOrientation('theta', 'current')
MD.getOrientation('phi', 'current')
MD.findEndSwitch('theta', 'ccw')
MD.findEndSwitch('phi', 'ccw')
MD.turnMotor('theta', 50000, 'cw')
MD.turnMotor('phi',   100000, 'cw')
MD.turnMotor('theta', 50000, 'ccw')
MD.turnMotor('phi',   100000, 'ccw')

#%%

# List of things to check to verify functionality

# Should complete without errors.
from matplotlib import pyplot as plt
from scipy.stats import linregress
import numpy as np
from motor_driver_interface_v2 import MotorDriver
COM = r'COM15'
MD = MotorDriver(COM)

# Assert info should reflect last assert statement
print(MD.getAssertInfo())

# Test side: ensure TXRXID pin is grounded.
assert MD.getId() == 'TEST'
# Laser should turn off/on 5 times.
for i in range(5):
    MD.writeLaser(True)
    time.sleep(.5)
    MD.writeLaser(False)
    time.sleep(.5)

# Probe side: ensure TXRXID pin is 3.3V
assert MD.getId() == 'PROBE'
print(MD.readSensor()) # Should reflect INTENSITY pin; 4095 for 3.3V and 0 for GND

# Regression lines should match datapoints fairly closely
steps = []
times = []
for i in [1, 10, 100, 1000, 10000]:
    for j in range(i, 10*i, i):
        steps.append(j)
        times.append(MD.turnMotor('phi', j, 'cw'))
plt.plot(steps, times, '.')
m, b, _, _, _ = linregress(steps, times)
plt.plot(steps, m*np.array(steps)+b, '--')
plt.xscale('log')
plt.yscale('log')
plt.figure()
steps = []
times = []
for i in [1, 10, 100, 1000, 10000]:
    for j in range(i, 10*i, i):
        steps.append(j)
        times.append(MD.turnMotor('theta', j, 'cw'))
plt.plot(steps, times, '.')
m, b, _, _, _ = linregress(steps, times)
plt.plot(steps, m*np.array(steps)+b, '--')
plt.xscale('log')
plt.yscale('log')


def getData(orientation):
    return np.sin(2*np.pi*orientation/360)

otp = [[], []]
for orientation in np.linspace(0, 360, 30):
    MD.turnMotor('phi', int(9142000/30), 'cw')
    otp[0].append(orientation)
    otp[1].append(getData(orientation))
plt.plot(otp[0], otp[1])
plt.xlabel('Orientation (degrees)')
plt.ylabel('Measurement')

