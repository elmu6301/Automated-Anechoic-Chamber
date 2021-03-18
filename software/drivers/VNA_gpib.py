import pyvisa
import matplotlib.pyplot as plt
import numpy as np

def init_VNA(address):
    rm = pyvisa.ResourceManager()  # Download https://www.keysight.com/main/software.jspx?id=2175637&pageMode=CV&cc=US&lc=eng
    print("All connected GPIB devices: ")
    print(rm.list_resources()) #this prints all connected devices (not needed in code but should run once to get device name)
    print("")
    instrument = rm.open_resource('GPIB0::%d::INSTR' % address)  #Open the VNA connection
    # instrument.read_termination = '\n'      #Set the read termination character  (due to VNA's data output, this truncated the output data too early)
    # instrument.write_termination = '\n'     #Set the write termination character
    identify = instrument.query("*IDN?")      #Query the instrument to ensure it is connected
    print("Selected GPIB device: " + identify)
    if identify:                            #If the instrument is correctly found
        instrument.write("*RST")            #Reset to default setup
        instrument.write("FORM4")           # Set input/output data format to ASCII

        #To Do: read freq data, set number of points, manual triggereing
        #Do we want more features such as setting channel 2?

    return instrument

#Set start and stop freq
def init_freq_sweep(instrument, start_freq, stop_freq):
    print("Setting frequency range from " + start_freq + " to " + stop_freq)
    instrument.write("STAR " + start_freq) #Should we ask to enter units or just assume inputs have format 1 GHz?
    instrument.write("STOP " + stop_freq)
    # instrument.write("STPSIZE 0.5 GHz") #Currently doesn't work

    #Do we care about setting CENTER or SPAN:FULL/SPAN:LINK ?

#Commands to collect dB and Phase values
def collect_freq_sweep_data(instrument):
    # instrument.write("LISFREQ")  # Set to frequency list sweep mode ---> Doesn't seem to work yet

    instrument.write("LOGM")  # Set display to log magnitude format
    instrument.write("LINFREQ")  # Select linear frequency sweep  ---> Do we want logarithmic?
    data_db = instrument.query("OUTPFORM")  # Output format is a list of form (db, 0)

    print("Magnitude (dB) Marker at 2.5 GHz (see first value for dB, last for GHz):")
    marker(instrument, "2.5 GHz")

    instrument.write("PHAS")  # Set display to phase format
    data_degree = instrument.query("OUTPFORM")  # Output format is a list of form (degrees, 0)

    print("Phase (degrees) Marker at 2.5 GHz (see first value for degrees, last for GHz): ")
    marker(instrument, "2.5 GHz")

    return data_db, data_degree

#Run the frequency sweep for all s-parameters
def sparam_data(instrument): #Will we ever want to do only a couple (not all 4)?

    # #Collect data for s-parameter S11
    print("Collecting s11 data...")
    instrument.write("S11")
    s11_db, s11_degree = collect_freq_sweep_data(instrument)

    # Collect data for s-parameter S12
    print("Collecting s12 data...")
    instrument.write("S12")
    s12_db, s12_degree = collect_freq_sweep_data(instrument)

    # Collect data for s-parameter S21
    print("Collecting s21 data...")
    instrument.write("S21")
    s21_db, s21_degree = collect_freq_sweep_data(instrument)

    # Collect data for s-parameter S22
    print("Collecting s22 data...")
    instrument.write("S22")
    s22_db, s22_degree = collect_freq_sweep_data(instrument)

    instrument.write("NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

    #Set the frequency by using start/stop freq and default number of points (for demo)
    freq = []
    i = 1.01
    while i <= 3.01:
        freq.append(i)
        i = i + (3-1)/201
    # freq_rounded = [round(elem, 3) for elem in freq]

    #Format the data:
    s11_db_only = data_formatting(s11_db)
    s11_degree_only = data_formatting(s11_degree)
    s12_db_only = data_formatting(s12_db)
    s12_degree_only = data_formatting(s12_degree)
    s21_db_only = data_formatting(s21_db)
    s21_degree_only = data_formatting(s21_degree)
    s22_db_only = data_formatting(s22_db)
    s22_degree_only = data_formatting(s22_degree)

    #return one large array which can be easily parsed into file columns
    return np.array([freq, s11_db_only, s11_degree_only, s12_db_only, s12_degree_only, s21_db_only, s21_degree_only, s22_db_only, s22_degree_only],dtype=object)

#Remove column of 0's from VNA's output data by reformatting and splitting the input data string to create a list with all 0's at odd list indices
def data_formatting(data):

    data_col1 = data.replace(" ", "").replace("\n", ",").split(',')[0::2] #[0::2] takes every other list element starting at index 0

    return np.array(data_col1[:-1],dtype=float)

def file_save(filename, data): #Do we want to pass in user comments too?
    print("\nSaving collected data to: " + filename)
    data_transpose = data.T
    col_names = "Freq (GHz), S11 Mag (dB), S11 Phase (deg), S12 Mag (dB), S12 Phase (deg), S21 Mag (dB), S21 Phase (deg), S22 Mag (dB), S22 Phase (deg)" #Will frequency ever not be GHz?
    np.savetxt(filename, data_transpose, delimiter=',', header=col_names, comments="") #More specification options available

def plot(filename):
    print("Plotting data stored in: " + filename)
    freq, s11_db, s11_degree, s12_db, s12_degree, s21_db, s21_degree, s22_db, s22_degree = np.loadtxt(filename, delimiter=',', skiprows=1, comments="#", unpack=True)

    fig1 = plt.figure("Figure 1: Magnitude")
    plt.title("S-parameter Magnitude Values")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Magnitude (dB)")
    plt.plot(freq, s11_db, label="S11")
    plt.plot(freq, s12_db, label="S12")
    plt.plot(freq, s21_db, label="S21")
    plt.plot(freq, s22_db, label="S22")
    plt.legend()
    fig1.savefig("antenna_s_params_magnitude.jpg")

    fig2 = plt.figure("Figure 2: Phase")
    plt.title("S-parameter Phase Values")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Phase (Degrees)")
    plt.plot(freq, s11_degree, label="S11")
    plt.plot(freq, s12_degree, label="S12")
    plt.plot(freq, s21_degree, label="S21")
    plt.plot(freq, s22_degree, label="S22")
    plt.legend()
    fig2.savefig("antenna_s_params_phase.jpg")
    # plt.show() #Shows the plots on screen but code halts until they are closed (which is why I saved them as files instead)


def marker(instrument, freq_val):
    instrument.write("MARK1 " + freq_val) #Can set up to 4 marks
    print(instrument.query("OUTPMARK")) #(dB or degree, ?, freq)

def exit(instrument):  #This hasn't been tested
    instrument.write("NOOP")

def main():
    print("Beginning execution of VNA commands")
    print("-----------------------------------")
    hp8719a = init_VNA(16)                      #Connect to the VNA
    init_freq_sweep(hp8719a, "1 GHz", "3 GHz")  #Set the desired frequency range
    data_out = sparam_data(hp8719a)             #Measure the data (dB and degree for all s-param)
    file_save("antenna_s_params.csv", data_out) #Store the data
    plot("antenna_s_params.csv")                #Plot the data

    # exit(hp8719a)
    # marker(hp8719a, "2 GHz") #Can use to verify values at a freq

if __name__ == "__main__":
    main()