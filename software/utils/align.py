from drivers.motor_driver_interface import MotorDriver
import keyboard
import os
import time
import numpy as np
from utils import error_codes


def flush_input():
    """
    Attempts to flush input.
    :return:
    """
    try:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def _printInstructions(status, increment, sensor_output, test_theta, test_theta_a, test_phi, test_phi_a, probe_phi, probe_phi_a, mcu_updated, laser_state, ambient_output, ambient_std):
    """
    Prints the instructions for aligning the system along with system information such as the current test-side
    theta angle.
    :param status: Current status of the system.
    :param increment: Current step amount to increment by.
    :param sensor_output: Current sensor output of the photo-transistor.
    :param test_theta: Current angle of the test-side theta motor.
    :param test_theta_a: Current alignment status of the test-side theta motor.
    :param test_phi: Current angle of the test-side phi motor.
    :param test_phi_a: Current alignment status of the test-side phi motor.
    :param probe_phi: Current angle of the probe-side phi motor.
    :param probe_phi_a: Current alignment status of the probe-side phi motor.
    :param mcu_updated: Current status of the MCU.
    :param laser_state: Current state of the laser (on or off).
    :param ambient_output: Ambient light level.
    :param ambient_std: Ambient light standard deviation from the current sensor reading.
    :return:
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Calibration routine')
    print('\tControls:')
    print('\t\ta / d: rotate test-theta CCW / CW (+spacebar: find end switch)')
    print('\t\tw / s: rotate test-phi   CCW / CW (+spacebar: find end switch)')
    print('\t\tq / e: rotate probe-phi  CCW / CW (+spacebar: find end switch)')
    print('\t\tz:     set steps per press')
    print('\t\tf:     align system with current settings')
    print('\t\tb:     toggle laser state')
    print('\t\tv:     get current sensor output')
    print('\t\th:     get current ambient light level')
    print('\t\tc:     program current settings to flash')
    print('\t\tg:     import settings from flash')
    print('\t\tx:     exit')
    print('\tCurrent motor orientations:')
    if test_theta != None:
        print('\t\tTest-theta:      %d'%(test_theta))
        if test_theta_a != None:
            print('\t\t\tAligned: %d'%(test_theta_a))
    else:
        print('\t\tTest-theta:     Unknown -- must find end switch.')
    if test_phi != None:
        print('\t\tTest-phi:        %d'%(test_phi))
        if test_phi_a != None:
            print('\t\t\tAligned: %d'%(test_phi_a))
    else:
        print('\t\tTest-phi:       Unknown -- must find end switch.')
    if probe_phi != None:
        print('\t\tProbe-phi:       %d'%(probe_phi))
        if probe_phi_a != None:
            print('\t\t\tAligned: %d'%(probe_phi_a))
    else:
        print('\t\tProbe-phi:      Unknown -- must find end switch.')
    print('\t\tMCU up to date:  %s'%(mcu_updated))
    print('\tCurrent steps per press:')
    print('\t\t%d'%(increment))
    print('\tCurrent laser state:')
    print('\t\t%s'%(laser_state))
    if sensor_output != None:
        print('\tLast sensor reading:')
        print('\t\t%f Volts'%(sensor_output))
        if ambient_output!=None and ambient_std!=None:
            print('\t\t%f std. devs. from ambient level'%(np.abs(sensor_output-ambient_output)/ambient_std))
            print('\tAmbient light:')
            print('\t\t%f +/- %f mean +/- std. dev. Volts'%(ambient_output, ambient_std))
    print('\n\t%s'%(status))


def findAlignedPosition(MD_test, MD_probe):
    """
    Runs the alignnment calibration routine.
    :param MD_test: Test-side motor driver.
    :param MD_probe: Probe-side motor driver.
    :return:
    """
    increment = 100000
    sensor_output = None
    ambient_output = None
    ambient_std = None
    test_theta = None
    test_phi = None
    probe_phi = None
    test_theta_a = None
    test_phi_a = None
    probe_phi_a = None
    mcu_updated = False
    laser_state = False
    MD_test.writeLaser(False)
    error_code = error_codes.SUCCESS

    MD_test.setFreq('theta', 32768)
    MD_test.setFreq('phi', 65536)
    MD_probe.setFreq('phi', 65536)
    
    def printInstructions(status):
        _printInstructions(status, increment, sensor_output, test_theta, test_theta_a, test_phi, test_phi_a, probe_phi, probe_phi_a, mcu_updated, laser_state, ambient_output, ambient_std)
    
    def end():
        printInstructions('Exited program.')
        flush_input()
        
    printInstructions('Ready for next command.')
    
    while True:
        if keyboard.is_pressed('a'): # Rotate test-theta CW
            mcu_updated = False
            if keyboard.is_pressed('space'): # Find end switch
                printInstructions('Aligning test-theta with end switch CW...')
                error_code = MD_test.findEndSwitch('theta', 'ccw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_THETA_FAULT
                    break
                test_theta = 0
            else:
                printInstructions('Rotating test-theta CW...')
                error_code = MD_test.turnMotor('theta', increment, 'ccw', gradual=True)
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_THETA_FAULT
                    end()
                    break
                if test_theta != None:
                    test_theta -= increment
            while keyboard.is_pressed('a'):
                pass
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('d'): # Rotate test-theta CCW
            mcu_updated = False
            if keyboard.is_pressed('space'): # Find end switch
                printInstructions('Aligning test-theta with end switch CCW...')
                error_code = MD_test.findEndSwitch('theta', 'cw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_THETA_FAULT
                    end()
                    break
                test_theta = 0
            else:
                printInstructions('Rotating test-theta CCW...')
                error_code = MD_test.turnMotor('theta', increment, 'cw', gradual=True)
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_THETA_FAULT
                    end()
                    break
                if test_theta != None:
                    test_theta += increment
            while keyboard.is_pressed('d'):
                pass
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('w'): # Rotate test-phi CCW
            mcu_updated = False
            if keyboard.is_pressed('space'): # Find end switch
                printInstructions('Aligning test-phi with end switch CCW...')
                error_code = MD_test.findEndSwitch('phi', 'ccw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_PHI_FAULT
                    end()
                    break
                test_phi = 0
            else:
                printInstructions('Rotating test-phi CCW...')
                error_code = MD_test.turnMotor('phi', increment, 'ccw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_PHI_FAULT
                    end()
                    break
                if test_phi != None:
                    test_phi -= increment
            while keyboard.is_pressed('w'):
                pass
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('s'): # Rotate test-phi CW
            mcu_updated = False
            if keyboard.is_pressed('space'): # Find end switch
                printInstructions('Aligning test-phi with end switch CW...')
                error_code = MD_test.findEndSwitch('phi', 'cw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_PHI_FAULT
                    end()
                    break
                test_phi = 0
            else:
                printInstructions('Rotating test-phi CW...')
                error_code = MD_test.turnMotor('phi', increment, 'cw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_PHI_FAULT
                    end()
                    break
                if test_phi != None:
                    test_phi += increment
            while keyboard.is_pressed('s'):
                pass
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('q'): # Rotate probe-phi CCW
            mcu_updated = False
            if keyboard.is_pressed('space'): # Find end switch
                printInstructions('Aligning probe-phi with end switch CCW...')
                error_code = MD_probe.findEndSwitch('phi', 'ccw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.PROBE_PHI_FAULT
                    end()
                    break
                probe_phi = 0
            else:
                printInstructions('Rotating probe-phi CCW...')
                error_code = MD_probe.turnMotor('phi', increment, 'ccw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.PROBE_PHI_FAULT
                    end()
                    break
                if probe_phi != None:
                    probe_phi -= increment
            while keyboard.is_pressed('q'):
                pass
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('e'): # Rotate probe-phi CW
            mcu_updated = False
            if keyboard.is_pressed('space'): # Find end switch
                printInstructions('Aligning probe-phi with end switch CW...')
                error_code = MD_probe.findEndSwitch('phi', 'cw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.PROBE_PHI_FAULT
                    end()
                    break
                probe_phi = 0
            else:
                printInstructions('Rotating probe-phi CW...')
                error_code = MD_probe.turnMotor('phi', increment, 'cw')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.PROBE_PHI_FAULT
                    end()
                    break
                if probe_phi != None:
                    probe_phi += increment
            while keyboard.is_pressed('e'):
                pass
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('z'):
            while keyboard.is_pressed('z'):
                pass
            printInstructions('Configuring step size...')
            print('\n\t', end='')
            while True:
                try:
                    flush_input()
                    raw = input('Type step size, then enter.\n\t\t')
                    raw = int(raw)
                    assert 0 < raw < 0xFFFFFFFF
                    increment = raw
                    break
                except:
                    printInstructions('Configuring step size...')
                    print('\n\tInvalid input. ', end='')
            printInstructions('Ready for next command.')
        
        if keyboard.is_pressed('c'):
            printInstructions('Updating aligned orientation on MCU...')
            if (test_theta != None) and (test_phi != None):
                MD_test.setAlignedOrientation(test_theta, test_phi)
                test_theta_a = test_theta
                test_phi_a = test_phi
            if probe_phi != None:
                MD_probe.setAlignedOrientation(0, probe_phi)
                probe_phi_a = probe_phi
            mcu_updated = True
            while keyboard.is_pressed('c'):
                pass
            printInstructions('Ready for next command.')
        
        if keyboard.is_pressed('v'):
            printInstructions('Reading sensor value...')
            MD_test.writeLaser(True)
            time.sleep(.1)
            sensor_output = 3.3*MD_probe.readSensor()/4096
            MD_test.writeLaser(laser_state)
            printInstructions('Ready for next command.')
        
        if keyboard.is_pressed('b'):
            printInstructions('Toggling laser state...')
            MD_test.writeLaser(not laser_state)
            laser_state = not laser_state
            printInstructions('Ready for next command.')
        
        if keyboard.is_pressed('f'):
            if (mcu_updated == False) or (test_theta==None) or (test_phi==None) or (probe_phi==None):
                printInstructions('Ready for next command.')
                print('\nError: system must be calibrated before alignment.')
            else:
                printInstructions('Aligning system...')
                error_code = MD_test.align('theta', gradual=True)
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_THETA_FAULT
                    end()
                    break
                error_code = MD_test.align('phi')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.TEST_PHI_FAULT
                    end()
                    break
                error_code = MD_probe.align('phi')
                if error_code != error_codes.SUCCESS:
                    if error_code == error_codes.MISC:
                        error_code = error_codes.PROBE_PHI_FAULT
                    end()
                    break
            printInstructions('Ready for next command.')
        
        if keyboard.is_pressed('g'):
            printInstructions('Importing settings...')
            test_theta = MD_test.getOrientation('theta', 'current')
            test_theta_a = MD_test.getOrientation('theta', 'aligned')
            test_phi   = MD_test.getOrientation('phi', 'current')
            test_phi_a = MD_test.getOrientation('phi', 'aligned')
            probe_phi  = MD_probe.getOrientation('phi', 'current')
            probe_phi_a = MD_probe.getOrientation('phi', 'aligned')
            mcu_updated = True
            printInstructions('Ready for next command.')
            
        if keyboard.is_pressed('h'):
            printInstructions('Measuring ambient light level...')
            old_laser_state = laser_state
            MD_test.writeLaser(False)
            values = []
            for i in range(100):
                values.append(MD_probe.readSensor())
            MD_test.writeLaser(old_laser_state)
            ambient_output = 3.3*np.mean(values)/4096
            ambient_std = 3.3*np.std(values)/4096
            printInstructions('Ready for next command.')
                
        if keyboard.is_pressed('x'): # Exit function
            end()
            break
    
    return error_code