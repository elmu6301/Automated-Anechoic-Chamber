import sys
import getopt
import json
from optparse import OptionParser

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
            print(f"Error: Could not generate experiment commands from '{config_name}'.")
            return False
        # print(cmds)
        print(f"Successfully generated experiment commands from '{config_name}'.")
        return cmds
    else:
        print(f"Error: No configuration file was passed in, could not generate experiment commands.")
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


def config_run(option, opt, value, parser):
    if parser.values.run_type == "f":
        parser.values.run_type = opt[1]
    else:
        parser.values.run_type = "e"


def process_cmd_line():

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
    parser.add_option("-s", "--skipAlign", action="callback", callback=config_run, dest="run_type",
                      help="Skip the alignment routine.")
    # Parse command line
    (options, args) = parser.parse_args()

    # Error Checking
    if options.run_type == "e":
        print("Error: Cannot simultaneously only run the alignment routine and with out the alignment routine. "
              "See usage below:")
        parser.print_help()
        return False
    return options


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print_welcome_sign()
    # Setup Phase
    print("\nSetting up system...")

    # Process Command Line
    args = process_cmd_line()
    if not args:
        exit(-1)
    cfg = args.cfg
    run_type = args.run_type
    if run_type == "s":
        print("Running the alignment routine only.")
    elif run_type == "s":
        print("Skipping the alignment routine.")
    cmds = False
    # Process Configuration File if running the entire system
    if run_type in ("f", "s"):
        cmds = process_config(cfg)
        if not cmds:
            exit(-1)
        parser.print_cmds(cmds) # Print out the commands

    # Connect to USB devices
    devices = connect_to_devices()
    if not devices:
        print("Unable to connect to devices...")
        # TODO Add call to shutdown
        print("Closing down direcMeasure...")
        exit(-1)

    # Connect to VNA
    # TODO

    # Run alignment routine
    if run_type in ("f", "a"):
        print("\nStarting device connection process...")
        res = run_alignment_routine(devices)
        if res is False:
            print("Unable to align system...")
            # TODO Add call to shutdown
            print("Closing down direcMeasure...")
            exit(-1)
    print("Successfully completed setup phase.")

    if run_type in ("f", "s"):
        # Start Running the experiments
        res = run_experiments(devices, cmds)
        if res[0] is False:
            print(f"Error: Issue executing {res[1]} received {res[2]} instead")

    # Shutdown Phase
    print("\nClosing down system...")
    print("Disconnecting devices...")
    if devices != "":
        disconnect_from_devices(devices)
    print("Successfully closed down system...")

    exit(1)
