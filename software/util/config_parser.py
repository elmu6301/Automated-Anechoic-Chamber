# Include
import pydoc
import os
import json
'''
config_parser.py
This file contains functions to find, open, and.
'''

root_base = "software"
config_base = "\\configs"
allowed_expt = ("sweepPhi", "sweepTheta", "sweepFreq")


# Gets the path to the repository
def get_root_path():
    path = os.getcwd()
    if path.rfind(root_base) == -1:
        return False
    while not path.endswith(root_base):
        os.chdir("..")
        path = os.getcwd()
    return path


# Attempts to locate the file and returns the full file path if possible
def find_config(file_name, file_path=None):
    full_name = ''

    # Check to see if name is valid
    if file_name is None or file_name == '':
        print("Error: No config file detected...")
        return False
    elif file_name.endswith(".json") is False:
        print("Error: Config file must be a json file...")
        return False

    # Get the root path
    root_path = get_root_path()
    config_repo_path = root_path + config_base

    # Walking down file searching in the config repository
    for root, dir, files in os.walk(config_repo_path):
        if file_name in files:
            full_name = os.path.join(root, file_name)
            return full_name
    print(f"Unable to find '{file_name}' in configuration file repository located '{config_repo_path}'")
    # Walking down file searching in the root path
    for root, dir, files in os.walk(root_path):
        if file_name in files:
            full_name = os.path.join(root, file_name)
            return full_name

    # File was not found
    print(f"Unable to find '{file_name}' in direcMeasure path located '{root_path}'")
    return False


# Opens the file and returns the contents of flow
def get_expt_flow(full_file_name):
    if full_file_name == '':
        return False
    if full_file_name.rfind(root_base) == -1:
        # Get file name with file path
        full_file_name = find_config(full_file_name)

    #
    flow = False
    # print(f"full_file_name {full_file_name}")
    with open(full_file_name, "r") as file:
        data = json.load(file)
        flow = data.get("flow")
        # print(flow)
    # # Search for other config files and load them into the
    # index = 0
    # for expt in flow:
    #     expType = expt.get("expType")
    #     if expType.endswith(".json"):
    #         print(f"Found other config file: {expType}")
    #         full_file_name = find_config(expType)
    #         if full_file_name is False:
    #             print(f"Unable to locate {expType}")
    #         with open(full_file_name, "r") as file:
    #             data = json.load(file)
    #             flow = data.get("flow")
    #
    #     index += 1
    return flow


def gen_expt_cmds(flow):
    cmds = []
    for expt in flow:
        print("Found experiment: " + expt.get("expType"))
        if expt.get("expType") == "sweepPhi":
            freq = expt.get("freq")
            startPhi = expt.get("startPhi")
            endPhi = expt.get("endPhi")
            samples = expt.get("samples")
            print("Phi Sweep:")
            print(f"\tFrequency: {freq} Hz")
            print(f"\tStarting Angle: {startPhi}")
            print(f"\tEnding Angle: {endPhi}")
            print(f"\tEnding Angle: {samples}")

        elif expt.get("expType") == "sweepTheta":
            freq = expt.get("freq")
            startTheta = expt.get("startTheta")
            endTheta = expt.get("endTheta")
            samples = expt.get("samples")
            print("Phi Sweep:")
            print(f"\tFrequency: {freq} Hz")
            print(f"\tStarting Angle: {startTheta}")
            print(f"\tEnding Angle: {endTheta}")
            print(f"\tEnding Angle: {samples}")

        elif expt.get("expType") == "sweepFreq":
            freq = expt.get("freq")
            phi = expt.get("phi")
            theta = expt.get("theta")
            print(f"\tFrequenies: {freq} Hz")
            print(f"\tPhi Angle: {phi}")
            print(f"\tTheta Angle: {theta}")
        else:
            return False
    return True


# main
def main():
    print("\nRunning the config parser")
    file_name = "sample_exp.json"
    flow = get_expt_flow(file_name)
    cmds = gen_expt_cmds(flow)

if __name__ == "__main__":
    main()
