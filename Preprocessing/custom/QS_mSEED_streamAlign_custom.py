# Script to align mSEED stream trace times for a specific time window(s)

# Import modules
import os, sys
from obspy import read
from obspy import UTCDateTime

# Change these only
# -------------------------------------------------------------------------
strms = [
    "/path/to/folder/xyz.mseed",
    "/path/to/folder/mno.mseed",
    "/path/to/folder/abc.mseed",
]  # List of mSEED files
fs = 1000  # Trace sampling frequency, in Hz
# List of original start times in UTCDateTime
starttimes = [
    UTCDateTime("2019-01-03T23:55:00.000000"),  # xyz's original start time
    UTCDateTime("2023-05-05T01:00:00.000000"),  # mno's original start time
    UTCDateTime("2019-01-23T09:23:00.000000"),  # abc's original start time
]
# -------------------------------------------------------------------------

# Loop through mSEED files
if len(strms) != len(starttimes):
    print("Error: number of mSEED files and original start times do not match")
    sys.exit(1)

# Align traces to original start time
for s in range(len(strms)):
    strm = read(strms[s])  # Read mSEED file
    starttime = starttimes[s]  # Original start time
    shifts = []  # List of time shifts
    for tr in strm:
        shift = starttime - tr.stats.starttime  # Required time shift
        if shift < (1 / fs):  # Check if time shift < sampling period
            tr.stats.starttime += shift  # Apply time shift
            shifts.append(shift)  # Record time shift
        else:
            print("Error: time shift is greater than or equal to sampling period")
            print(tr)
            sys.exit(1)

    # Write aligned mSEED files into an "aligned" subfolder
    print("Indexed time shifts:", [(i, ts) for i, ts in enumerate(shifts)])
    print(strm.__str__(extended=True), "\n")
    splitstrm = strms[s].split("/")
    if not os.path.isdir("/".join(splitstrm[:-1]) + "/aligned"):
        os.makedirs(
            "/".join(splitstrm[:-1]) + "/aligned"
        )  # Create all directories that do not already exist
    strm.write(
        "/".join(splitstrm[:-1]) + "/aligned/aligned_" + splitstrm[-1], format="MSEED"
    )

print("Stream trace times aligned")
