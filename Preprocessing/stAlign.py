# Script to align stream trace times

# Import modules
import sys
from glob import glob
from obspy import read
from obspy import UTCDateTime

# Change these only
# -------------------------------------------------------------------------------------
strms = sorted(glob("/path/to/folder/*.mseed*"))  # List of mSEED files
fs = 1000  # Trace sampling frequency, in Hz
chunk = 7200  # Chunk size of streams, in seconds
# List of original start times in UTCDateTime
starttimes = [UTCDateTime("2023-01-30T23:55:00.000000") + c * chunk for c in range(12)]
# -------------------------------------------------------------------------------------

# Loop through mSEED files
if len(strms) != len(starttimes):
    print("Error: listed number of mSEED files and original start times do not match")
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

    # Write aligned mSEED files
    print("Indexed time shifts:", [(i, ts) for i, ts in enumerate(shifts)])
    print(strm.__str__(extended=True), "\n")
    splitstrm = strms[s].split("/")
    strm.write("/".join(splitstrm[:-1]) + "/aligned_" + splitstrm[-1], format="MSEED")

print("Stream trace times aligned")
