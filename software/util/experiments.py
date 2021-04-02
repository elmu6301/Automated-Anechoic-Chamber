# Include
import pydoc
import os
import json
from drivers import MSP430_usb as usb
from drivers import VNA_gpib as vna

'''
experiments.py
This file contains functions generate commands and run various experiments.
'''
div = 2
steps_per_degree = 4494400 #9144000
polarization_amt = 90


def degrees_to_steps(degree):
    return int((steps_per_degree*float(degree))/360)


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
    cmd_str = "MOVE:PHI:"+dir+ '%d' % (abs(rel_phi))
    test_cmds += [cmd_str] * samples

    # TODO Generate gpib commands
    # gpib_cmds.append('TODO')

    cmds = {"type": "sweepPhi", "test": test_cmds, "probe": probe_cmds, "gpib": gpib_cmds}
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
    cmd_str = "MOVE:THETA:" + dir + '%d' % (abs(rel_theta))
    test_cmds += [cmd_str] * samples

    # TODO Generate gpib commands
    # gpib_cmds.append('TODO')

    cmds = {"type": "sweepTheta", "test": test_cmds, "probe": probe_cmds, "gpib": gpib_cmds}
    return cmds, phi_offset, end_angle


def gen_sweepFreq_cmds(start_phi, start_theta, orients, freq):
    test_cmds = []
    probe_cmds = []
    gpib_cmds = []

    # Generate gpib commands
    num_points = 0
    if len(freq) != 3:
        return False
    if not freq[0].endswith(" GHz") and not freq[0].endswith(" MHz"):
        return False
    if not freq[1].endswith(" GHz") and not freq[1].endswith(" MHz"):
        return False
    try:
        num_points = int(freq[2])
        if num_points not in vna.allowed_num_points:
            min_diff = abs(vna.allowed_num_points[0] - num_points)
            for point in vna.allowed_num_points:
                min_diff = min(min_diff, abs(point - num_points))
            if min_diff+num_points in vna.allowed_num_points:
                num_points = min_diff+num_points
            else:
                num_points = num_points - min_diff
            return num_points
    except ValueError:
        return False
    # TODO add checks for valid number of points
    gpib_cmds.append({"startF": freq[0], "stopF": freq[1], "num_points": num_points})

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
        test_cmds.append(t_cmd)

        if relPhi < 0:
            t_cmd = "MOVE:THETA:CW:"
        else:
            t_cmd = "MOVE:THETA:CC:"
        t_cmd += '%d' % (abs(degrees_to_steps(relTheta)))
        # Add command to test commands
        test_cmds.append(t_cmd)
        # update previous angles
        prevPhi = phi
        prevTheta = theta

    # Polarization
    p_cmd = len(test_cmds)
    # print("p_cmd = {}",p_cmd)
    probe_cmds.append(p_cmd)
    p_cmd = "MOVE:THETA:CC:" + '%d' % (abs(degrees_to_steps(polarization_amt)))
    probe_cmds.append(p_cmd)
    test_cmds += test_cmds.copy()

    cmds = {"type": "sweepFreq", "test": test_cmds, "probe": probe_cmds, "gpib": gpib_cmds}
    return cmds, prevPhi, prevTheta


def run_sweepFreq(devices, vna, t_cmds, p_cmds, g_cmds):
    test_dev = devices[0]
    probe_dev = devices[0]
    data_out = []
    if len(devices) == 2:
        probe_dev = devices[1]

    # Configure VNA start and stop frequency and number of points
    vna_cfg_cmds = g_cmds[0]
    # vna.init_freq_sweep(vna_cfg_cmds['startF'], vna_cfg_cmds['stopF'])  # Set start and stop freq
    # TODO add call to set the number of points

    # Setup loop control variables
    polarziation_pnt = p_cmds[0]
    pi, gi = 1, 1
    done = False

    # Send out commands
    for ti in range(len(t_cmds)-1):
        # Check for polarization request
        if polarziation_pnt == ti:
            polar_cmd = p_cmds[pi]
            pi += 1
            print(f"[{ti}] Sending {polar_cmd} to PROBE DEV...")

            res, resp = probe_dev.write_to_device(polar_cmd)  # polarization
            if not res or resp != polar_cmd:
                return False, polar_cmd, resp

        # Test side commands
        phi_cmd = t_cmds[ti]
        theta_cmd = t_cmds[ti+1]
        print(f"[{ti}] Sending {phi_cmd} to TEST DEV...")
        res, resp = test_dev.write_to_device(phi_cmd)  # phi
        if not res or resp != phi_cmd:
            return False, phi_cmd, resp
        print(f"[{ti+1}] Sending {theta_cmd} to TEST DEV...")
        res, resp = test_dev.write_to_device(theta_cmd)  # theta
        if not res or resp != theta_cmd:
            return False, theta_cmd, resp

        # Collect Data
        # print(f"Triggering measurement on the VNA\n")
        # data = vna.sparam_data(0)
        # data_out.append(data)

        # Update loop control variables
        ti += 2
    return True, True, True


def run_sweepPhi(devices, t_cmds, p_cmds, g_cmds):
    return True, True, True


def run_sweepTheta(devices, t_cmds, p_cmds, g_cmds):
    return True, True, True


# main
def main():
    print("Experiments!!!")
    # cmds = gen_sweepPhi_cmds(360,180,-10,10,1.4)
    # cmds = gen_sweepTheta_cmds(360, 180, -10, 10, 1.4)
    # cmds = gen_sweepFreq_cmds(100,100,[[100,100],[0,0], [100,100]], [100])
    # print(f"Final orientation: {cmds[1]},{cmds[2]}")
    # print(cmds[0])
    # for cmd in cmds.get("test"):
    #     print(cmd)
    # test = usb.MSP430("COM1", "Eval Board", open=True)


if __name__ == "__main__":
    main()
