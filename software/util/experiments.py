# Include
import pydoc
import os
import json

from drivers.motor_driver_interface_v2 import findSystemMotorDrivers, MotorDriver
import numpy as np
from drivers.VNA_gpib import VNA_HP8719A


'''
experiments.py
This file contains functions generate commands and run various experiments.
'''

def run_sweepFreq(args):
    # Get necessary configuration settings
    try:
        test_theta_start = args['test-theta start']
        assert (type(test_theta_start) == float) and (-180 <= test_theta_start <= 180)
        test_theta_end   = args['test-theta end']
        assert (type(test_theta_end) == float) and (-180 <= test_theta_end <= 180)
        if test_theta_end == test_theta_start:
            test_theta_end += 360
        test_theta_steps = args['test-theta steps']
        assert (type(test_theta_steps) == int) and (test_theta_steps > 0)
        test_phi_start   = args['test-phi start']
        assert (type(test_phi_start) == float) and (-180 <= test_phi_start <= 180)
        test_phi_end     = args['test-phi end']
        assert (type(test_phi_end) == float) and (-180 <= test_phi_end <= 180)
        if test_phi_end == test_phi_start:
            test_phi_end += 360
        test_phi_steps   = args['test-phi steps']
        assert (type(test_phi_steps) == int) and (test_phi_steps > 0)
        probe_phi_start  = args['probe-phi start']
        assert type(probe_phi_start) == float) and (-180 <= probe_phi_start <= 180)
        probe_phi_end    = args['probe-phi end']
        assert (type(probe_phi_end) == float) and (-180 <= probe_phi_end <= 180)
        if probe_phi_start == probe_phi_end:
            probe_phi_end += 360
        probe_phi_steps  = args['probe-phi steps']
        assert (type(probe_phi_steps) == int) and (probe_phi_steps > 0)
        alignment        = args['alignment']
        assert type(alignment) == bool
        if alignment == True:
            alignment_tolerance = args['alignment tolerance'}
            assert (type(alignment_tolerance) == float) and (alignment_tolerance >= 0)
        freq_start       = args['start frequency']
        assert type(freq_start) == float
        freq_stop        = args['stop frequency']
        assert type(freq_stop) == float
        freq_sweep_type  = args['frequency sweep type']
        assert freq_sweep_type in ['log', 'linear']
        freq_sweep_type = 1 if freq_sweep_type == 'log' else 0
        data_type        = args['VNA data type']
        if type(data_type) == str:
            assert data_type in ['logmag', 'phase', 'sparam']
            data_type = [data_type]
        else:
            assert (type(data_type) == list) and set(data_type).issubset(set(['logmag', 'phase', 'sparam']))
    except:
        return ERROR_CODE__BAD_ARGS
    
    def disconnect():
        try:
            del Test_MD
        except:
            pass
        try:
            del Probe_MD
        except:
            pass
        try:
            del VNA # Close VNA connection -- no function in class
        except:
            pass
    
    # Connect to motor driver PCBs
    rv = findSystemMotorDrivers()
    if rv['error code'] != ERROR_CODE__SUCCESS:
        return rv['error code']
    Test_MD = rv['test motor driver']
    Probe_MD = rv['probe motor driver']
    
    # Connect to VNA
    try:
        VNA = VNA_HP8719A(None) # unused parameter address
        VNA.freq_sweep_type(freq_sweep_type)
        VNA.init_freq_sweep(freq_start, freq_stop)
    except:
        disconnect()
        return ERROR_CODE__VNA
    
    # Run alignment routine
    if alignment == True:
        Test_MD.writeLaser(False)
        ambient_values = []
        for i in range(100):
            val = Probe_MD.readSensor()
            ambient_values.append(val)
        error_code = Test_MD.align('theta')
        if error_code != ERROR_CODE__SUCCESS:
            disconnect()
            return ERROR_CODE__TEST_THETA_FAULT
        error_code = Test_MD.align('phi')
        if error_code != ERROR_CODE__SUCCESS:
            disconnect()
            return ERROR_CODE__TEST_PHI_FAULT
        error_code = Probe_MD.align('phi')
        if error_code != ERROR_CODE__SUCCESS:
            disconnect()
            return ERROR_CODE__PROBE_PHI_FAULT
        Test_MD.writeLaser(True)
        time.sleep(.1)
        aligned_value = Probe_MD.readSensor()
        Test_MD.writeLaser(False)
        if (aligned_value < np.mean(ambient_values)) \
          or ((np.abs(aligned_value-np.mean(ambient_values))/np.std(ambient_values)) > alignment_tolerance):
            disconnect()
            return ERROR_CODE__ALIGNMENT
        if Test_MD.getOrientation('theta', 'aligned') != Test_MD.getOrientation('theta', 'current'):
            disconnect()
            return ERROR_CODE__ALIGNMENT
        if Test_MD.getOrientation('phi', 'aligned') != Test_MD.getOrientation('phi', 'current'):
            disconnect()
            return ERROR_CODE__ALIGNMENT
        if Probe_MD.getOrientation('phi', 'aligned') != Probe_MD.getOrientation('phi', 'current'):
            disconnect()
            return ERROR_CODE__ALIGNMENT
    
    # Move motors to start location
    test_theta_offset = int(4494000*np.abs(test_theta_start)/360)
    test_theta_dir    = 'cw' if test_theta_start >= 0 else 'ccw'
    test_phi_offset   = int(9142000*np.abs(test_phi_start)/360)
    test_phi_dir      = 'cw' if test_phi_start >= 0 else 'ccw'
    probe_phi_offset  = int(9142000*np.abs(probe_phi_start)/360)
    probe_phi_dir     = 'cw' if probe_phi_start >= 0 else 'ccw'
    error_code = Test_MD.turnMotor('theta', test_theta_offset, test_theta_dir)
    if error_code != ERROR_CODE__SUCCESS:
        disconnect()
        return ERROR_CODE__TEST_THETA_FAULT
    error_code = Test_MD.turnMotor('phi', test_phi_offset, test_phi_dir)
    if error_code != ERROR_CODE__SUCCESS:
        disconnect()
        return ERROR_CODE__TEST_PHI_FAULT
    error_code = Probe_MD.turnMotor('phi', probe_phi_offset, probe_phi_dir)
    if error_code != ERROR_CODE__SUCCESS:
        disconnect()
        return ERROR_CODE__PROBE_PHI_FAULT
    
    # Take measurements at specified orientations
    Data = []
    test_theta_increment = int(4494000*np.abs(test_theta_start-test_theta_end)/(360*test_theta_steps))
    test_theta_direction = 'cw' if test_theta_end-test_theta_start > 0 else 'ccw'
    test_phi_increment   = int(9142000*np.abs(test_phi_start-test_phi_end)/(360*test_phi_steps))
    test_phi_direction   = 'cw' if test_phi_end-test_phi_start > 0 else 'ccw'
    probe_phi_increment  = int(4494000*np.abs(probe_phi_start-probe_phi_end)/(360*probe_phi_steps))
    probe_phi_direction  = 'cw' if probe_phi_end-probe_phi_start > 0 else 'ccw'
    for idx__test_theta in np.arange(test_theta_steps):
        for idx__probe_phi in np.arange(probe_phi_steps):
            for idx__test_phi in np.arange(test_phi_steps):
                test_theta_orientation = test_theta_start+idx__test_theta*((test_theta_end-test_theta_start)/test_theta_steps)
                test_phi_orientation   = test_phi_start+idx__test_phi*((test_phi_end-test_phi_start)/test_phi_steps)
                probe_phi_orientation  = probe_phi_start+idx__probe_phi*((probe_phi_end-probe_phi_start)/probe_phi_steps)
                logmag_data = None
                if 'logmag' in data_type:
                    logmag_data = VNA.logmag_data(freq_sweep_type)
                phase_data = None
                if 'phase' in data_type:
                    phase_data = VNA.phase_data(freq_sweep_type)
                sparam_data = None
                if 'sparam' in data_type:
                    sparam_data = VNA.sparam_data(freq_sweep_type)
                Data.append({'test-theta':  test_theta_orientation,
                             'test-phi':    test_phi_orientation,
                             'probe-phi':   probe_phi_orientation,
                             'logmag data': logmag_data,
                             'phase data':  phase_data,
                             'sparam data': sparam_data})
                error_code = Test_MD.turnMotor('phi', test_phi_increment, test_phi_direction)
                if error_code != ERROR_CODE__SUCCESS:
                    disconnect()
                    return ERROR_CODE__TEST_PHI_FAULT
            error_code = Probe_MD.turnMotor('phi', probe_phi_increment, probe_phi_direction)
            if error_code != ERROR_CODE__SUCCESS:
                disconnect()
                return ERROR_CODE__PROBE_PHI_FAULT
            if np.abs(test_phi_start-test_phi_end) != 360:
                error_code = Test_MD.turnMotor('phi', test_phi_increment, 'ccw' if test_phi_direction == 'cw' else 'cw')
                if error_code != ERROR_CODE__SUCCESS:
                    disconnect()
                    return ERROR_CODE__TEST_PHI_FAULT
        error_code = Test_MD.turnMotor('theta', test_theta_increment, test_theta_direction)
        if error_code != ERROR_CODE__SUCCESS:
            disconnect()
            return ERROR_CODE__TEST_THETA_FAULT
        if np.abs(probe_phi_start-probe_phi_end) != 360:    
            error_code = Probe_MD.turnMotor('phi', probe_phi_steps*probe_phi_increment, 'ccw' if probe_phi_direction == 'cw' else 'cw')
            if error_code != ERROR_CODE__SUCCESS:
                disconnect()
                return ERROR_CODE__PROBE_PHI_FAULT
    error_code = Test_MD.turnMotor('theta', test_theta_steps*test_theta_increment, 'ccw' if test_theta_direction == 'cw' else 'cw')
    if error_code != ERROR_CODE__SUCCESS:
        disconnect()
        return ERROR_CODE__TEST_THETA_FAULT
    
    # Disconnect and save/plot data
    disconnect()
    # save data as CSV
    # plot data
    
    return ERROR_CODE__SUCCESS


