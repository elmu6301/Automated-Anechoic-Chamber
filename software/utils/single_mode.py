
import numpy as np
import time
from utils import error_codes
from utils.util import printf
from drivers.motor_driver_interface import getMotorDriverComPorts, MotorDriver

SPR = {
    'test phi': 9142000,
    'test theta': 4494000,
    'probe phi': 4494000}

def angleToSteps(angle, motor):
    assert motor in ['test phi', 'test theta', 'probe phi']
    angle = np.mod(angle+180, 360)-180
    return int(SPR[motor]*(angle/360.))
def stepsToAngle(steps, motor):
    assert motor in ['test phi', 'test theta', 'probe phi']
    return np.mod((360.*(float(steps)/SPR[motor])) + 180, 360) - 180

def initMotorDriver(motor):
    assert motor in ['test phi', 'test theta', 'probe phi']
    ports = getMotorDriverComPorts()
    if motor=='test phi' or motor=='test theta':
        for port in ports:
            MD = MotorDriver(port.name)
            identity = MD.getId()
            if identity == 'TEST':
                return MD
            else:
                del MD
        return error_codes.CONNECTION_TEST
    elif motor == 'probe phi':
        for port in ports:
            MD = MotorDriver(port.name)
            identity = MD.getId()
            if identity == 'PROBE':
                return MD
            else:
                del MD
        return error_codes.CONNECTION_PROBE

def getCurrentAngle(MD, motor):
    assert motor in ['test phi', 'test theta', 'probe phi']
    current_steps = MD.getOrientation('theta' if motor=='test theta' else 'phi', 'current')
    assert current_steps != None
    aligned_steps = MD.getOrientation('theta' if motor=='test theta' else 'phi', 'aligned')
    assert aligned_steps != None
    current_angle = stepsToAngle(current_steps-aligned_steps, motor)
    current_angle = np.mod(current_angle+180, 360)-180
    return current_angle
def rotateMotorAbs(angle, motor, direction, grad_accel):
    printf('Setup', None, 'Parsing arguments...')
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
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Setup', None, 'Calculating steps to rotate...')
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
    printf('Setup', None, 'Parsing arguments...')
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
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Setup', None, 'Calculating steps to rotate...')
    num_steps = angleToSteps(angle, motor)
    if num_steps<0:
        num_steps = np.abs(num_steps)
        direction = 'cw' if direction=='ccw' else 'ccw'
    printf('Setup', None, '\tDone.')
    printf('Setup', None, '\tRotating by %f-degree increment through %d-step %s offset from current orientation.'%(np.abs(angle), np.abs(num_steps), direction))
    printf('Running', None, 'Starting motor rotation...')
    t0 = time.time()
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
    printf('Setup', None, 'Parsing arguments...')
    try:
        assert motor in ['test phi', 'test theta', 'probe phi']
        printf('Setup', None, '\tDone.')
        printf('Setup', None, '\tMotor: '+motor)
        printf('Setup', None, 'Detecting motor drivers...')
        MD = initMotorDriver(motor)
    except:
        return error_codes.BAD_ARGS
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Running', None, 'Reading current angle...')
    try:
        current_angle = MD.getOrientation('theta' if motor=='test theta' else 'phi', 'current')
    except:
        return error_codes.CALIBRATION
    printf('Running', None, '\tDone.')
    printf('Running', None, 'Updating 0 angle...')
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
    printf('Setup', None, 'Parsing arguments...')
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
    if MD == error_codes.CONNECTION_PROBE or MD==error_codes.CONNECTION_TEST:
        return MD
    printf('Setup', None, '\tDone.')
    printf('Running', None, 'Rotating to end switch...')
    t0 = time.time()
    try:
        error_code = MD.findEndSwitch('theta' if motor=='test theta' else 'phi', direction)
        del MD
        printf('Running', None, '\tDone.')
        printf('Running', None, '\tTime taken: %f seconds.'%(time.time()-t0))
        return error_code
    except:
        del MD
        return error_codes.MISC