# Include
import pydoc
import os
import json
import pdb

from drivers import VNA_gpib as vna
from utils import util


DEF_ALIGN = True
DEF_ALIGN_TOLERANCE = 10.0

DEF_RUN_PLOTTER = False
DEF_DATA_FILE_NAME = "data"
DEF_PLOT_TYPE = "3d"
DEF_FREQ = "10GHz"
DEF_PROBE_PHI = 0
DEF_TEST_PHI = 0
DEF_TEST_THETA = 0

ALLOWED_PLOT_TYPES = ("3d", "cutPhi", "cutTheta")

'''
config_parser.py
This file contains functions to find, open, and generate flows and commands.
'''

config_base = "\\configs"
allowed_expt = ("sweepPhi", "sweepTheta", "sweepFreq")


# Attempts to locate the file and returns the full file path if possible
def find_config(file_name, file_path=None):
    full_name = ''

    # Check to see if name is valid
    if file_name is None or file_name == '':
        return False
    elif file_name.endswith(".json") is False:
        return False

    return util.get_file_path(file_name, "configs")


# Opens the file and returns the contents of flow
def get_config(full_file_name):
    if full_file_name == '':
        return False
    if full_file_name.rfind(util.root_base) == -1:
        # Get file name with file path
        full_file_name = find_config(full_file_name)

    flow = False
    meas = False
    plot = False
    calib = False
    error = [False, False, False]
    # Open file and get connents
    with open(full_file_name, "r") as file:
        # Check to see if the file is in the correct JSON format
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            return flow, meas, calib, plot

        # Pull key sections
        flow = data.get("flow")
        meas = data.get("meas")
        plot = data.get("plot")
        calib = data.get("calibrate")

        # Provide defaults for meas if not provided
        if meas is None or not meas:
            meas = {}
        meas.setdefault("deviceAddress", vna.DEF_DEV_ADDR)
        meas.setdefault("freqSweepMode", vna.DEF_FREQ_MODE)
        meas.setdefault("sParams", vna.DEF_S_PARAMS)

        # Check for valid modes
        if meas["freqSweepMode"] not in vna.ALLOWED_FREQ_MODES:
            error[0] = True

        # Provide defaults for calib if not provided
        if calib is None or not calib:
            calib = {}

        calib.setdefault("align", DEF_ALIGN)
        calib.setdefault("alignTolerance", DEF_ALIGN_TOLERANCE)
        # Assign align to a boolean
        if type(calib['align']) == str:
            if calib['align'] in ("True", "true"):
                calib['align'] = True
            elif calib['align'] in ("False", "false"):
                calib['align'] = False
            else:
                error[1] = True

        # Check for valid tolerances
        if type(calib["alignTolerance"]) != float and type(calib["alignTolerance"]) != int\
                or calib["alignTolerance"] <= 0:
            error[1] = True
        else:
            calib["alignTolerance"] = float(calib["alignTolerance"])

        # Provide defaults for plot
        if plot is None or not plot:
            plot = {}
        plot.setdefault("runPlotter", DEF_RUN_PLOTTER)
        plot.setdefault("dataFileName", DEF_DATA_FILE_NAME)
        plot.setdefault("plotType", DEF_PLOT_TYPE)
        plot.setdefault("plotFreq", DEF_FREQ)
        plot.setdefault("plotTestPhi", DEF_TEST_PHI)
        plot.setdefault("plotTestTheta", DEF_TEST_THETA)
        plot.setdefault("plotProbePhi", DEF_PROBE_PHI)

        # Assign runPlotter to a boolean
        if type(plot["runPlotter"]) == str:
            if plot["runPlotter"] in ("True", "true"):
                plot["runPlotter"] = True
            elif plot["runPlotter"] in ("False", "false"):
                plot["runPlotter"] = False
            else:
                error[2] = True

        # Check for valid file names remove any extensions
        if plot["dataFileName"].rfind(".") != -1:
            plot["dataFileName"] = plot["dataFileName"][0:plot["dataFileName"].rfind(".")]

        # Verify a good plot type
        if plot["plotType"] not in ALLOWED_PLOT_TYPES:
            error[2] = True

        # Convert frequency to a float in GHz
        try:
            if 'MHz' in plot["plotFreq"]:
                 plot["plotFreq"] = 1e6 * float(plot["plotFreq"][:-3])
            elif 'GHz' in plot["plotFreq"]:
                plot["plotFreq"] = 1e9 * float(plot["plotFreq"][:-3])
            elif 'Hz' in plot["plotFreq"]:
                plot["plotFreq"] = float(plot["plotFreq"][:-3])
            else:
               error[2] = True

            # Convert orientations to floats
            plot["plotTestPhi"] = float(plot["plotTestPhi"])
            plot["plotTestTheta"] = float(plot["plotTestTheta"])
            plot["plotProbePhi"] = float(plot["plotProbePhi"])
        except:
            # plot = False
            error[2] = True

        # generate path name
        time_stamp_base = util.append_date_time_str(plot["dataFileName"])
        path = util.get_file_path('', os.path.join("data", time_stamp_base))
        if not error[2] and time_stamp_base and path:
            plot["dataFileName"] = os.path.join(path, time_stamp_base)

        # print(json.dumps(meas, indent=4))
        # print(json.dumps(plot, indent=4))
        # print(json.dumps(calib, indent=4))
        if error[0]:
            meas = False
        if error[1]:
            calib = False
        if error[2]:
            plot = False

    return flow, meas, calib, plot


