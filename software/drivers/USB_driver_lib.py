"""USB_driver_lib.py

This file contains the USB driver library.

"""

# Include
import usb.core
import usb.util
import sys
# from usb.backend import libusb1

appleId = 0x05AC
ipodId = 0x1265

#MCU
tiId = 0x2047
mspId = 0x0300# 0x0013 #0x03FE
# Developer Includes
'''
:param phi
:param theta
'''


def set_orientation(phi, theta):
    print(f"Setting orientation to ({phi}, {theta})")
    return


def connect_to_device(vendorId, productId, timeout=None):
    # print(f"Connecting to device with vendorId '{vendorId}' and productId '{productId}")
    dev = usb.core.find(idVendor=vendorId, idProduct=productId)
    if dev is None:
        print(f"Could not connect to device with vendorId '{vendorId}' and productId '{productId}")
        return False
    else:
        print(f"Connected to device with vendorId '{vendorId}' and productId '{productId}")
        # dev.set_configuration(1)
        cfg = usb.util.find_descriptor(dev, bConfigurationValue=1)
        # print(cfg)
        dev.set_configuration(cfg)
        # print(dev)
        # for cfg in dev:
        #     sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
        return True


def test_connection(vendorId, productId, timeout):
    print(f"Testing connection to device with vendorId '{vendorId}' and productId '{productId}'")
    return


def print_avail_devices():
    for device in usb.core.find(find_all=True):
        print(device)


# main
def main():
    print("\nRunning USB_driver_lib.py")
    # # connect_to_device(appleId, ipodId)
    # connect_to_device(tiId, mspId)

    #
    # # print_avail_devices()
    # # test_connection(0xFFE, 0x1EF, 100)
    # # set_orientation(180, 90)

    # find our device
    dev = usb.core.find(idVendor=tiId, idProduct=mspId)

    # was it found?
    if dev is None:
        raise ValueError('Device not found')

    # set the active configuration. With no arguments, the first
    # configuration will be the active one
    dev.set_configuration()

    # get an endpoint instance
    cfg = dev.get_active_configuration()
    # for cfg in dev:
    #     sys.stdout.write(str(cfg.bConfigurationValue) + '\n')
    #     for intf in cfg:
    #         sys.stdout.write('\t' + \
    #                          str(intf.bInterfaceNumber) + \
    #                          ',' + \
    #                          str(intf.bAlternateSetting) + \
    #                          '\n')
    #         for ep in intf:
    #             sys.stdout.write('\t\t' + \
    #                              str(ep.bEndpointAddress) + \
    #                              '\n')

    intf = cfg[(1, 0)]
    print(intf)
    ep = usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match=
            lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
    assert ep is not None
    print(ep)
    dev.write(2, 'LED OUT')
    # write the data
    # ep.write('test')


if __name__ == "__main__":
    main()
