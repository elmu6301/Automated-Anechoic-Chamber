import pyvisa
import matplotlib.pyplot as plt
import numpy as np

def init_VNA(address):
    rm = pyvisa.ResourceManager()  # Download https://www.keysight.com/main/software.jspx?id=2175637&pageMode=CV&cc=US&lc=eng
    print(rm.list_resources()) #this prints all connected devices (not needed in code but should run once to get device name)
    instrument = rm.open_resource('GPIB0::%d::INSTR' % address)  #Open the VNA connection
    # instrument.read_termination = '\n'      #Set the read termination character
    # instrument.write_termination = '\n'     #Set the write termination character
    identify = instrument.query("*IDN?")      #Query the instrument to ensure it is connected
    print(identify)
    if identify:                            #If the instrument is correctly found
        instrument.write("*RST")            #Reset to default setup
        instrument.write("FORM4")           # Set input/output data format to ASCII

        #set # points
        #collect phase, get freq

        #do we need phase measurements, set channel?

    return instrument

#Set start and stop freq
def init_freq_sweep(instrument, start_freq, stop_freq):
    print("Setting frequency range from " + start_freq + " to " + stop_freq)
    instrument.write("STAR " + start_freq) #Should we ask to enter units or just assume inputs have format 1 GHz?
    instrument.write("STOP " + stop_freq)
    instrument.write("STPSIZE 0.5 GHz") #Currently doesn't work

    #Do we care about setting CENTER or SPAN:FULL/SPAN:LINK ?

#Commands to collect dB and Phase values
def collect_freq_sweep_data(instrument):
    instrument.write("LISFREQ")  # Set to frequency list sweep mode ---> Does this change to 0 to frequency in the output command?

    instrument.write("LOGM")  # Set display to log magnitude format
    instrument.write("LINFREQ")  # Select linear frequency sweep  ---> Do we want logarithmic?
    data_db = instrument.query("OUTPFORM")  # Output format is a list of form (db, 0)
    instrument.write("PHAS")  # Set display to phase format
    data_degree = instrument.query("OUTPFORM")  # Output format is a list of form (degrees, 0)

    return data_db, data_degree

#Run the frequency sweep for all s-parameters
def sparam_data(instrument): #Will we ever want to do only a couple (not all 4)?

    # #Collect data for s-parameter S11
    # print("Collecting s11 data...")
    # instrument.write("S11")
    # s11_db, s11_degree = collect_freq_sweep_data(instrument)
    #
    # # Collect data for s-parameter S12
    # print("Collecting s12 data...")
    # instrument.write("S12")
    # s12_db, s12_degree = collect_freq_sweep_data(instrument)
    #
    # # Collect data for s-parameter S21
    # print("Collecting s21 data...")
    # instrument.write("S21")
    # s21_db, s21_degree = collect_freq_sweep_data(instrument)
    #
    # # Collect data for s-parameter S22
    # print("Collecting s22 data...")
    # instrument.write("S22")
    # s22_db, s22_degree = collect_freq_sweep_data(instrument)
    #
    # instrument.write("NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

    #This is example data to test my file and plotting functions without being in the lab:
    s11_db = [(-3.720898000000000E+01,   0.000000000000000E+00),(-3.807226000000000E+01,   0.000000000000000E+00),(-3.856250000000000E+01,   0.000000000000000E+00),
              (-3.892773000000000E+01,   0.000000000000000E+00),(-3.930273000000000E+01,   0.000000000000000E+00),(-3.971484000000000E+01,   0.000000000000000E+00),
              (-4.060742000000000E+01,   0.000000000000000E+00),(-4.211523000000000E+01,   0.000000000000000E+00),(-4.337110000000000E+01,   0.000000000000000E+00),
              (-4.383985000000000E+01,   0.000000000000000E+00)]

    s11_degree = [(7.931250000000000E+01,   0.000000000000000E+00),(2.275586000000000E+01,   0.000000000000000E+00),(-3.135254000000000E+01,   0.000000000000000E+00),
                  (-8.624609000000000E+01,   0.000000000000000E+00),(-1.423281000000000E+02,   0.000000000000000E+00),(1.602266000000000E+02,   0.000000000000000E+00),
                  (1.011094000000000E+02,   0.000000000000000E+00),(4.547071000000000E+01,   0.000000000000000E+00),(-4.196777000000000E+00,   0.000000000000000E+00),
                  (-5.637500000000000E+01,   0.000000000000000E+00)]

    freq = list(range(1,11))

    s12_db = s11_db
    s21_db = s11_db
    s22_db = s11_db
    s12_degree = s11_degree
    s21_degree = s11_degree
    s22_degree = s11_degree

    #Format the data:
    s11_db_only = data_formatting(s11_db)
    s11_degree_only = data_formatting(s11_degree)
    s12_db_only = data_formatting(s12_db)
    s12_degree_only = data_formatting(s12_degree)
    s21_db_only = data_formatting(s21_db)
    s21_degree_only = data_formatting(s21_degree)
    s22_db_only = data_formatting(s22_db)
    s22_degree_only = data_formatting(s22_degree)

    #return one large array which can be easily parsed into columns
    return np.array([freq, s11_db_only, s11_degree_only, s12_db_only, s12_degree_only, s21_db_only, s21_degree_only, s22_db_only, s22_degree_only])

#Remove column of 0's from VNA's output data
def data_formatting(data):
    data_col1 = []    #Initialize the list of data to return

    for i in data:
        data_col1.append(i[0]) #Only save the first value of every listed data pair

    return data_col1

def file_save(filename, data): #Do we want to pass in user comments too?
    data_transpose = data.T
    col_names = "Freq (GHz), S11 dB, S11 Phase (deg), S12 dB, S12 Phase (deg), S21 dB, S21 Phase (deg), S22 dB, S22 Phase (deg)" #Will frequency ever not be GHz?
    np.savetxt(filename, data_transpose, delimiter=',', header=col_names, comments="") #More specification options available

def plot(filename):
    freq, s11_db, s11_degree, s12_db, s12_degree, s21_db, s21_degree, s22_db, s22_degree = np.loadtxt(filename, delimiter=',', skiprows=1, comments="#", unpack=True)

    plt.figure("Figure 1: dB")
    plt.title("S-parameter dB Values")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("dB")
    plt.plot(freq, s11_db, label="S11")
    plt.plot(freq, s12_db, label="S12")
    plt.plot(freq, s21_db, label="S21")
    plt.plot(freq, s22_db, label="S22")
    plt.legend()

    plt.figure("Figure 2: Phase")
    plt.title("S-parameter Phase Values")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Phase (Degrees)")
    plt.plot(freq, s11_degree, label="S11")
    plt.plot(freq, s12_degree, label="S12")
    plt.plot(freq, s21_degree, label="S21")
    plt.plot(freq, s22_degree, label="S22")
    plt.legend()
    plt.show()


def marker(instrument):
    instrument.write("MARK1 " + freq_val) #Can set up to 4 marks
    print(instrument.query("OUTPMARK")) #(dB, ?, freq)

def main():
    print("Beginning execution of VNA commands")
    # hp8719a = init_VNA(16)    #Connect to the VNA
    # init_freq_sweep(hp8719a, "1 GHz", "3 GHz") #Set the desired frequency range
    # data_out = sparam_data(hp8719a)
    data_out = sparam_data("hi")
    file_save("demo.csv", data_out)
    plot("demo.csv")
    # for i in range(1,9): #Add breakpoint to line 155 for demo
    #   marker("2.4 GHz") #Can use to verify values at a freq

if __name__ == "__main__":
    main()