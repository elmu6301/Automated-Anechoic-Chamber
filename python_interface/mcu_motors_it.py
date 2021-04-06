#%%
# -*- coding: utf-8 -*-

# Section 1

COM = r'COM27'#r'COM21'
motor = 'theta'

def degreesToSteps(degrees):
    return int(9140000*(degrees/360))

from motor_driver_interface import MotorDriver

MD = MotorDriver(COM)

#MD.alignMotor(motor)

#%%
# Section 2

MD.turnMotor(motor, degreesToSteps(1), 'cw')

#%%
# Section 3

MD.turnMotor(motor, degreesToSteps(3), 'ccw')

#%%
# Section 4

MD.alignMotor(motor)