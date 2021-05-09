import os
from datetime import datetime


root_base = "software"
log_file = None

"""
util.py
This file contains functions to support printing, logging, searching for files, etc. 
"""


def initLog(log_name=None, log_path=None):
    """
    Creates a log file associated with a given run.
    :param log_name: Name of the log file.
    :param log_path: File path of the log file.
    """
    global log_file
    if log_name == None:
        dt = datetime.now()
        log_name = r'log__%d_%d_%d__%d_%d_%d.txt'%(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    if log_path == None:
        log_path = os.path.join(os.getcwd(), 'logs')
    log_file = open(os.path.join(log_path, log_name), 'a')


def closeLog():
    """
    Closes the log file.
    :return:
    """
    if log_file != None:
        log_file.close()


def printf(phase, flag, msg):
    """
    Prints out messages to the command line by specifying flag and phase.
    :param phase: Current phase of the system.
    :param flag: Flag indicating message type.
    :param msg: String containing message.
    :return:
    """
    global log_file
    if flag in ("Error", "Warning"):
        print(f"({phase}) {flag}: {msg}")
        if log_file != None:
            print(f"({phase}) {flag}: {msg}", file=log_file)
    else:
        print(f"({phase}):".ljust(11), f"{msg}")
        if log_file != None:
            print(f"({phase}):".ljust(11), f"{msg}", file=log_file)


def gen_col_names(sparam_list):
    """
    Generates the appropriate column names for the CSV file.
    :param sparam_list: List of S-Parameters to include.
    :return: List containing the column names.
    """
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


def get_file_path(file_name, dir_path):
    """
    Gets the file path of the file by first looking at the directory path specified. If no file name is specified
    but a directory path is, a directory using the specified directory path will be created.
    :param file_name:
    :param dir_path:
    :return: Returns the full file path if found or created otherwise, return False
    """
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
    """
    Appends timestamp to the file name
    :param file_name: The file name to append the timestamp to.
    :return: String containing the updated file name.
    """
    if file_name != '':
        if file_name.endswith(".csv"):
            file_name = file_name[0:file_name.rfind(".csv")]
        curr_time = datetime.now()
        date_time = curr_time.strftime("_%H_%M_%m_%d_%Y")
        file_name += date_time
        return file_name
    else:
        return False