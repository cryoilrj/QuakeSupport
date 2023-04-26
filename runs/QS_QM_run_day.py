# Script to run QuakeMigrate in 12 x 2-hr chunks

# Import modules
import time
import fileinput
import subprocess, os
from obspy import UTCDateTime
from datetime import datetime
from datetime import timedelta

# Change these
# -------------------------------------------------------------------
year, jd = "2023", "007"  # Target year and Julian day (3 characters)
# Names of QuakeMigrate scripts (in order)
qm_scripts = [
    "penguin_detect.py",  # Detect script
    "penguin_trigger.py",  # Trigger script
    "penguin_locate.py",  # Locate script
]
qm_run_name = "penguin_example"  # Default QuakeMigrate run name
run_path = "/path/to/QM/run/examples/folder"  # Path to run folder
# -------------------------------------------------------------------

# Default QuakeMigrate start and end times
qm_starttime = "2023-01-30T00:00:00.000000Z"  # Start time
qm_endtime = "2023-01-30T00:00:01.000000Z"  # End time

# Julian day calculations
date = datetime.strptime(year + jd, "%Y%j").strftime("%Y-%m-%d")  # YYYY-MM-DD format
jd_starttime = UTCDateTime(date + "T00:00:00.000000Z")  # Start time of Julian day
prev_jd = f"{(jd_starttime - timedelta(days=1)).julday:03}"  # Previous Julian day
next_jd = f"{(jd_starttime + timedelta(days=1)).julday:03}"  # Next Julian day

# Reset QuakeMigrate scripts before any runs
subprocess.run(["python", "QS_QM_reset.py"])

# Loop through the day (modify only if targeting specific chunks e.g., range(3, 6))
# ---------------------------------------------------------------------------------
for c in range(12):
# ---------------------------------------------------------------------------------

    # Chunk metadata
    chunk_starttime = f"{jd_starttime + timedelta(hours=2 * c)}"  # Start time
    chunk_endtime = f"{UTCDateTime(chunk_starttime) + timedelta(hours=2)}"  # End time
    chunk_run_name = f"{qm_run_name}_{year}_{jd}_{c}"  # Run name

    # Apply a 4 minute buffer to start and end times of detect script
    buffer_starttime = f"{UTCDateTime(chunk_starttime) - timedelta(minutes=4)}"
    buffer_endtime = f"{UTCDateTime(chunk_endtime) + timedelta(minutes=4)}"

    # Modify detect script
    with fileinput.FileInput(qm_scripts[0], inplace=True) as file:
        for line in file:
            line = line.replace(qm_starttime, buffer_starttime)
            line = line.replace(qm_endtime, buffer_endtime)
            line = line.replace(qm_run_name, chunk_run_name)
            print(line, end="")
    time.sleep(1)  # Enable modified scripts to be sequentially ordered

    # Modify trigger and locate scripts
    for s in range(1, 3):
        with fileinput.FileInput(qm_scripts[s], inplace=True) as file:
            for line in file:
                line = line.replace(qm_starttime, chunk_starttime)
                line = line.replace(qm_endtime, chunk_endtime)
                line = line.replace(qm_run_name, chunk_run_name)
                print(line, end="")
        time.sleep(1)  # Enable modified scripts to be sequentially ordered

    try:
        # Unlock the appropriate mSEED file(s) for QuakeMigrate to read
        locked = f"{jd}_{c}"
        os.chdir(run_path + "/inputs/mSEED/" + year)  # Navigate to mSEED folder
        os.rename(locked, jd)  # Unlock target mSEED file
        # Unlock buffer mSEED file (if applicable)
        if c == 0:
            os.rename(f"{prev_jd}_buffer", prev_jd)
        elif c == 11:
            os.rename(f"{next_jd}_buffer", next_jd)

        # Run QuakeMigrate
        os.chdir(run_path)  # Navigate back to QuakeMigrate run folder
        subprocess.run(["python", "QS_QM_run.py"])  # Run QuakeMigrate scripts

    # Failsafe ensures mSEED files and scripts are always reset
    finally:
        # Relock the mSEED file(s) after QuakeMigrate is done reading
        os.chdir(run_path + "/inputs/mSEED/" + year)  # Navigate to mSEED folder
        os.rename(jd, locked)  # Relock target mSEED file
        # Relock buffer mSEED file (if applicable)
        if c == 0:
            os.rename(prev_jd, f"{prev_jd}_buffer")
        elif c == 11:
            os.rename(next_jd, f"{next_jd}_buffer")

        # Reset QuakeMigrate scripts for next iteration
        os.chdir(run_path)  # Navigate back to QuakeMigrate run folder
        subprocess.run(["python", "QS_QM_reset.py"])  # Reset QuakeMigrate scripts

print(f"{year}_{jd} run completed")
