'''
Types of plotting supported:
- S-parameter vs. frequency
- S-parameter vs. theta
- S-parameters vs. phi
- 3D s-parameter pattern
- Cuts in a phi plane
- Cuts in a theta plane

For all functions in this file we assume theta is the major axis and phi is the minor azimuthal axis
'''

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as axes3d
# from plotting import csv_functions as csv_f
import pdb



parameter_col_name_conversions_db = {'S11':'dB(S11)','S12':'dB(S12)','S21':'dB(S21)','S22':'dB(S22)'}
parameter_col_name_conversions_deg = {'S11':'Degrees(S11)','S12':'Degrees(S12)','S21':'Degrees(S21)','S22':'Degrees(S22)'}


def plot3DRadPattern(csv_filename,plot_filename,param,frequency):
    #Based on example code: https://stackoverflow.com/questions/36816537/spherical-coordinates-plot-in-matplotlib
    
    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(param) == str
    assert type(frequency) == float

    print("Plotting data stored in: " + csv_filename)
    theta,phi,param_vals = getSparamData3D(csv_filename,param,frequency)
    # theta, phi, param_vals = csv_f.getSparamData3D(csv_filename, param, frequency)

    #Convert to radians
    theta *= np.pi/180
    phi *= np.pi/180

    THETA,PHI = np.meshgrid(theta,phi)
    pdb.set_trace()
    X = param_vals * np.sin(PHI) * np.cos(THETA)
    Y = param_vals * np.sin(PHI) * np.sin(THETA)
    Z = param_vals * np.cos(PHI)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')
    plot = ax.plot_surface(X, Y, Z,rstride=1,cstride=1,cmap=plt.get_cmap('jet'),linewidth=0,antialiased=False,alpha=0.5)
    fig.colorbar(plot, shrink=0.5, aspect=5)
    plt.savefig(plot_filename)
    plt.show()

def plotThetaCut(csv_filename,plot_filename,param,frequency,theta):
    #Polar plot of selected sparam magnitude at a selected value of theta (and theta + 180 if in data file)

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(param) == str
    assert type(frequency) == float
    assert type(theta) == float

    print("Plotting data stored in: " + csv_filename)
    phi_vals,param_vals = getThetaCutData(csv_filename,param,frequency,theta)
    #phi_vals, param_vals = csv_f.getThetaCutData(csv_filename, param, frequency, theta)

    #Convert to radians
    phi_vals *= np.pi/180

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(phi_vals, param_vals)
    ax.set_rmax(max(param_vals))
    ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.deg2rad(90))
    ax.grid(True)

    title = 'Theta = ' + str(theta) + ' Cut'
    ax.set_title('Theta = ' + str(theta) + ' Cut at ' + str(frequency) + ' GHz', va='bottom')
    plt.savefig(plot_filename)
    plt.show()


def plotPhiCut(csv_filename,plot_filename,param,frequency,phi):
    #Polar plot of selected sparam magnitude at a selected value of phi

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(param) == str
    assert type(frequency) == float
    assert type(phi) == float
    
    print("Plotting data stored in: " + csv_filename)
    theta_vals,param_vals = getPhiCutData(csv_filename,param,frequency,phi)
    # theta_vals, param_vals = csv_f.getPhiCutData(csv_filename, param, frequency, phi)

    #Convert to radians
    theta_vals *= np.pi/180

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(theta_vals, param_vals)
    ax.set_rmax(max(param_vals))
    ax.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    ax.set_theta_direction(1)
    ax.set_theta_offset(np.deg2rad(-90))
    ax.grid(True)

    ax.set_title('Phi = ' + str(phi) + ' Cut at ' + str(frequency) + ' GHz', va='bottom')
    plt.savefig(plot_filename)
    plt.show()



