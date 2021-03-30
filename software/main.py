import sys
import getopt
import json
from optparse import OptionParser

# Custom Modules
from drivers import MSP430_usb as usb
from drivers import VNA_gpib as hpVna
from util import config_parser as parser
from util import experiments as expt


# Global Variables
curr_phase = "Setup"
mode = "Debug"
default_vna_cfg = {'deviceAddress': '16', 'freqSweepMode': 'log'}

def print_usage():
    print("\tDirecMeasure Usage")
    print("\t\t- Run with laser alignment: main.py -c <configfile>")
    print("\t\t- Run without laser alignment: main.py -c <configfile> -l")


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
        print(f"({phase}): {msg}")


def config_run(option, opt, value, parser):
    """ Used to set the run_type variable from the command line arguments"""
    if parser.values.run_type == "f":
        parser.values.run_type = opt[1]
    else:
        parser.values.run_type = "e"


def process_cmd_line():
    """ Processes the command line arguments and sets up the system control variables accordingly"""

    # Set up parser
    parser = OptionParser()
    welcome = "\n  ********************************************************  *             " \
             "Welcome to direcMeasure v1.0             * \n  " \
             "********************************************************\n"
    usage = welcome + "usage: ./direcMeasure --config<config_file>"
    parser.set_usage(usage)
    parser.set_defaults(run_type="f")

    # Add options
    parser.add_option("-c", "--config", type="string", action="store", dest="cfg", default='',
                      help="Configuration file used to control the system. Must be a JSON file.")
    parser.add_option("-a", "--alignOnly", action="callback", callback=config_run, dest="run_type",
                      help="Only run the alignment routine.")
    parser.add_option("-s", "--skipAlign", action="callback", callback=config_run, dest="run_type",
                      help="Skip the alignment routine.")
    # Parse command line
    (options, args) = parser.parse_args()

    # Error Checking
    if options.run_type == "e":
        printf(curr_phase, "Error", "Cannot simultaneously run the alignment routine only and run the system with out "
                                    "the alignment routine. See usage below: ")
        parser.print_help()
        return False
    return options


def connect_to_usb_devices():
    """ Connects to the devices. Raises errors if there are any issues connecting to the devices"""

    printf(curr_phase, None, "Starting USB device connection process...")

    devices = []
    # Find device port names
    ports = usb.find_ports(usb.def_port_name)
    # print(f"Found ports: {ports}")
    #Open devices and add to devices
    for port in ports:
        dev = usb.MSP430(port, None, True)
        if dev:
            devices.append(dev)
        else:
            printf(curr_phase, "Warning", " Could not connect to device...")

    # Check for valid USB devices
    if len(devices) == 0:  # No devices are connected
        printf(curr_phase, "Error", "No USB devices connected. Ensure the test-side and probe-side devices are"
                                    " connected and powered on.")
        return False
    elif len(devices) == 1:  # Only one device is connected
        side = devices[0].devLoc.lower()
        if side == "test":
            side = "probe"
            printf(curr_phase, "Error", f"No {side}-side USB devices connected. Ensure the {side}-side device"
                                    " is connected and powered on.")
        elif side == "probe":
            side = "test"
            printf(curr_phase, "Error", f"No {side}-side USB devices connected. Ensure the {side}-side device"
                                        " is connected and powered on.")
        return False
    else:
        for dev in devices:
            if not dev:
                print()
        if devices[0].devLoc == devices[1].devLoc:
            printf(curr_phase, "Error", f"USB devices must be of different types, cannot have two devices located "
                                        "on the {devices[0].devLoc.lower()}-side. Ensure that the test-side device"
                                        " is set to TX and that the probe-side device is set to RX.")

            disconnect_from_devices(devices)
            return False
        devices.sort(reverse=True, key=usb.sort_devices_by)

    printf(curr_phase, None, "Successfully connected to all devices...")
    return devices


def connect_to_devices():
    devices = []
    # devices = connect_to_usb_devices()
    # vna = connect_to_vna()
    devices.append(vna)
    return devices


def disconnect_from_devices(devices):
    """ Disconnects from the connected devices. """
    printf(curr_phase, None, "Starting device disconnection process...")
    result = True
    if devices:
        for dev in devices:
            res = dev.disconnect_from_port()
            if not res:
                printf(curr_phase, "Error", f"Could not disconnect from device {dev}")
                result = False
    else:
        result = False
        printf(curr_phase, "Warning", f"No devices to disconnect from.")
    return result


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

        # Check to see if the user configured the VNA otherwise use the default values
        if not meas:
            print("Using default meas")
            meas = default_vna_cfg
        printf(curr_phase, None, f"Running with VNA with address {meas['deviceAddress']} "
                                 f"and in {meas['freqSweepMode']} mode.")

        # Generate commands
        cmds = parser.gen_expt_cmds(flow)

        if not cmds:
            printf(curr_phase, "Error", f"Could not generate experiment commands from '{config_name}'.")
            return False
        printf(curr_phase, None, f"Successfully generated experiment commands from '{config_name}'.")
        return cmds, meas
    else:
        printf(curr_phase, "Error", f"No configuration file was passed in, could not generate experiment commands.")
        return False