def gen_expt_cmds(flow):
    cmds = []
    #try:
    for expt in flow:
        cmd = {}
        experiment_type  = expt.get("expType")
        if experiment_type.endswith(".json"):
            inner_flow, inner_meas = get_config(experiment_type)
            inner_cmds = gen_expt_cmds(inner_flow)
            if inner_cmds is not False:
                for i_cmd in inner_cmds:
                    cmds.append(i_cmd)
        else:
            assert experiment_type in ['sweepFreq', 'sweepTheta', 'sweepPhi']
        cmd['experiment type'] = experiment_type
        if experiment_type != "sweepPhi":
            test_theta_start = float(expt.get("startTestTheta"))
            assert -180 <= test_theta_start <= 180
            cmd['test-theta start'] = test_theta_start
            test_theta_end   = float(expt.get("endTestTheta"))
            assert -180 <= test_theta_end <= 180
            cmd['test-theta end'] = test_theta_end
            test_theta_steps = int(expt.get("stepsTestTheta"))
            assert test_theta_steps > 0
            cmd['test-theta steps'] = test_theta_steps
        else:
            test_theta_orientation = float(expt.get("orientationTestTheta"))
            assert -180 <= test_theta_orientation <= 180
            cmd['test-theta orientation'] = test_theta_orientation
        if experiment_type != "sweepTheta":
            test_phi_start   = float(expt.get("startTestPhi"))
            assert -180 <= test_phi_start <= 180
            cmd['test-phi start'] = test_phi_start
            test_phi_end     = float(expt.get("endTestPhi"))
            assert -180 <= test_phi_end <= 180
            cmd['test-phi end'] = test_phi_end
            test_phi_steps   = int(expt.get("stepsTestPhi"))
            assert test_phi_steps > 0
            cmd['test-phi steps'] = test_phi_steps
        else:
            test_phi_orientation = float(expt.get("orientationTestPhi"))
            assert -180 <= test_phi_orientation <= 180
            cmd['test-phi orientation'] = test_phi_orientation
        probe_phi_start  = float(expt.get("startProbePhi"))
        assert -180 <= probe_phi_start <= 180
        cmd['probe-phi start'] = probe_phi_start
        probe_phi_end    = float(expt.get("endProbePhi"))
        assert -180 <= probe_phi_end <= 180
        cmd['probe-phi end'] = probe_phi_end
        probe_phi_steps  = int(expt.get("stepsProbePhi"))
        assert probe_phi_steps > 0
        cmd['probe-phi steps'] = probe_phi_steps
        freq_start       = expt.get("startFrequency")
        if 'MHz' in freq_start:
            freq_start = 1e-3 * float(freq_start[:-3])
        elif 'GHz' in freq_start:
            freq_start = float(freq_start[:-3])
        else:
            assert False
        cmd['start frequency'] = freq_start
        freq_stop        = expt.get("stopFrequency")
        if 'MHz' in freq_stop:
            freq_stop = 1e-3 * float(freq_stop[:-3])
        elif 'GHz' in freq_stop:
            freq_stop = float(freq_stop[:-3])
        else:
            assert False
        cmd['stop frequency'] = freq_stop

        num_points = expt.get("numPoints")
        assert num_points in vna.ALLOWED_NUM_POINTS
        cmd['number of points'] = num_points

        cmds.append(cmd)
    #except:
    #    return False
    return cmds


def print_cmds(cmds):
    print(f"cmds:")
    for c in cmds['cmds']:
        d = json.dumps(c, indent=4)
        print(f"{d}")
    print(f"\nmeas:\n{json.dumps(cmds['meas'], indent=4)}")
    print(f"\ncalibrate:\n{json.dumps(cmds['calib'], indent=4)}")
    print(f"\nplot:\n{json.dumps(cmds['plot'], indent=4)}")
