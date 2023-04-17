# Script to prepare mSEED files for QuakeMigrate input in 12 x 2-hr chunks

# Import modules
import os
import warnings
import numpy as np
from glob import glob
from obspy import read

# Suppress UserWarning due to centering converting data dtype from integer to float
# ObsPy automatically chooses a suitable encoding when writing the centered mSEED data
warnings.simplefilter("ignore", UserWarning)

# Change these only
# -----------------------------------------------------------------------------------
strms = sorted(glob("/path/to/folder/*.mSEED*"))  # List of chronological mSEED files
channels = ["HHZ", "HHN", "HHE"]  # Seismogram channels
input_path_QM = "/path/to/QM/input/folder/year/"  # QuakeMigrate input year folder
# -----------------------------------------------------------------------------------

# Loop through mSEED files
chunk = 0  # Index of day chunks
for s in strms:
    strm = read(s)
    print(len(strm), "traces:")

    # Group traces based on channel
    vert = strm.select(channel=channels[0])
    horz1 = strm.select(channel=channels[1])
    horz2 = strm.select(channel=channels[2])
    comps = [vert, horz1, horz2]

    # Zero-center trace data
    vert_c, horz1_c, horz2_c = [], [], []
    for comp in comps:
        for trc in comp:
            trc.data = trc.data - np.mean(trc.data)
            print(trc)
            if trc.stats.channel == channels[0]:
                vert_c.append(trc)
            elif trc.stats.channel == channels[1]:
                horz1_c.append(trc)
            elif trc.stats.channel == channels[2]:
                horz2_c.append(trc)
    comps_c = [vert_c, horz1_c, horz2_c]
    print("\n")

    # Get trace temporal data information
    year = str(trc.stats.starttime.year)  # Year
    jul = trc.stats.starttime.strftime("%j")  # Julian day
    time = trc.stats.starttime  # Start time
    time_str = (
        str(time.hour).rjust(2, "0")
        + str(time.minute).rjust(2, "0")
        + str(time.second).rjust(2, "0")
    )  # Reformat start time to HHMMSS

    # Create QuakeMigrate-formatted input mSEED destination folders
    # Assumptions:
    # 1. The chunk size are 2-hrs, but other sizes are accepted as long as...
    # 2. The strms mSEED files are in chronological order and cover one full day
    # 3. The first and last strms mSEED files are the start and end chunks of the day
    dests = []
    if chunk != 0 and chunk != len(strms) - 1:
        df = input_path_QM + jul + "_" + str(chunk)
        dests.append(df)
    elif chunk == 0:  # Add buffer folder at the start of the day
        df_buffer = input_path_QM + jul + "_buffer"
        jul_endtime = trc.stats.endtime.strftime("%j")
        df = input_path_QM + jul_endtime + "_" + str(chunk)
        dests.extend([df_buffer, df])
    elif chunk == len(strms) - 1:  # Add buffer folder at the end of the day
        df = input_path_QM + jul + "_" + str(chunk)
        jul_endtime = trc.stats.endtime.strftime("%j")
        df_buffer = input_path_QM + jul_endtime + "_buffer"
        dests.extend([df, df_buffer])
    chunk += 1
    for dest in dests:
        if not os.path.isdir(dest):
            os.makedirs(dest)  # Create all directories that do not already exist

        # Write QuakeMigrate-formatted input mSEED for each station-channel trace
        for c in comps_c:
            for trce in c:
                sta = trce.stats.station  # Station
                cha = trce.stats.channel  # Channel
                filename = (
                    year + jul + "_" + time_str + "_" + sta + "_" + cha + ".mseed"
                )
                trce.write(dest + "/" + filename, format="MSEED")

print("mSEED files prepared for QuakeMigrate input")
