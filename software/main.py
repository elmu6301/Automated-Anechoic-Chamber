from drivers import MSP430_usb as usb


def print_menu():
    print("~~~~~~~~~Menu~~~~~~~~~~")
    print("'o' : set orientation")
    print("'w' : write data")
    print("'h' : get help")
    print("'q' : quit")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Welcome to MSP430 User Interface v0.0")
    print_menu()

    active = True

    port = input("MSP430 COM port: ")
    msp430 = usb.MSP430(port, open=False)
    port_conn = msp430.connect_to_port()

    while not port_conn:
        print(f"Unable to connect to {port} try a different port or entering port like: COMXX")
        port = input("MSP430 COM port: ")
        msp430.port = port
        port_conn = msp430.connect_to_port()

    while active:
        action = input("--> ")
        if action == 'o':
            phi = input("phi: ")
            theta = input("theta: ")
            print(f"Sending {phi,theta} to device...")
        elif action == 'w':
            data = input("data: ")
            res = msp430.write_to_device(data)
            if res:
                print("Data transfer was successful!")
            else:
                print("Data transfer was not successful!")
        elif action == 'h':
            print_menu()
        elif action == 'q':
            print(f"Closing port {port}")
            msp430.disconnect_from_port()
            active = False
        else:
            print("Command not recognized. Enter 'h' for help")
