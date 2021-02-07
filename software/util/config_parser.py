# Include
import pydoc
import os
import json
'''
config_parser.py
This file contains functions to find, open, and.
'''


def find_config(file_name,file_path):
    # Check to see if file_name is valid
    if file_name is None or file_name == '':
        print("Error: No config file detected...")
    elif file_name.endswith(".json") is False:
        print("Error: Config file must be a json file...")
    # find the file
    cfg = open(file_name, "r")





# main
def main():
    print("\nRunning the config parser")


if __name__ == "__main__":
    main()
