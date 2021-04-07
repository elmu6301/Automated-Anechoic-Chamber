# Include
import pydoc
import os
import json

from drivers.motor_driver_interface import findSystemMotorDrivers, MotorDriver
import numpy as np
from drivers.VNA_gpib import VNA_HP8719A
from util import error_codes
import time

TT_SPR = 4494000
TP_SPR = 9142000
PP_SPR = 4494000


def _printf(phase, flag, msg):
    """ Prints out messages to the command line by specifying flag and phase. """
    if flag in ("Error", "Warning"):
        print(f"({phase}) {flag}: {msg}")
    else:
        print(f"({phase}):".ljust(11), f"{msg}")


def run_Align():
    current_phase = 'Setup'

    def printf(msg):
        _printf(current_phase, None, msg)

    printf('Setting up the system...')
    printf('\tDetecting motor drivers...')
    rv = findSystemMotorDrivers()
    if rv['error code'] != error_codes.SUCCESS:
        return rv['error code']
    printf('\t\tDone.')
    printf('\tConnecting to test-side device...')
    Test_MD = rv['test motor driver']
    printf('\t\tDone.')
    printf('\tConnecting to probe-side device...')
    Probe_MD = rv['probe motor driver']
    printf('\t\tDone.')

    def disconnect():
        try:
            del Test_MD
        except:
            pass
        try:
            del Probe_MD
        except:
            pass

    current_phase = 'Running'
    printf('Running alignment phase...')
    printf('\tMeasuring ambient light level...')
    t0 = time.time()
    Test_MD.writeLaser(False)
    ambient_values = []
    for i in range(100):
        val = Probe_MD.readSensor()
        ambient_values.append(val)
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\t\tMean: %f Volts.' % (3.3 * np.mean(ambient_values) / 4096))
    printf('\t\tStd. dev.: %f Volts.' % (3.3 * np.std(ambient_values) / 4096))
    printf('\tAligning test-theta motor...')
    t0 = time.time()
    error_code = Test_MD.align('theta')
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.TEST_THETA_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\tAligning test-phi motor...')
    t0 = time.time()
    error_code = Test_MD.align('phi')
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.TEST_PHI_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\tAligning probe-phi motor...')
    t0 = time.time()
    error_code = Probe_MD.align('phi')
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.PROBE_PHI_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\tMeasuring light level when aligned...')
    t0 = time.time()
    Test_MD.writeLaser(True)
    time.sleep(.1)
    aligned_value = Probe_MD.readSensor()
    Test_MD.writeLaser(False)
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\t\tLight level: %f Volts.' % (3.3 * aligned_value / 4096))
    printf('\t\t%f std. devs. above the ambient level.' % (
                (aligned_value - np.mean(ambient_values)) / np.std(ambient_values)))
    if Test_MD.getOrientation('theta', 'aligned') != Test_MD.getOrientation('theta', 'current'):
        disconnect()
        return error_codes.ALIGNMENT
    if Test_MD.getOrientation('phi', 'aligned') != Test_MD.getOrientation('phi', 'current'):
        disconnect()
        return error_codes.ALIGNMENT
    if Probe_MD.getOrientation('phi', 'aligned') != Probe_MD.getOrientation('phi', 'current'):
        disconnect()
        return error_codes.SUCCESS

    current_phase = 'Shutdown'
    printf('Shutting down the system...')
    disconnect()
    printf('\tDone.')
    return error_codes.SUCCESS


'''
experiments.py
This file contains functions generate commands and run various experiments.
'''


