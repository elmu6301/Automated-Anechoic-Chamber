# Include
import pydoc
import os
import json
'''
config_parser.py
This file contains functions to find, open, and.
'''


def get_path():
    return True


def find_config():
    assert True


def get_expt_flow():
    assert True


def gen_expt_cmds():
    assert True


def find_config1(file_name,file_path):
    # Check to see if file_name is valid
    if file_name is None or file_name == '':
        print("Error: No config file detected...")
    elif file_name.endswith(".json") is False:
        print("Error: Config file must be a json file...")
    # find the file
    cfg = open(file_name, "r")


# main
def main():

    print("\nRunning the config parser")

    # Testing reading/loading ability
    data = None
    flow = None
    with open("../configs/sample_exp.json", "r") as file:
        data = json.load(file)
        flow = data.get("flow")
        print(flow)
    if data is None:
        print("Could not find/load file...")
    # else:
    #     print(data)

    # Testing data parsing
    for expt in flow:
        print("Found experiment: "+expt.get("expType"))


if __name__ == "__main__":
    main()
