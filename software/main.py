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
        opts, args = getopt.gnu_getopt(argv, "hlc:")
    except getopt.GetoptError as err:
        # print("Error: Invalid command line input entered...")
        # print_usage()
        return False
    config = ''
    run_alignment = True
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
            # print(f"Opening {config}...")
        # Run the system without
        elif opt == '-l':
            print("Running direcMeasure without laser alignment...")
            run_alignment = False
    return config, run_alignment


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
    print(f"\nStarting configuration file parsing process on {config_name}...")
    if config_name != '':
        # Find Config
        full_cfg_name = parser.find_config(config_name)
        if not full_cfg_name:
            print(f"Error: Could not locate the file '{config_name}'. Ensure that '{config_name}' "
                  f"is located in the configuration file repository.")
            return False
        # print(f"Found file: {full_cfg_name}")
        # Get flow
        flow = parser.get_expt_flow(full_cfg_name)
        if not flow:
            print(f"Error: Could read in data from '{config_name}'. Ensure that '{config_name}' "
                  f"is the correct format. See the User Manual for Details.")
            return False
        # print(flow)
        # Generate commands
        cmds = parser.gen_expt_cmds(flow)
        if not cmds:
            print(f"Error: Could generate experiment commnands from '{config_name}'.")
            return False
        # print(cmds)
        return cmds
    else:
        return True


def run_experiments(devices, cmds):
    for sub_expt in cmds:
        print(f"\nRunning Type: {sub_expt['type']}")
        t_cmds = sub_expt['test']
        p_cmds = sub_expt['probe']
        g_cmds = sub_expt['gpib']
        for cmd in t_cmds:
            print(f"\tSending '{cmd}' to test device...")
            resp = devices[0].write_to_device(cmd)
            print(resp)
            if resp != cmd:
                return False, cmd
    return True, True



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_welcome_sign()

    # Process Command Line
    args = process_cmd_line(sys.argv[1:])
    if not args:
        print("Error: Could not parse command line arguments. See usage below:")
        print_usage()
        exit(-1)
    cfg = args[0]
    align = args[1]

    # Process Configuration File
    cmds = process_config(cfg)
    if not cmds:
        print("Error: Could not process configuration file. ")
        exit(-1)
    # parser.print_cmds(cmds)
    # Connect to devices
    devices = connect_to_devices()
    if not devices:
        print("Unable to connect to devices...")
        print("Closing down direcMeasure...")
        exit(-1)
    numDev = len(devices)

    res = run_experiments(devices, cmds)
    if res[0] is False:
        print(f"Error: Issue executing {res[1]}...")
        exit(-1)

    # print_menu()
    #
    # active = True
    # curDev = 0
    #
    # while active:
    #     action = input("--> ")
    #     if action == 'a':
    #         i = 0
    #         for dev in devices:
    #             print(f"Device[{i}]: {dev.port} {dev.devLoc}")
    #             i += 1
    #         print(f"Current device is Device[{curDev}]: {devices[curDev].port} {devices[curDev].devLoc}")
    #     elif action == 'd':
    #         if numDev != 1:
    #
    #             device = input("device (TX/RX): ")
    #             if device in ("TX", "tx"):
    #                 curDev = 0
    #                 print(f"Current device is Device[{curDev}]: {devices[curDev].port} {devices[curDev].devLoc}")
    #             elif device in ("RX", "rx"):
    #                 curDev = 1
    #                 print(f"Current device is Device[{curDev}]: {devices[curDev].port} {devices[curDev].devLoc}")
    #             else:
    #                 print("Unable to identify the device. Use TX or RX to specify the device you would like to "
    #                       "switch to...")
    #         else:
    #             print("Only one device connected. Cannot switch to other device...")
    #
    #     elif action == 'w':
    #         data = input("data: ")
    #         res = devices[curDev].write_to_device(data)
    #         if res == 'NACK\n':
    #             print("Data transfer was not successful!")
    #         else:
    #             print("Data transfer was successful!")
    #             print(f"Received: {res}")
    #     elif action == 'h':
    #         print_menu()
    #     elif action == 'q':
    #
    #         active = False
    #     else:
    #         print("Command not recognized. Enter 'h' for help")
    print("Disconnecting device...")
    disconnect_from_devices(devices)
    print("\nClosing down direcMeasure...")

    exit(1)