def run_sweepFreq(args):
    current_phase = 'Setup'

    def printf(msg):
        _printf(current_phase, None, msg)

    # Get necessary configuration settings
    printf('Parsing configuration settings...')
    try:
        printf('\tTest-theta axis:')
        test_theta_start = args['test-theta start']
        assert (type(test_theta_start) == float) and (-180 <= test_theta_start <= 180)
        printf('\t\tStart: %f degrees' % (test_theta_start))
        test_theta_end = args['test-theta end']
        assert (type(test_theta_end) == float) and (-180 <= test_theta_end <= 180)

        if test_theta_end == test_theta_start:
            test_theta_end += 360
        printf('\t\tEnd: %f degrees' % (test_theta_end))
        test_theta_steps = args['test-theta steps']
        assert (type(test_theta_steps) == int) and (test_theta_steps > 0)
        printf('\t\tSteps: %d' % (test_theta_steps))
        printf('\tTest-phi axis:')
        test_phi_start = args['test-phi start']
        assert (type(test_phi_start) == float) and (-180 <= test_phi_start <= 180)
        printf('\t\tStart: %f degrees' % (test_phi_start))
        test_phi_end = args['test-phi end']
        assert (type(test_phi_end) == float) and (-180 <= test_phi_end <= 180)

        if test_phi_end == test_phi_start:
            test_phi_end += 360
        printf('\t\tEnd: %f degrees' % (test_phi_end))
        test_phi_steps = args['test-phi steps']
        assert (type(test_phi_steps) == int) and (test_phi_steps > 0)
        printf('\t\tSteps: %d' % (test_phi_steps))
        printf('\tProbe-phi axis:')
        probe_phi_start = args['probe-phi start']
        assert (type(probe_phi_start) == float) and (-180 <= probe_phi_start <= 180)
        printf('\t\tStart: %f degrees' % (probe_phi_start))
        probe_phi_end = args['probe-phi end']
        assert (type(probe_phi_end) == float) and (-180 <= probe_phi_end <= 180)

        if probe_phi_start == probe_phi_end:
            probe_phi_end += 360
        printf('\t\tEnd: %f degrees' % (probe_phi_end))
        probe_phi_steps = args['probe-phi steps']
        assert (type(probe_phi_steps) == int) and (probe_phi_steps > 0)
        printf('\t\tSteps: %d' % (probe_phi_steps))
        printf('\tAlignment:')
        alignment = args['alignment']
        assert type(alignment) == bool
        printf('\t\tWill use: %s' % (alignment))

        if alignment == True:
            alignment_tolerance = args['alignment tolerance']
            assert (type(alignment_tolerance) == float) and (alignment_tolerance >= 0)
            printf('\t\tTolerance: %f standard deviations' % (alignment_tolerance))
        printf('\tVNA settings:')
        freq_start = args['start frequency']
        assert type(freq_start) == float
        printf('\t\tStart frequency: %f GHz' % (freq_start))
        freq_stop = args['stop frequency']
        assert type(freq_stop) == float
        printf('\t\tStop frequency: %f GHz' % (freq_stop))
        freq_sweep_type = args['frequency sweep type']
        assert freq_sweep_type in ['log', 'linear']
        printf('\t\tSweep type: %s' % (freq_sweep_type))
        freq_sweep_type = 1 if freq_sweep_type == 'log' else 0
        data_type = args['VNA data type']

        if type(data_type) == str:
            assert data_type in ['logmag', 'phase', 'sparam']
            data_type = [data_type]
        else:
            assert (type(data_type) == list) and set(data_type).issubset(set(['logmag', 'phase', 'sparam']))
        printf('\t\tTypes of data to collect: %s' % (', '.join(data_type)))
    except:
        return error_codes.BAD_ARGS

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
            del VNA  # need to implement __del__ to close pyvisa connection
        except:
            pass

    # Connect to motor driver PCBs
    printf('Setting up the system...')
    printf('\tDetecting motor drivers...')
    rv = findSystemMotorDrivers()
    if rv['error code'] != error_codes.SUCCESS:
        return rv['error code']
    printf('\t\tDone.')
    printf('\tConnecting to test-side device...')
    Test_MD = rv['test motor driver']
    printf('\t\tDone.')
    printf('\tConnecting to probe-side device...')
    Probe_MD = rv['probe motor driver']
    printf('\t\tDone.')

    ###############################################################
    # Elena: connect to VNA here

    # Connect to VNA
    printf('\tConnecting to VNA...')
    try:
        VNA = VNA_HP8719A(None)  # unused parameter address
        VNA.freq_sweep_type(freq_sweep_type)
        VNA.init_freq_sweep(freq_start, freq_stop)
    except:
        pass
        # disconnect()
        # return error_codes.VNA
    printf('\t\tDone.')

    ################################################################

    current_phase = 'Running'
    # Run alignment routine
    if alignment == True:
        printf('Running alignment phase...')
        printf('\tMeasuring ambient light level...')
        t0 = time.time()
        Test_MD.writeLaser(False)
        ambient_values = []
        for i in range(100):
            val = Probe_MD.readSensor()
            ambient_values.append(val)
        printf('\t\tDone.')
        printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        printf('\t\tMean: %f Volts.' % (3.3 * np.mean(ambient_values) / 4096))
        printf('\t\tStd. dev.: %f Volts.' % (3.3 * np.std(ambient_values) / 4096))
        printf('\tAligning test-theta motor...')
        t0 = time.time()
        error_code = Test_MD.align('theta', gradual=True)
        if error_code != error_codes.SUCCESS:
            disconnect()
            return error_codes.TEST_THETA_FAULT
        printf('\t\tDone.')
        printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        printf('\tAligning test-phi motor...')
        t0 = time.time()
        error_code = Test_MD.align('phi')
        if error_code != error_codes.SUCCESS:
            disconnect()
            return error_codes.TEST_PHI_FAULT
        printf('\t\tDone.')
        printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        printf('\tAligning probe-phi motor...')
        t0 = time.time()
        error_code = Probe_MD.align('phi')
        if error_code != error_codes.SUCCESS:
            disconnect()
            return error_codes.PROBE_PHI_FAULT
        printf('\t\tDone.')
        printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        printf('\tMeasuring light level when aligned...')
        t0 = time.time()
        Test_MD.writeLaser(True)
        time.sleep(.1)
        aligned_value = Probe_MD.readSensor()
        Test_MD.writeLaser(False)
        printf('\t\tDone.')
        printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        printf('\t\tLight level: %f Volts.' % (3.3 * aligned_value / 4096))
        printf('\t\t%f std. devs. above the ambient level.' % (
                    (aligned_value - np.mean(ambient_values)) / np.std(ambient_values)))
        if Test_MD.getOrientation('theta', 'aligned') != Test_MD.getOrientation('theta', 'current'):
            disconnect()
            return error_codes.ALIGNMENT
        if Test_MD.getOrientation('phi', 'aligned') != Test_MD.getOrientation('phi', 'current'):
            disconnect()
            return error_codes.ALIGNMENT
        if Probe_MD.getOrientation('phi', 'aligned') != Probe_MD.getOrientation('phi', 'current'):
            disconnect()
            return error_codes.SUCCESS
        if (aligned_value < np.mean(ambient_values)) \
                or ((np.abs(aligned_value - np.mean(ambient_values)) / np.std(ambient_values)) < alignment_tolerance):
            disconnect()
            return error_codes.ALIGNMENT
    else:
        printf('Skipping alignment phase.')

    # Move motors to start location
    printf('Moving motors to starting orientations...')
    test_theta_offset = int(TT_SPR * np.abs(test_theta_start) / 360)
    test_theta_dir = 'cw' if test_theta_start >= 0 else 'ccw'
    test_phi_offset = int(TP_SPR * np.abs(test_phi_start) / 360)
    test_phi_dir = 'cw' if test_phi_start >= 0 else 'ccw'
    probe_phi_offset = int(PP_SPR * np.abs(probe_phi_start) / 360)
    probe_phi_dir = 'cw' if probe_phi_start >= 0 else 'ccw'
    printf('\tMoving test-theta motor...')
    t0 = time.time()
    error_code = Test_MD.turnMotor('theta', test_theta_offset, test_theta_dir, gradual=True)
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.TEST_THETA_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\tMoving test-phi motor...')
    t0 = time.time()
    error_code = Test_MD.turnMotor('phi', test_phi_offset, test_phi_dir)
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.TEST_PHI_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\tMoving probe-phi motor...')
    t0 = time.time()
    error_code = Probe_MD.turnMotor('phi', probe_phi_offset, probe_phi_dir)
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.PROBE_PHI_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))

    # Take measurements at specified orientations
    printf('Running measurement phase...')
    Data = []
    test_theta_increment = 0 if test_theta_steps == 1 else int(
        TT_SPR * np.abs(test_theta_start - test_theta_end) / (360 * (test_theta_steps - 1)))
    test_theta_direction = 'cw' if test_theta_end - test_theta_start > 0 else 'ccw'
    test_phi_increment = 0 if test_phi_steps == 1 else int(
        TP_SPR * np.abs(test_phi_start - test_phi_end) / (360 * (test_phi_steps - 1)))
    test_phi_direction = 'cw' if test_phi_end - test_phi_start > 0 else 'ccw'
    probe_phi_increment = 0 if probe_phi_steps == 1 else int(
        PP_SPR * np.abs(probe_phi_start - probe_phi_end) / (360 * (probe_phi_steps - 1)))
    probe_phi_direction = 'cw' if probe_phi_end - probe_phi_start > 0 else 'ccw'
    measurement_number = 1
    total_measurements = test_theta_steps * probe_phi_steps * test_phi_steps
    for idx__test_theta in np.arange(test_theta_steps):
        for idx__probe_phi in np.arange(probe_phi_steps):
            for idx__test_phi in np.arange(test_phi_steps):
                printf('\tTaking measurement %d of %d...' % (measurement_number, total_measurements))
                measurement_number += 1
                test_theta_orientation = test_theta_start + idx__test_theta * (
                    ((test_theta_end - test_theta_start) / (test_theta_steps - 1)) if test_theta_steps != 1 else 0)
                test_phi_orientation = test_phi_start + idx__test_phi * (
                    ((test_phi_end - test_phi_start) / (test_phi_steps - 1)) if test_phi_steps != 1 else 0)
                probe_phi_orientation = probe_phi_start + idx__probe_phi * (
                    ((probe_phi_end - probe_phi_start) / (probe_phi_steps - 1)) if probe_phi_steps != 1 else 0)
                printf('\t\tTest-theta orientation: %f degrees.' % (test_theta_orientation))
                printf('\t\tTest-phi orientation: %f degrees.' % (test_phi_orientation))
                printf('\t\tProbe-phi orientation: %f degrees.' % (probe_phi_orientation))

                ##################################################################################
                #   Elena: take/record data here; see variables representing current orientation above

                time.sleep(1)
                logmag_data = None
                if 'logmag' in data_type:
                    printf('\t\tTaking logmag measurement...')
                    t0 = time.time()
                    # logmag_data = VNA.logmag_data(freq_sweep_type)
                    printf('\t\t\tDone.')
                    printf('\t\t\tTime taken: %f seconds.' % (time.time() - t0))
                phase_data = None
                if 'phase' in data_type:
                    printf('\t\tTaking phase measurement...')
                    t0 = time.time()
                    # phase_data = VNA.phase_data(freq_sweep_type)
                    printf('\t\t\tDone.')
                    printf('\t\t\tTime taken: %f seconds.' % (time.time() - t0))
                sparam_data = None
                if 'sparam' in data_type:
                    printf('\t\tTaking s-parameter measurement...')
                    t0 = time.time()
                    # sparam_data = VNA.sparam_data(freq_sweep_type)
                    printf('\t\t\tDone.')
                    printf('\t\t\tTime taken: %f seconds.' % (time.time() - t0))
                Data.append({'test-theta': test_theta_orientation,
                             'test-phi': test_phi_orientation,
                             'probe-phi': probe_phi_orientation,
                             'logmag data': logmag_data,
                             'phase data': phase_data,
                             'sparam data': sparam_data})

                ##################################################################################

                if idx__test_phi != test_phi_steps - 1:
                    printf('\tMoving test-phi motor...')
                    t0 = time.time()
                    error_code = Test_MD.turnMotor('phi', test_phi_increment, test_phi_direction)
                    if error_code != error_codes.SUCCESS:
                        disconnect()
                        return error_codes.TEST_PHI_FAULT
                    printf('\t\tDone.')
                    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
            if idx__probe_phi != probe_phi_steps - 1:
                printf('\tMoving probe-phi motor...')
                t0 = time.time()
                error_code = Probe_MD.turnMotor('phi', probe_phi_increment, probe_phi_direction)
                if error_code != error_codes.SUCCESS:
                    disconnect()
                    return error_codes.PROBE_PHI_FAULT
                printf('\t\tDone.')
                printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
            if np.abs(test_phi_start - test_phi_end) != 360:
                printf('\tMoving test-phi motor...')
                t0 = time.time()
                error_code = Test_MD.turnMotor('phi', (test_phi_steps - 1) * test_phi_increment,
                                               'ccw' if test_phi_direction == 'cw' else 'cw')
                if error_code != error_codes.SUCCESS:
                    disconnect()
                    return error_codes.TEST_PHI_FAULT
                printf('\t\tDone.')
                printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        if idx__test_theta != test_theta_steps - 1:
            printf('\tMoving test-theta motor...')
            t0 = time.time()
            error_code = Test_MD.turnMotor('theta', test_theta_increment, test_theta_direction, gradual=True)
            if error_code != error_codes.SUCCESS:
                disconnect()
                return error_codes.TEST_THETA_FAULT
            printf('\t\tDone.')
            printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
        if np.abs(probe_phi_start - probe_phi_end) != 360:
            printf('\tMoving probe-phi motor...')
            t0 = time.time()
            error_code = Probe_MD.turnMotor('phi', (probe_phi_steps - 1) * probe_phi_increment,
                                            'ccw' if probe_phi_direction == 'cw' else 'cw')
            if error_code != error_codes.SUCCESS:
                disconnect()
                return error_codes.PROBE_PHI_FAULT
            printf('\t\tDone.')
            printf('\t\tTime taken: %f seconds.' % (time.time() - t0))
    printf('\tMoving test-theta motor...')
    t0 = time.time()
    error_code = Test_MD.turnMotor('theta', (test_theta_steps - 1) * test_theta_increment,
                                   'ccw' if test_theta_direction == 'cw' else 'cw', gradual=True)
    if error_code != error_codes.SUCCESS:
        disconnect()
        return error_codes.TEST_THETA_FAULT
    printf('\t\tDone.')
    printf('\t\tTime taken: %f seconds.' % (time.time() - t0))

    current_phase = 'Shutdown'
    printf('Shutting down the system...')
    disconnect()
    printf('\tDone.')

    ##############################################################################
    # Elena: plot data here

    ##############################################################################

    return error_codes.SUCCESS