def plot2DSparamFrequency(csv_filename,plot_filename,params,theta,phi):
    #Plots magnitude and phase for constant theta and phi

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(params) == list
    assert type(theta) == float
    assert type(phi) == float

    print("Plotting data stored in: " + plot_filename)
    freq,params_db,params_db_names,params_deg,names = getSparamFrequencyData(csv_filename,params,theta,phi)
    # freq, params_db, params_db_names, params_deg, names = csv_f.getSparamFrequencyData(csv_filename, params, theta, phi)

    fig1 = plt.figure("Figure 1: Magnitude")
    plt.title("S-parameter Magnitude Values")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Magnitude (dB)")
    for i in range(0,len(params_db_names)):
        plt.plot(freq,params_db[i],label=params_db_names[i])
    plt.legend()
    fig1.savefig('magnitude_' + plot_filename)

    fig2 = plt.figure("Figure 2: Phase")
    plt.title("S-parameter Phase Values")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Phase (Degrees)")
    for i in range(0,len(params_deg)):
        plt.plot(freq,params_db[i],label=params_deg[i])
    plt.legend()
    fig1.savefig('phase_' + plot_filename)

def plot2DSparamPhi(csv_filename,plot_filename,params,theta,frequency):
    #Plots magnitude and phase for constant frequency and theta

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(params) == list
    assert type(theta) == float
    assert type(frequency) == float

    print("Plotting data stored in: " + plot_filename)

def plot2DSparamTheta(csv_filename,plot_filename,params,phi,frequency):
    #Plots magnitude and phase for a constant frequency and phi

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(params) == list
    assert type(frequency) == float
    assert type(phi) == float

    print("Plotting data stored in: " + plot_filename)


def getSparamData3D(csv_filename, sparam, frequency):
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
    assert type(csv_filename) == str
    assert type(sparam) == str
    assert type(frequency) == float
    assert type(phi) == float

    freq_raw, theta_raw, phi_raw, params_col_names, param_raw = getRawData(csv_filename, [sparam], dBOnly=True)
    param_raw = param_raw[0]

    assert frequency in freq_raw
    assert phi in phi_raw
    assert max(theta_raw) - min(theta_raw) <= 360
    assert max(phi_raw) - min(phi_raw) <= 360

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
    assert type(csv_filename) == str
    assert type(sparams) == list
    for param in sparams:
        assert param in parameter_col_name_conversions_db.keys()
        if not dBOnly:
            assert param in parameter_col_name_conversions_deg.keys()

    data = np.genfromtxt(csv_filename, dtype=float, delimiter=',', names=True, encoding='utf-8-sig', deletechars='')
    column_names = data.dtype.names
    data = np.array(data.tolist()).T

    # assert 'Frequency' in column_names
    # assert 'Theta' in column_names
    # assert 'Phi' in column_names
    for sparam in sparams:
        assert parameter_col_name_conversions_db[sparam] in column_names
        if not dBOnly:
            assert parameter_col_name_conversions_deg[sparam] in column_names

    params_col_names_dB = []
    params_col_names_deg = []
    params_raw_dB = []
    params_raw_deg = []
    for i in range(0, len(column_names)):
        col_name = column_names[i]
        if col_name == 'Theta':
            theta_raw = data[i]
        if col_name == 'Phi':
            phi_raw = data[i]
        if col_name == 'Frequency':
            freq_raw = data[i]
        for sparam in sparams:
            param_col_name_db = parameter_col_name_conversions_db[sparam]
            param_col_name_deg = parameter_col_name_conversions_deg[sparam]
            if col_name == param_col_name_db:
                params_col_names_dB.append(param_col_name_db)
                params_raw_dB.append(data[i])
            if not dBOnly and col_name == param_col_name_deg:
                params_col_names_deg.append(param_col_name_deg)
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


# plot3DRadPattern('horn_gregor.csv','horn_rad_pattern_4.jpg','S21',4.00)
#plotThetaCut('horn_gregor.csv','ThetaCut.jpg','S21',4.5,0.0)
#plotPhiCut('horn_gregor.csv','PhiCut.jpg','S21',4.4,90.0)
