# Script to prepare mSEED files for QuakeMigrate input for a specific time window(s)

# Import modules
import os
import warnings
import numpy as np
from obspy import read

# Suppress UserWarning due to centering converting data dtype from integer to float
# ObsPy automatically chooses a suitable encoding when writing the centered mSEED data
warnings.simplefilter("ignore", UserWarning)

# Change these only
# --------------------------------------------------------------------------------
strms = [
    "/path/to/folder/aligned/aligned_xyz.mseed",
    "/path/to/folder/aligned/aligned_mno.mseed",
    "/path/to/folder/aligned/aligned_abc.mseed",
]  # List of mSEED files
channels = ["HHZ", "HHN", "HHE"]  # Seismogram channels
# Important assumption: All strms mSEED files are for the same year
input_path_QM = "/path/to/QM/input/folder/year/"  # QuakeMigrate input year folder
# --------------------------------------------------------------------------------

# Loop through mSEED files
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
    dests = []
    label = s.split("/")[-1].split(".")[0]
    jul_starttime = trc.stats.starttime.strftime("%j")
    jul_endtime = trc.stats.endtime.strftime("%j")
    if jul_starttime == jul_endtime:
        df = input_path_QM + jul + "_" + label
        dests.append(df)
    else:
        # Add buffer folders if mSEED data covers more than one day
        df_startBuffer = input_path_QM + jul_starttime + "_" + label + "_buffer"
        df_endBuffer = input_path_QM + jul_endtime + "_" + label + "_buffer"
        dests.extend([df_startBuffer, df_endBuffer])
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
