import sys
import os
import getopt
import json
from optparse import OptionParser
import pdb

# Custom Modules
from utils import config_parser as parser
from utils import experiments as expt
from utils import util
from utils import single_mode

from utils import error_codes
from utils.calibrate import calibrate

from plotting import plotting as plots
import time

# Global Variables
curr_phase = "Setup"
mode = "Debug"
DEF_ANGLE = 200

""" 
    Main file that controls and runs the entire system. 
"""


def set_usage(exe_name):
    """!
    @brief Sets up the usage message.
    @param exe_name name of the executable
    @return A string containing the usage message.
    """
    exe_name ="./" + exe_name
    help = f"\tGet Help:\n\t\t{exe_name} --h\n\t\t{exe_name} --help\n"
    align = f"\tAlign System:\n\t\t{exe_name} --a\n\t\t{exe_name} --alignOnly\n"
    calibrate = f"\tCalibrate System:\n\t\t{exe_name} --calibrate\n"
    full_syst = f"\tRun Entire System:\n\t\t{exe_name} --config <config_file.json>\n"
    plot3d = f"\t3D Plot:\n\t\t{exe_name} --plot --dataFile <data.csv> --plotType 3d --freq <freq>\n"
    plotPhi = f"\tPhi Cut Plot: \n\t\t{exe_name} --plot --dataFile <data.csv> --plotType cutPhi " \
              f"--freq <freq> --phi <phi>\n"
    plotTheta = f"\tTheta Cut Plot:\n\t\t{exe_name} --plot --dataFile <data.csv> --plotType cutTheta" \
                f" --freq <freq> --theta <theta>\n"

    return help + align + calibrate + full_syst + plot3d + plotPhi + plotTheta


def print_welcome_sign():
    """!
    @brief Prints the welcome sign on the console.
    """
    print("\n  ********************************************************")
    print("  *             Welcome to direcMeasure v1.0             *")
    print("  ********************************************************\n")


def config_run(option, opt, value, parser):
    """!
    Used to set the run_type variable from the command line arguments.
    :param option: Long version name of the option flag name.
    :param opt: Name of the option flag name. Can be either short or long version.
    :param value: Value associated with the option flag.
    :param parser: The OptionParser to use.
    """
    print(f"Option = {option}")
    if parser.values.run_type == "f":
        if (opt == '-a') or (opt == '--alignOnly'):
            parser.values.run_type = 'a'
        elif (opt == '-c') or (opt == '--config'):
            parser.values.run_type = 'f'
        elif (opt == '--setTestPhi'):
            parser.values.run_type = 's'
    else:
        parser.values.run_type = "e"


def process_cmd_line_alt():
    """
    Alternate version of process_cmd_line. Processes the command line arguments and sets up the
    system control variables accordingly. If an error occurred, an error message indicating the fault will be printed
    before the returning False.
    :return Returns options if no errors occurred, otherwise False.
    """
    # Set up parser
    opt_parser = OptionParser()
    opt_parser.prog = "direcMeasure"
    usage = set_usage(opt_parser.prog)
    opt_parser.set_usage(usage)
    opt_parser.set_defaults(run_type="s", verbose=False)

    # Test Phi Options
    opt_parser.add_option("--alignOnly", action="callback", callback=config_run, dest="run_type",
                      help="Only run the alignment routine.")

    opt_parser.add_option("--setTestPhi", type="float", action="store", dest="test_phi", default=None,
                          help="Sets the test-side phi angle to the specified angle. Must be in degrees "
                           "and between -180 and 180 degrees.")
    opt_parser.add_option("--zeroTestPhi", action="store_true", dest="zero_test_phi", default=False,
                          help="Sets the current test-side phi angle to be the zero reference.")
    opt_parser.add_option("--alignTestPhi", action="store_true", dest="align_test_phi", default=False,
                          help="Aligns the test-side phi motor with the end-switch.")

    # Test Theta Options
    opt_parser.add_option("--setTestTheta", type="float", action="store", dest="test_theta", default=None,
                          help="Sets the test-side theta angle to the specified angle. Must be in degrees "
                               "and between -180 and 180 degrees.")
    opt_parser.add_option("--zeroTestTheta", action="store_true", dest="zero_test_theta", default=False,
                          help="Sets the current test-side theta angle to be the zero reference.")
    opt_parser.add_option("--alignTestTheta", action="store_true", dest="align_test_theta", default=False,
                          help="Aligns the test-side test motor with the end-switch.")

    # Probe Theta Options
    opt_parser.add_option("--setProbePhi", type="float", action="store", dest="probe_phi", default=None,
                          help="Sets the probe-side phi angle to the specified angle. Must be in degrees "
                               "and between -180 and 180 degrees.")
    opt_parser.add_option("--zeroProbePhi", action="store_true", dest="zero_probe_phi", default=False,
                          help="Sets the current probe-side phi angle to be the zero reference.")
    opt_parser.add_option("--alignProbePhi", action="store_true", dest="align_probe_phi", default=False,
                          help="Aligns the probe-side phi motor with the end-switch.")
                          
    (options, args) = opt_parser.parse_args()
    # print(type(options))

    print(options)
    return False


