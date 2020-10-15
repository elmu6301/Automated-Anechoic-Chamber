"""USB_driver_lib.py

This file contains the USB driver library.

"""

# Include


# Developer Includes
'''
:param phi
:param theta
'''
def set_orientation(phi, theta):
    print(f"Setting orientation to ({phi}, {theta})")
    return

def connect_to_device(vendorId, productId, timeout):
    print(f"Connecting to device with vendorId '{vendorId}' and productId '{productId}")
    return

def test_connection(vendorId, productId, timeout):
    print(f"Testing connection to device with vendorId '{vendorId}' and productId '{productId}'")
    return
# main
def main():
    print("\nRunning USB_driver_lib.py")
    connect_to_device(0xFFE, 0x1EF, 100)
    test_connection(0xFFE, 0x1EF, 100)
    set_orientation(180, 90)


if __name__ == "__main__":
    main()