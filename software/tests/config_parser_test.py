import pytest
from utils import config_parser as cfg
import time
import random


def test_get_path():
    path = cfg.get_root_path()
    assert path.endswith("Automated-Anechoic-Chamber\\software")


def test_find_config():
    file_name = "sample_exp.json"
    file_path = cfg.find_config(file_name)
    print(f"\nFile '{file_name}' found at {file_path}")
    assert True


def test_get_expt_flow():

    # Existing file input
    file_name = "sample_exp.json"
    flow = cfg.get_expt_flow(file_name)
    assert flow

    file_path = cfg.find_config(file_name)
    flow = cfg.get_expt_flow(file_path)
    assert flow


def test_gen_expt_cmds():
    file_name = "sample_exp.json"
    flow = cfg.get_expt_flow(file_name)
    cmds = cfg.gen_expt_cmds(flow)
    assert cmds
    r_cmds = cmds[0]
    assert r_cmds