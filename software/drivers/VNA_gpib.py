import pyvisa
import matplotlib.pyplot as plt
import numpy as np
import time

from utils import util

DEF_FREQ_MODE = "lin"
DEF_DEV_ADDR = 16
DEF_S_PARAMS = "S21"

ALLOWED_NUM_POINTS = (3, 11, 21, 51, 101, 201, 401, 801, 1601)
ALLOWED_FREQ_MODES = (DEF_FREQ_MODE, "log")


def printMsg(curr_phase, msg):
    util.printf(curr_phase, None, msg)


def printError(curr_phase, msg):
    util.printf(curr_phase, "Error", msg)


class VNA_HP8719A:
    def __init__(self, sparam_list, address=16, freq_mode="lin"):
        self.address = address
        self.freq_mode = freq_mode
        self.sparam_list = sparam_list
        self.instrument = self.connect_VNA()
        self.instrument.write('POWE 0')
        self.instrument.write('AVERON')
        self.instrument.write('AVERFACT 20')
        self.instrument.write('S21')
        self.instrument.write('LOGM')

    def connect_VNA(self):
        curr_phase = 'Setup'
        rm = pyvisa.ResourceManager()  # Download https://www.keysight.com/main/software.jspx?id=2175637&pageMode=CV&cc=US&lc=eng
        # print("All connected GPIB devices: ")
        # print(rm.list_resources()) #this prints all connected devices (not needed in code but should run once to get device name)
        # print("")
        try:
            instrument = rm.open_resource('GPIB0::%d::INSTR' % self.address)  # Open the VNA connection
            instrument.timeout = 30000
        except:
            return False
        # instrument.read_termination = '\n'      #Set the read termination character  (due to VNA's data output, this truncated the output data too early)
        # instrument.write_termination = '\n'     #Set the write termination character
        identify = instrument.query("*IDN?")  # Query the instrument to ensure it is connected
        printMsg(curr_phase, "Selected GPIB device: " + identify)
        if "HEWLETT PACKARD,8719A" in identify:  # If the instrument is correctly found
            instrument.write("*RST")  # Reset to default setup
            instrument.write("FORM4")  # Set input/output data format to ASCII
            return instrument
        else:
            printError(curr_phase, "Error: An instrument other than the VNA HP8719A has been connected."
                                   " Please connect the correct instrument or run alternative code.")
            return False

            # To Do: manual triggereing
            # Do we want more features such as setting channel 2?
            # Is the Identify Error too specific? --> Note in User Manual where it's located in case they need to disable it?

    # Return instrument to default state
    def reset(self):
        self.instrument.write("*RST")

    # Set start and stop freq. Note: Must pass in frequency units as "X GHz" or "X MHz"
    # Also sets number of points and lin vs log freq sweep type
    def init_freq_sweep(self, start_freq, stop_freq, num_pts):
        curr_phase = 'Running'
        printMsg(curr_phase, "Setting frequency range from " + start_freq + " to " + stop_freq + " with " + str(
            num_pts) + " points")
        self.instrument.write("STAR " + start_freq)
        self.instrument.write("STOP " + stop_freq)
        self.instrument.write("POIN " + str(
            num_pts))  # Will round up to be one of the following values: 3, 11, 21, 51, 101, 201, 401, 801, 1601
        # NOTE: there is a min freq span for each number of points see operating manual page 52
        self.freq_sweep_type()  # Set the freq sweep mode for all following measurements (lin or log)

        self.degree = self.instrument.query('OUTPFORM')

        # Checking if Start and Stop Freq changed due to selected number of points or log freq sweep
        real_start_freq = self.instrument.query("STAR?")  # Ask VNA for set start frequency
        real_stop_freq = self.instrument.query("STOP?")  # Ask VNA for set stop frequency
        self.instrument.write(
            "NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

        # Check if the span is too small for log freq sweep (automatically defaults to lin sweep in that case)
        if self.freq_mode == "log" and int(self.instrument.query("LOGFREQ?")) == 0:
            printError(curr_phase, "You need > 2 octaves in span to run a logarithmic frequency sweep")
            return False, real_start_freq, real_stop_freq

        user_start_freq = start_freq.split(" ")  # Split the units from the number for start freq
        if user_start_freq[1] == "GHz":
            user_start_freq[0] = float(user_start_freq[0]) * 10 ** 9  # Convert from GHz to Hz
        elif user_start_freq[1] == "MHz":
            user_start_freq[0] = float(user_start_freq[0]) * 10 ** 6  # Convert MHz to Hz
        else:
            printError(curr_phase, "Units other than MHz or GHz were used")
            return False, real_start_freq, real_stop_freq  # Note returns as string not float

        user_stop_freq = stop_freq.split(" ")  # Split the units from the number for start freq
        if user_stop_freq[1] == "GHz":
            user_stop_freq[0] = float(user_stop_freq[0]) * 10 ** 9  # Convert from GHz to Hz
        elif user_stop_freq[1] == "MHz":
            user_stop_freq[0] = float(user_stop_freq[0]) * 10 ** 6  # Convert MHz to Hz
        else:
            printError(curr_phase, "Units other than MHz or GHz were used")
            return False, real_start_freq, real_stop_freq  # Note returns as string not float

        if float(real_start_freq) - user_start_freq[0] != 0 or float(real_stop_freq) - user_stop_freq[0] != 0:
            return False, real_start_freq, real_stop_freq  # Note returns as string not float
        else:
            return True, real_start_freq, real_stop_freq  # Note returns as string not float

        # Do we care about setting CENTER or SPAN:FULL/SPAN:LINK ?

    # Select the ype of frequency sweep (linear or logarithmic)
    def freq_sweep_type(self):
        curr_phase = "Running"
        if self.freq_mode == "log":
            self.instrument.write(
                "LOGFREQ")  # Select logarithmic frequency sweep - NOTE: requires at least 2 octave span
        elif self.freq_mode == "lin":
            self.instrument.write("LINFREQ")  # Select linear frequency sweep
        else:
            printError(curr_phase, "Entered a non-valid frequency sweep type")
            return False

    # Collect frequency value at each data point
    def freq_data(self):
        try:
            data_hz = self.instrument.query("OUTPLIML")  # Output format is a list of form (MHz or GHz, -1 or 0, 0, 0)
        except Exception as e:
            print(e)
            return False
        return data_hz

    # Collect logarithmic magnitude data for a frequency sweep
    def logmag_data(self):
        # self.instrument.write("LOGM")  # Set display to log magnitude format
        # time.sleep(5)
        try:
            start_time = time.perf_counter_ns()
            self.instrument.write('AVERREST')
            time.sleep(2.5)
            # self.instrument.write('NUMG 20')
            # self.instrument.query('OPC?')
            data_db = self.instrument.query("OUTPFORM")  # Output format is a list of form (db, 0)
            end_time = time.perf_counter_ns()
            total_time = (end_time - start_time) / (10 ** 9)
            # print(f"Magnitude data time in s: {total_time}")
        except Exception as e:
            print(e)
            return False
        return data_db

    # Collect phase data for a frequency sweep
    def phase_data(self):
        self.instrument.write("PHAS")  # Set display to phase format
        # time.sleep(5)
        try:
            start_time = time.perf_counter_ns()
            data_degree = self.instrument.query("OUTPFORM")  # Output format is a list of form (degrees, 0)
            end_time = time.perf_counter_ns()
            total_time = (end_time - start_time) / (10 ** 9)
            # print(f"Phase data time in s: {total_time}")
        except Exception as e:
            print(e)
            return False
        return data_degree

    # Collect data for the specified sparam
    def sparam_select(self, sparam):
        # Collect data for selected s-parameter
        curr_phase = "Running"
        printMsg(curr_phase, "Collecting " + sparam + " data...")
        # self.instrument.write(sparam)
        # time.sleep(5)
        db = self.logmag_data()
        # if not db:
        #     print("Error on logmag data collection exiting now ")
        #     return [], []
        # time.sleep(20)
        degree = self.degree  # self.phase_data()
        # time.sleep(20)

        if db is False or degree is False:
            printError(curr_phase, "Ran into an error during data collection")
            return [], []
        else:
            # Format the data (convert the raw VNA output to a numpy array):
            db_only = self.data_formatting(db, False)
            degree_only = self.data_formatting(degree, False)

            # return np.array([db_only, degree_only], dtype=object) #Return a single array of data for the sparam
            return db_only, degree_only

    # Collect frequency sweep data for the chosen s-parameters
    def sparam_data(self):

        data_all = []
        col_names = []

        if "S11" in self.sparam_list:
            s11_db, s11_deg = self.sparam_select("S11")

            if not len(s11_db) or not len(s11_deg):
                # self.instrument.write("NOOP")
                self.reset()
                return False, False
            else:
                data_all.append(s11_db)
                data_all.append(s11_deg)
                col_names.append("S11 (db)")
                col_names.append("S11 (deg)")

        if "S12" in self.sparam_list:
            s12_db, s12_deg = self.sparam_select("S12")

            if not len(s12_db) or not len(s12_deg):
                # self.instrument.write("NOOP")
                self.reset()
                return False, False
            else:
                data_all.append(s12_db)
                data_all.append(s12_deg)
                col_names.append("S12 (db)")
                col_names.append("S12 (deg)")

        if "S21" in self.sparam_list:
            s21_db, s21_deg = self.sparam_select("S21")

            if not len(s21_db) or not len(s21_deg):
                # self.instrument.write("NOOP")
                self.reset()
                return False, False
            else:
                data_all.append(s21_db)
                data_all.append(s21_deg)
                col_names.append("S21 (db)")
                col_names.append("S21 (deg)")

        if "S22" in self.sparam_list:
            s22_db, s22_deg = self.sparam_select("S22")

            if not len(s22_db) or not len(s22_deg):
                # self.instrument.write("NOOP")
                self.reset()
                return False, False
            else:
                data_all.append(s22_db)
                data_all.append(s22_deg)
                col_names.append("S22 (db)")
                col_names.append("S22 (deg)")

        # This must be run after sparam data is collected due to the nature of the GPIB command
        freq = self.freq_data()  # Collect frequency data for each data point in the sweep defined by init_freq_sweep()

        if freq is False:
            # self.instrument.write("NOOP")
            self.reset()
            return False, False
        else:
            freq_only = self.data_formatting(freq,
                                             True)  # Format the data (convert the raw VNA output to a numpy array)
            # data_all.append(freq_only)
            # col_names.append("Freq (Hz)")
            data_all.insert(0, freq_only)
            col_names.insert(0, "Freq (Hz)")

        # self.instrument.write("NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

        # Return a dictionary containing the collected data
        return data_all, col_names

    # Remove extra columns of 0's from VNA data
    def data_formatting(self, data, freq):
        if freq:
            data_col1 = data.replace(" ", "").replace("\n", ",").split(',')[
                        0::4]  # [0::4] takes every 4th list element starting at index 0
        else:
            data_col1 = data.replace(" ", "").replace("\n", ",").split(',')[
                        0::2]  # [0::2] takes every other list element starting at index 0

        return np.array(data_col1[:-1], dtype=float)

    def file_save(self, filename, data, col_names):  # Do we want to pass in user comments too?
        print("\nSaving collected data to: " + filename)
        data_transpose = data.T
        # col_names = "Freq (GHz), S11 Mag (dB), S11 Phase (deg), S12 Mag (dB), S12 Phase (deg), S21 Mag (dB), S21 Phase (deg), S22 Mag (dB), S22 Phase (deg)" #Will frequency ever not be GHz?
        np.savetxt(filename, data_transpose, delimiter=',', header=col_names,
                   comments="")  # More specification options available

    def plot(self, filename):
        print("Plotting data stored in: " + filename)
        freq, s11_db, s11_degree, s12_db, s12_degree, s21_db, s21_degree, s22_db, s22_degree = np.loadtxt(filename,
                                                                                                          delimiter=',',
                                                                                                          skiprows=1,
                                                                                                          comments="#",
                                                                                                          unpack=True)

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

    # Set a marker on the VNA display and print the value to the command line
    def marker(self, freq_val):
        self.instrument.write("MARK1 " + freq_val)  # Can set up to 4 marks
        print(self.instrument.query("OUTPMARK"))  # (dB or degree, ?, freq)


def main():
    import csv_functions as csv_f
    print("Beginning execution of VNA commands")
    print("-----------------------------------")
    num_param_points = 801
    current_theta_val = 1
    current_phi_val = 2
    current_probe_phi_val = 3
    sparams_all = ['S11 (db)', 'S11 (deg)', 'S12 (db)', 'S12 (deg)', 'S21 (db)', 'S21 (deg)', 'S22 (db)', 'S22 (deg)']
    sparams_taken = []

    col_names = ['Freq (Hz)', 'Test Phi (deg)', 'Test Theta (deg)', 'Probe Phi (deg)', 'S11 (db)', 'S11 (deg)',
                 'S12 (db)', 'S12 (deg)', 'S21 (db)', 'S21 (deg)', 'S22 (db)', 'S22 (deg)']
    # VNA creation
    hp8719a = VNA_HP8719A("S11, S12, S21, S22", 16, freq_mode="lin")
    if hp8719a.instrument:
        # Collect data
        hp8719a.init_freq_sweep("100 MHz", "10 GHz", num_param_points)
        data_out, test = hp8719a.sparam_data()

        # insert data into array
        t_t = [current_theta_val] * num_param_points
        t_p = [current_phi_val] * num_param_points
        p_p = [current_probe_phi_val] * num_param_points
        data_out.insert(1, t_t)
        data_out.insert(2, t_p)
        data_out.insert(3, p_p)
        freq = data_out[0][0]
        print(freq)
        data_to_save = np.array(data_out, dtype=object)
        data = np.array([[-1]] * len(col_names))
        # data = data.T
        csv_f.createCSV("outFile", col_names, data)
        csv_f.appendToCSV("outFile", data_to_save)
        return freq
    else:
        print("Error device not connected")


def plot_main(freq):
    import plotting as plots
    data_file = "C:\\Users\\elena\\Documents\\College\\Automated-Anechoic-Chamber\\software\\data\\outFile.csv"
    plot_file = "C:\\Users\\elena\\Documents\\College\\Automated-Anechoic-Chamber\\software\\data\\outPlot.jpg"
    plots.plot3DRadPattern(data_file, plot_file, 'S21', freq)

    # Notes 4/3:
    # Make sure Elena's code passes units as GHz or MHz (capitalzation is important) --> need any other units?
    # Does Elena want real start/stop freq as strings or floats? (currently strings)
    # log sweep must be > 2 octave span --> discuss how to handle this with Elena
    #   #[should I also return a variable that indicates it isn't a log sweep? -> if want to say lin vs. log I should add code to check LINFREQ? as well
    # Is handling of bad OUTP command okay?
    # Do I need to add try/except stuff in the initialization of frequency? Or other place where weird time out errors occur such as IDN
    # Issue: if I trigger an error, when I run the code again it timesout on the connection command which makes me think I'm
    # not exiting properly but I can't write more commands in the session once its timed out.... (ie adding NO{ command before returning
    # False creates an error
    # Should I place NOPs after every query command instead of doing it once at the end of each function init_freq and sparam?
    # Should i try reset instead of NOP?
    # All errors seem to be timeout errors so far (which seem to occur inconsistenly)

    # THINGS TO TRY:
    # In main, put try catch around commands to see if that'll catch exceptions
    # Ask what to default to lin vs log freq sweep? _. lin
    # Maybe add check if it's in lin mode if it fails the log mode check
    # Test more string sparam inputs

    # IF SPAN IS NOT 2 OCTAVES BUT LOG MODE SELECTED, DON'T RUN MY CODE (check that span is > 2, not >=)
    # Add __dil__ function to disconnect?

    # hp8719a.reset()
    # hp8719a.marker("2 GHz") #Can use to verify values at a freq

# if __name__ == "__main__":
# for i in range(0,3):
#    freq = main()
# freq = 1.000000000000000000e+09
# plot_main(freq)