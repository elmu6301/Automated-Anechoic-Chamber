# Include
import pydoc
import os
import json
'''
experiments.py
This file contains functions generate commands and run various experiments.
'''


def gen_phi_sweep_cmds(start_angle, end_angle, theta_angle, freq, samples):
    cmds = []
    cmd = 'to_%d'% (theta_angle)
    cmds.append(cmd)
    cmd = 'ps_%d_%d_%d' % (start_angle, end_angle, samples)
    cmds.append(cmd)
    for cmd in cmds:
        print(cmd)
    return cmds


def gen_theta_sweep_cmds(start_angle, end_angle, phi_angle, freq, samples):
    cmds = []
    cmd = 'po_%d' % (phi_angle)
    cmds.append(cmd)
    cmd = 'ts_%d_%d_%d' % (start_angle, end_angle, samples)
    cmds.append(cmd)
    for cmd in cmds:
        print(cmd)
    return cmds


# main
def main():
    print("Experiments!!!")
    cmds = gen_phi_sweep_cmds(0,180,90,1.4,1000)
    cmds = gen_theta_sweep_cmds(0,180,90,1.4,1000)

if __name__ == "__main__":
    main()
