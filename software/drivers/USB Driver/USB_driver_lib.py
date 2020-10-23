"""USB_driver_lib.py

This file contains the USB driver library.

"""

# Include
import usb.core
import usb.util
from usb.backend import libusb1

appleId = 0x05AC
ipodId = 0x1265
# Developer Includes
'''
:param phi
:param theta
'''
def set_orientation(phi, theta):
    print(f"Setting orientation to ({phi}, {theta})")
    return

def connect_to_device(vendorId, productId, timeout=None):
    print(f"Connecting to device with vendorId '{vendorId}' and productId '{productId}")
    dev = usb.core.find(idVendor=vendorId, idProduct=productId)
    if dev is None:
        raise ValueError(f"Could not connect to device with vendorId '{vendorId}' and productId '{productId}")
    else:
        print("Connected")
    return

def test_connection(vendorId, productId, timeout):
    print(f"Testing connection to device with vendorId '{vendorId}' and productId '{productId}'")
    return
# main
def main():
    print("\nRunning USB_driver_lib.py")
    connect_to_device(appleId, ipodId)
    # test_connection(0xFFE, 0x1EF, 100)
    # set_orientation(180, 90)


if __name__ == "__main__":
    main()
    # import os
    # os.environ['PYUSB_DEBUG'] = 'debug'
    # import usb.core
    # usb.core.find()
    # be = libusb1.get_backend()
    # if be is None:
    #     print("no backend")

    # for device in usb.core.find(find_all=True):
    #     print(device)
