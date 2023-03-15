# Script to center data and reformat mSEED files for QuakeMigrate input

# Import modules
import warnings
import os, glob
import numpy as np
from obspy import read

warnings.simplefilter("ignore", UserWarning)
# Change these only
strms = sorted(
    glob.glob("/path/to/mSEED/folder/*day.mSEED*")
)  # Sorted list of mSEED files
channels = ["HHZ", "HHE", "HHN"]  # Seismogram channels corresponding to components
input_path_QM = "/path/to/QM/input/folder/year/"  # QuakeMigrate input folder (year)

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

    # Center data
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

    # Prepare QuakeMigrate input folder
    year = str(trc.stats.starttime.year)  # Year
    jul = trc.stats.starttime.strftime("%j")  # Julian day
    time = trc.stats.starttime  # Start time
    time_str = (
        str(time.hour).rjust(2, "0")
        + str(time.minute).rjust(2, "0")
        + str(time.second).rjust(2, "0")
    )  # Reformat start time to HHMMSS
    dest = (
        input_path_QM + jul + "_" + str(chunk)
    )  # Reformatted mSEED destination folder
    chunk += 1
    if not os.path.isdir(dest):
        os.mkdir(dest)  # Create lowest level directory if it does not already exist

    # Loop through each station-channel trace and write reformatted mSEED files
    for c in comps_c:
        for trce in c:
            s = trce.stats.station  # Station
            cha = trce.stats.channel  # Channel
            filename = year + jul + "_" + time_str + "_" + s + "_" + cha + ".mseed"
            trce.write(dest + "/" + filename, format="MSEED")

print("QM input files written")
