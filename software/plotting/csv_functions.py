import numpy as np
from utils import util
import pdb

DEF_FILE_NAME = "data.txt"

parameter_col_name_conversions_db = {'S11': 'dB(S11)', 'S12': 'dB(S12)', 'S21': 'dB(S21)', 'S22': 'dB(S22)'}
parameter_col_name_conversions_deg = {'S11': 'Degrees(S11)', 'S12': 'Degrees(S12)', 'S21': 'Degrees(S21)',
                                      'S22': 'Degrees(S22)'}


def createCSV(filename, col_names, data):
    """
    Creates a CSV file.
    :param filename: Name of file to create.
    :param col_names: List of column names for file.
    :param data: Data arrays to add to file.
    :return:
    """
    assert type(filename) == str
    assert type(data) == np.ndarray
    assert type(col_names) == list

    # Append file name
    if filename.rfind(".csv") == -1:
        filename += ".csv"
        # print(f"file_name = {file_name}")

    col_name_str = ''
    for i in range(0, len(col_names)):
        if i == len(col_names) - 1:
            col_name_str += col_names[i]
        else:
            col_name_str += (col_names[i] + ', ')
    data = data.T
    np.savetxt(filename, data, delimiter=',', header=col_name_str, comments='')

    #     return False


def appendToCSV(filename, data):
    """
    Appends to a CSV file.
    :param filename: Name of file to append to.
    :param data: Data to append to file.
    :return:
    """
    assert type(filename) == str
    assert type(data) == np.ndarray
    data = data.T

    # Append file name
    if filename.rfind(".csv") == -1:
        filename += ".csv"
        # print(f"file_name = {file_name}")

    f = open(filename, 'ab')
    np.savetxt(f, data, delimiter=',')
    f.close()


def unitTestCSV():
    antenna_name = 'horn.csv'
    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    col_names = ['Theta', 'Phi', 'Frequency']
    createCSV(antenna_name, data, col_names)

    more_data = np.array([[10, 11, 12], [13, 14, 15]])
    appendToCSV(antenna_name, more_data)


def getSparamData3D(csv_filename, sparam, frequency):
    """
    Gets the 3D for a given frequency and set of S-parameters
    :param csv_filename: Name of file to get data from.
    :param sparam: S-params to get.
    :param frequency: Frequency to get data at.
    :return:
    """
    assert type(csv_filename) == str
    assert type(sparam) == str
    assert type(frequency) == float

    freq_raw, theta_raw, phi_raw, params_col_names, param_raw = getRawData(csv_filename, [sparam], dBOnly=True)
    param_raw = param_raw[0]

    assert frequency in freq_raw
    assert max(theta_raw) - min(theta_raw) <= 360
    assert max(phi_raw) - min(phi_raw) <= 360

    theta = np.sort(np.unique(theta_raw))
    phi = np.sort(np.unique(phi_raw))
    assert len(theta) * len(phi) * len(np.unique(freq_raw)) == len(param_raw)

    param = np.ndarray((len(phi), len(theta)))
    for i in range(0, len(phi)):
        phi_val = phi[i]
        print(phi_val)
        for j in range(0, len(theta)):
            theta_val = theta[j]
            for k in range(0, len(param_raw)):
                if theta_raw[k] == theta_val and phi_raw[k] == phi_val and freq_raw[k] == frequency:
                    param[i][j] = param_raw[k]

    # assert len(param) == len(phi) and len(param) == len(theta)
    # assert len(param[0]) == len(phi[0]) and len(param[0]) == len(theta[0])

    return theta, phi, param


def getThetaCutData(csv_filename, sparam, frequency, theta):
    """
    Gets the theta cut for a given frequency and set of S-parameters.
    :param csv_filename: Name of file to get data from.
    :param sparam: S-params to get.
    :param frequency: Frequency to get data at.
    :param theta: Theta angle to get data at.
    :return: phi and param values
    """
    assert type(csv_filename) == str
    assert type(sparam) == str
    assert type(frequency) == float
    assert type(theta) == float

    freq_raw, theta_raw, phi_raw, params_col_names, param_raw = getRawData(csv_filename, [sparam], dBOnly=True)
    param_raw = param_raw[0]

    assert frequency in freq_raw
    assert theta in theta_raw
    assert max(theta_raw) - min(theta_raw) <= 360
    assert max(phi_raw) - min(phi_raw) <= 360

    if theta - 180 in theta_raw:
        theta_other = theta - 180
        both = True
    elif theta + 180 in theta_raw:
        theta_other = theta + 180
        both = True
    else:
        theta = False

    phi_unique = np.sort(np.unique(phi_raw))
    phi_values = np.ndarray(2 * len(phi_unique) if both else len(phi_unique))
    param_values = np.ndarray(2 * len(phi_unique) if both else len(phi_unique))

    for i in range(0, len(phi_unique)):
        phi_val = phi_unique[i]
        # print(phi_val)
        for k in range(0, len(param_raw)):
            if theta_raw[k] == theta and phi_raw[k] == phi_val and freq_raw[k] == frequency:
                param_values[i] = param_raw[k]
                phi_values[i] = phi_raw[k]
        if both:
            for k in range(0, len(param_raw)):
                if theta_raw[k] == theta_other and phi_raw[k] == phi_val and freq_raw[k] == frequency:
                    param_values[2 * (len(phi_unique)) - i - 1] = param_raw[k]
                    phi_values[2 * (len(phi_unique)) - i - 1] = phi_raw[k] + 360 * (1 - i / (len(phi_unique) - 1))

    return phi_values, param_values


