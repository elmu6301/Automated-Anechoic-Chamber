import sys
import getopt
from drivers import MSP430_usb as usb
from util import config_parser as parser
import json


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
        print("Error: Invalid command line input entered...")
        print_usage()
        sys.exit()
    config = ''
    # Parse all options
    for opt, arg in opts:
        # Check to see if the user needs help
        if opt == "-h":
            print_usage()
            sys.exit()
        # Check to see if
        elif opt == '-c':
            config = arg
            if config == '' or config is None:
                print("Error: No config file detected...")
                sys.exit()
            elif config.endswith(".json") is False:
                print("Error: Config file must be a json file...")
                sys.exit()
            print(f"Opening {config}...")
        # Run the system without
        elif opt == '-l':
            print("Running direcMeasure without laser alignment...")


def connect_to_devices():
    print("\nStarting device connection process...")
    devices = []
    # Find device port names
    ports = usb.find_ports(usb.def_port_name)
    print(f"Found ports: {ports}")
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_welcome_sign()
    print_usage()
    process_cmd_line(sys.argv[1:])

    devices = connect_to_devices()
    if not devices:
        print("Unable to connect to devices...")
        print("Closing down direcMeasure...")
        exit(-1)
    numDev = len(devices)

    print_menu()

    active = True
    curDev = 0

    while active:
        action = input("--> ")
        if action == 'a':
            i = 0
            for dev in devices:
                print(f"Device[{i}]: {dev.port} {dev.devLoc}")
                i += 1
            print(f"Current device is Device[{curDev}]: {devices[curDev].port} {devices[curDev].devLoc}")
        elif action == 'd':
            if numDev != 1:

                device = input("device (TX/RX): ")
                if device in ("TX", "tx"):
                    curDev = 0
                    print(f"Current device is Device[{curDev}]: {devices[curDev].port} {devices[curDev].devLoc}")
                elif device in ("RX", "rx"):
                    curDev = 1
                    print(f"Current device is Device[{curDev}]: {devices[curDev].port} {devices[curDev].devLoc}")
                else:
                    print("Unable to identify the device. Use TX or RX to specify the device you would like to "
                          "switch to...")
            else:
                print("Only one device connected. Cannot switch to other device...")

        elif action == 'w':
            data = input("data: ")
            res = devices[curDev].write_to_device(data)
            if res == 'NACK\n':
                print("Data transfer was not successful!")
            else:
                print("Data transfer was successful!")
                print(f"Received: {res}")
        elif action == 'h':
            print_menu()
        elif action == 'q':
            print("Disconnecting device...")
            disconnect_from_devices(devices)
            active = False
        else:
            print("Command not recognized. Enter 'h' for help")

    print("Closing down direcMeasure...")

    exit(1)
