import sys
import getopt
import json
from optparse import OptionParser

# Custom Modules
from util import config_parser as parser
from util import experiments as expt

from util import error_codes
from util.run_find_aligned_position import calibrate
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
    parser.set_defaults(run_type="f")

    # Add options
    parser.add_option("-c", "--config", type="string", action="store", dest="cfg", default='',
                      help="Configuration file used to control the system. Must be a JSON file.")
    parser.add_option("-a", "--alignOnly", action="callback", callback=config_run, dest="run_type",
                      help="Only run the alignment routine.")
    # parser.add_option("-s", "--skipAlign", action="callback", callback=config_run, dest="run_type",
    #                  help="Skip the alignment routine.")
    parser.add_option("--calibrate", action="store_true", dest="calibrate", default=False,
                      help="Run the calibration interface.")
    # Parse command line
    (options, args) = parser.parse_args()

    # Error Checking
    if options.run_type == "e":
        printf(curr_phase, "Error", "Cannot simultaneously run the alignment routine only and run the system with out "
                                    "the alignment routine. See usage below: ")
        parser.print_help()
        return False

    num_modes = int(options.cfg != '') + int(options.run_type == 'a') + int(options.calibrate)
    if num_modes == 0:
        printf(curr_phase, "Error", "No options specified. See usage below:")
        parser.print_help()
    if num_modes > 1:
        printf(curr_phase, "Error", "Mutually-exclusive options specified. See usage below:")
        parser.print_help()
    if options.calibrate:
        options.run_type = "c"
    return options


def process_config(config_name):
    """ Parses the configuration file and generates the appropriate commands. """
    if config_name != '':
        # Find Config
        printf(curr_phase, None, f"Starting configuration file parsing process on {config_name}...")
        full_cfg_name = parser.find_config(config_name)
        if not full_cfg_name:
            printf(curr_phase, "Error", f"Could not locate the file '{config_name}'. Ensure that '{config_name}'"
                                        f" is located in the configuration file repository.")
            return False
        # Get flow and meas config from the configuration file
        flow, meas = parser.get_expt_flow_meas(full_cfg_name)
        if not flow:
            printf(curr_phase, "Error", f"Could not read in data from '{config_name}'. Ensure that '{config_name}' "
                                        f"is the correct format. See the User Manual for Details.")
            return False
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
    # Elena: write error-handling code below
    if error_code == error_codes.SUCCESS:  # routine finished without issues
        print('success error code')
    elif error_code == error_codes.CONNECTION:  # could not find any connected motor driver PCBs
        print('connection error code')
    elif error_code == error_codes.CONNECTION_PROBE:  # could not find a probe motor driver PCB
        print('probe connection error code')
    elif error_code == error_codes.CONNECTION_TEST:  # could not find a test motor driver PCB
        print('test connection error code')
    elif error_code == error_codes.DISTINCT_IDS:  # detected two motor driver PCBs, but they were both configured as test or probe
        print('distinct ids error code')
    elif error_code == error_codes.VNA:  # could not connect to VNA
        print('vna error code')
    elif error_code == error_codes.TEST_THETA_FAULT:  # test-theta motor fault
        print('test-theta fault error code')
    elif error_code == error_codes.TEST_PHI_FAULT:  # test-phi motor fault
        print('test-phi fault error code')
    elif error_code == error_codes.PROBE_PHI_FAULT:  # probe-phi motor fault
        print('probe-phi fault error code')
    elif error_code == error_codes.ALIGNMENT:  # alignment routine failed
        print('alignment error code')
    elif error_code == error_codes.BAD_ARGS:  # routine was called with invalid arguments
        print('bad args error code')
    elif error_code == error_codes.MISC:  # issue not listed above
        print('misc error code')
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


def run_alignment_routine(devices):
    """ Runs the alignment routine. """
    print()
    printf(curr_phase, None, "Starting alignment process...")
    # TODO - add calls to alignment functions here
    printf(curr_phase, None, "Successfully completed alignment process...")
    return True


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
        # printf(curr_phase, "Debug", "Running the alignment routine only.")
        print('(Setup):   ', 'Running the alignment routine only.')
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
        # parser.print_cmds(cmds) # Print out the commands

    # Start execution/running phase
    # curr_phase = "Running"
    if run_type in ("f"):  # , "s"):
        # Start Running the experiments
        res = run_experiments(cmds)
        if res[0] is False:
            printf(curr_phase, "Error", f"Issue executing {res[1]} received {res[2]} instead")
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