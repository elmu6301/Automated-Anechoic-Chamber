import sys
import getopt
import json
from optparse import OptionParser

# Custom Modules
from util import config_parser as parser
from util import experiments as expt

from util import error_codes
from util.calibrate import calibrate
import time

# Global Variables
curr_phase = "Setup"
mode = "Debug"


def print_usage():
    print("\tDirecMeasure Usage")
    print("\t\t- Run with laser alignment: main.py -c <configfile>")
    print("\t\t- Run without laser alignment: main.py -c <configfile> -l")
    print("\t\t- Calibrate the system: main.py --calibrate")


def print_welcome_sign():
    """ Prints the welcome sign"""
    print("\n  ********************************************************")
    print("  *             Welcome to direcMeasure v1.0             *")
    print("  ********************************************************\n")


def printf(phase, flag, msg):
    """ Prints out messages to the command line by specifying flag and phase. """
    if flag in ("Error", "Warning"):
        print(f"({phase}) {flag}: {msg}")
    else:
        print(f"({phase}):".ljust(11), f"{msg}")


def config_run(option, opt, value, parser):
    """ Used to set the run_type variable from the command line arguments"""
    if parser.values.run_type == "f":
        if (opt == '-a') or (opt == '--alignOnly'):
            parser.values.run_type = 'a'
        elif (opt == '-c') or (opt == '--config'):
            parser.values.run_type = 'f'
    else:
        parser.values.run_type = "e"


def process_cmd_line():
    """ Processes the command line arguments and sets up the system control variables accordingly"""

    # Set up parser
    parser = OptionParser()
    usage = "usage: ./direcMeasure --config<config_file>"
    parser.set_usage(usage)
    parser.set_defaults(run_type="f", verbose=False)
    parser.prog = "direcMeasure"

    # Add options
    parser.add_option("-c", "--config", type="string", action="store", dest="cfg", default='',
                      help="Configuration file used to control the system. Must be a JSON file.")
    parser.add_option("-a", "--alignOnly", action="callback", callback=config_run, dest="run_type",
                      help="Only run the alignment routine.")
    # parser.add_option("-s", "--skipAlign", action="callback", callback=config_run, dest="run_type",
    #                  help="Skip the alignment routine.")
    parser.add_option("--calibrate", action="store_true", dest="calibrate", default=False,
                      help="Run the calibration interface.")

    # Check to make sure a config file was entered with the -c
    index = -1
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-c" or sys.argv[i] == "--config":
            index = i + 1
    # insert default values if needed
    if index >= len(sys.argv) or index > 0 and parser.has_option(sys.argv[index]):
        sys.argv.insert(index, None)

    # Parse command line
    (options, args) = parser.parse_args()

    # Error Checking
    if options.run_type == "e":
        printf(curr_phase, "Error", "Cannot simultaneously run the alignment routine only and run the system with out "
                                    "the alignment routine. See usage for more information on command line options.")
        parser.print_help()
        return False

    # Config file checks
    if options.cfg is None:
        printf(curr_phase, "Error", f"Configuration file flag detected but no configuration was detected. See usage "
                                    f"for more information on command line options. ")
        parser.print_help()
        return False

    num_modes = int(options.cfg != '') + int(options.run_type == 'a') + int(options.calibrate)

    if num_modes == 0:
        printf(curr_phase, "Error", "Cannot configure system as no command lines arguments were inputted."
                                    " See usage for more information on command line options. ")
        parser.print_help()
        return False
    if num_modes > 1:
        printf(curr_phase, "Error", "Mutually-exclusive options specified. Cannot simultaneously run the "
                                    "calibration routine and the run the full run the system. See usage for more "
                                    "information on command line options.")
        parser.print_help()
        return False
    if options.calibrate:
        options.run_type = "c"

    if options.cfg != '' and not options.cfg.endswith(".json"):
        printf(curr_phase, "Error", f"The configuration file entered '{options.cfg}' is not a JSON file. "
                                    f" See the User Manual for more information on configuration files and "
                                    f"usage for more information on command line options.")
        parser.print_help()
        return False

    return options


def process_config(config_name):
    """ Parses the configuration file and generates the appropriate commands. """
    if config_name != '' and config_name is not None:
        # Find Config
        printf(curr_phase, None, f"Starting configuration file parsing process on {config_name}...")
        full_cfg_name = parser.find_config(config_name)
        if not full_cfg_name:
            printf(curr_phase, "Error", f"Could not locate the file '{config_name}'. Ensure that '{config_name}'"
                                        f" is located in the configuration file repository:\n\t\t "
                                        f"'{parser.get_root_path() + parser.config_base}'.")
            return False
        # Get flow and meas config from the configuration file
        flow, meas, calib, plot = parser.get_config(full_cfg_name)
        errors = 0
        if not flow:
            printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'flow' section"
                                        f" in '{config_name}' is correctly formatted. See the User Manual for details.")
            errors += 1
        if not meas:
            printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'meas' section"
                                        f" in '{config_name}' is correctly formatted. See the User Manual for details.")
            errors += 1
        if not calib:
            printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'calibrate' "
                                        f"section in '{config_name}' is correctly formatted. "
                                        f"See the User Manual for details.")
            errors += 1
        if not plot:
            printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that the 'plot' section"
                                        f" in '{config_name}' is correctly formatted. See the User Manual for details.")
            errors += 1
        if errors != 0:
            return False
        return [flow, meas, calib, plot]

        # Generate commands
        cmds = parser.gen_expt_cmds(flow)
        if not cmds:
            printf(curr_phase, "Error", f"Could not generate experiment commands from '{config_name}'.")
            return False
        printf(curr_phase, None, f"Successfully generated experiment commands from '{config_name}'.")
        return cmds
    else:
        printf(curr_phase, "Error", f"No configuration file was passed in, could not generate experiment commands.")
        return False


