"""
Script to perform multiple, sequential QuakeMigrate runs in the same year

Inputs:
    - QuakeMigrate-formatted input mSEED files
    - QuakeMigrate run scripts

Outputs:
    - QuakeMigrate run outputs
"""

# --- Import modules ---
import os
import subprocess
import sys
import time
from pathlib import Path
from obspy import UTCDateTime

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
mseed_path = Path("./inputs/mSEED")  # QuakeMigrate inputs mSEED directory

# Detect, trigger, and locate QuakeMigrate script names (in order)
qm_scripts = [
    Path("./sample_detect.py"),  # Detect
    Path("./sample_trigger.py"),  # Trigger
    Path("./sample_locate.py"),  # Locate
]

# Corresponding run.py and reset.py script names
run_script = Path("./sample_run.py")  # Run
reset_script = Path("./sample_reset.py")  # Reset

# QuakeMigrate run name
qm_run_name = "sampleQM"

# Run year
year = "2023"

# Time buffer (in seconds) to prevent data gaps during QuakeMigrate runs
time_buffer = 5 * 60  # 5 minutes (300 seconds)

# Detect stage time buffer (in seconds)
det_buffer = 4 * 60  # 4 minutes (240 seconds)

# Choose the type of data time intervals:
# 1: Regular time chunks (consecutive, uniform intervals)
# 2: Custom times (specific, variable intervals)
time_type = 1

# Start time of your selected starting time chunk in the processing window
# Must be an integer multiple of chunk_size from the start time of the initial time chunk
# Ignore if using custom times
selected_starttime = UTCDateTime("2023-01-06T00:00:00.000000Z")

# Number and size (in seconds) of time chunks, ignore if using custom times
time_chunks = 4
chunk_size = 2 * 60 * 60  # 2 hours (7200 seconds)

# Custom start and end times, ignore if using regular time chunks
times = [
    [
        UTCDateTime("2019-01-06T00:00:00.000000Z"),  # Start time
        UTCDateTime("2019-01-06T00:32:00.000000Z"),  # End time
    ],
    [
        UTCDateTime("2019-01-24T09:24:00.000000Z"),  # Start time
        UTCDateTime("2019-01-24T09:28:00.000000Z"),  # End time
    ],
    [
        UTCDateTime("2019-01-12T01:00:00.000000Z"),  # Start time
        UTCDateTime("2019-01-12T01:24:00.000000Z"),  # End time
    ],
]

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Set QuakeMigrate template times ---
    qm_starttime = "yyyy-mm-ddT00:00:00.000000Z"  # Start time
    qm_endtime = "yyyy-mm-ddT00:00:00.000001Z"  # End time

    # --- Initial QuakeMigrate scripts reset ---
    python_interpreter = sys.executable  # Dynamic Python interpreter selection
    subprocess.run([python_interpreter, str(reset_script)], check=True)

    # --- Generate pairs of start and end times ---
    if time_type == 1:  # Regular time chunks
        times = [
            [
                (selected_starttime + t * chunk_size),
                (selected_starttime + (t + 1) * chunk_size),
            ]
            for t in range(time_chunks)
        ]
    elif time_type == 2:  # Custom times
        times.sort()  # Sort times chronologically
        times = times
    else:
        time_type_error = "Invalid time_type value; must be 1 or 2"
        raise ValueError(time_type_error)

    # --- Run QuakeMigrate for each pair of start/end times ---
    for start, end in times:
        # Define run name
        start_str = start.strftime("%Y%m%d%H%M%S%f")
        end_str = end.strftime("%Y%m%d%H%M%S%f")
        run_name = f"{qm_run_name}_{start_str}_{end_str}"

        # Detect buffered start/end times
        det_start = f"{start - det_buffer}"
        det_end = f"{end + det_buffer}"

        # Update QuakeMigrate scripts
        for script in qm_scripts:
            content = script.read_text()

            if "detect" in script.name:  # Update detect
                content = content.replace(qm_starttime, det_start).replace(
                    qm_endtime, det_end
                )
            else:  # Update trigger and locate
                content = content.replace(qm_starttime, str(start)).replace(
                    qm_endtime, str(end)
                )

            content = content.replace(qm_run_name, run_name)
            script.write_text(content)  # Write modified string back to file
            time.sleep(1.0)  # Ensure sequential script updates

        # mSEED directories to unlock and lock
        input_yr = Path(mseed_path / year)
        start_buffer = (start - time_buffer).strftime("%Y%m%d%H%M%S%f")
        end_buffer = (end + time_buffer).strftime("%Y%m%d%H%M%S%f")
        unlockables = [
            (input_yr / f.name, input_yr / f.name.split("_")[0])
            for f in input_yr.glob(f"*{start_buffer}_{end_buffer}*")
        ]

        # Unlock mSEED directories and run QuakeMigrate scripts
        try:
            for locked, unlocked in unlockables:
                os.rename(str(locked), str(unlocked))

            subprocess.run([python_interpreter, str(run_script)], check=True)

        # Log errors and raise an exception to exit the try block
        except Exception as e:
            log_file = Path(f"{run_name}_log.txt")  # Error log file
            with open(log_file, "a") as log:
                log.write(f"Error occurred: {e}\n")
            raise RuntimeError(f"Error occurred: {e}")

        # Relock mSEED directories and reset QuakeMigrate scripts
        finally:
            for locked, unlocked in unlockables:
                os.rename(str(unlocked), str(locked))

            subprocess.run([python_interpreter, str(reset_script)], check=True)

    print("################################################")
    print("QuakeMigrate runs completed")
    print("################################################")