def run_experiments(devices, cmds):
    """ Runs the experiments in cmds."""
    if not devices or not cmds:
        return False, False, False
    for sub_expt in cmds:
        # Split cmds into usable pieces
        expt_type = sub_expt['type']
        t_cmds = sub_expt['test']
        p_cmds = sub_expt['probe']
        g_cmds = sub_expt['gpib']
        # expt_res = ''

        # Run the appropriate function for the sub-experiment
        if expt_type == "sweepFreq":
            printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            expt_res = expt.run_sweepFreq(devices, t_cmds, p_cmds, g_cmds)
            if expt_res[0] is False:
                return False, expt_res[1], expt_res[2]
        elif expt_type == "sweepPhi":
            printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            expt_res = expt.run_sweepPhi(devices, t_cmds, p_cmds, g_cmds)
            if expt_res[0] is False:
                return False, expt_res[1], expt_res[2]
        elif expt_type == "sweepTheta":
            printf(curr_phase, "Debug", f"Running Type: {expt_type}")
            expt_res = expt.run_sweepTheta(devices, t_cmds, p_cmds, g_cmds)
            if expt_res[0] is False:
                return False, expt_res[1], expt_res[2]
        else:
            printf(curr_phase, "Error", f"Could not run experiment of type '{expt_type}'")
            return False, expt_type
    return True, True, True


def run_alignment_routine(devices):
    """ Runs the alignment routine. """
    print()
    printf(curr_phase, None, "Starting alignment process...")
    # TODO - add calls to alignment functions here
    printf(curr_phase, None, "Successfully completed alignment process...")
    return True


def connect_to_vna(vna_cfg):
    printf(curr_phase, None, "Starting VNA connection process...")
    if not vna_cfg:
        printf(curr_phase, "Error", "No GPIB devices connected. Ensure the VNA is connected and powered on.")
        return False
    dev_addr = vna_cfg['deviceAddress']
    dev_vna = hpVna.VNA_HP8719A(dev_addr)
    if not dev_vna.instrument:
        printf(curr_phase, "Error", "No GPIB devices connected. Ensure the VNA is connected and powered on.")
        return False
    # print(dev_vna)
    printf(curr_phase, None, "Successfully connected to VNA...")
    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print_welcome_sign()
    # Setup Phase
    printf(curr_phase, None, "Setting up system...")

    # Process Command Line
    args = process_cmd_line()
    if not args:
        exit(-1)
    cfg = args.cfg
    vna_cfg = ''
    run_type = args.run_type

    if run_type == "a":
        printf(curr_phase, "Debug", "Running the alignment routine only.")
    elif run_type == "s":
        printf(curr_phase, "Debug", "Skipping the alignment routine.")
    cmds = False
    # Process Configuration File if running the entire system
    if run_type in ("f", "s"):
        cmds, vna_cfg = process_config(cfg)
        if not cmds:
            exit(-1)
        # parser.print_cmds(cmds) # Print out the commands

    # Connect to USB devices
    # devices = connect_to_devices()
    # if not devices:
    #     printf(curr_phase, "Error", "Unable to connect to devices...")
    #     # TODO Add call to shutdown
    #     printf(curr_phase, "Error", "Closing down direcMeasure...")
    #     exit(-1)

    # Connect to VNA
    # TODO
    vna = connect_to_vna(vna_cfg)

    # Run alignment routine
    # if run_type in ("f", "a"):
    #     print()
    #     printf(curr_phase, None, "Starting alignment process...")
    #     res = run_alignment_routine(devices)
    #     if res is False:
    #         printf(curr_phase, "Error", "Unable to align system...")
    #         # TODO Add call to shutdown
    #         printf(curr_phase, "Error", "Closing down direcMeasure...")
    #         exit(-1)
    printf(curr_phase, None, "Successfully completed setup phase.")

    # Start execution/running phase
    # curr_phase = "Running"
    # if run_type in ("f", "s"):
    #     # Start Running the experiments
    #     res = run_experiments(devices, cmds)
    #     if res[0] is False:
    #         printf(curr_phase, "Error", f"Issue executing {res[1]} received {res[2]} instead")

    # Shutdown Phase
    curr_phase = "Shutdown"
    print()
    printf(curr_phase, None, "Closing down system...")
    printf(curr_phase, None, "Disconnecting devices...")
    # if devices != "":
        # disconnect_from_devices(devices)
    printf(curr_phase, None, "Successfully closed down system...")

    exit(1)
