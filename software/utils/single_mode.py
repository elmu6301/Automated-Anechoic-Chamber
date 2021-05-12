
import numpy as np
import time
from utils import error_codes
from utils.util import printf
from drivers.motor_driver_interface import getMotorDriverComPorts, MotorDriver

# Number of steps per 360 degree rotation for the following motors
SPR = {
    'test phi': 9142000,
    'test theta': 4494000,
    'probe phi': 4494000}

def angleToSteps(angle, motor):
    """
    Converts an angle to the corresponding number of steps
    :param angle The angle to convert
    :param motor Which motor to convert for -- see below for valid values
    :return Number of steps
    """
    # Verify validity of arguments.
    assert motor in ['test phi', 'test theta', 'probe phi']
    # Calculate angle.
    angle = np.mod(angle+180, 360)-180
    return int(SPR[motor]*(angle/360.))
def stepsToAngle(steps, motor):
    """
    Converts a number of steps to the corresponding angle
    :param steps The number of steps
    :param motor Which motor to convert for -- see below for valid values
    :return Angle corresponding to input number of steps.
    """
    # Verify validity of arguments.
    assert motor in ['test phi', 'test theta', 'probe phi']
    # Calculate steps.
    return np.mod((360.*(float(steps)/SPR[motor])) + 180, 360) - 180

def initMotorDriver(motor):
    """
    Finds a USB motor driver for the selected motor.
    :param motor Which motor/orientation to find device for -- see below for valid values.
    :return Either the motor driver, or an error indicating that it failed to find that motor driver.
    """
    # Verify validity of arguments.
    assert motor in ['test phi', 'test theta', 'probe phi']
    # Get list of motor driver devices attached to computer.
    ports = getMotorDriverComPorts()
    if motor=='test phi' or motor=='test theta':
        # Find a test-side motor driver device.
        for port in ports:
            MD = MotorDriver(port.name)
            identity = MD.getId()
            if identity == 'TEST':
                return MD
            else:
                del MD
        # None found.
        return error_codes.CONNECTION_TEST
    elif motor == 'probe phi':
        # Find a probe-side motor driver device.
        for port in ports:
            MD = MotorDriver(port.name)
            identity = MD.getId()
            if identity == 'PROBE':
                return MD
            else:
                del MD
        # None found.
        return error_codes.CONNECTION_PROBE

def getCurrentAngle(MD, motor):
    """
    Returns current angle of selected motor.
    :param MD Motor driver class for this motor.
    :param motor Which motor to find angle for -- see below for valid values.
    :return Angle of the selected motor.
    """
    # Verify validity of arguments.
    assert motor in ['test phi', 'test theta', 'probe phi']
    # Check whether current orientation is valid in flash.
    current_steps = MD.getOrientation('theta' if motor=='test theta' else 'phi', 'current')
    assert current_steps != None
    # Check whether aligned orientation is valid in flash.
    aligned_steps = MD.getOrientation('theta' if motor=='test theta' else 'phi', 'aligned')
    assert aligned_steps != None
    # Aligned orientation is 0; use this to calculate current angle.
    current_angle = stepsToAngle(current_steps-aligned_steps, motor)
    current_angle = np.mod(current_angle+180, 360)-180
    return current_angle
def rotateMotorAbs(angle, motor, direction, grad_accel):
    """
    Rotates the selected motor to an absolute angle.
    :param angle The angle to which to rotate the motor.
    :param motor Which motor to rotate -- see below for valid values.
    :param direction Which direction in which to rotate the motor -- see below for valid values.
    :param grad_accel Whether or not to accelerate motor gradually (true for yes).
    :return Error code indicating whether or not it was successful.
    """
    printf('Setup', None, 'Parsing arguments...')
    # Parse arguments and verify that they are valid.
    try:
        assert motor in ['test phi', 'test theta', 'probe phi']
        assert direction in ['cw', 'ccw']
        assert grad_accel in [True, False]
        assert type(angle) == float
        printf('Setup', None, '\tDone.')
        printf('Setup', None, '\tMotor: '+motor)
        printf('Setup', None, '\tDirection: '+direction)
        printf('Setup', None, '\tGradual acceleration: '+str(grad_accel))
        printf('Setup', None, 'Detecting motor drivers...')
        MD = initMotorDriver(motor)
    except:
        return error_codes.BAD_ARGS
    # Determine whether or not the desired USB device was attached to the computer.
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Setup', None, 'Calculating steps to rotate...')
    # Calculate the angle by which we need to rotate.
    angle = np.mod(angle+180, 360)-180
    try:
        current_angle = getCurrentAngle(MD, motor)
    except:
        return error_codes.CALIBRATION
    num_steps = angleToSteps(angle-current_angle, motor)
    if direction=='cw' and num_steps<0:
        num_steps += SPR[motor]
    elif direction=='ccw' and num_steps>0:
        num_steps -= SPR[motor]
    printf('Setup', None, '\tDone.')
    printf('Setup', None, '\tRotating to %f degrees through %d-step %s offset from current orientation.'%(angle, np.abs(num_steps), direction))
    printf('Running', None, 'Starting motor rotation...')
    t0 = time.time()
    # Rotate the motor.
    try:
        error_code = MD.turnMotor('theta' if motor=='test theta' else 'phi', int(np.abs(num_steps)), direction, grad_accel)
        printf('Running', None, '\tDone.')
        printf('Running', None, '\tTime taken: %f seconds.'%(time.time()-t0))
        del MD
        return error_code
    except:
        del MD
        return error_codes.MISC
