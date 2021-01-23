import sys
import getopt
from drivers import MSP430_usb as usb


def print_menu():
    print("~~~~~~~~~Menu~~~~~~~~~~")
    print("'o' : set orientation")
    print("'w' : write data")
    print("'h' : get help")
    print("'q' : quit")


def print_usage():
    print("Usage: main.py -c <configfile> -t <test>")


def process_cmd_line(argv):
    print("Parsing cmd line...")
    # Get all options and their arguments
    try:
        opts, args = getopt.gnu_getopt(argv, 'ht:c:')
    except getopt.GetoptError as err:
        print("Error invalid input")
        sys.exit()
    config = ''
    # Parse all options
    for opt, arg in opts:
        if opt == "-h":
            print_usage()
            sys.exit()
        elif opt == '-c':
            print("Arg: " + arg)
            config = arg
    print("Opening config: " + config)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    process_cmd_line(sys.argv[1:])

    print("Welcome to MSP430 User Interface v0.0")
    active = True
    port = input("MSP430 COM port: ")
    msp430 = usb.MSP430(port, open=False)
    port_conn = msp430.connect_to_port()

    while not port_conn:
        print(f"Unable to connect to {port} try a different port or entering port like: COMXX")
        port = input("MSP430 COM port: ")
        msp430.port = port
        port_conn = msp430.connect_to_port()

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
        elif action == 'h':
            print_menu()
        elif action == 'q':
            print(f"Closing port {port}")
            msp430.disconnect_from_port()
            active = False
        else:
            print("Command not recognized. Enter 'h' for help")