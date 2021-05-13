"""
    List of error codes and their corresponding causes.
"""
SUCCESS          = 0  # Routine executed with no issues detected
CONNECTION       = 1  # Could not connect to any motor driver PCBs
CONNECTION_PROBE = 2  # Could not connect to a probe motor driver PCB
CONNECTION_TEST  = 3  # Could not connect to a test motor driver PCB
DISTINCT_IDS     = 4  # Connected to two motor driver PCBs, but both had the same ID
VNA              = 5  # Could not connect to the VNA
TEST_THETA_FAULT = 6  # Fault signal from test-theta motor
TEST_PHI_FAULT   = 7  # Fault signal from test-phi motor
PROBE_PHI_FAULT  = 8  # Fault signal from probe-phi motor
ALIGNMENT        = 9  # Alignment routine was not successful
BAD_ARGS         = 10 # Invalid arguments passed to routine
MISC             = 11 # Error other than those specified above
STOPPED          = 12 # The user issued a keyboard interrupt to stop the program.
CALIBRATION      = 13 # The user needs to calibrate the motor before running this command.