# Include
import pydoc
import serial
import random
'''
host_usb.py
This file contains the USB library for the host machine.
'''
# MSP430 = None
global MSP430


def to_usb_str(cmdStr):
    # Check to make sure that the command is not empty and is a string
    if cmdStr is not None and isinstance(cmdStr, str):
        usb_str = cmdStr
        # add carriage return if not already added
        if not usb_str.endswith('\r'):
            usb_str += '\r'
        # encode the string to ascii and return
        return usb_str.encode('ascii')
    return None


def connect_to_port(port, baudrate):
    global MSP430
    try:
        MSP430 = serial.Serial(port, baudrate=baudrate)
        # MSP430.open()
        if MSP430.isOpen():
            print(f"{port} is open", end='')
        while MSP430.in_waiting:
            MSP430.read()
        # print(f"Connected to {port}")
    except Exception as e:
        print(f"Could not connect to {port}")

        return False
    return True


def disconnect_from_port():
    global MSP430

    try:
        # Wait for the lines to settle
        while MSP430.out_waiting and MSP430.in_waiting:
            pass
        # close the port
        MSP430.close()

        # Check to make sure that the port is
        if MSP430.isOpen():
            # print("Port is still open")
            return False
    except Exception as e:
        print(f"Could not disconnect from MSP340 {e}", end='')
        return False
    return True


def write_to_device(data):
    if data is not None:
        global MSP430
        # Convert Data to a USB string
        usb_data = to_usb_str(data)
        if usb_data:
            # Try writing to device
            try:
                MSP430.write(usb_data)
            except Exception as e:
                print(f"Could write to the MSP340")
                return False
            # Wait for response
            while MSP430.in_waiting == 0:
                pass
            response = MSP430.readline()
            return response.decode()
        return False
    return False


def set_orientation(phi, theta):
    global MSP430
    # Check inputs
    if not isinstance(phi, int) and not isinstance(theta, int):
        return False
    if not isinstance(phi, int) or not (0 <= phi <= 360):
        phi = 1000
    if not isinstance(theta, int) or not (0 <= theta <= 360):
        theta = 1000

    # combine string
    orient_str = '%d,%d' % (phi,theta)
    # send orientations to the device
    return orient_str # write_to_device(orient_str)


# main
def main():
    print("\nRunning USB_driver_lib.py")
    connect_to_port('COM12', baudrate = 9600)
    rand_int = random.randint(1, 1000)
    rand_str = "RAND%d" % (rand_int)
    print(rand_str)
    res = write_to_device(rand_str)
    # res = write_to_device('LED OFF')
    print(res)
    disconnect_from_port()


if __name__ == "__main__":
    main()
