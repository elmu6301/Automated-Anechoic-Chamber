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
def get_expt_flow():
    return True


def gen_expt_cmds():
    return True


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
