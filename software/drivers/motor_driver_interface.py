# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))

import serial
import serial.tools.list_ports
import time
from utils import error_codes

CMDDELIM = '\n'
ARGDELIM = ':'
QUERY    = '?'
ACK      = 'a'
NACK     = 'nack'
IDEN     = 'IDEN'
ALIGN    = 'ALIGN'
WLASER   = 'WLASER'
RSENSOR  = 'RSENSOR'
RASSERT  = 'RASSERT'
INVBSL   = 'INVBSL'
MOVE     = 'MOVE'
FREQ     = 'FREQ'
ORIENT   = 'ORIENTATION'
ABORT    = 'ABORT'


def getMotorDriverComPorts(vid=0x2047, pid=0x3Df):
    """
    Gets the comports of the associated motor drivers.
    """
    ports = []
    for candidate in serial.tools.list_ports.comports():
        if (candidate.vid==vid) and (candidate.pid == pid):
            ports.append(candidate)
    return ports
    
def findSystemMotorDrivers():
    """
    Connects to the test and probe motor divers.
    :return: An error code indicating success or failure.
    """
    ports = getMotorDriverComPorts()
    if len(ports) == 0:
        return {'error code': error_codes.CONNECTION}
    Test_MD  = None
    Probe_MD = None
    for port in ports:
        try:
            MD = MotorDriver(port.name)
            identity = MD.getId()
            if identity == 'TEST':
                Test_MD = MD
            elif identity == 'PROBE':
                Probe_MD = MD
            else:
                assert False
        except:
            pass
    if (Test_MD == None) and (Probe_MD == None):
        return {'error code': error_codes.CONNECTION}
    elif Test_MD == None:
        del Probe_MD
        if len(ports) == 2:
            return {'error code': error_codes.DISTINCT_IDS}
        else:
            return {'error code': error_codes.CONNECTION_TEST}
    elif Probe_MD == None:
        del Test_MD
        if len(ports) == 2:
            return {'error code': error_codes.DISTINCT_IDS}
        else:
            return {'error code': error_codes.CONNECTION_PROBE}
    return {'test motor driver':  Test_MD,
            'probe motor driver': Probe_MD,
            'error code':         error_codes.SUCCESS}

