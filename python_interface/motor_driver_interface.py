# -*- coding: utf-8 -*-

import serial
import time

TERM_CHAR = '\n'
ACK_CHAR = 'a'
DONE_CHAR = 'd'

TURNMOTOR_CMD = '0'
ALIGNMOTOR_CMD = '1'
WRITELASER_CMD = '2'
READSENSOR_CMD = '3'
REPORTSTATUS_CMD = '4'
CHECKASSERTINFO_CMD = '5'
INVOKEBSL_CMD = '6'

THETA_MSG = '0'
PHI_MSG = '1'

CW_MSG = '0'
CCW_MSG = '1'

LASEROFF_MSG = '0'
LASERON_MSG = '1'

class MotorDriver:
    def __init__(self, port,
                 baudrate=9600,
                 bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE):
        self.ser = serial.Serial(port=port,
                                 baudrate=baudrate,
                                 bytesize=bytesize,
                                 parity=parity,
                                 stopbits=stopbits)
    def __del__(self):
        try:
            self.ser.close()
        except:
            pass
    def _transmitMsg(self, msg):
        msg = msg+TERM_CHAR
        msg = msg.encode()
        self.ser.write(msg)
    def _nextMsg(self):
        msg = []
        while (len(msg) == 0) or (msg[-1] != TERM_CHAR):
            while self.ser.in_waiting == 0:
                pass
            msg.append(self.ser.read().decode('ascii'))
        msg = ''.join(msg)
        return msg[:-1]
    def turnMotor(self, motor, num_steps, direction):
        assert motor in ['theta', 'phi']
        assert type(num_steps) == int
        assert num_steps == num_steps&0xFFFFFFFF
        assert direction in ['cw', 'ccw']
        msg = []
        msg.append(TURNMOTOR_CMD)
        if motor == 'theta':
            msg.append(THETA_MSG)
        else:
            msg.append(PHI_MSG)
        msg += '%010d'%(num_steps)
        if direction == 'cw':
            msg.append(CW_MSG)
        else:
            msg.append(CCW_MSG)
        self._transmitMsg(''.join(msg))
        print('sent message', ''.join(msg))
        t_0 = time.time()
        rv = self._nextMsg()
        assert rv == ACK_CHAR
        print('acked')
        rv = self._nextMsg()
        assert rv == DONE_CHAR
        print('done')
        print('Time taken:', time.time()-t_0)
    def startTurnMotor(self, motor, num_steps, direction):
        assert motor in ['theta', 'phi']
        assert type(num_steps) == int
        assert num_steps == num_steps&0xFFFFFFFF
        assert direction in ['cw', 'ccw']
        msg = []
        msg.append(TURNMOTOR_CMD)
        if motor == 'theta':
            msg.append(THETA_MSG)
        else:
            msg.append(PHI_MSG)
        msg += '%010d'%(num_steps)
        if direction == 'cw':
            msg.append(CW_MSG)
        else:
            msg.append(CCW_MSG)
        self._transmitMsg(''.join(msg))
        print('sent message', ''.join(msg))
        rv = self._nextMsg()
        assert rv == ACK_CHAR
        print('acked')
    def waitForDone(self):
        assert self._nextMsg()  == DONE_CHAR
        print('done')
    def alignMotor(self, motor):
        assert motor in ['theta', 'phi']
        msg = []
        msg.append(ALIGNMOTOR_CMD)
        if motor == 'theta':
            msg.append(THETA_MSG)
        else:
            msg.append(PHI_MSG)
        self._transmitMsg(''.join(msg))
        rv = self._nextMsg()
        assert rv == ACK_CHAR
        rv = self._nextMsg()
        assert rv == DONE_CHAR
    def writeLaser(self, state):
        assert state in [True, False]
        msg = []
        msg.append(WRITELASER_CMD)
        if state:
            msg.append(LASERON_MSG)
        else:
            msg.append(LASEROFF_MSG)
        self._transmitMsg(''.join(msg))
        print('Wrote message')
        rv = self._nextMsg()
        assert rv == ACK_CHAR
        print('Acked')
        rv = self._nextMsg()
        assert rv == DONE_CHAR
        print('Done')
    def readSensor(self):
        msg = []
        msg.append(READSENSOR_CMD)
        self._transmitMsg(''.join(msg))
        print('Wrote message')
        rv = self._nextMsg()
        assert rv == ACK_CHAR
        print('Acked')
        rv = self._nextMsg()
        assert rv[-1] == DONE_CHAR
        print('Done')
        return int(rv[:-1])
    def checkAssertInfo(self):
        msg = []
        msg.append(CHECKASSERTINFO_CMD)
        self._transmitMsg(''.join(msg))
        print('Wrote message')
        assert self._nextMsg() == ACK_CHAR
        print('Acked')
        file = self._nextMsg()
        if file == DONE_CHAR:
            print('No previous ASSERT info saved')
            print('Done')
            return None
        print('File:', file)
        expression = self._nextMsg()
        print('Expression:', expression)
        line = int(self._nextMsg())
        print('Line:', line)
        assert self._nextMsg() == DONE_CHAR
        print('Done')
        return {'File': file, 'Expression': expression, 'Line': line}
    def invokeBsl(self):
        msg = []
        msg.append(INVOKEBSL_CMD)
        self._transmitMsg(''.join(msg))
        print('Wrote message')
        assert self._nextMsg() == ACK_CHAR
        print('Acked')
        assert self._nextMsg() == DONE_CHAR
        print('Done')
        
        
        
        
        
        
        
        
        
        
        
        
        