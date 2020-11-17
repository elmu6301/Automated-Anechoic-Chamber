import pytest
from drivers import host_usb
import time
import random

port = 'COM12'


def test_to_usb_str():
    # test with string "LED ON"
    test_str = "LED ON"
    usb_str = host_usb.to_usb_str(test_str)
    expected = b'LED ON\r'
    assert usb_str == expected
    print(f"\n\tCase 'LED ON': expected {expected} got {usb_str}")

    # test with None
    test_str = None
    usb_str = host_usb.to_usb_str(test_str)
    assert usb_str == None
    print(f"\tCase 'None': expected {None} got {usb_str}")


def test_set_orientation():
    #        0    1    2    3     5    5     6     7     8    9
    phi =   [0, 271, 360, None, 271, None, 2710, 271, -271, 271]
    theta = [0, 100, 360, None, None, 100, 100 ,10000, 100, -100]
    # test valid values for phi and theta
    res = host_usb.set_orientation(phi[0], theta[0])
    assert res == "0,0"
    print(f"\n\tCase {phi[0],theta[0]}: expected 0,0 got {res}")

    res = host_usb.set_orientation(phi[1], theta[1])
    assert res == "271,100"
    print(f"\tCase {phi[1],theta[1]}: expected 271,100 got {res}")

    res = host_usb.set_orientation(phi[2], theta[2])
    assert res == "360,360"
    print(f"\tCase {phi[2],theta[2]}: expected 360,360 got {res}")

    # test invalid values for phi and theta
    res = host_usb.set_orientation(phi[3], theta[3])
    assert not res
    print(f"\tCase {phi[3],theta[3]}: expected False got {res}")

    res = host_usb.set_orientation(phi[4], theta[4])
    assert res == "271,1000"
    print(f"\tCase {phi[4],theta[4]}: expected 271,1000 got {res}")

    res = host_usb.set_orientation(phi[5], theta[5])
    assert res == "1000,100"
    print(f"\tCase {phi[5],theta[5]}: expected 1000,100 got {res}")

    res = host_usb.set_orientation(phi[6], theta[6])
    assert res == "1000,100"
    print(f"\tCase {phi[6],theta[6]}: expected 1000,100 got {res}")

    res = host_usb.set_orientation(phi[7], theta[7])
    assert res == "271,1000"
    print(f"\tCase {phi[7],theta[7]}: expected 271,1000 got {res}")

    res = host_usb.set_orientation(phi[8], theta[8])
    assert res == "1000,100"
    print(f"\tCase {phi[8],theta[8]}: expected 1000,100 got {res}")

    res = host_usb.set_orientation(phi[9], theta[9])
    assert res == "271,1000"
    print(f"\tCase {phi[9],theta[9]}: expected 271,1000 got {res}")


def test_connect_to_port():
    baudrate = 9600

    # test connecting to an unopened port
    print("\n\tCase 0: expected COM12 is open got ", end='')
    assert host_usb.connect_to_port(port, baudrate)

    # test connecting to an opened port
    print("\n\tCase 1: expected Could not connect to COM12 got ", end='')
    assert not host_usb.connect_to_port(port, baudrate)

    # test a random port that should not exist
    print("\tCase 2: expected Could not connect to COM27 got ", end='')
    assert not host_usb.connect_to_port('COM27', baudrate)


def test_write_to_device():
    # Test with None
    res = host_usb.write_to_device(None)
    assert not res
    print(f"\n\tCase CMD = None: expected 'False' got '{res}' ")
    # time.sleep(1)

    # Turn the LED ON
    res = host_usb.write_to_device('LED ON')
    assert res == "ACK\n"
    print(f"\tCase CMD = 'LED ON': expected 'ACK' got {res}", end='')
    # time.sleep(3)
#
    # Turn the LED OFF
    res = host_usb.write_to_device('LED OFF')
    assert res == "ACK\n"
    print(f"\tCase CMD = 'LED OFF': expected 'ACK' got {res}", end='')
    # time.sleep(1)
#
    # Send an Unknown Command
    res = host_usb.write_to_device('BAD CMD')
    assert res == "NACK\n"
    print(f"\tCase CMD = 'BAD CMD': expected 'NACK' got {res}", end='')
    # time.sleep(1)

    rand_int = random.randint(1, 1000)
    rand_str = "RAND%d" % rand_int
    res = host_usb.write_to_device(rand_str)
    assert int(res) == rand_int
    print(f"\tCase CMD = '{rand_str}': expected '{rand_int}' got {res}", end='')


def test_disconnect_from_port():
    # try disconnect from an existing port, should pass
    res = host_usb.disconnect_from_port()
    assert res
    print(f"\n\tCase 0: expected 'True' got {res}")
    # try disconnect from a non-existing port, should fail
    print("\tCase 1: ", end='')
    res = host_usb.disconnect_from_port()
    assert not res
    print(f"\n\t        expected 'False' got {res}")