def run_sweepPhi(args):
    try:
        test_theta_orientation = args['test-theta orientation']
        assert (type(test_theta_orientation) == float) and (-180 <= test_theta_orientation <= 180)
        probe_phi_orientation  = args['probe-phi orientation']
        assert (type(probe_phi_orientation) == float) and (-180 <= probe_phi_orientation <= 180)
        args['test-theta start'] = test_theta_orientation
        args['test-theta end'] = test_theta_orientation
        args['test-theta steps'] = 1
        args['probe-phi start'] = probe_phi_orientation
        args['probe-phi end'] = probe_phi_orientation
        args['probe-phi steps'] = 1
    except:
        return ERROR_CODE__BAD_ARGS
    error_code = run_sweepFreq(args)
    return error_code
    


def run_sweepTheta(args):
    try:
        test_phi_orientation = args['test-phi orientation']
        assert (type(test_phi_orientation) == float) and (-180 <= test_phi_orientation <= 180)
        probe_phi_orientation  = args['probe-phi orientation']
        assert (type(probe_phi_orientation) == float) and (-180 <= probe_phi_orientation <= 180)
        args['test-phi start'] = test_phi_orientation
        args['test-phi end'] = test_phi_orientation
        args['test-phi steps'] = 1
        args['probe-phi start'] = probe_phi_orientation
        args['probe-phi end'] = probe_phi_orientation
        args['probe-phi steps'] = 1
    except:
        return ERROR_CODE__BAD_ARGS
    error_code = run_sweepFreq(args)
    return error_code


# main
def main():
    print("Experiments!!!")
    # cmds = gen_sweepPhi_cmds(360,180,-10,10,1.4)
    # cmds = gen_sweepTheta_cmds(360, 180, -10, 10, 1.4)
    # cmds = gen_sweepFreq_cmds(100,100,[[100,100],[0,0], [100,100]], [100])
    # print(f"Final orientation: {cmds[1]},{cmds[2]}")
    # print(cmds[0])
    # for cmd in cmds.get("test"):
    #     print(cmd)
    # test = usb.MSP430("COM1", "Eval Board", open=True)


if __name__ == "__main__":
    main()
