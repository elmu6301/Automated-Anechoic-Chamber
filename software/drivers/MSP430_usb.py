# Include
import pydoc
import serial
import random
'''
host_usb.py
This file contains the USB library for the host machine.
'''

from serial.tools import list_ports


class MSP430:

    def __init__(self, port, name=None, open=True):
        self.port = port
        self.name = name
        self.MSP430 = None
        self.baudrate = 9600
        self.port_name = "MSP Application UART1"  #CHECK THIS IT MAY HAVE CHANGED
        if open:
            try:
                self.connect_to_port()
            except:
                pass

    def find_port(self):
        #Inspired by: https://stackoverflow.com/questions/35724405/pyserial-get-the-name-of-the-device-behind-a-com-port
        #Formats:
            #print(port) = COM5 - MSP Application UART1 (COM5)
            #print(port.description) = MSP Application UART1 (COM5)
            #print(port.device) = COM5

        ports = list(list_ports.comports())

        for port in ports:
            if port.device:
                if self.port_name in str(port.description):
                    return port.device

    def connect_to_port(self):
        try:
            self.port = self.find_port()
            self.MSP430 = serial.Serial(self.port, baudrate=self.baudrate)
            # MSP430.open()
            if self.MSP430.isOpen():
                print(f"{self.port} is open")
            while self.MSP430.in_waiting:
                self.MSP430.read()
            # print(f"Connected to {port}")
        except Exception as e:
            print(f"Could not connect to {self.port}")
            return False
        return True

    def disconnect_from_port(self):
        try:
            # Wait for the lines to settle
            while self.MSP430.out_waiting and self.MSP430.in_waiting:
                pass
            # close the port
            self.MSP430.close()
            # Check to make sure that the port is
            if self.MSP430.isOpen():
                # print("Port is still open")
                return False
        except Exception as e:
            print(f"Could not disconnect from MSP340 {e}")
            return False
        return True

    def write_to_device(self, data):
        if data is not None:
            # Convert Data to a USB string
            usb_data = to_usb_str(data)
            if usb_data:
                # Try writing to device
                try:
                    self.MSP430.write(usb_data)
                except Exception as e:
                    print(f"Could write to the MSP340")
                    return False
                # Wait for response
                while self.MSP430.in_waiting == 0:
                    pass
                response = self.MSP430.readline()
                return response.decode()
            return False
        return False

    def set_orientation(self, phi, theta):
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
        return orient_str # self.write_to_device(orient_str)


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


# main
def main():
    print("\nMSP430_usb.py")
    msp430 = MSP430('COM12', "Eval Board")
    # msp430.connect_to_port()

    res = msp430.write_to_device("LED ON")

    # rand_int = random.randint(1, 1000)
    # rand_str = "RAND%d" % (rand_int)
    # print(rand_str)
    # res = msp430.write_to_device(rand_str)
    print(res)
    msp430.disconnect_from_port()


if __name__ == "__main__":
    main()
