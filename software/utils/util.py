import os
from datetime import datetime
import numpy as np


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


def findClosest(arr, n, target):
    # Corner cases
    if (target <= arr[0]):
        return arr[0]
    if (target >= arr[n - 1]):
        return arr[n - 1]

    # Doing binary search
    i = 0
    j = n
    mid = 0
    while (i < j):
        mid = int((i + j) / 2)

        if (arr[mid] == target):
            return arr[mid]

        # If target is less than array
        # element, then search in left
        if (target < arr[mid]):

            # If target is greater than previous
            # to mid, return closest of two
            if (mid > 0 and target > arr[mid - 1]):
                return getClosest(arr[mid - 1], arr[mid], target)

            # Repeat for left half
            j = mid

        # If target is greater than mid
        else:
            if (mid < n - 1 and target < arr[mid + 1]):
                return getClosest(arr[mid], arr[mid + 1], target)

            # update i
            i = mid + 1

    # Only single element left after search
    return arr[mid]


# Method to compare which one is the more close.
# We find the closest by taking the difference
# between the target and both values. It assumes
# that val2 is greater than val1 and target lies
# between these two.
def getClosest(val1, val2, target):
    if (target - val1 >= val2 - target):
        return val2
    else:
        return val1


# Gets the path to the repository
def get_root_path():
    path = os.getcwd()
    if path.rfind(root_base) == -1:
        return False
    while not path.endswith(root_base):
        os.chdir("..")
        path = os.getcwd()
    return path


def get_file_path(file_name, dir_path):
    # Navigate to the correct base
    root_path = get_root_path()
    search_base_path = os.path.join(root_path, dir_path)

    # Find a file
    if file_name != '':
        # Check to see if the path exists
        if not os.path.isdir(search_base_path):
            return False

        # Walking down file searching in the specified repository
        for root, dir, files in os.walk(search_base_path):
            if file_name in files:
                full_name = os.path.join(root, file_name)
                return full_name

        # Walking down file searching in the root path
        for root, dir, files in os.walk(root_path):
            if file_name in files:
                full_name = os.path.join(root, file_name)
                return full_name
        return False
    else:
        # Make a directory if needed
        if not os.path.isdir(search_base_path):
            try:
                os.mkdir(search_base_path)
            except:
                return False

        return search_base_path


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