def run_sweepPhi(args):
    try:
        test_theta_orientation = args['test-theta orientation']
        assert (type(test_theta_orientation) == float) and (-180 <= test_theta_orientation <= 180)
        probe_phi_orientation = args['probe-phi orientation']
        assert (type(probe_phi_orientation) == float) and (-180 <= probe_phi_orientation <= 180)
        args['test-theta start'] = test_theta_orientation
        args['test-theta end'] = test_theta_orientation
        args['test-theta steps'] = 1
        args['probe-phi start'] = probe_phi_orientation
        args['probe-phi end'] = probe_phi_orientation
        args['probe-phi steps'] = 1
    except:
        return error_codes.BAD_ARGS
    error_code = run_sweepFreq(args)
    return error_code


def run_sweepTheta(args):
    try:
        test_phi_orientation = args['test-phi orientation']
        assert (type(test_phi_orientation) == float) and (-180 <= test_phi_orientation <= 180)
        probe_phi_orientation = args['probe-phi orientation']
        assert (type(probe_phi_orientation) == float) and (-180 <= probe_phi_orientation <= 180)
        args['test-phi start'] = test_phi_orientation
        args['test-phi end'] = test_phi_orientation
        args['test-phi steps'] = 1
        args['probe-phi start'] = probe_phi_orientation
        args['probe-phi end'] = probe_phi_orientation
        args['probe-phi steps'] = 1
    except:
        return error_codes.BAD_ARGS
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