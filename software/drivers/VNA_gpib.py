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


def printMsg(curr_phase,msg):
    """
    Prints a message using the formatting from util.py
    :param curr_phase: Current phase of system.
    :param msg: Message
    """
    util.printf(curr_phase, None, msg)


def printError(curr_phase,msg):
    """
    Prints an error message using the formatting from util.py
    :param curr_phase: Current phase of system.
    :param msg: Message
    """
    util.printf(curr_phase, "Error", msg)


class VNA_HP8719A:
    """
    HP8719A VNA GPIB communication class. Used to communicate with the VNA device.
    """

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
        """
        Connects to the VNA.
        :return: Returns the device if connection was successful, otherwise False.
        """
        curr_phase = 'Setup'
        rm = pyvisa.ResourceManager()
        try:
            instrument = rm.open_resource('GPIB0::%d::INSTR' % self.address)  #Open the VNA connection
            instrument.timeout = 30000
        except:
            return False
        # instrument.read_termination = '\n'      #Set the read termination character  (due to VNA's data output, this truncated the output data too early)
        # instrument.write_termination = '\n'     #Set the write termination character
        identify = instrument.query("*IDN?")      #Query the instrument to ensure it is connected
        printMsg(curr_phase, "Selected GPIB device: " + identify)
        if "HEWLETT PACKARD,8719A" in identify:     #If the instrument is correctly found
            instrument.write("*RST")                #Reset to default setup
            instrument.write("FORM4")               # Set input/output data format to ASCII
            return instrument
        else:
            printError(curr_phase, "Error: An instrument other than the VNA HP8719A has been connected."
                                  " Please connect the correct instrument or run alternative code.")
            return False

    def reset(self):
        """
        Return instrument to default state
        """
        self.instrument.write("*RST")

    def init_freq_sweep(self, start_freq, stop_freq, num_pts):
        """
        Set start and stop freq. Also sets number of points and lin vs log freq sweep type
        :param start_freq: Starting frequency of frequency sweep
        :param stop_freq: Stopping frequency of frequency sweep
        :param num_pts: Number of points to take on frequency sweep
        :return:
        """
        curr_phase = 'Running'
        printMsg(curr_phase,"Setting frequency range from " + start_freq + " to " + stop_freq + " with " + str(num_pts) + " points")
        self.instrument.write("STAR " + start_freq)
        self.instrument.write("STOP " + stop_freq)
        self.instrument.write("POIN " + str(num_pts)) # Will round up to be one of the following values: 3, 11, 21, 51, 101, 201, 401, 801, 1601
        #NOTE: there is a min freq span for each number of points see operating manual page 52
        self.freq_sweep_type()  # Set the freq sweep mode for all following measurements (lin or log)
        
        
        self.degree = self.instrument.query('OUTPFORM')

        #Checking if Start and Stop Freq changed due to selected number of points or log freq sweep
        real_start_freq = self.instrument.query("STAR?") #Ask VNA for set start frequency
        real_stop_freq = self.instrument.query("STOP?")  # Ask VNA for set stop frequency
        self.instrument.write("NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

        #Check if the span is too small for log freq sweep (automatically defaults to lin sweep in that case)
        if self.freq_mode == "log" and int(self.instrument.query("LOGFREQ?")) == 0:
            printError(curr_phase,"You need > 2 octaves in span to run a logarithmic frequency sweep")
            return False, real_start_freq, real_stop_freq

        user_start_freq = start_freq.split(" ") #Split the units from the number for start freq
        if user_start_freq[1] == "GHz":
            user_start_freq[0] = float(user_start_freq[0]) * 10**9 #Convert from GHz to Hz
        elif user_start_freq[1] == "MHz":
            user_start_freq[0] = float(user_start_freq[0]) * 10**6 #Convert MHz to Hz
        else:
            printError(curr_phase,"Units other than MHz or GHz were used")
            return False, real_start_freq, real_stop_freq #Note returns as string not float

        user_stop_freq = stop_freq.split(" ")  # Split the units from the number for start freq
        if user_stop_freq[1] == "GHz":
            user_stop_freq[0] = float(user_stop_freq[0]) * 10 ** 9  # Convert from GHz to Hz
        elif user_stop_freq[1] == "MHz":
            user_stop_freq[0] = float(user_stop_freq[0]) * 10 ** 6  # Convert MHz to Hz
        else:
            printError(curr_phase,"Units other than MHz or GHz were used")
            return False, real_start_freq, real_stop_freq #Note returns as string not float

        if float(real_start_freq) - user_start_freq[0] != 0 or float(real_stop_freq) - user_stop_freq[0] != 0:
            return False, real_start_freq, real_stop_freq #Note returns as string not float
        else:
            return True, real_start_freq, real_stop_freq #Note returns as string not float

    def freq_sweep_type(self):
        """
        Select the type of frequency sweep (linear or logarithmic)
        :return: False if an error occured
        """

        curr_phase = "Running"
        if self.freq_mode == "log":
            self.instrument.write("LOGFREQ")  # Select logarithmic frequency sweep - NOTE: requires at least 2 octave span
        elif self.freq_mode == "lin":
            self.instrument.write("LINFREQ")  # Select linear frequency sweep
        else:
            printError(curr_phase,"Entered a non-valid frequency sweep type")
            return False

    #
    def freq_data(self):
        """
        Collect frequency value at each data point
        :return: The frequency data if no errors occurred, otherwise False.
        """
        try:
            data_hz = self.instrument.query("OUTPLIML")  # Output format is a list of form (MHz or GHz, -1 or 0, 0, 0)
        except Exception as e:
            print(e)
            return False
        return data_hz

    def logmag_data(self):
        """
        Collect logarithmic magnitude data for a frequency sweep
        :return: The data from the logarithmic magnitude.
        """
        self.instrument.write("LOGM")  # Set display to log magnitude format
        # time.sleep(5)
        try:
            start_time = time.perf_counter_ns()
            self.instrument.write('AVERREST')
            time.sleep(2.5)
            #self.instrument.write('NUMG 20')
            #self.instrument.query('OPC?')
            data_db = self.instrument.query("OUTPFORM")  # Output format is a list of form (db, 0)
            end_time = time.perf_counter_ns()
            total_time = (end_time - start_time) / (10 ** 9)
        except Exception as e:
            print(e)
            return False
        return data_db

    def phase_data(self):
        """
        Collect phase data for a frequency sweep
        :return: Phase data from a frequency sweep.
        """
        self.instrument.write("PHAS")  # Set display to phase format
        # time.sleep(5)
        try:
            start_time = time.perf_counter_ns()
            data_degree = self.instrument.query("OUTPFORM")  # Output format is a list of form (degrees, 0)
            end_time = time.perf_counter_ns()
            total_time = (end_time - start_time)/(10 ** 9)
            # print(f"Phase data time in s: {total_time}")
        except Exception as e:
            print(e)
            return False
        return data_degree

    def sparam_select(self, sparam):
        """
        Collect data for the specified S-Parameters
        :param sparam: S-parameters to collect data from.
        :return: Data from all S-Parameters.
        """
        # Collect data for selected s-parameter
        curr_phase = "Running"
        printMsg(curr_phase,"Collecting " + sparam + " data...")
        #self.instrument.write(sparam)
        # time.sleep(5)
        db = self.logmag_data()
        # if not db:
        #     print("Error on logmag data collection exiting now ")
        #     return [], []
        # time.sleep(20)
        degree = self.degree #self.phase_data()
        # time.sleep(20)

        if db is False or degree is False:
            printError(curr_phase,"Ran into an error during data collection")
            return [], []
        else:
            #Format the data (convert the raw VNA output to a numpy array):
            db_only = self.data_formatting(db, False)
            degree_only = self.data_formatting(degree, False)

            # return np.array([db_only, degree_only], dtype=object) #Return a single array of data for the sparam
            return db_only, degree_only

    def sparam_data(self):
        """
        Collect frequency sweep data for the chosen s-parameters
        :return: Data for the given s-parameters
        """
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

        #This must be run after sparam data is collected due to the nature of the GPIB command
        freq = self.freq_data()  # Collect frequency data for each data point in the sweep defined by init_freq_sweep()

        if freq is False:
            # self.instrument.write("NOOP")
            self.reset()
            return False, False
        else:
            freq_only = self.data_formatting(freq, True)  # Format the data (convert the raw VNA output to a numpy array)
            # data_all.append(freq_only)
            # col_names.append("Freq (Hz)")
            data_all.insert(0, freq_only)
            col_names.insert(0, "Freq (Hz)")

        #self.instrument.write("NOOP")  # No operation + sets operation bit to complete (puts VNA back in listen mode so can use front panel)

        #Return a dictionary containing the collected data
        return data_all, col_names

    def marker(self, freq_val):
        """
        Set a marker on the VNA display and print the value to the command line
        :param freq_val: Frequency to display marker at.
        :return:
        """
        self.instrument.write("MARK1 " + freq_val) #Can set up to 4 marks
        print(self.instrument.query("OUTPMARK")) #(dB or degree, ?, freq)