def rotateMotorInc(angle, motor, direction, grad_accel):
    """
    Rotate the given motor to the selected angle relative to the current angle.
    :param angle The angle by which to rotate the motor.
    :motor Which motor to rotate -- see below for valid values.
    :direction Which direction in which to rotate the motor -- see below for valid values.
    :param grad_accel Whether or not to accelerate the motor gradually (True for yes).
    :return Error code indicating whether it was successful or not.
    """
    printf('Setup', None, 'Parsing arguments...')
    # Parse arguments and verify that they are valid.
    try:
        assert motor in ['test phi', 'test theta', 'probe phi']
        assert direction in ['cw', 'ccw']
        assert grad_accel in [True, False]
        assert type(angle) == float
        printf('Setup', None, '\tDone.')
        printf('Setup', None, '\tMotor: '+motor)
        printf('Setup', None, '\tDirection: '+direction)
        printf('Setup', None, '\tGradual acceleration: '+str(grad_accel))
        printf('Setup', None, 'Detecting motor drivers...')
        MD = initMotorDriver(motor)
    except:
        return error_codes.BAD_ARGS
    # Determine whether or not we found the desired USB device attached to the computer.
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Setup', None, 'Calculating steps to rotate...')
    # Calculate the number of steps by which to rotate.
    num_steps = angleToSteps(angle, motor)
    if num_steps<0:
        num_steps = np.abs(num_steps)
        direction = 'cw' if direction=='ccw' else 'ccw'
    printf('Setup', None, '\tDone.')
    printf('Setup', None, '\tRotating by %f-degree increment through %d-step %s offset from current orientation.'%(np.abs(angle), np.abs(num_steps), direction))
    printf('Running', None, 'Starting motor rotation...')
    t0 = time.time()
    # Rotate the motor.
    try:
        error_code = MD.turnMotor('theta' if motor=='test theta' else 'phi', num_steps, direction, grad_accel)
        del MD
        printf('Running', None, '\tDone.')
        printf('Running', None, '\tTime taken: %f seconds.'%(time.time()-t0))
        return error_code
    except:
        del MD
        return error_codes.MISC
def zeroCurrentAngle(motor):
    """
    Programs the current angle to 0 in flash memory for the selected device.
    :param motor Which motor to configure -- see below for valid values.
    :return Error code indicating whether or not it was successful.
    """
    printf('Setup', None, 'Parsing arguments...')
    # Parse arguments and verify that they are valid.
    try:
        assert motor in ['test phi', 'test theta', 'probe phi']
        printf('Setup', None, '\tDone.')
        printf('Setup', None, '\tMotor: '+motor)
        printf('Setup', None, 'Detecting motor drivers...')
        MD = initMotorDriver(motor)
    except:
        return error_codes.BAD_ARGS
    # Determine whether or not we found the desired USB device attached to the computer.
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Running', None, 'Reading current angle...')
    # Read the current angle of the device.
    try:
        current_angle = MD.getOrientation('theta' if motor=='test theta' else 'phi', 'current')
    except:
        return error_codes.CALIBRATION
    printf('Running', None, '\tDone.')
    printf('Running', None, 'Updating 0 angle...')
    # Program the current angle to be the aligned angle (0).
    try:
        if motor=='test theta':
            MD.setAlignedOrientation(theta=current_angle)
        else:
            MD.setAlignedOrientation(phi=current_angle)
        del MD
        printf('Running', None, '\tDone.')
        return error_codes.SUCCESS
    except:
        del MD
        return error_codes.MISC    
def alignMotor(motor, direction):
    """
    Rotates the selected motor to its end switch.
    :param motor Which motor to rotate -- see below for valid values.
    :param direction Which direction to initially look for the end switch in -- see below for valid values.
    :return Error code indicating whether or not it was successful.
    """
    printf('Setup', None, 'Parsing arguments...')
    # Parse arguments and verify that they are valid.
    try:
        assert motor in ['test phi', 'test theta', 'probe phi']
        assert direction in ['cw', 'ccw']
        printf('Setup', None, '\tDone.')
        printf('Setup', None, '\tMotor: '+motor)
        printf('Setup', None, '\tDirection: '+direction)
        printf('Setup', None, 'Detecting motor drivers...')
        MD = initMotorDriver(motor)
    except:
        return error_codes.BAD_ARGS
    # Determine whether or not we found the desired USB device attached to the computer.
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Running', None, 'Rotating to end switch...')
    t0 = time.time()
    # Rotate the motor to the end switch.
    try:
        error_code = MD.findEndSwitch('theta' if motor=='test theta' else 'phi', direction)
        del MD
        printf('Running', None, '\tDone.')
        printf('Running', None, '\tTime taken: %f seconds.'%(time.time()-t0))
        return error_code
    except:
        del MD
        return error_codes.MISC