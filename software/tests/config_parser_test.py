import pytest
from util import config_parser as cfg
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
    cfg.get_expt_flow()
    assert True


def test_gen_expt_cmds():
    cfg.gen_expt_cmds()
    assert True