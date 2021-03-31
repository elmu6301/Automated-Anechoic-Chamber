import pyvisa
import matplotlib.pyplot as plt
import numpy as np

allowed_num_points = (3, 11, 21, 51, 101, 201, 401, 801, 1601)


class VNA_HP8719A:
    def __init__(self, address):
        self.address = 16  #CHECK THIS IT MAY HAVE CHANGED
        # try:
        self.instrument = self.connect_VNA()
        # except:
        #     pass

    def connect_VNA(self):
        rm = pyvisa.ResourceManager()  # Download https://www.keysight.com/main/software.jspx?id=2175637&pageMode=CV&cc=US&lc=eng
        # print("All connected GPIB devices: ")
        # print(rm.list_resources()) #this prints all connected devices (not needed in code but should run once to get device name)
        # print("")
        try:
            instrument = rm.open_resource('GPIB0::%d::INSTR' % self.address)  #Open the VNA connection
        except:
            return False
        # instrument.read_termination = '\n'      #Set the read termination character  (due to VNA's data output, this truncated the output data too early)
        # instrument.write_termination = '\n'     #Set the write termination character
        identify = instrument.query("*IDN?")      #Query the instrument to ensure it is connected
        print("Selected GPIB device: " + identify)
        if "HEWLETT PACKARD,8719A" in identify:     #If the instrument is correctly found
            instrument.write("*RST")                #Reset to default setup
            instrument.write("FORM4")               # Set input/output data format to ASCII
            return instrument
        else:
            print("Error: An instrument other than the VNA HP8719A has been connected. Please connect the correct instrument or run alternative code.")
            return False
        # return False

            #To Do: read freq data, set number of points, manual triggereing
            #Do we want more features such as setting channel 2?
            #CREATE SEPARATE FUNCTION FOR DATA FORMAT/OTHER INITIALIZATION COMMANDS BESIDES CONNECT?
            #Is the Identify Error too specific? --> Note in User Manual where it's located in case they need to disable it?

    # Return instrument to default state
    def reset(self):
        self.instrument.write("*RST")

    #Set start and stop freq. Note: Must pass in frequency units as "X GHz"
    def init_freq_sweep(self, start_freq, stop_freq):
        print("Setting frequency range from " + start_freq + " to " + stop_freq)
        self.instrument.write("STAR " + start_freq)
        self.instrument.write("STOP " + stop_freq)

        #Do we care about setting CENTER or SPAN:FULL/SPAN:LINK ?

    #Select the ype of frequency sweep (linear or logarithmic)
    def freq_sweep_type(self, type):
        if type == 1:
            self.instrument.write("LOGFREQ")  # Select logarithmic frequency sweep
        else:
            self.instrument.write("LINFREQ")  # Select linear frequency sweep

    #Collect logarithmic magnitude data for a frequency sweep
    def logmag_data(self, type_freq_sweep):
        self.freq_sweep_type(type_freq_sweep)
        self.instrument.write("LOGM")  # Set display to log magnitude format
        data_db = self.instrument.query("OUTPFORM")  # Output format is a list of form (db, 0)
        return data_db

    #Collect phase data for a frequency sweep
    def phase_data(self, type_freq_sweep):
        self.freq_sweep_type(type_freq_sweep)
        self.instrument.write("PHAS")  # Set display to phase format
        data_degree = self.instrument.query("OUTPFORM")  # Output format is a list of form (degrees, 0)
        return data_degree

    # Collect frequency sweep data for all s-parameters
    def sparam_data(self, type_freq_sweep):

        # Collect data for s-parameter S11
        print("Collecting s11 data...")
        self.instrument.write("S11")
        s11_db = self.logmag_data(type_freq_sweep)
        s11_degree = self.phase_data(type_freq_sweep)

        # Collect data for s-parameter S12
        print("Collecting s12 data...")
        self.instrument.write("S12")
        s12_db = self.logmag_data(type_freq_sweep)
        s12_degree = self.phase_data(type_freq_sweep)

        # Collect data for s-parameter S21
        print("Collecting s21 data...")
        self.instrument.write("S21")
        s21_db = self.logmag_data(type_freq_sweep)
        s21_degree = self.phase_data(type_freq_sweep)

        # Collect data for s-parameter S22
        print("Collecting s22 data...")
        self.instrument.write("S22")
        s22_db = self.logmag_data(type_freq_sweep)
        s22_degree = self.phase_data(type_freq_sweep)

        self.instrument.write("NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

        #Set the frequency by using start/stop freq and default number of points (for demo) --> THIS DOES WEIRD THINGS, REPLACE WITH GPIB COMMAND
        freq = []
        i = 1.01
        while i <= 3.01:
            freq.append(i)
            i = i + (3-1)/201
        # freq_rounded = [round(elem, 3) for elem in freq]

        #Format the data (convert the raw VNA output to a numpy array):
        s11_db_only = self.data_formatting(s11_db)
        s11_degree_only = self.data_formatting(s11_degree)
        s12_db_only = self.data_formatting(s12_db)
        s12_degree_only = self.data_formatting(s12_degree)
        s21_db_only = self.data_formatting(s21_db)
        s21_degree_only = self.data_formatting(s21_degree)
        s22_db_only = self.data_formatting(s22_db)
        s22_degree_only = self.data_formatting(s22_degree)

        #return one large array which can be easily parsed into file columns
        return np.array([freq, s11_db_only, s11_degree_only, s12_db_only, s12_degree_only, s21_db_only, s21_degree_only, s22_db_only, s22_degree_only], dtype=object)

    #Remove column of 0's from VNA's output data by reformatting and splitting the input data string to create a list with all 0's at odd list indices
    def data_formatting(self, data):
        data_col1 = data.replace(" ", "").replace("\n", ",").split(',')[0::2] #[0::2] takes every other list element starting at index 0

        return np.array(data_col1[:-1], dtype=float)

    def file_save(self, filename, data): #Do we want to pass in user comments too?
        print("\nSaving collected data to: " + filename)
        data_transpose = data.T
        col_names = "Freq (GHz), S11 Mag (dB), S11 Phase (deg), S12 Mag (dB), S12 Phase (deg), S21 Mag (dB), S21 Phase (deg), S22 Mag (dB), S22 Phase (deg)" #Will frequency ever not be GHz?
        np.savetxt(filename, data_transpose, delimiter=',', header=col_names, comments="") #More specification options available

    def plot(self, filename):
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

    #Set a marker on the VNA display and print the value to the command line
    def marker(self, freq_val):
        self.instrument.write("MARK1 " + freq_val) #Can set up to 4 marks
        print(self.instrument.query("OUTPMARK")) #(dB or degree, ?, freq)

def main():
    print("Beginning execution of VNA commands")
    print("-----------------------------------")
    hp8719a = VNA_HP8719A(16) #DO WE WANT TO RESET HERE EVERYTIME OR JUST CALL THE RESET FUNCTION IN MAIN?
    if hp8719a.instrument:
        hp8719a.init_freq_sweep("2 GHz", "2.5 GHz")  #Set the desired frequency range
        data_out = hp8719a.sparam_data(1)             #Measure the data (dB and degree for all s-param)
        hp8719a.file_save("antenna_s_params2.csv", data_out) #Store the data
        hp8719a.plot("antenna_s_params2.csv")                #Plot the data

    # hp8719a.marker("2 GHz") #Can use to verify values at a freq

if __name__ == "__main__":
    main()