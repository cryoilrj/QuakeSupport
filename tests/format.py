"""
Script to prepare mSEED files for QuakeMigrate input

Inputs:
    - Aligned (or raw if alignment not needed) mSEED files

Outputs:
    - QuakeMigrate-formatted input mSEED files
    - Run log
"""

# --- Import modules ---
import datetime
import logging
import numpy as np
from obspy import read
from pathlib import Path
import sys
import warnings

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
a_mseed_path = Path("./inputs/aligned_mSEED")  # Aligned mSEED directory

# Output paths
log_path = Path("./inputs/logs")  # Log directory
mseed_path = Path("./inputs/mSEED")  # QuakeMigrate inputs mSEED directory

# Wildcard pattern to match aligned mSEED files
# Sometimes, the wildcard may be too broad and match unwanted files
# Alternatively, point a_mseed_path to a directory containing only target files
mseed_pattern = "*.mseed"

# Seismogram channels
channels = ["GPZ", "GP1", "GP2"]

# Directory structure and file naming format used by QuakeMigrate to query waveform archives
# Accepts "YEAR/JD/*_STATION_*" and "YEAR/JD/STATION"
# Refer to quakemigrate/io/data.py in QuakeMigrate repository for format details
# Match archive_format in detect.py and locate.py
archive_format = "YEAR/JD/*_STATION_*"

# Verbose logging flag (includes trace information if True)
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
    log_file = log_path / f"format_{current_time}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(logger_format)
    logger.addHandler(file_handler)

    # --- Suppress UserWarning from zero-centering data type conversion ---
    # ObsPy automatically handles encoding when writing .mseed data
    warnings.simplefilter("ignore", UserWarning)

    logging.info("################################################")
    logging.info("Preparing mSEED files for QuakeMigrate input...")
    logging.info("################################################\n")

    logging.info("mSEED preparation")
    logging.info("################################################")

    # --- Sort aligned mSEED files chronologically ---
    strms = sorted(a_mseed_path.glob(mseed_pattern))

    # --- Loop through mSEED files ---
    for s in strms:
        strm = read(s)
        strm_file_path = Path(s)

        # Ensure at least one trace is available
        if len(strm) == 0:
            logging.error(f"No traces found in {strm_file_path.name}, skipping file...")
            continue  # Skip to the next file

        logging.info(f"Preparing {strm_file_path.name} with {len(strm)} traces...")

        # Zero-center trace data
        comps = [[trc for trc in strm.select(channel=ch)] for ch in channels]
        for comp in comps:
            for trc in comp:
                trc.data = trc.data - np.mean(trc.data)

                # Log trace information if verbose
                if verbose_logging:
                    logging.info(trc)
        if verbose_logging:
            logging.info("################################################\n")

        # Get trace temporal data information
        trc = strm[0]
        year = str(trc.stats.starttime.year)  # Year
        jul_starttime = trc.stats.starttime.strftime("%j")  # Start time julian day
        jul_endtime = trc.stats.endtime.strftime("%j")  # End time julian day
        time_str = trc.stats.starttime.strftime("%H%M%S")  # Start time HHMMSS format

        # Input mSEED directory identifier
        label = strm_file_path.name.split(".")[0]

        dests = []
        # mSEED data spans a single day
        if jul_starttime == jul_endtime:
            df = mseed_path / year / (jul_starttime + "_" + label)
            dests.append(df)

        # mSEED data spans multiple days
        # Create input mSEED directories for start and end days
        else:
            df_start = mseed_path / year / (jul_starttime + "_" + label)
            df_end = mseed_path / year / (jul_endtime + "_" + label)
            dests.extend([df_start, df_end])

        # Create input mSEED directories
        for dest in dests:
            dest_path = Path(dest)
            dest_path.mkdir(parents=True, exist_ok=True)

            # Write QuakeMigrate-formatted input mSEED for each trace
            for c in comps:
                for trce in c:
                    sta = trce.stats.station  # Station
                    cha = trce.stats.channel  # Channel
                    if archive_format == "YEAR/JD/*_STATION_*":
                        filename = f"{year}{jul_starttime}_{time_str}_{sta}_{cha}.mseed"
                    elif archive_format == "YEAR/JD/STATION":
                        filename = f"{sta}_{cha}.mseed"
                    else:
                        archive_format_error = "Invalid archive_format"
                        logging.error(archive_format_error)
                        raise ValueError(archive_format_error)
                    trce.write(dest / filename, format="MSEED")

    logging.info("################################################\n")

    logging.info("################################################")
    logging.info("mSEED files prepared for QuakeMigrate input")
    logging.info("################################################")
