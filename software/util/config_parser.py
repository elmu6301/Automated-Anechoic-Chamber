# Include
import pydoc
import os
import json

try:
    import experiments
except ImportError:
    from util import experiments
#

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

    #
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
        # print(meas)
    return flow, meas


def gen_expt_cmds(flow):
    cmds = []
    try:
        for expt in flow:
            cmd = {}
            experiment_type  = expt.get("expType")
            if experiment_type.endswith(".json"):
                inner_flow, inner_meas = get_expt_flow_meas(type)
                inner_cmds = gen_expt_cmds(inner_flow)
                if inner_cmds is not False:
                    for i_cmd in inner_cmds:
                        cmds.append(i_cmd)
            else:
                assert experiment_type in ['sweepFreq', 'sweepTheta', 'sweepPhi']
            cmd['experiment type'] = experiment_type
            if experiment_type != "sweepPhi":
                test_theta_start = float(expt.get("startTestTheta"))
                assert -180 <= test_theta_start <= 180
                cmd['test-theta start'] = test_theta_start
                test_theta_end   = float(expt.get("endTestTheta"))
                assert -180 <= test_theta_end <= 180
                cmd['test-theta end'] = test_theta_end
                test_theta_steps = int(expt.get("stepsTestTheta"))
                assert test_theta_steps > 0
                cmd['test-theta steps'] = test_theta_steps
            else:
                test_theta_orientation = float(expt.get("orientationTestTheta"))
                assert -180 <= test_theta_orientation <= 180
                cmd['test-theta orientation'] = test_theta_orientation
            if experiment_type != "sweepTheta":
                test_phi_start   = float(expt.get("startTestPhi"))
                assert -180 <= test_phi_start <= 180
                cmd['test-phi start'] = test_phi_start
                test_phi_end     = float(expt.get("endTestPhi"))
                assert -180 <= test_phi_end <= 180
                cmd['test-phi end'] = test_phi_end
                test_phi_steps   = int(expt.get("stepsTestPhi"))
                assert test_phi_steps > 0
                cmd['test-phi steps'] = test_phi_steps
            else:
                test_phi_orientation = float(expt.get("orientationTestPhi"))
                assert -180 <= test_phi_orientation <= 180
                cmd['test-phi orientation'] = test_phi_orientation
            probe_phi_start  = float(expt.get("startProbePhi"))
            assert -180 <= probe_phi_start <= 180
            cmd['probe-phi start'] = probe_phi_start
            probe_phi_end    = float(expt.get("endProbePhi"))
            assert -180 <= probe_phi_end <= 180
            cmd['probe-phi end'] = probe_phi_end
            probe_phi_steps  = int(expt.get("stepsProbePhi"))
            assert probe_phi_steps > 0
            cmd['probe-phi steps'] = probe_phi_steps
            assert expt.get("alignment").upper() in ['TRUE', 'FALSE']
            alignment        = True if expt.get("alignment").upper() == 'TRUE' else False
            cmd['alignment'] = alignment
            if alignment == True:
                alignment_tolerance = float(expt.get("alignmentTolerance"))
                assert alignment_tolerance >= 0
                cmd['alignment tolerance'] = alignment_tolerance
            freq_start       = expt.get("startFrequency")
            if 'MHz' in freq_start:
                freq_start = 1e-3 * float(freq_start[:-3])
            elif 'GHz' in freq_start:
                freq_start = float(freq_start[:-3])
            else:
                assert False
            cmd['start frequency'] = freq_start
            freq_stop        = expt.get("stopFrequency")
            if 'MHz' in freq_stop:
                freq_stop = 1e-3 * float(freq_stop[:-3])
            elif 'GHz' in freq_stop:
                freq_stop = float(freq_stop[:-3])
            else:
                assert False
            cmd['stop frequency'] = freq_stop
            freq_sweep_type  = expt.get("sweepType").lower()
            assert freq_sweep_type in ['log', 'linear']
            cmd['frequency sweep type'] = freq_sweep_type
            data_type        = expt.get("vnaDataType").split(', ')
            assert set(data_type).issubset(set(['logmag', 'phase', 'sparam']))
            cmd['VNA data type'] = data_type
            cmds.append(cmd)
    except:
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