class MotorDriver:
    """
        Motor driver class.

        Used to communicate with the custom PCBs via USB.
    """
    def __init__(self, port,
                 debug=False,
                 baudrate=9600,
                 bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE):
        self.ser = serial.Serial(port=port,
                                 baudrate=baudrate,
                                 bytesize=bytesize,
                                 parity=parity,
                                 stopbits=stopbits)
        self.debug = debug

    def __del__(self):
        try:
            self.ser.close()
        except:
            pass

    def _txCmd(self, args):
        """
        Sends a command.
        :param args: Command to send.
        :return: Command that was sent.
        """
        assert type(args)==list
        assert len(args)>=1
        msg = ARGDELIM.join(args)+CMDDELIM
        self.ser.write(msg.encode('ASCII'))
        return msg[:-1]

    def _rxCmd(self):
        """
        Listens for a message from the PCB.
        :return: Message that was received.
        """
        msg = []
        try:
            while (len(msg)==0) or (msg[-1] != CMDDELIM):
                while self.ser.in_waiting == 0:
                    pass
                msg.append(self.ser.read().decode('ASCII'))
        finally:
            if self.debug:
                print(msg)
        msg = ''.join(msg)
        return msg[:-1]

    def getId(self):
        """
        Gets the device side ID (TEST or PROBE).
        :return: Device identification.
        """
        args = [IDEN]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return rv

    def getAssertInfo(self):
        """
        Gets assertion failure information.
        :return: Returns the file, line, and condition of an assert statement in the firmware that failed.
        """
        args = [RASSERT]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = []
        for i in range(3):
            rv.append(self._rxCmd())
        assert self._rxCmd() == cmd
        return {'File': rv[0], 'Condition': rv[1], 'Line': int(rv[2])}

    def invokeBsl(self):
        """
        Invokes BSL.
        :return:
        """
        args = [INVBSL]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd

    def writeLaser(self, state):
        """
        Writes to the laser to turn it off or on.
        :param state: State to set the laser to.
        """
        args = [WLASER]
        args.append('ON' if state else 'OFF')
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd

    def readSensor(self):
        """
        Reads sensor.
        :return: Value of the sensor
        """
        args = [RSENSOR]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return int(rv)

    def abort(self, motor):
        """
        Aborts a command.
        :param motor: Motor driver to abort.
        :return: An error code indicating success or failure.
        """
        try:
            assert motor in ['theta', 'phi']
        except:
            return error_codes.BAD_ARGS
        args = [ABORT]
        args.append('PHI' if motor=='phi' else 'THETA')
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        if rv == cmd:
            return error_codes.SUCCESS
        else:
            return error_codes.MISC

    def turnMotor(self, motor, num_steps, direction, gradual=False):
        """
        Moves the motor a number of steps in given direction.
        :param motor: Motor to turn.
        :param num_steps: Number of steps to move by.
        :param direction: Direction to move.
        :param gradual: Move gradually or not.
        :return: An error code indicating success or failure.
        """
        try:
            assert motor in ['theta', 'phi']
            assert type(num_steps) == int
            assert num_steps == num_steps&0xFFFFFFFF
            assert direction in ['cw', 'ccw']
            assert type(gradual) == bool
        except:
            return error_codes.BAD_ARGS
        args = [MOVE]
        args.append('PHI' if motor=='phi' else 'THETA')
        args.append('CW' if direction=='cw' else 'CC')
        args.append('GRADUAL' if gradual else 'JUMP')
        args.append('%d'%(num_steps))
        cmd = self._txCmd(args)
        try:
            assert self._rxCmd() == ACK
            rv = self._rxCmd()
            if rv == cmd:
                return error_codes.SUCCESS
            else:
                return error_codes.MISC
        except KeyboardInterrupt:
            self.abort(motor)
            return error_codes.STOPPED

    def findEndSwitch(self, motor, direction, gradual=False):
        """
        Finds the end-switch of motor by looking in the given direction.
        :param motor: Motor to find end-switch of.
        :param direction: Direction to look for end-switch
        :param gradual: Determines if the motor should move gradually or not.
        :return: An error code indicating success or failure.
        """
        try:
            assert motor in ['theta', 'phi']
            assert direction in ['cw', 'ccw']
            assert type(gradual) == bool
        except:
            return error_codes.BAD_ARGS
        args = [ALIGN]
        args.append('PHI' if motor=='phi' else 'THETA')
        args.append('CW' if direction=='cw' else 'CC')
        args.append('GRADUAL' if gradual else 'JUMP')
        cmd = self._txCmd(args)
        try:
            assert self._rxCmd() == ACK
            rv = self._rxCmd()
            if rv == cmd:
                return error_codes.SUCCESS
            else:
                return error_codes.MISC
        except KeyboardInterrupt:
            self.abort(motor)
            return error_codes.STOPPED

    def getFreq(self, motor):
        """
        Gets the frequency of the motor.
        :param motor: Motor to query.
        :return: Frequency of the motor
        """
        assert motor in ['theta', 'phi']
        args = [FREQ]
        args.append(('PHI' if motor=='phi' else 'THETA')+QUERY)
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return int(rv)

    def setFreq(self, motor, freq):
        """
        Sets the frequency of a motor
        :param motor: Motor to set frequency.
        :param freq: Frequency to use.
        :return:
        """
        assert motor in ['theta', 'phi']
        assert type(freq) == int
        assert freq == freq&0xFFFFFFFF
        args = [FREQ]
        args.append('PHI' if motor=='phi' else 'THETA')
        args.append('%d'%(freq))
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd

    def setAlignedOrientation(self, theta, phi):
        """
        Sets the aligned orientation.
        :param theta: Theta angle of the aligned orientation.
        :param phi: Phi angle of the aligned orientation.
        :return:
        """
        assert type(theta) == int
        assert 0 <= abs(theta) < 0xFFFFFFFF
        assert type(phi) == int
        assert 0 <= abs(phi) < 0xFFFFFFFF
        args = [ORIENT]
        args.append('THETA')
        args.append('ALIGNED')
        args.append('%d'%(theta))
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd
        args = [ORIENT]
        args.append('PHI')
        args.append('ALIGNED')
        args.append('%d'%(phi))
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd

    def getOrientation(self, motor, info):
        """
        Gets current or aligned orientation.
        :param motor: Motor to query
        :param info: Specifies whether to collect current or aligned orientation.
        :return:
        """
        assert motor in ['theta', 'phi']
        assert info in ['aligned', 'current']
        args = [ORIENT]
        args.append('THETA' if motor=='theta' else 'PHI')
        args.append(('ALIGNED' if info=='aligned' else 'CURRENT')+QUERY)
        cmd = self._txCmd(args)
        rv = self._rxCmd()
        if rv == NACK:
            return None
        assert rv == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return int(rv)

    def align(self, motor, gradual=False):
        """
        Alings a motor.
        :param motor: Motor to align
        :param gradual: Whether to use move gradually or not.
        :return:
        """
        try:
            assert motor in ['theta', 'phi']
        except:
            return error_codes.BAD_ARGS
        align_offset = self.getOrientation(motor, 'aligned')
        if align_offset == None:
            print('Must calibrate system')
            return error_codes.MISC
        orientation = self.getOrientation(motor, 'current')
        if orientation != None:
            direction = 'cw' if orientation<0 else 'ccw'
        else:
            direction = 'cw'
        error_code = self.findEndSwitch(motor, direction, gradual=False)
        if error_code != error_codes.SUCCESS:
            return error_code
        direction = 'ccw' if align_offset<0 else 'cw'
        error_code = self.turnMotor(motor, abs(align_offset), direction, gradual=gradual)
        return error_code