def getPhiCutData(csv_filename, sparam, frequency, phi):
    """
    Gets a phi cut for a given frequency and set of S-parameters
     :param csv_filename: Name of file to get data from.
    :param sparam: S-params to get.
    :param frequency: Frequency to get data at.
    :param phi: Phi angle to get data at.
    :return: theta and param values
    """
    assert type(csv_filename) == str
    assert type(sparam) == str
    assert type(frequency) == float
    assert type(phi) == float

    freq_raw, theta_raw, phi_raw, params_col_names, param_raw = getRawData(csv_filename, [sparam], dBOnly=True)
    param_raw = param_raw[0]

    frequency = freq_raw[0]
    phi = phi_raw[0]
    # assert frequency in freq_raw
    # assert phi in phi_raw
    # assert max(theta_raw) - min(theta_raw) <= 360
    # assert max(phi_raw) - min(phi_raw) <= 360

    theta_values = np.sort(np.unique(theta_raw))
    param_values = np.ndarray(len(theta_values))

    for i in range(0, len(theta_values)):
        theta_val = theta_values[i]
        print(theta_val)
        for k in range(0, len(param_raw)):
            if theta_raw[k] == theta_val and phi_raw[k] == phi and freq_raw[k] == frequency:
                param_values[i] = param_raw[k]

    return theta_values, param_values


def getSparamFrequencyData(csv_filename, params, theta, phi):
    """
    Gets the frequency data for a given phi, theta, and s-parameters.
    :param csv_filename: Name of file to get data from.
    :param params: S-params to get.
    :param theta: Theta angle to get data at.
    :param phi: Phi angle to get data at.
    :return: freq, params_dB, params_col_names_dB, params_deg, params_col_names_deg values
    """
    assert type(csv_filename) == str
    assert type(params) == list
    assert type(theta) == float
    assert type(phi) == float

    freq_raw, theta_raw, phi_raw, params_col_names_dB, params_raw_dB, param_col_name_deg, params_raw_deg = getRawData(
        csv_filename, params)

    freq = unique(freq_raw).sort()
    params_dB = np.ndarray(len(params), len(freq))
    params_deg = np.ndarray(len(params), len(freq))
    for i in range(0, len(freq)):
        freq_val = freq[i]
        for j in range(0, len(params_raw_dB)):
            assert len(params_raw_dB[j]) == len(params_raw_deg[j])
            for k in range(0, len(params_raw_dB[j])):
                if theta_raw[k] == theta and phi_raw[k] == phi and freq_val == freq_raw[k]:
                    params_dB[j][i] = params_raw_dB[j][k]
                    params_deg[j][i] = params_raw_deg[j][k]

    return freq, params_dB, params_col_names_dB, params_deg, params_col_names_deg


def getRawData(csv_filename, sparams, dBOnly=False):
    """
    Gets the raw data.
    :param csv_filename: Name of file to get data from.
    :param sparams: S-parameters to get data at.
    :param dBOnly: Boolean determining whether to only get the dB data.
    :return: data
    """

    assert type(csv_filename) == str
    assert type(sparams) == list
    for param in sparams:
        assert param in parameter_col_name_conversions_db.keys()
        if not dBOnly:
            assert param in parameter_col_name_conversions_deg.keys()

    data = np.genfromtxt(csv_filename, dtype=float, delimiter=',', names=True, encoding='utf-8-sig', deletechars='')
    column_names = data.dtype.names
    data = np.array(data.tolist()).T

    assert 'Frequency' in column_names
    assert 'Theta' in column_names
    assert 'Phi' in column_names
    for sparam in sparams:
        assert parameter_col_name_conversions_db[sparam] in column_names
        if not dBOnly:
            assert parameter_col_name_conversions_deg[sparam] in column_names

    params_col_names_dB = []
    params_col_names_deg = []
    params_raw_dB = []
    params_raw_deg = []
    # theta_raw = []
    # phi_raw = []
    print(type(data))
    # print(data)
    for i in range(0, len(column_names)):
        col_name = column_names[i]
        if col_name == 'Theta':
            if type(data[i]) != list:
                theta_raw = [data[i]]
            else:
                theta_raw = data[i]
        if col_name == 'Phi':
            if type(data[i]) != list:
                phi_raw = [data[i]]
            else:
                phi_raw = data[i]
        if col_name == 'Frequency':
            if type(data[i]) != list:
                freq_raw = [data[i]]
            else:
                freq_raw = data[i]
        for sparam in sparams:
            param_col_name_db = parameter_col_name_conversions_db[sparam]
            param_col_name_deg = parameter_col_name_conversions_deg[sparam]
            if col_name == param_col_name_db:
                params_col_names_dB.append(param_col_name_db)
                if type(data[i]) != list:
                    params_raw_dB.append([data[i]])
                else:
                    params_raw_dB.append(data[i])
            if not dBOnly and col_name == param_col_name_deg:
                params_col_names_deg.append(param_col_name_deg)
                if type(data[i]) != list:
                    params_raw_deg.append([data[i]])
                else:
                    params_raw_deg.append(data[i])

    assert len(theta_raw) == len(phi_raw)
    for i in range(0, len(params_raw_dB)):
        assert len(theta_raw) == len(params_raw_dB[i])
    for i in range(0, len(params_raw_deg)):
        assert len(theta_raw) == len(params_raw_deg[i])

    if dBOnly:
        return freq_raw, theta_raw, phi_raw, params_col_names_dB, params_raw_dB
    else:
        return freq_raw, theta_raw, phi_raw, params_col_names_dB, params_raw_dB, param_col_name_deg, params_raw_deg
#
# # antenna_name = 'horn.csv'
# unitTestCSV()
# getSparamData(antenna_name,[])










