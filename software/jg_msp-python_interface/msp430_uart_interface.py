#%%
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 21:46:17 2020

@author: jgamm
"""

import serial
def flush():
    global MSP430
    while MSP430.in_waiting:
        MSP430.read()

try:
    MSP430 = serial.Serial('COM6', baudrate = 115200)
    flush()
except:
    pass



def query_available():
    print('Checking MCU availability...')
    flush()
    MSP430.write(b'q\n')
    resp = await_response()
    if resp == 'A':
        print('\tNo command pending')
    elif resp == 'N':
        print('\tCommand pending')
    else:
        print('\tUnknown response: %s'%(resp))
    return resp == 'A'

def await_response():
    global MSP430
    while MSP430.in_waiting == 0:
        pass
    response = MSP430.read()
    assert response in [b'A', b'D', b'N']
    return response.decode()

def configure_motor_driver(timer=0, 
                           step_port=1, step_pin=2, 
                           dir_port=1, dir_pin=4, 
                           res_port=1, res_pin=5, 
                           sd_port=2, sd_pin=2):
    global MSP430
    flush()
    print('Configuring motor driver...')
    available = query_available()
    if not available:
        print('\tCannot configure; MCU busy')
        return
    s = 'c%d%d%d%d%d%d%d%d%d\n'%(timer, step_port-1, step_pin, dir_port-1, dir_pin, res_port-1, res_pin, sd_port-1, sd_pin)
    print('\tWriting string: %s'%(s[:-1]))
    MSP430.write(s.encode('ascii'))
    r = await_response()
    if r == 'A':
        print('\tAcked')
    elif r == 'N':
        print('\tNacked')
        return
    else:
        print('\tUnknown response: %s'%(r))
        return
    r = await_response()
    if r == 'D':
        print('\tDone')
    else:
        print('\tUnknown response: %s'%(r))

def turn_motor(direction=True, num_steps=1e5, frequency=3e4):
    global MSP430
    flush()
    print('Turning motor...')
    available = query_available()
    if not available:
        print('\tCannot turn motor; MCU busy')
        return
    s = 't%d%010d%010d\n'%(direction, num_steps, frequency)
    print('\tWriting string: %s'%(s[:-1]))
    MSP430.write(s.encode('ascii'))
    r = await_response()
    if r == 'A':
        print('\tAcked')
    elif r == 'N':
        print('\tNacked')
        MSP430.flush()
        return
    else:
        print('\tUnknown response: %s'%(r))
        MSP430.flush()
        return
    r = await_response()
    if r == 'D':
        print('\tDone')
    else:
        print('\tUnknown response: %s'%(r))

assert query_available()

while True:
    turn_motor(False, 25000, 30e3)
    turn_motor(False, 25000, 30e3)
    turn_motor(True, 25000, 30e3)
    turn_motor(True, 25000, 30e3)
    turn_motor(True, 25000, 30e3)
    turn_motor(True, 25000, 30e3)
    turn_motor(False, 25000, 30e3)
    turn_motor(False, 25000, 30e3)

turn_motor(False, 25000, 30e3)

# 9,144,000 @ 30kHz

