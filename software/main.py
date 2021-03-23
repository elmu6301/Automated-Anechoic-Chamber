import sys
import getopt
import json

# Custom Modules
from drivers import MSP430_usb as usb
from util import config_parser as parser
from util import experiments as expt


def print_menu():
    print("~~~~~~~~~Menu~~~~~~~~~~")
    print("'a' : check available devices")
    print("'d' : set current device")
    print("'w' : write data")
    print("'h' : get help")
    print("'q' : quit")


def print_usage():
    print("\tDirecMeasure Usage")
    print("\t\t- Run with laser alignment: main.py -c <configfile>")
    print("\t\t- Run without laser alignment: main.py -c <configfile> -l")


def print_welcome_sign():
    print("\n  ********************************************************")
    print("  *             Welcome to direcMeasure v0.0             *")
    print("  ********************************************************\n")


def process_cmd_line(argv):
    # Get all options and their arguments
    try:
        opts, args = getopt.gnu_getopt(argv, "halc:")
    except getopt.GetoptError as err:
        # print("Error: Invalid command line input entered...")
        # print_usage()
        return False
    config = ''
    run_alignment = True
    align_only = False
    # Parse all options
    for opt, arg in opts:
        # Check to see if the user needs help
        if opt == "-h":
            print_usage()
            return False
        # Check to see if
        elif opt == '-c':
            config = arg
            if config == '' or config is None:
                print("Error: No config file detected...")
                return False
            elif config.endswith(".json") is False:
                print("Error: Config file must be a json file...")
                return False
        elif opt == '-a':
            print("Running direcMeasure laser alignment routine only...")
            align_only = True
        # Run the system without laser alignment
        elif opt == '-l':
            # print("Running direcMeasure without laser alignment...")
            run_alignment = False
        # Run the system without laser alignment
    return config, align_only, run_alignment


def connect_to_devices():
    print("\nStarting device connection process...")
    devices = []
    # Find device port names
    ports = usb.find_ports(usb.def_port_name)
    # print(f"Found ports: {ports}")
    # Open devices and add to devices
    for port in ports:
        dev = usb.MSP430(port, None, True)
        if not dev:
            return False
        devices.append(dev)
        print(f"Identified device as {dev.devLoc}")
    if len(devices) == 2:
        if devices[0].devLoc == devices[1].devLoc:
            print(f"Cannot have two devices located on the {devices[1].devLoc} side.")
            disconnect_from_devices(devices)
            return False
        devices.sort(reverse=True, key=usb.sort_devices_by)
    return devices


def disconnect_from_devices(devices):
    print("\nStarting device disconnection process...")
    for dev in devices:
        res = dev.disconnect_from_port()
        if not res:
            return False
    return devices


def process_config(config_name):
    if config_name != '':
        # Find Config
        print(f"\nStarting configuration file parsing process on {config_name}...")
        full_cfg_name = parser.find_config(config_name)
        if not full_cfg_name:
            print(f"Error: Could not locate the file '{config_name}'. Ensure that '{config_name}' "
                  f"is located in the configuration file repository.")
            return False
        # print(f"Found file: {full_cfg_name}")
        # Get flow
        flow, meas = parser.get_expt_flow_meas(full_cfg_name)
        if not flow:
            print(f"Error: Could read in data from '{config_name}'. Ensure that '{config_name}' "
                  f"is the correct format. See the User Manual for Details.")
            return False
        # print(flow)
        # Generate commands
        cmds = parser.gen_expt_cmds(flow)
        if not cmds:
            print(f"Error: Could generate experiment commands from '{config_name}'.")
            return False
        # print(cmds)
        print(f"Successfully generated experiment commands from '{config_name}'.")
        return cmds
    else:
        return False


def run_experiments(devices, cmds):
    for sub_expt in cmds:
        # Split cmds into usable pieces
        expt_type = sub_expt['type']
        t_cmds = sub_expt['test']
        p_cmds = sub_expt['probe']
        g_cmds = sub_expt['gpib']
        # expt_res = ''

        # Run the appropriate function for the sub-experiment
        if expt_type == "sweepFreq":
            print(f"\nRunning Type: {expt_type}")
            expt_res = expt.run_sweepFreq(devices, t_cmds, p_cmds, g_cmds)
            if expt_res[0] is False:
                return False, expt_res[1], expt_res[2]
        elif expt_type == "sweepPhi":
            print(f"\nRunning Type: {expt_type}")
            expt_res = expt.run_sweepPhi(devices, t_cmds, p_cmds, g_cmds)
            if expt_res[0] is False:
                return False, expt_res[1], expt_res[2]
        elif expt_type == "sweepTheta":
            print(f"\nRunning Type: {expt_type}")
            expt_res = expt.run_sweepTheta(devices, t_cmds, p_cmds, g_cmds)
            if expt_res[0] is False:
                return False, expt_res[1], expt_res[2]
        else:
            print(f"\nError: Could not run experiment of type '{expt_type}'")
            return False, expt_type
    return True, True, True


def run_alignment_routine(devices):
    print("\nStarting alignment process...")
    # TODO
    print("Successfully completed alignment process...")
    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_welcome_sign()
    # Setup Phase
    print("\nSetting up system...")
    # Process Command Line
    args = process_cmd_line(sys.argv[1:])
    if not args:
        print("Error: Could not parse command line arguments. See usage below:")
        print_usage()
        exit(-1)
    cfg = args[0]
    full_run = not args[1]
    align = args[2]
    # cmds = False
    # Process Configuration File if running the entire system
    # if full_run:
    cmds = process_config(cfg)
    if not cmds:
        print("Error: Could not process configuration file. ")
        exit(-1)
    parser.print_cmds(cmds) # Print out the commands

    # Connect to USB devices
    # devices = connect_to_devices()
    # if not devices:
    #     print("Unable to connect to devices...")
    #     print("Closing down direcMeasure...")
    #     exit(-1)

    # Connect to VNA here
    # TODO

    # Run alignment routine
    # if align:
    #     print("\nStarting device connection process...")
    #     res = run_alignment_routine(devices)
    #     if res is False:
    #         print("Unable to align system...")
    #         print("Closing down direcMeasure...")
    #         exit(-1)

    print("Successfully completed setup phase.")

    # if full_run:
    #     # Start Running the experiments
    #     res = run_experiments(devices, cmds)
    #     if res[0] is False:
    #         print(f"Error: Issue executing {res[1]} received {res[2]} instead")
    #
    # # Shutdown Phase
    # print("\nClosing down system...")
    # # print("Disconnecting devices...")
    # # disconnect_from_devices(devices)
    # print("Successfully closed down system...")

    exit(1)
