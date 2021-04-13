# Include
import pydoc
import os
import json

from drivers.motor_driver_interface import findSystemMotorDrivers, MotorDriver
from drivers.VNA_gpib import *
from plotting import csv_functions as csv
from plotting import plotting as plots
from utils import error_codes
from utils import util


import time
import numpy as np

TT_SPR = 4494000
TP_SPR = 9142000
PP_SPR = 4494000

'''
experiments.py
This file contains functions generate commands and run various experiments.
'''


def run_Align():
    current_phase = 'Setup'

    def printf(msg):
        util.printf(current_phase, None, msg)

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


def run_sweepFreq(cmd_args, vna_args, calib_args, plot_args):
    current_phase = 'Setup'

    def printf(msg):
        util.printf(current_phase, None, msg)

    # Get necessary configuration settings
    printf('Parsing configuration settings...')
    freq_stop, freq_start = 0, 0
    try:
        printf('\tTest-theta axis:')
        test_theta_start = cmd_args['test-theta start']
        assert (type(test_theta_start) == float) and (-180 <= test_theta_start <= 180)
        printf('\t\tStart: %f degrees' % (test_theta_start))
        test_theta_end = cmd_args['test-theta end']
        assert (type(test_theta_end) == float) and (-180 <= test_theta_end <= 180)

        if test_theta_end == test_theta_start:
            test_theta_end += 360
        printf('\t\tEnd: %f degrees' % (test_theta_end))
        test_theta_steps = cmd_args['test-theta steps']
        assert (type(test_theta_steps) == int) and (test_theta_steps > 0)
        printf('\t\tSteps: %d' % (test_theta_steps))
        printf('\tTest-phi axis:')
        test_phi_start = cmd_args['test-phi start']
        assert (type(test_phi_start) == float) and (-180 <= test_phi_start <= 180)
        printf('\t\tStart: %f degrees' % (test_phi_start))
        test_phi_end = cmd_args['test-phi end']
        assert (type(test_phi_end) == float) and (-180 <= test_phi_end <= 180)

        if test_phi_end == test_phi_start:
            test_phi_end += 360
        printf('\t\tEnd: %f degrees' % (test_phi_end))
        test_phi_steps = cmd_args['test-phi steps']
        assert (type(test_phi_steps) == int) and (test_phi_steps > 0)
        printf('\t\tSteps: %d' % (test_phi_steps))
        printf('\tProbe-phi axis:')
        probe_phi_start = cmd_args['probe-phi start']
        assert (type(probe_phi_start) == float) and (-180 <= probe_phi_start <= 180)
        printf('\t\tStart: %f degrees' % (probe_phi_start))
        probe_phi_end = cmd_args['probe-phi end']
        assert (type(probe_phi_end) == float) and (-180 <= probe_phi_end <= 180)

        if probe_phi_start == probe_phi_end:
            probe_phi_end += 360
        printf('\t\tEnd: %f degrees' % (probe_phi_end))
        probe_phi_steps = cmd_args['probe-phi steps']
        assert (type(probe_phi_steps) == int) and (probe_phi_steps > 0)
        printf('\t\tSteps: %d' % (probe_phi_steps))

        printf('\tAlignment:')
        alignment = calib_args['align']
        assert type(alignment) == bool
        printf('\t\tWill use: %s' % (alignment))

        if alignment == True:
            alignment_tolerance = calib_args['alignTolerance']
            assert (type(alignment_tolerance) == float) and (alignment_tolerance >= 0)
            printf('\t\tTolerance: %f standard deviations' % (alignment_tolerance))


        printf('\tVNA settings:')
        vna_address = vna_args['deviceAddress']
        assert (type(vna_address) == int)
        printf('\t\tDevice Address is: %s' % (vna_address))

        freq_sweep_type = vna_args['freqSweepMode']
        assert freq_sweep_type in ALLOWED_FREQ_MODES
        printf('\t\tSweep type: %s' % (freq_sweep_type))
        sParams = vna_args['sParams']
        printf('\t\tTypes of data to collect: %s' % sParams)

        num_points = cmd_args['number of points']
        assert type(num_points) == int and num_points in ALLOWED_NUM_POINTS
        printf('\t\tNumber of points to sweep: %f GHz' % (freq_stop))

        freq_start = cmd_args['start frequency']
        assert type(freq_start) == float
        printf('\t\tStart frequency: %f GHz' % (freq_start))
        freq_stop = cmd_args['stop frequency']
        assert type(freq_stop) == float
        printf('\t\tStop frequency: %f GHz' % (freq_stop))

        printf('\tPlot settings:')
        base_file_name = plot_args['dataFileName']
        assert type(base_file_name) == str
        csv_file_name = base_file_name +".csv"
        plot_file_name = base_file_name +".jpg"
        printf('\t\tRaw Data File: %s' % (csv_file_name))
        printf('\t\tPlot File: %s' % (plot_file_name))

        plot_type = plot_args['plotType']
        printf('\t\tPlot Type: %s' % (plot_type))
        plot_freq = plot_args['plotTestPhi']
        printf('\t\tFrequency to Plot: %s Hz' % (plot_freq ))

        plot_t_theta = plot_args['plotTestTheta']
        assert (type(plot_t_theta) == float) and (-180 <= plot_t_theta <= 180)
        printf('\t\tTest theta Angle to Plot: %s deg' % (plot_t_theta))
        plot_t_phi = plot_args['plotTestPhi']
        assert (type(plot_t_phi) == float) and (-180 <= plot_t_phi <= 180)
        printf('\t\tTest phi Angle to Plot: %s deg' % (plot_t_phi))
        plot_p_phi = plot_args['plotProbePhi']
        assert (type(plot_p_phi) == float) and (-180 <= plot_p_phi <= 180)
        printf('\t\tProbe phi Angle to Plot: %s deg' % (plot_p_phi))

        # CREATE THE CSV
        # generate the appropriate column names
        col_names = util.gen_col_names(sParams)
        # print(csv_file_name)
        data = np.array([[-1]] * len(col_names)) # trash data
        csv.createCSV(csv_file_name, col_names, data)


    except Exception as e:
        print(f"Exception: {e}")
        return error_codes.BAD_ARGS
        pass
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
    # UNCOMMENT FOR TESTING UI stuff
    # return error_codes.SUCCESS

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

    Test_MD.setFreq('theta', 32768)
    Test_MD.setFreq('phi', 65536)
    Probe_MD.setFreq('phi', 65536)

    printf('\t\tDone.')

    # Connect to VNA
    printf('\tConnecting to VNA...')
    VNA = ""
    try:
        # Connect to VNA and configure it
        VNA = VNA_HP8719A(sparam_list=sParams, address=vna_address, freq_mode=freq_sweep_type)
        if not VNA.instrument:
            return error_codes.VNA
        # Configure start and stop frequency
        startF = "%f GHz" % freq_start
        stopF = "%f GHz" % freq_stop

        res, real_startF, real_stopF = VNA.init_freq_sweep(startF, stopF, num_points)

        # if not res:
        #     printf(f"\tTried running VNA with start frequency of "
        #            f"{real_startF} GHz and stop frequency of {real_stopF} GHz ")
        #     return error_codes.VNA
        # printf(f"\tRunning VNA with start frequency of {real_startF} GHz and stop frequency of {real_stopF} GHz ")


    except Exception as e:
        print(f"Exception: {e}")
        # disconnect()
        return error_codes.VNA
    printf('\t\tDone.')

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
                # Take data
                data_out = []
                col_names = []
                # Note don't need to use column names just append to data_out and cast as np array

                data_out, temp = VNA.sparam_data()
                # Append orientation info to data # TODO verify this
                data_out.insert(1, [test_theta_orientation] * num_points)
                data_out.insert(2, [test_phi_orientation] * num_points)
                data_out.insert(3, [probe_phi_orientation] * num_points)
                data_to_save = np.array(data_out, dtype=object)
                # Write to CSV file
                csv.appendToCSV(csv_file_name, data_to_save)

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
    if plot_type == "3d":
        plots.plot3DRadPattern(csv_file_name,plot_file_name,sParams,plot_freq)
    elif plot_type == "cutPhi":
        plots.plotPhiCut(csv_file_name,plot_file_name,sParams,plot_freq,plot_t_phi)
    elif plot_type == "cutTheta":
        plots.plotThetaCut(csv_file_name, plot_file_name, sParams, plot_freq, plot_t_theta)
    else:
        return error_codes.BAD_ARGS

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


if __name__ == "__main__":
    main()