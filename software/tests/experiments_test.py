import pytest
from utils import experiments as expt
import time
import random


def test_gen_sweepPhi_cmds():
    # Test Data
    start_angle = 0
    end_angle = 360
    theta_offset = 10
    samples = 10
    freq = 10
    # Generate Commands and Split by tyoe
    res = expt.gen_sweepPhi_cmds(start_angle, end_angle, theta_offset, samples, freq)
    # Check to make sure that we got a result
    assert res
    assert res[1] == end_angle and res[2] == theta_offset
    # Check the commands generated
    r_cmds = res[0]
    r_test = r_cmds.get("test")
    assert len(r_test) == samples + 1


def test_gen_sweepTheta_cmds():
    # Test Data
    start_angle = 0
    end_angle = 360
    phi_offset = 10
    samples = 10
    freq = 10
    # Generate Commands and Split by tyoe
    res = expt.gen_sweepTheta_cmds(start_angle, end_angle, phi_offset, samples, freq)
    # Check to make sure that we got a result
    assert res
    assert res[2] == end_angle and res[1] == phi_offset
    # Check the commands generated
    r_cmds = res[0]
    r_test = r_cmds.get("test")
    assert len(r_test) == samples + 1


def test_gen_sweepFreq_cmds():
    # Test Data
    start_phi = 0
    start_theta = 360
    orientations = [[360,180], [0,180], [0,0]]
    freq = 10
    # Generate Commands and Split by tyoe
    res = expt.gen_sweepFreq_cmds(start_phi, start_theta, orientations, freq)
    # Check to make sure that we got a result
    assert res
    assert res[1] == orientations[2][0] and res[2] == orientations[2][1]
    # Check the commands generated
    r_cmds = res[0]
    r_test = r_cmds.get("test")
    assert len(r_test) == len(orientations)
