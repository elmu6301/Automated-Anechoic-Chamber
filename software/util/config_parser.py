# Include
import pydoc
import os
import json
from drivers import VNA_gpib as vna

try:
    import experiments
except ImportError:
    from util import experiments

'''
config_parser.py
This file contains functions to find, open, and generate flows and commands.
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
def get_expt_flow_meas(full_file_name):
    if full_file_name == '':
        return False
    if full_file_name.rfind(root_base) == -1:
        # Get file name with file path
        full_file_name = find_config(full_file_name)

    flow = False
    meas = False
    # print(f"full_file_name {full_file_name}")
    with open(full_file_name, "r") as file:
        try:
            data = json.load(file)
        except json.decoder.JSONDecodeError:
            return False, False

        flow = data.get("flow")
        meas = data.get("meas")
        # print(flow)
        # print(f"meas: {meas}")
    # Error check measurement
    if meas is None or not meas:
        meas = {"deviceAddress": 16, "freqSweepMode": "lin"}
    meas.setdefault("deviceAddress", 16)  # TODO update to generic value
    meas.setdefault("freqSweepMode", "lin")  # TODO update to generic value
    if meas["freqSweepMode"] not in ("lin", "log"):
        return False, False

    return flow, meas


def gen_expt_cmds(flow):
    cmds = []
    curr_theta = 0
    curr_phi = 0
    # print(f"Currently at ({curr_phi},{curr_theta})")

    for expt in flow:
        type = expt.get("expType")
        # print("Found experiment: " + type)
        if type == "sweepPhi":
            # Get inputs for command generator
            freq = expt.get("freq")
            startPhi = expt.get("startPhi")
            endPhi = expt.get("endPhi")
            samples = expt.get("samples")
            theta = expt.get("theta")
            # Generate commands
            phi_cmds = experiments.gen_sweepPhi_cmds(startPhi, endPhi, theta, samples, freq)
            # Check to see if commands were generated incorrectly
            if phi_cmds:
                cmds.append(phi_cmds[0])
                curr_phi = phi_cmds[1]
                curr_theta += phi_cmds[2]
                # print(f"Currently at ({curr_phi},{curr_theta})")
            else:
                return False

        elif type == "sweepTheta":
            # Get inputs for command generator
            freq = expt.get("freq")
            startTheta = expt.get("startTheta")
            endTheta = expt.get("endTheta")
            samples = expt.get("samples")
            phi = expt.get("phi")
            # Generate commands
            theta_cmds = experiments.gen_sweepTheta_cmds(startTheta, endTheta, phi, samples, freq)
            # Check to see if commands were generated incorrectly
            if theta_cmds:
                cmds.append(theta_cmds[0])
                curr_phi += theta_cmds[1]
                curr_theta = theta_cmds[2]
                # print(f"Currently at ({curr_phi},{curr_theta})")
            else:
                return False

        elif type == "sweepFreq":
            # Get inputs for command generator
            freq = expt.get("freq")
            orients = expt.get("orientations")
            # Generate commands
            # print(freq)
            freq_cmds = experiments.gen_sweepFreq_cmds(curr_phi, curr_theta, orients, freq)
            # Check to see if commands were generated incorrectly
            if freq_cmds and not isinstance(freq_cmds, int):
                cmds.append(freq_cmds[0])
                curr_phi = freq_cmds[1]
                curr_theta = freq_cmds[2]
                # print(f"Currently at ({curr_phi},{curr_theta})")
            elif isinstance(freq_cmds, int):
                err = f"Invalid number of points entered in experiment '{type}'. Number of points must match" \
                      f"one of the following \n\t\t\t   {str(vna.allowed_num_points)}. Try using {freq_cmds} instead."
                return err
            else:
                # print("Error detected")
                return False

        elif type.endswith(".json"):
            # print(f"\tOpening {type}")
            inner_flow, inner_meas = get_expt_flow_meas(type)  # ignore meas of the referenced config
            # print(inner_flow)
            inner_cmds = gen_expt_cmds(inner_flow)
            if inner_cmds is not False:
                for i_cmd in inner_cmds:
                    cmds.append(i_cmd)
            else:
                return False
        else:
            return False
    return cmds


def print_cmds(cmds):
    for cmd_set in cmds:
        print(f"\nExperiment Type: {cmd_set['type']}")
        t_cmds = cmd_set['test']
        p_cmds = cmd_set['probe']
        g_cmds = cmd_set['gpib']
        for t in t_cmds:
            print(f"\t TEST: {t}")
        for p in p_cmds:
            print(f"\tPROBE: {p}")
        for g in g_cmds:
            print(f"\t GPIB: {g}")


# main
def main():
    print("\nRunning the config parser")
    file_name = "sample_exp.json"
    flow = get_expt_flow(file_name)
    cmds = gen_expt_cmds(flow)
    # print(f"\nGenerated the following commands: \n{cmds}")

    print_cmds(cmds)


if __name__ == "__main__":
    main()
