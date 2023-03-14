# Script to align trace times within a stream

# Import modules
import glob
from obspy import read

# Change these only
strms = sorted(glob.glob("/path/to/folder/*.mseed*"))  # Sorted list of mSEED files
fs = 1000  # Trace sampling frequency

# Loop through mSEED files
for s in strms:
    strm = read(s)
    starttimes = [t.stats.starttime for t in strm]  # Start times of all stream traces

    # Apply alignment
    shift = max(starttimes) - min(starttimes)  # Compute the time shift
    if shift < (1 / fs):  # Less than sampling frequency
        for tr in strm:
            if tr.stats.starttime < max(starttimes):
                tr.stats.starttime += shift  # Align streams nominally

    # Write aligned mSEED files
    print(shift, "shift")
    print(strm.__str__(extended=True), "\n")
    splitstr = s.split("/")
    strm.write("/".join(splitstr[:-1]) + "/aligned_" + splitstr[-1], format="MSEED")

print("Streams aligned")
