# -*- coding: utf-8 -*-

import serial
import time
from error_codes import *

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

def getMotorDriverComPorts(pid=0x3Df):
    ports = []
    for candidate in serial.tools.list_ports.comports():
        if candidate.pid == pid:
            ports.append(candidate)
    return ports
    
def findSystemMotorDrivers():
    ports = getMotorDriverPorts()
    if len(ports) != 2:
        return {'error code': ERROR_CODE__MISC}
    Test_MD  = None
    Probe_MD = None
    for port in ports:
        try:
            MD = MotorDriver(port.name)
            identity = MotorDriver.getId()
            if identity == 'TEST':
                Test_MD = MD
            elif identity == 'PROBE':
                Probe_MD = MD
            else:
                assert False
        except:
            return {'error code': ERROR_CODE__CONNECTION}
    if Test_MD == None:
        del Probe_MD
        return {'error code': ERROR_CODE__CONNECTION_TEST}
    if Probe_MD == None:
        del Test_MD
        return {'error code': ERROR_CODE__CONNECTION_PROBE}
    return {'test motor driver':  Test_MD,
            'probe motor driver': Probe_MD,
            'error code':         ERROR_CODE__SUCCESS}

class MotorDriver:
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
        assert type(args)==list
        assert len(args)>=1
        msg = ARGDELIM.join(args)+CMDDELIM
        self.ser.write(msg.encode('ASCII'))
        return msg[:-1]
    def _rxCmd(self):
        msg = []
        while (len(msg)==0) or (msg[-1] != CMDDELIM):
            while self.ser.in_waiting == 0:
                pass
            msg.append(self.ser.read().decode('ASCII'))
        if self.debug:
            print(msg)
        msg = ''.join(msg)
        return msg[:-1]
    def getId(self):
        args = [IDEN]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return rv
    def getAssertInfo(self):
        args = [RASSERT]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = []
        for i in range(3):
            rv.append(self._rxCmd())
        assert self._rxCmd() == cmd
        return {'File': rv[0], 'Condition': rv[1], 'Line': int(rv[2])}
    def invokeBsl(self):
        args = [INVBSL]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd
    def writeLaser(self, state):
        args = [WLASER]
        args.append('ON' if state else 'OFF')
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd
    def readSensor(self):
        args = [RSENSOR]
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return int(rv)
    def turnMotor(self, motor, num_steps, direction, gradual=False):
        assert motor in ['theta', 'phi']
        assert type(num_steps) == int
        assert num_steps == num_steps&0xFFFFFFFF
        assert direction in ['cw', 'ccw']
        assert type(gradual) == bool
        args = [MOVE]
        args.append('PHI' if motor=='phi' else 'THETA')
        args.append('CW' if direction=='cw' else 'CC')
        args.append('GRADUAL' if gradual else 'JUMP')
        args.append('%d'%(num_steps))
        cmd = self._txCmd(args)
        t0 = time.time()
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd
        return time.time()-t0
    def findEndSwitch(self, motor, direction, gradual=False):
        assert motor in ['theta', 'phi']
        assert direction in ['cw', 'ccw']
        assert type(gradual) == bool
        args = [ALIGN]
        args.append('PHI' if motor=='phi' else 'THETA')
        args.append('CW' if direction=='cw' else 'CC')
        args.append('GRADUAL' if gradual else 'JUMP')
        cmd = self._txCmd(args)
        t0 = time.time()
        assert self._rxCmd() == ACK
        assert self._rxCmd() == cmd
        return time.time()-t0
    def getFreq(self, motor):
        assert motor in ['theta', 'phi']
        args = [FREQ]
        args.append(('PHI' if motor=='phi' else 'THETA')+QUERY)
        cmd = self._txCmd(args)
        assert self._rxCmd() == ACK
        rv = self._rxCmd()
        assert self._rxCmd() == cmd
        return int(rv)
    def setFreq(self, motor, freq):
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
    def align(self, motor):
        assert motor in ['theta', 'phi']
        align_offset = self.getOrientation(motor, 'aligned')
        if align_offset == None:
            print('Must calibrate system')
            assert False
        orientation = self.getOrientation(motor, 'current')
        if orientation != None:
            direction = 'cw' if orientation<0 else 'ccw'
        else:
            direction = 'cw'
        self.findEndSwitch(motor, direction)
        direction = 'ccw' if orientation<0 else 'cw'
        self.turnMotor(motor, abs(align_offset), direction)