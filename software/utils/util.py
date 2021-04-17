import os
from datetime import datetime
import math


root_base = "software"


def printf(phase, flag, msg):
    """ Prints out messages to the command line by specifying flag and phase. """
    if flag in ("Error", "Warning"):
        print(f"({phase}) {flag}: {msg}")
    else:
        print(f"({phase}):".ljust(11), f"{msg}")


def gen_col_names(sparam_list):
    """ Generates the appropriate column names for the CSV file. """
    col_names = ['Frequency', 'Theta', 'Phi', 'Probe Phi']
    if "S11" in sparam_list:
        col_names.append('dB(S11)')
        col_names.append('Degrees(S11)')
    if "S12" in sparam_list:
        col_names.append('dB(S12')
        col_names.append('Degrees(S12)')
    if "S21" in sparam_list:
        col_names.append('dB(S21)')
        col_names.append('Degrees(S21)')
    if "S22" in sparam_list:
        col_names.append('dB(S22)')
        col_names.append('Degrees(S22)')
    return col_names


# Gets the path to the repository
def get_root_path():
    path = os.getcwd()
    if path.rfind(root_base) == -1:
        return False
    while not path.endswith(root_base):
        os.chdir("..")
        path = os.getcwd()
    return path


def append_date_time_str(file_name):
    if file_name != '':
        if file_name.endswith(".csv"):
            file_name = file_name[0:file_name.rfind(".csv")]
        curr_time = datetime.now()
        date_time = curr_time.strftime("_%H_%M_%m_%d_%Y")
        file_name += date_time
        return file_name
    else:
        return False

def calc_num_octaves(startFreq, stopFreq):
    return math.log(stopFreq/startFreq,2)  #- math.log(startFreq,2)
