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
from plotting import csv_functions as csv_f
import pdb




def plot3DRadPattern(csv_filename,plot_filename,param,frequency):
    #Based on example code: https://stackoverflow.com/questions/36816537/spherical-coordinates-plot-in-matplotlib
    
    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(param) == str
    assert type(frequency) == float

    print("Plotting data stored in: " + csv_filename)
    theta,phi,param_vals = csv_f.getSparamData3D(csv_filename,param,frequency)

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
    phi_vals,param_vals = csv_f.getThetaCutData(csv_filename,param,frequency,theta)

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
    theta_vals,param_vals = csv_f.getPhiCutData(csv_filename,param,frequency,phi)

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

    print("Plotting data stored in: " + filename)
    freq,params_db,params_db_names,params_deg,names = csv_f.getSparamFrequencyData(csv_filename,params,theta,phi)

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
    for i in range(0,len(params_deg_names)):
        plt.plot(freq,params_db[i],label=params_deg_names[i])
    plt.legend()
    fig1.savefig('phase_' + plot_filename)

def plot2DSparamPhi(csv_filename,plot_filename,parameter,theta,frequency):
    #Plots magnitude and phase for constant frequency and theta

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(params) == list
    assert type(theta) == float
    assert type(frequency) == float

    print("Plotting data stored in: " + filename)

def plot2DSparamTheta(csv_filename,plot_filename,parameter,phi,frequency):
    #Plots magnitude and phase for a constant frequency and phi

    assert type(csv_filename) == str
    assert type(plot_filename) == str
    assert type(params) == list
    assert type(frequency) == float
    assert type(phi) == float

    print("Plotting data stored in: " + filename)

# plot3DRadPattern('horn_gregor.csv','horn_rad_pattern_4.jpg','S21',4.00)
#plotThetaCut('horn_gregor.csv','ThetaCut.jpg','S21',4.5,0.0)
#plotPhiCut('horn_gregor.csv','PhiCut.jpg','S21',4.4,90.0)