def handle_error_code(error_code):
    if error_code == error_codes.SUCCESS:  # routine finished without issues
        printf(curr_phase, None, "Successfully ran routine without issues. ")
    elif error_code == error_codes.CONNECTION:  # could not find any connected motor driver PCBs
        printf(curr_phase, "Error", "No USB devices connected. Ensure the test-side and probe-side devices"
                                    " are connected and powered on. ")
    elif error_code == error_codes.CONNECTION_PROBE:  # could not find a probe motor driver PCB
        printf(curr_phase, "Error", "Detected device on test-side. No probe-side USB devices connected."
                                    " Ensure the probe-side device is connected and powered on. ")
    elif error_code == error_codes.CONNECTION_TEST:  # could not find a test motor driver PCB
        printf(curr_phase, "Error", "Detected device on probe-side. No test-side USB devices connected."
                                    " Ensure the test-side device is connected and powered on. ")
    elif error_code == error_codes.DISTINCT_IDS:  # detected two motor driver PCBs, but they were both configured as test or probe
        printf(curr_phase, "Error", "USB devices must be of different types. Ensure that the test-side device is set "
                                    "to TX and that the probe-side device is set to RX.")
    elif error_code == error_codes.VNA:  # could not connect to VNA
        printf(curr_phase, "Error", "No GPIB devices connected. Ensure the VNA is connected and powered on. ")
    elif error_code == error_codes.TEST_THETA_FAULT:  # test-theta motor fault
        printf(curr_phase, "Error", "Motor driver fault detected on the test-side theta motor. Ensure"
                                    " that the theta motor driver is properly connected to the test-side device.")
    elif error_code == error_codes.TEST_PHI_FAULT:  # test-phi motor fault
        printf(curr_phase, "Error", "Motor driver fault detected on the test-side phi motor. Ensure"
                                    " that the phi motor driver is properly connected to the test-side device.")
    elif error_code == error_codes.PROBE_PHI_FAULT:  # probe-phi motor fault
        printf(curr_phase, "Error", "Motor driver fault detected on the probe-side phi motor. Ensure"
                                    " that the phi motor driver is properly connected to the probe-side device.")
    elif error_code == error_codes.ALIGNMENT:  # alignment routine failed
        printf(curr_phase, "Error", "Alignment error detected. System could not be aligned. Try running the calibration"
                                    " routine to ensure proper alignment. ")
    elif error_code == error_codes.BAD_ARGS:  # routine was called with invalid arguments
        printf(curr_phase, "Error", "Unable to run routine as invalid arguments were entered.")
    elif error_code == error_codes.MISC:  # issue not listed above
        printf(curr_phase, "Error", "An unknown error has occurred.")
    else:
        assert False


def run_experiments(cmds):
    """ Runs the experiments in cmds."""
    for sub_expt in cmds:
        # Split cmds into usable pieces
        expt_type = sub_expt['experiment type']

        # Run the appropriate function for the sub-experiment
        if expt_type == "sweepFreq":
            printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            # print(sub_expt)
            error_code = expt.run_sweepFreq(sub_expt)
        elif expt_type == "sweepPhi":
            printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            error_code = expt.run_sweepPhi(sub_expt)
        elif expt_type == "sweepTheta":
            printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            error_code = expt.run_sweepTheta(sub_expt)
        else:
            printf(curr_phase, "Error", f"Could not run experiment of type '{expt_type}'")
            return False, expt_type
        handle_error_code(error_code)

    return True, True, True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print_welcome_sign()
    # Setup Phase
    # printf(curr_phase, None, "Setting up system...")

    # Process Command Line
    args = process_cmd_line()
    if not args:
        exit(-1)
    cfg = args.cfg
    run_type = args.run_type
    if run_type == "a":
        printf(curr_phase, None, "Running the alignment routine only.")
    # elif run_type == "s":
    #    printf(curr_phase, "Debug", "Skipping the alignment routine.")
    elif run_type == "c":
        printf(curr_phase, "Debug", "Starting the calibration interface.")
    cmds = False
    # Process Configuration File if running the entire system
    if run_type in ("f"):  # , "s"):
        cmds = process_config(cfg)
        if not cmds:
            exit(-1)
        parser.print_cmds(cmds) # Print out the commands
    exit(-1)
    # Start execution/running phase
    curr_phase = "Running"
    if run_type in ("f"):  # , "s"):
        # Start Running the experiments
        res = run_experiments(cmds)
        if res[0] is False:
            printf(curr_phase, "Error", f"Issue executing {res[1]} received {res[2]} instead.")
    elif run_type == "c":
        time.sleep(1)
        error_code = calibrate()
        handle_error_code(error_code)
    elif run_type == 'a':
        error_code = expt.run_Align()
        handle_error_code(error_code)

    # Shutdown Phase
    # curr_phase = "Shutdown"
    # print()
    # printf(curr_phase, None, "Closing down system...")
    # printf(curr_phase, None, "Successfully closed down system...")

    exit(1)