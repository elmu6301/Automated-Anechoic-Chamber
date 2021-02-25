import sys
import getopt
from drivers import MSP430_usb as usb
from util import config_parser as parser
import json


def print_menu():
    print("~~~~~~~~~Menu~~~~~~~~~~")
    print("'o' : set orientation")
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_welcome_sign()
    print_usage()
    process_cmd_line(sys.argv[1:])

    print("\nStarting device connection process")
    active = True
    msp430 = usb.MSP430(port=None, open=False)
    port_conn = msp430.connect_to_port()
    if port_conn is False:
        print("Closing down direcMeasure...")
        exit(-1)

    print_menu()
    while active:
        action = input("--> ")
        if action == 'o':
            phi = input("phi: ")
            theta = input("theta: ")
            print(f"Sending {phi, theta} to device...")
        elif action == 'w':
            data = input("data: ")
            res = msp430.write_to_device(data)
            if res == 'NACK\n':
                print("Data transfer was not successful!")
            else:
                print("Data transfer was successful!")
                print(f"Received: {res}")
        elif action == 'h':
            print_menu()
        elif action == 'q':
            print("Disconnecting device...")
            msp430.disconnect_from_port()
            active = False
        else:
            print("Command not recognized. Enter 'h' for help")
    print("Closing down direcMeasure...")
    exit(1)
