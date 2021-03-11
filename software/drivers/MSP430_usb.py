# Include
import pydoc
import serial
import random
from serial.tools import list_ports

'''
host_usb.py
This file contains the USB library for the host machine.
'''

def_port_name = "MSP430-USB Example"
dev_identifier = "IDEN"


class MSP430:

    def __init__(self, port=None, name=None, open=True):
        self.port = port
        self.name = name
        self.devLoc = ''
        self.MSP430 = None
        self.baudrate = 9600
        self.port_name = def_port_name
        self.curr_phi = 0
        self.curr_theta = 0
        if open:
            try:
                self.connect_to_port()
            except:
                pass

    def find_port(self):
        #Inspired by: https://stackoverflow.com/questions/35724405/pyserial-get-the-name-of-the-device-behind-a-com-port

        ports = list(list_ports.comports())

        for port in ports:
            if port.device:
                if self.port_name in str(port.description):
                    return port.device

    def connect_to_port(self):
        try:
            # Get port if not passed in
            if self.port is None:
                self.port = self.find_port()
            # Open COM port
            self.MSP430 = serial.Serial(self.port, baudrate=self.baudrate)

            if self.MSP430 is None:
                self.port = self.find_port()
                self.MSP430 = serial.Serial(self.port, baudrate=self.baudrate)
            # if self.MSP430.isOpen():
            #     print(f"{self.port} is open")
            while self.MSP430.in_waiting:
                self.MSP430.read()
            # print(f"Connected to {self.port}")
            # identify if the port is test or probe
            loc = self.write_to_device(dev_identifier)
            if loc == "TEST":
                self.devLoc = "TEST"
            elif loc == "PROBE":
                self.devLoc = "PROBE"
            else:
                print(f"Could not identify device location: {loc}")
                return False
            # print(f"Device identified as: {loc}")
        except Exception as e:
            print(f"Could not connect to {self.port} because {e}")
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
                print("Port is still open")
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
                    print(f"Error: Could not write to the MSP340 because {e}")
                    return False
                # Wait for ACK or NACK
                while self.MSP430.in_waiting == 0:
                    pass
                cmd_received = self.MSP430.readline().decode()
                if cmd_received != "a\n":
                    print(
                        f"Error: Device did not acknowledge command, received {cmd_received[0:len(cmd_received) - 1]}")
                    return False

                # Wait for Done Response
                while self.MSP430.in_waiting == 0:
                    pass
                done_resp = self.MSP430.readline().decode()
                if done_resp.endswith("\n"):
                    done_resp = done_resp[0:len(done_resp) - 1]
                return done_resp
            return False
        return False

    def send_orient_cmd(self, data):
        if data is not None:
            # Convert Data to a USB string
            usb_data = to_usb_str(data)
            if usb_data:
                # Try writing to device
                try:
                    self.MSP430.write(usb_data)
                except Exception as e:
                    print(f"Error: Could not write to the MSP340 because {e}")
                    return False
                # Wait for ACK or NACK
                while self.MSP430.in_waiting == 0:
                    pass
                cmd_received = self.MSP430.readline().decode()
                if cmd_received != "a\n":
                    print(f"Error: Device did not acknowledge command, received {cmd_received[0:len(cmd_received)-1]}")
                    return False

                # Wait for Done Response
                while self.MSP430.in_waiting == 0:
                    pass
                done_resp = self.MSP430.readline().decode()
                if done_resp.endswith("\n"):
                    done_resp = done_resp[0:len(done_resp) - 1]
                return done_resp
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


def sort_devices_by(msp430):
    return msp430.devLoc


def find_ports(port_name):
    ports = list(list_ports.comports())
    found_dev = []
    for port in ports:
        if port.device:
            if port_name in str(port.description):
                found_dev.append(port.device)
    return found_dev


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
    import time
    msp430s = []
    ports = find_ports(def_port_name)
    print(f"Found ports: {ports}")
    for port in ports:
        msp430 = MSP430(port, "Eval Board", open=True)
        msp430s.append(msp430)

    for msp430 in msp430s:
        res = msp430.write_to_device("LED ON")
        time.sleep(2)
        res = msp430.write_to_device("LED OFF")
        msp430.disconnect_from_port()


if __name__ == "__main__":
    main()
