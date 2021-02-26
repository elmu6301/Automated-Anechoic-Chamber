import pytest
from drivers import MSP430_usb as usb
import time
import random

port = None
msp430 = usb.MSP430(port, open=False)


def test_to_usb_str():
    # test with string "LED ON"
    test_str = "LED ON"
    usb_str = usb.to_usb_str(test_str)
    expected = b'LED ON\r'
    assert usb_str == expected
    print(f"\n\tCase 'LED ON': expected {expected} got {usb_str}")

    # test with None
    test_str = None
    usb_str = usb.to_usb_str(test_str)
    assert usb_str == None
    print(f"\tCase 'None': expected {None} got {usb_str}")


def test_set_orientation():
    # TODO
    assert True


def test_find_port():
    usb_port = msp430.find_port()
    print(f"Found device at {usb_port}")
    assert usb_port #== 'COM4'


def test_connect_to_port():
    print("\n\t", end='')
    # test connecting to an unopened port
    assert msp430.connect_to_port()
    print("\t", end='')
    # test connecting to an opened port
    assert not msp430.connect_to_port()



def test_write_to_device():
    # Turn the LED ON
    res = msp430.write_to_device('LED ON')
    assert res == "ACK\n"
    print(f"\n\tCase CMD = 'LED ON': expected 'ACK' got {res}", end='')
    time.sleep(1)
#
    # Turn the LED OFF
    res = msp430.write_to_device('LED OFF')
    assert res == "ACK\n"
    print(f"\tCase CMD = 'LED OFF': expected 'ACK' got {res}", end='')
    time.sleep(1)

    # Send an Unknown Command
    res = msp430.write_to_device('BAD CMD')
    assert res == "NACK\n"
    print(f"\tCase CMD = 'BAD CMD': expected 'NACK' got {res}", end='')
    # time.sleep(1)

    # Send a command with a random integer
    rand_int = random.randint(1, 1000)
    rand_str = "RAND%d" % rand_int
    res = msp430.write_to_device(rand_str)
    assert int(res) == rand_int
    print(f"\tCase CMD = '{rand_str}': expected '{rand_int}' got {res}", end='')

    # Test with None
    res = msp430.write_to_device(None)
    assert not res
    print(f"\tCase CMD = None: expected 'False' got '{res}' ")
   # time.sleep(1)


def test_disconnect_from_port():
    # try disconnect from an existing port, should pass
    res = msp430.disconnect_from_port()
    assert res
    print(f"\n\tCase existing port: expected 'True' got {res}")
    # try disconnect from a non-existing port, should fail
    res = msp430.disconnect_from_port()
    print(f"\n\tCase non-existing port: expected 'False' got {res}")
    assert not res