def process_cmd_line():
    """
    Processes the command line arguments and sets up the
    system control variables accordingly. If an error occurred, an error message indicating the fault will be printed before the returning False.
    :return Returns options if no errors occurred, otherwise False.
    """
    # Set up parser
    opt_parser = OptionParser()
    opt_parser.prog = "direcMeasure"
    usage = set_usage(opt_parser.prog)
    opt_parser.set_usage(usage)
    opt_parser.set_defaults(run_type="f", verbose=False)

    # Main options
    opt_parser.add_option("-c", "--config", type="string", action="store", dest="cfg", default='',
                      help="Configuration file used to control the system. Must be a JSON file.")
    opt_parser.add_option("-a", "--alignOnly", action="callback", callback=config_run, dest="run_type",
                      help="Only run the alignment routine.")
    opt_parser.add_option("--calibrate", action="store_true", dest="calibrate", default=False,
                      help="Run the calibration interface.")
    opt_parser.add_option("--plot", action="store_true", dest="plot", default=False,
                      help="Run the calibration interface.")
    # Plot options
    opt_parser.add_option("--dataFile", type="string", action="store", dest="data_file", default='',
                      help="Plot option. Input data file to plot")
    opt_parser.add_option("--plotType", type="string", action="store", dest="plot_type", default='',
                      help=f"Plot option. Type of plot to generate. Must be one of the following"
                           f" {parser.ALLOWED_PLOT_TYPES}.")
    opt_parser.add_option("--freq", type="string", action="store", dest="plot_freq", default='',
                          help="Plot option. Frequency to plot at. Must be in Hz, MHz, or GHz")
    opt_parser.add_option("--phi", type="float", action="store", dest="plot_phi", default=200.0,
                      help="Plot option. Test phi angle to plot at. Must be in degrees "
                           "and between -180 and 180 degrees.")
    opt_parser.add_option("--theta", type="float", action="store", dest="plot_theta", default=200.0,
                      help="Plot option. Test theta angle to plot at. Must be in degrees "
                           "and between -180 and 180 degrees.")
    opt_parser.add_option("--probePhi", type="float", action="store", dest="plot_p_phi", default=200.0,
                      help="Plot option. Probe phi angle to plot at. Must be in degrees "
                           "and between -180 and 180 degrees.")
    opt_parser.add_option("--sParams", type="string", action="store", dest="sParams", default="S21",
                      help="Plot option. S parameters to plot.")
    opt_parser.add_option("--logName", type="string", action="store", dest="log_name", default=None,
                      help="Filename for terminal output log.")
    opt_parser.add_option("--logPath", type="string", action="store", dest="log_path", default=None,
                      help="Filepath for terminal output log.")
    opt_parser.add_option("--dataPath", type="string", action="store", dest="data_path", default=None,
                      help="Filepath for data file taken during experiment.")
    opt_parser.add_option("--dataName", type="string", action="store", dest="data_name", default=None,
                      help="Filename for data file taken during experiment.")
    opt_parser.add_option("--plotName", type="string", action="store", dest="plot_name", default=None,
                      help="Filename for plot generated during experiment.")
    opt_parser.add_option("--plotPath", type="string", action="store", dest="plot_path", default=None,
                      help="Filepath for plot generated during experiment.")

    opt_parser.add_option("--setTestPhi", type="float", action="store", dest="test_phi", default=None,
                          help="Sets the test-side phi angle to the specified angle. Must be in degrees "
                               "and between -180 and 180 degrees.")
    opt_parser.add_option("--zeroTestPhi", action="store_true", dest="zero_test_phi", default=False,
                          help="Sets the current test-side phi angle to be the zero reference.")
    opt_parser.add_option("--alignTestPhi", action="store_true", dest="align_test_phi", default=False,
                          help="Aligns the test-side phi motor with the end-switch.")

    # Test Theta Options
    opt_parser.add_option("--setTestTheta", type="float", action="store", dest="test_theta", default=None,
                          help="Sets the test-side theta angle to the specified angle. Must be in degrees "
                               "and between -180 and 180 degrees.")
    opt_parser.add_option("--zeroTestTheta", action="store_true", dest="zero_test_theta", default=False,
                          help="Sets the current test-side theta angle to be the zero reference.")
    opt_parser.add_option("--alignTestTheta", action="store_true", dest="align_test_theta", default=False,
                          help="Aligns the test-side test motor with the end-switch.")

    # Probe Theta Options
    opt_parser.add_option("--setProbePhi", type="float", action="store", dest="probe_phi", default=None,
                          help="Sets the probe-side phi angle to the specified angle. Must be in degrees "
                               "and between -180 and 180 degrees.")
    opt_parser.add_option("--zeroProbePhi", action="store_true", dest="zero_probe_phi", default=False,
                          help="Sets the current probe-side phi angle to be the zero reference.")
    opt_parser.add_option("--alignProbePhi", action="store_true", dest="align_probe_phi", default=False,
                          help="Aligns the probe-side phi motor with the end-switch.")

    # Options determining how the motor will rotate
    opt_parser.add_option("--direction", action="store", dest="direction", default=None,
                          help="The direction in which motor should rotate.")
    opt_parser.add_option("--gradualAcceleration", action="store_true", dest="grad_accel", default=None,
                          help="Gradually accelerate the motor to its maximum frequency. Recommended for test-theta motor.")
    opt_parser.add_option("--jumpAcceleration", action="store_false", dest="grad_accel",
                          help="Instantly accelerate the motor to its maximum frequency. Recommended for test-phi and probe-phi motors.")
    opt_parser.add_option("--incremental", action="store_true", dest="incremental", default=False,
                          help="Whether input angle should be interpreted as absolute or relative to current angle.")

    # Check to make sure a config file was entered with the -c
    index = -1
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-c" or sys.argv[i] == "--config":
            index = i + 1

    if index >= len(sys.argv) or index > 0 and opt_parser.has_option(sys.argv[index]):
        sys.argv.insert(index, None)

    # Parse command line
    (options, args) = opt_parser.parse_args()
    # print(options)

    # Check for single mode
    if options.test_phi != None or options.zero_test_phi or options.align_test_phi or \
            options.test_theta != None or options.zero_test_theta or options.align_test_theta \
            or options.probe_phi != None or options.zero_probe_phi or options.align_probe_phi:
        if options.run_type == 'f':
            options.run_type = 's'
        else:
            options.run_type = 'e'

    # Error Checking
    if options.run_type == "e":
        util.printf(curr_phase, "Error", "Cannot simultaneously run the alignment routine only and run the system with out "
                                    "the alignment routine. See usage for more information on command line options.")
        opt_parser.print_help()
        return False

    # Config file checks
    if options.cfg is None:
        util.printf(curr_phase, "Error", f"Configuration file flag detected but no configuration was detected. See usage "
                                    f"for more information on command line options. ")
        opt_parser.print_help()
        return False

    num_modes = int(options.cfg != '') + int(options.run_type == 'a') + int(options.run_type == 's') + \
                int(options.calibrate) + int(options.plot)

    if num_modes == 0:
        util.printf(curr_phase, "Error", "Cannot configure system as no command lines arguments were inputted."
                                    " See usage for more information on command line options. ")
        opt_parser.print_help()
        return False
    if num_modes > 1:
        util.printf(curr_phase, "Error", "Mutually-exclusive options specified. Cannot simultaneously run the "
                                    "calibration routine and the run the full run the system. See usage for more "
                                    "information on command line options.")
        opt_parser.print_help()
        return False
    if options.calibrate:
        options.run_type = "c"

    if options.plot:
        options.run_type = "p"
        if options.data_file == '':
            util.printf(curr_phase, "Error", f"Plotting requested but no input data file was entered."
                                             f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False

        if options.data_file == '' or not options.data_file.endswith(".csv"):
            util.printf(curr_phase, "Error", f"The input data file entered '{options.data_file}' is not a csv file. "
                                             f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False

        if options.plot_type == '':
            util.printf(curr_phase, "Error", f"Plotting requested but no plot type was specified. "
                                             f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False

        if options.plot_type not in parser.ALLOWED_PLOT_TYPES:
            util.printf(curr_phase, "Error",
                        f"Plotting requested but invalid plot type {options.plot_type} was specified. "
                        f"Plot type must one of the following {parser.ALLOWED_PLOT_TYPES}"
                        f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False

        if options.plot_type == "cutPhi" and options.plot_phi == 200:
            util.printf(curr_phase, "Error",
                        f"Phi cut plot requested but no phi angle was specified. "
                        f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False
        elif options.plot_type == "cutTheta" and options.plot_theta == 200:
            util.printf(curr_phase, "Error",
                        f"Theta cut plot requested but no theta angle was specified. "
                        f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False

        if 'MHz' in options.plot_freq:
            options.plot_freq = 1e6 * float(options.plot_freq[:-3])
        elif 'GHz' in options.plot_freq:
            options.plot_freq = 1e9 * float(options.plot_freq[:-3])
        elif 'Hz' in options.plot_freq:
            options.plot_freq = float(options.plot_freq[:-3])
        else:
            util.printf(curr_phase, "Error",
                        f"Plotting requested but invalid plot frequency {options.plot_freq} was specified. "
                        f"Plot type must be in units of Hz, MHz, or GHz (e.g. 10GHz or \"10 GHz\")."
                        f" See usage for more information on command line options.")
            opt_parser.print_help()
            return False

    if options.cfg != '' and not options.cfg.endswith(".json"):
        util.printf(curr_phase, "Error", f"The configuration file entered '{options.cfg}' is not a JSON file. "
                                    f" See the User Manual for more information on configuration files and "
                                    f"usage for more information on command line options.")
        opt_parser.print_help()
        return False

    return options


def process_config(config_name):
    """
    Parses the configuration file and generates the appropriate commands for plotting, measurement setup,
    experiments, and calibration.
    :param config_name: Name of the configuration file to parse.
    """
    if config_name != '' and config_name is not None:
        # Find Config
        util.printf(curr_phase, None, f"Starting configuration file parsing process on {config_name}...")
        full_cfg_name = parser.find_config(config_name)
        if not full_cfg_name:
            util.printf(curr_phase, "Error", f"Could not locate the file '{config_name}'. Ensure that '{config_name}'"
                                        f" is located in the configuration file repository:\n\t\t "
                                        f"'{util.get_root_path() + parser.config_base}'.")
            return False
        # Get flow and meas config from the configuration file
        flow, meas, calib, plot = parser.get_config(full_cfg_name)
        errors = 0
        if not flow:
            util.printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'flow' section"
                                        f" in '{config_name}' is correctly formatted. See the User Manual for details.")
            errors += 1
        if not meas:
            util.printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'meas' section"
                                        f" in '{config_name}' is correctly formatted. See the User Manual for details.")
            errors += 1
        if not calib:
            util.printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'calibrate' "
                                        f"section in '{config_name}' is correctly formatted. "
                                        f"See the User Manual for details.")
            errors += 1
        if not plot:
            util.printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'plot' section"
                                        f" in '{config_name}' is correctly formatted. See the User Manual for details.")
            errors += 1
        if errors != 0:
            return False

        # Generate commands
        cmds = parser.gen_expt_cmds(flow)
        if not cmds:
            util.printf(curr_phase, "Error", f"Could not generate experiment commands from '{config_name}'.")
            return False
        util.printf(curr_phase, None, f"Successfully generated experiment commands from '{config_name}'.")
        return {"cmds": cmds, "meas": meas, "calib": calib, "plot": plot}
    else:
        util.printf(curr_phase, "Error", f"No configuration file was passed in, could not generate experiment commands.")
        return False


def handle_error_code(error_code):
    """
    Identifies error codes and prints the appropriate error message associated with a code. If the error could not be
    identified, then the an assertion error will be raised.
    :param error_code: Error code that corresponds to an error.
    """
    curr_phase = "Shutdown"
    if error_code == error_codes.SUCCESS:  # routine finished without issues
        util.printf(curr_phase, None, "Successfully ran routine without issues. ")
    elif error_code == error_codes.CONNECTION:  # could not find any connected motor driver PCBs
        util.printf(curr_phase, "Error", "No USB devices connected. Ensure the test-side and probe-side devices"
                                         " are connected and powered on. ")
    elif error_code == error_codes.CONNECTION_PROBE:  # could not find a probe motor driver PCB
        util.printf(curr_phase, "Error", "No probe-side USB devices connected."
                                         " Ensure the probe-side device is connected and powered on. ")
    elif error_code == error_codes.CONNECTION_TEST:  # could not find a test motor driver PCB
        util.printf(curr_phase, "Error", "No test-side USB devices connected."
                                         " Ensure the test-side device is connected and powered on. ")
    elif error_code == error_codes.DISTINCT_IDS:  # detected two motor driver PCBs, but they were both configured as test or probe
        util.printf(curr_phase, "Error", "USB devices must be of different types. Ensure that the test-side device is"
                                         " set to TX and that the probe-side device is set to RX.")
    elif error_code == error_codes.VNA:  # could not connect to VNA
        util.printf(curr_phase, "Error", "No GPIB devices connected. Ensure the VNA is connected and powered on. ")
    elif error_code == error_codes.TEST_THETA_FAULT:  # test-theta motor fault
        util.printf(curr_phase, "Error", "Motor driver fault detected on the test-side theta motor. Ensure"
                                         " that the theta motor driver is properly connected to the test-side device.")
    elif error_code == error_codes.TEST_PHI_FAULT:  # test-phi motor fault
        util.printf(curr_phase, "Error", "Motor driver fault detected on the test-side phi motor. Ensure"
                                         " that the phi motor driver is properly connected to the test-side device.")
    elif error_code == error_codes.PROBE_PHI_FAULT:  # probe-phi motor fault
        util.printf(curr_phase, "Error", "Motor driver fault detected on the probe-side phi motor. Ensure"
                                         " that the phi motor driver is properly connected to the probe-side device.")
    elif error_code == error_codes.ALIGNMENT:  # alignment routine failed
        util.printf(curr_phase, "Error", "Alignment error detected. System could not be aligned. Try running the"
                                         " calibration routine to ensure proper alignment. ")
    elif error_code == error_codes.BAD_ARGS:  # routine was called with invalid arguments
        util.printf(curr_phase, "Error", "Unable to run routine as invalid arguments were entered.")
    elif error_code == error_codes.MISC:  # issue not listed above
        util.printf(curr_phase, "Error", "An unknown error has occurred.")
    elif error_code == error_codes.STOPPED:
        util.printf(curr_phase, "Error", "The user issued a keyboard interrupt to prematurely stop the program.")
    elif error_code == error_codes.CALIBRATION:
        util.printf(curr_phase, "Error", "The selected device is not calibrated and must be calibrated to perform the requested action."
                                         " This means that the device has never been calibrated, or since the last calibration it has encountered an error during a rotation command."
                                         " The user is advised to rotate to the end switch for this device, then manually rotate to the zero"
                                         " angle and specify it as such.")
    else:
        assert False


def run_experiments(cmds, meas, calib, plot):
    """
    Runs all experiments specified in cmds and uses the meas, calib, and plot settings to configure measurement,
    calibration, and plotting.
    :param cmds: List containing the sub-experiments to run.
    :param meas: Dictionary containing the measurement configuration.
    :param calib: Dictionary containing the calibration configuration.
    :param plot: Dictionary containing the plotting configuration.
    :return: Returns a True tuple
    """
    for sub_expt in cmds:
        # Split cmds into usable pieces
        expt_type = sub_expt['experiment type']

        # Run the appropriate function for the sub-experiment
        if expt_type == "sweepFreq":
            util.printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            # print(sub_expt)
            error_code = expt.run_sweepFreq(sub_expt, meas, calib, plot)
        elif expt_type == "sweepPhi":
            util.printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            error_code = expt.run_sweepPhi(sub_expt)
        elif expt_type == "sweepTheta":
            util.printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            error_code = expt.run_sweepTheta(sub_expt)
        else:
            util.printf(curr_phase, "Error", f"Could not run experiment of type '{expt_type}'")
            return False, expt_type
        handle_error_code(error_code)

    return True, True, True


    single_cfg = {'test_phi': args.test_phi, 'zero_test_phi': args.zero_test_phi, 'align_test_phi': args.align_test_phi,
              'test_theta':args.test_theta, 'zero_test_theta': args.zero_test_theta, 'align_test_theta':args.align_test_theta,
              'probe_phi': args.probe_phi, 'zero_probe_phi': args.zero_probe_phi, 'align_probe_phi': args.align_probe_phi}


def run_single_mode(cfg):
    print(f"Running single-mode with: {cfg}")
    error_code = error_codes.SUCCESS
    if cfg['align_test_phi'] == True:
        error_code = single_mode.alignMotor('test phi', cfg['direction'])
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['test_phi'] != None:
        if cfg['incremental']:
            error_code = single_mode.rotateMotorInc(cfg['test_phi'], 'test phi', cfg['direction'], cfg['grad_accel'])
        else:
            error_code = single_mode.rotateMotorAbs(cfg['test_phi'], 'test phi', cfg['direction'], cfg['grad_accel'])
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['zero_test_phi'] == True:
        error_code = single_mode.zeroCurrentAngle('test phi')
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['align_test_theta'] == True:
        error_code = single_mode.alignMotor('test theta', cfg['direction'])
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['test_theta'] != None:
        if cfg['incremental']:
            error_code = single_mode.rotateMotorInc(cfg['test_theta'], 'test theta', cfg['direction'], cfg['grad_accel'])
        else:
            error_code = single_mode.rotateMotorAbs(cfg['test_theta'], 'test theta', cfg['direction'], cfg['grad_accel'])
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['zero_test_theta'] == True:
        error_code = single_mode.zeroCurrentAngle('test theta')
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['align_probe_phi'] == True:
        error_code = single_mode.alignMotor('probe phi', cfg['direction'])
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['probe_phi'] != None:
        if cfg['incremental']:
            error_code = single_mode.rotateMotorInc(cfg['probe_phi'], 'probe phi', cfg['direction'], cfg['grad_accel'])
        else:
            error_code = single_mode.rotateMotorAbs(cfg['probe_phi'], 'probe phi', cfg['direction'], cfg['grad_accel'])
    if error_code != error_codes.SUCCESS:
        return error_code
    if cfg['zero_probe_phi'] == True:
        error_code = single_mode.zeroCurrentAngle('probe phi')
    if error_code != error_codes.SUCCESS:
        return error_code
    return error_codes.SUCCESS


def plot_data_file(data_file, plot_type, sParams, plot_freq, plot_t_phi, plot_t_theta, plot_p_phi):

    if data_file != '':
        # Find data file
        if data_file.rfind(".") == -1:
            data_file += ".csv"
        elif not data_file.endswith(".csv"):
            util.printf(curr_phase, "Error", f"The '{data_file}' is not a CSV file. Ensure that '{data_file}'"
                                             f" is a CSV file.")
            return False

        csv_file_name = util.get_file_path(data_file, "data")
        # print(csv_file_name)
        if not os.path.isfile(csv_file_name) or not csv_file_name:
            path = util.get_file_path('', "data")
            util.printf(curr_phase, "Error", f"Could not locate the file '{data_file}'. Ensure that '{data_file}'"
                                             f" is located in the data file repository:\n\t\t'{path}'.")
            return False

        plot_file_name = csv_file_name[0:len(csv_file_name)-4] + ".pdf"
        util.printf(curr_phase, None, f"Plotting '{data_file}' to {plot_file_name}")
        if plot_type == "3d":
            try:
                plots.plot3DRadPattern(csv_file_name, plot_file_name, sParams, plot_freq)
            except:
                return False
        elif plot_type == "cutPhi":
            try:
                plots.plotPhiCut(csv_file_name, plot_file_name, sParams, plot_freq, plot_t_phi)
            except:
                return False
        elif plot_type == "cutTheta":
            try:
                plots.plotThetaCut(csv_file_name, plot_file_name, sParams, plot_freq, plot_t_theta)
            except:
                return False
        else:
            return False
        return True
    return False


if __name__ == '__main__':
    """
    Entry for the main program. Prints welcome sign and parses command line inputs. Runs the appropriate routine based
    upon the parsed inputs. 
    """
    print_welcome_sign()

    # Process Command Line
    args = process_cmd_line()
    if not args:
        exit(-1)
    cfg = args.cfg

    single_cfg = {'test_phi': args.test_phi, 'zero_test_phi': args.zero_test_phi, 'align_test_phi': args.align_test_phi,
              'test_theta':args.test_theta, 'zero_test_theta': args.zero_test_theta, 'align_test_theta':args.align_test_theta,
              'probe_phi': args.probe_phi, 'zero_probe_phi': args.zero_probe_phi, 'align_probe_phi': args.align_probe_phi,
              'direction': args.direction, 'incremental': args.incremental, 'grad_accel': args.grad_accel}


    run_type = args.run_type
    if run_type != "c":
        util.initLog(args.log_name, args.log_path)
    if run_type == "p":
        curr_phase = 'Plotting'
        res = plot_data_file(args.data_file, args.plot_type, args.sParams, args.plot_freq, args.plot_phi,
                             args.plot_theta, args.plot_p_phi)
        if not res:
            util.printf(curr_phase, "Error", f"Could not generate '{args.plot_type}' plot from '{args.data_file}'.")
        exit(1)

    if run_type == "a":
        util.printf(curr_phase, None, "Running the alignment routine only.")

    elif run_type == "c":
        util.printf(curr_phase, "Debug", "Starting the calibration interface.")

    # Process Configuration File if running the entire system
    sys_cmds = False
    if run_type in ("f"):  # , "s"):
        sys_cmds = process_config(cfg)
        if not sys_cmds:
            exit(-1)

    # Start execution/running phase
    curr_phase = "Running"
    if run_type in ("f"):  # , "s"):
        # Start Running the experiments
        res = run_experiments(sys_cmds['cmds'], sys_cmds['meas'], sys_cmds['calib'], sys_cmds['plot'])

    elif run_type == "c":
        time.sleep(1)
        error_code = calibrate()
        handle_error_code(error_code)
    elif run_type == 'a':
        error_code = expt.run_Align()
        handle_error_code(error_code)
    elif run_type == 's':
        error_code = run_single_mode(single_cfg)
        handle_error_code(error_code)
    if run_type != "c":
        util.closeLog()

    # Shutdown Phase
    exit(1)