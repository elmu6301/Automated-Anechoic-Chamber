# Include
import pydoc
import os
import json
'''
experiments.py
This file contains functions generate commands and run various experiments.
'''


def degrees_to_steps(degree):
    return int((9144000*float(degree))/360)


def steps_to_degrees(steps):
    return int((360*float(steps))/9144000)


def gen_sweepPhi_cmds(start_angle, end_angle, theta_offset, samples, freq):
    test_cmds = []
    probe_cmds = []
    gpib_cmds = []
    # Check inputs
    if samples == 0:
        return False

    # Set up the theta axis
    t_cmd = "MOVE:THETA:"
    if theta_offset < 0:
        t_cmd += 'CW:%d' % (abs(degrees_to_steps(theta_offset)))
    else:
        t_cmd += 'CC:%d' % (abs(degrees_to_steps(theta_offset)))
    test_cmds.append(t_cmd)

    # Compute offset for each sample
    rel_phi = degrees_to_steps(float(end_angle - start_angle)/samples)
    dir = "CC:"
    if rel_phi < 0:
        dir = "CW:"
    # Generate Phi commands
    cmd_str = "MOVE:PHI:"+dir+ '%d' % (abs(degrees_to_steps(abs(rel_phi))))
    test_cmds += [cmd_str] * samples

    # TODO Generate gpib commands
    gpib_cmds.append('TODO')

    cmds = {"test": test_cmds, "probe": probe_cmds, "gpib": gpib_cmds}
    return cmds, end_angle, theta_offset


def gen_sweepTheta_cmds(start_angle, end_angle, phi_offset, samples, freq):
    test_cmds = []
    probe_cmds = []
    gpib_cmds = []
    # Check inputs
    if samples == 0:
        return False

    # Set up the theta axis
    t_cmd = "MOVE:PHI:"
    if phi_offset < 0:
        t_cmd += 'CW:%d' % (abs(degrees_to_steps(phi_offset)))
    else:
        t_cmd += 'CC:%d' % (abs(degrees_to_steps(phi_offset)))
    test_cmds.append(t_cmd)

    # Compute offset for each sample
    rel_theta = degrees_to_steps(float(end_angle - start_angle) / samples)
    dir = "CC:"
    if rel_theta < 0:
        dir = "CW:"
    # Generate Phi commands
    cmd_str = "MOVE:THETA:" + dir + '%d' % (abs(degrees_to_steps(abs(rel_theta))))
    test_cmds += [cmd_str] * samples

    # TODO Generate gpib commands
    gpib_cmds.append('TODO')

    cmds = {"test": test_cmds, "probe": probe_cmds, "gpib": gpib_cmds}
    return cmds, phi_offset, end_angle


def gen_sweepFreq_cmds(start_phi, start_theta, orients, freq=None):
    test_cmds = []
    probe_cmds = []
    gpib_cmds = []

    # Generate usb commands
    prevPhi = start_phi
    prevTheta = start_theta
    for o in orients:
        # Get orientation from user
        phi = int(o[0])
        theta = int(o[1])
        # Compute relative angle
        relPhi = phi - prevPhi
        relTheta = theta - prevTheta
        # Generate command
        t_cmd = ""
        if relPhi < 0:
            t_cmd += "MOVE:PHI:CW:"
        else:
            t_cmd += "MOVE:PHI:CC:"
        t_cmd += '%d' % (abs(degrees_to_steps(relPhi)))
        p_cmd = t_cmd
        if relPhi < 0:
            t_cmd += ";MOVE:THETA:CW:"
        else:
            t_cmd += ";MOVE:THETA:CC:"
        t_cmd += '%d' % (abs(degrees_to_steps(relTheta)))
        # Add command to test commands
        test_cmds.append(t_cmd)
        probe_cmds.append(p_cmd)
        # update previous angles
        prevPhi = phi
        prevTheta = theta
    # TODO Generate gpib commands
    if freq is not None:
        for f in freq:
            gpib_cmds.append('TODO')

    cmds = {"test": test_cmds, "probe": probe_cmds, "gpib": gpib_cmds}
    return cmds, prevPhi, prevTheta


# main
def main():
    print("Experiments!!!")
    # cmds = gen_sweepPhi_cmds(360,180,-10,10,1.4)
    # cmds = gen_sweepTheta_cmds(360, 180, -10, 10, 1.4)
    cmds = gen_sweepFreq_cmds(100,100,[[100,100],[0,0], [100,100]], [100])
    print(f"Final orientation: {cmds[1]},{cmds[2]}")
    print(cmds[0])
    # for cmd in cmds.get("test"):
    #     print(cmd)


if __name__ == "__main__":
    main()