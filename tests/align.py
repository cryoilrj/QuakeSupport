"""
Script to align offset stream trace times

Inputs:
    - Raw mSEED files

Outputs:
    - Aligned mSEED files
    - Run log
"""

# --- Import modules ---
import datetime
import logging
import sys
from pathlib import Path
from obspy import read, UTCDateTime

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
r_mseed_path = Path("./inputs/raw_mSEED")  # Raw mSEED directory

# Output paths
log_path = Path("./inputs/logs")  # Log directory
a_mseed_path = Path("./inputs/aligned_mSEED")  # Aligned mSEED directory

# Wildcard pattern to match raw mSEED files
# Sometimes, the wildcard may be too broad and match unwanted files
# Alternatively, point r_mseed_path to a directory containing only target files
mseed_pattern = "*.mseed"

# Trace sampling frequency (in Hz)
fs = 1000

# Time buffer (in seconds) to prevent data gaps during QuakeMigrate runs
time_buffer = 5 * 60  # 5 minutes (300 seconds)

# Choose the type of data time intervals:
# 1: Regular time chunks (consecutive, uniform intervals)
# 2: Custom times (specific, variable intervals)
time_type = 1

# Start time of the initial time chunk in the processing window
# Ignore if using custom times
starttime = UTCDateTime("2018-12-25T00:27:00.000000Z")

# Number and size (in seconds) of time chunks, ignore if using custom times
time_chunks = 3
chunk_size = 18  # 18 seconds

# Custom start times, ignore if using regular time chunks
starttimes = [
    UTCDateTime("2019-01-06T00:00:00.000000Z"),
    UTCDateTime("2019-01-24T09:24:00.000000Z"),
    UTCDateTime("2019-01-12T01:00:00.000000Z"),
]

# Verbose logging flag (includes time shift and stream information if True)
verbose_logging = False

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Ensure log directory exists ---
    log_path.mkdir(parents=True, exist_ok=True)

    # --- Set up root logger ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # --- Console logging handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logger_format)
    logger.addHandler(console_handler)

    # --- Configure file logging ---
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = log_path / f"align_{current_time}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(logger_format)
    logger.addHandler(file_handler)

    # --- Prepare start times ---
    if time_type == 1:  # Regular time chunks
        starttimes = [
            starttime - time_buffer + t * chunk_size for t in range(time_chunks)
        ]
    elif time_type == 2:  # Custom times
        starttimes = [st - time_buffer for st in starttimes]
        starttimes.sort()  # Sort start times chronologically
    else:
        time_type_error = "Invalid time_type value; must be 1 or 2"
        logging.error(time_type_error)
        raise ValueError(time_type_error)

    # --- Sort raw mSEED files chronologically ---
    strms = sorted(r_mseed_path.glob(mseed_pattern))

    # --- Check if number of mSEED files matches start times ---
    if len(strms) != len(starttimes):
        logging.error(
            f"Mismatch: {len(strms)} mSEED files vs {len(starttimes)} start times"
        )
        raise ValueError("Mismatch in number of mSEED files and start times")

    logging.info("################################################")
    logging.info("Aligning stream trace times...")
    logging.info("################################################\n")

    logging.info("Stream alignment")
    logging.info("################################################")

    # --- Align traces to original start times ---
    for strm_path, t_start in zip(strms, starttimes):
        strm = read(strm_path)  # Read stream
        strm_file_path = Path(strm_path)
        logging.info(f"Aligning {strm_file_path.name} traces...")

        shifts = []  # Time shift records
        for tr in strm:
            shift = t_start - tr.stats.starttime  # Time shift
            if shift >= (1 / fs):
                logging.error(f"Time shift for trace {tr.id} exceeds sampling period")
                raise ValueError(
                    f"Time shift for trace {tr.id} exceeds sampling period"
                )
            tr.stats.starttime += shift  # Apply time shift to trace
            shifts.append(shift)  # Record time shift

        if verbose_logging:
            # Log header
            logging.info("Trace Index | Time Shift [s] | Trace Information")
            logging.info("-----------------------------------------------------")

            # Iterate through each trace and its corresponding time shift
            for i, (trc, ts) in enumerate(zip(strm, shifts)):
                # Format each line with aligned columns
                logging.info(f"{i:<11} | {ts:<14.6f} | {trc}")
            logging.info("################################################\n")

        # Ensure aligned mSEED directory exists
        a_mseed_path.mkdir(parents=True, exist_ok=True)

        # Write stream to aligned mSEED directory
        aligned_file_path = a_mseed_path / f"aligned_{strm_file_path.name}"
        strm.write(aligned_file_path, format="MSEED")

    logging.info("################################################\n")

    logging.info("################################################")
    logging.info("Stream trace times aligned")
    logging.info("################################################")
