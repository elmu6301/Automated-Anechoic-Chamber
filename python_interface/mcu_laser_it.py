#%%
# -*- coding: utf-8 -*-

# Section 1

COM_test = r'COM15'
COM_probe = r'COM21'
motor = 'theta'

def degreesToSteps(degrees):
    return int(9140000*(degrees/360))

from motor_driver_interface_v2 import MotorDriver

Test = MotorDriver(COM_test)
Probe = MotorDriver(COM_probe)

vals = []
Test.writeLaser(True)
Test.turnMotor('theta', 10000, 'ccw')
Test.turnMotor('phi', 20000, 'ccw')
for i in range(200):
    Test.turnMotor('theta', 100, 'cw')
    for j in range(200):
        Test.turnMotor('phi', 200, 'cw')
        vals.append(Probe.readSensor())
    Test.turnMotor('phi', 200000, 'ccw')
        

#%%

# Section 2

Test.writeLaser(True)

#%%

# Section 3

Test.turnMotor('theta', degreesToSteps(.01), 'cw')
Test.turnMotor('theta', degreesToSteps(.01), 'ccw')

#%%

# Section 4

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

noise_mean = 400.481
noise_stdev = 33.448

Test.turnMotor('theta', degreesToSteps(.97), 'ccw')

measurements = []
# Left of the paper
for i in range(97):
    measurements.append(Probe.readSensor())
    Test.turnMotor('theta', degreesToSteps(.01), 'cw')
# On the paper
for i in range(97):
    measurements.append(Probe.readSensor())
    Test.turnMotor('theta', degreesToSteps(.01), 'cw')
# Right of the paper
for i in range(97):
    measurements.append(Probe.readSensor())
    Test.turnMotor('theta', degreesToSteps(.01), 'cw')

font = {'family': 'normal',
        'weight': 'bold',
        'size': 22}
msize = 20
matplotlib.rc('font', **font)
figsize = (16, 12)
plt.figure(figsize=figsize)
plt.plot(np.linspace(-1.455, 1.455, 3*97), measurements, color='blue', label='Measured ADC output')
plt.plot(np.linspace(-1.455, 1.455, 3*97), noise_mean + 10*noise_stdev*np.ones(len(measurements)), color='green', label='Noise mean+4*stdev')
plt.axvline(-.485, color='red', label='Edge of tube')
plt.axvline(.485, color='red')
plt.xlabel('Angle (degrees, rel. to straight at tube)')
plt.ylabel('Raw ADC output')
plt.legend()
print('Interval: ', .01*np.count_nonzero(np.array(measurements) >= noise_mean+10*noise_stdev), 'degrees')

#%%

# Section 5

Test.writeLaser(False)




#%%

Test.turnMotor('theta', degreesToSteps(2*.97), 'ccw')
Test.turnMotor('theta', degreesToSteps(.97), 'cw')

#from matplotlib import pyplot as plt
#import numpy as np
#
#Test.writeLaser(False)
#Test.writeLaser(True)
#Test.turnMotor('theta', degreesToSteps(.97), 'cw')
#Test.turnMotor('theta', degreesToSteps(3*97*.01), 'ccw')
#
#noise_mean = 39.27
#noise_stdev = 3.385
#
#measurements = []
## Left of the paper
#for i in range(97):
#    measurements.append(Probe.readSensor())
#    Test.turnMotor('theta', degreesToSteps(.01), 'cw')
## On the paper
#for i in range(97):
#    measurements.append(Probe.readSensor())
#    Test.turnMotor('theta', degreesToSteps(.01), 'cw')
## Right of the paper
#for i in range(97):
#    measurements.append(Probe.readSensor())
#    Test.turnMotor('theta', degreesToSteps(.01), 'cw')
#plt.plot(range(len(measurements)), measurements)
#plt.plot(range(len(measurements)), noise_mean + 4*noise_stdev*np.ones(len(measurements)))
#plt.axvline(97)
#plt.axvline(2*97)
#print('Interval: ', .01*np.count_nonzero(np.array(measurements) >= noise_mean+4*noise_stdev), 'degrees')

measurements = []
for i in range(1000):
    measurements.append(Probe.readSensor())
print(np.mean(measurements))
print(np.std(measurements))

print(Probe.readSensor())

# 97 * .01 degrees = .97
# Mean noise: 39.27
# Std noise: 3.385