"""
Script to download seismic data and instrument response inventory

Inputs:
    - Download credentials (pass empty strings if not required)
    - Station, location, and channel information
    - Network, data center, and time range information

Outputs:
    - Downloaded seismic mSEED files
    - Instrument response inventory file
    - Run log
"""

# --- Import modules ---
import datetime
import json
import logging
import sys
import time
import traceback
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.core import Stream

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
credentials_file = Path("./credentials.json")  # Download credentials file

# Output paths
r_mseed_path = Path("./inputs/raw_mSEED")  # Raw mSEED directory
log_path = Path("./inputs/logs")  # Log directory
response_file = Path("./inputs/response.xml")  # Instrument response inventory

# Network and data center
network = "5B"
datacenter = "IRISPH5"

# Station information
# Choose one option and uncomment the corresponding block:

# Option 1: String (single station)
# station_input = "16611"

# Option 2: Wildcard string (multiple stations)
station_input = "166*"  # Matches stations starting with "166"

# Option 3: List of station codes (multiple stations)
# station_input = [
#     "16611",
#     "16612",
#     "16613",
#     "16614",
#     "16615",
# ]

# Location and channel information
location_input = "--"
channel_input = "GP*"  # Matches channels starting with "GP"

# Time buffer (in seconds) to prevent data gaps during QuakeMigrate runs
time_buffer = 5 * 60  # 5 minutes (300 seconds)

# Choose the type of data time intervals:
# 1: Regular time chunks (consecutive, uniform intervals)
# 2: Custom times (specific, variable intervals)
time_type = 1

# Start and end times of the initial time chunk in the processing window
# If using custom times, set these to the first entry
# End time is defined as starttime + chunk_size
starttime = UTCDateTime("2023-01-06T00:00:00.000000Z")  # Start time
endtime = UTCDateTime("2023-01-06T02:00:00.000000Z")  # End time

# Number and size (in seconds) of time chunks, ignore if using custom times
time_chunks = 4
chunk_size = 2 * 60 * 60  # 2 hours (7200 seconds)

# Custom start and end times, ignore if using regular time chunks
times = [
    (
        UTCDateTime("2019-01-06T00:00:00.000000Z"),  # Start time
        UTCDateTime("2019-01-06T00:32:00.000000Z"),  # End time
    ),
    (
        UTCDateTime("2019-01-24T09:24:00.000000Z"),  # Start time
        UTCDateTime("2019-01-24T09:28:00.000000Z"),  # End time
    ),
    (
        UTCDateTime("2019-01-12T01:00:00.000000Z"),  # Start time
        UTCDateTime("2019-01-12T01:24:00.000000Z"),  # End time
    ),
]

# Concurrent workers for multithreading
workers = 6  # Recommended limit

# Retries and wait time (backoff, in seconds) between retries if a download fails
max_retries = 3  # Capped at 5 retries
retry_backoff = 120  # 2 minutes (120 seconds), capped at 3 minutes (180 seconds)

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################


def download_waveform_data(
    network,
    station,
    location,
    channel,
    starttime,
    endtime,
    datacenter,
    r_mseed_path,
):
    """Download seismic data and save it as a .mseed file."""
    master_stream = Stream()  # Set up master stream
    logging.info(f"Downloading seismic data from {starttime} to {endtime}...")
    stations = station if isinstance(station, list) else [station]

    # Download and concatenate seismic data
    for sta in stations:
        st = client.get_waveforms(
            network=network,
            station=sta,
            location=location,
            channel=channel,
            starttime=starttime,
            endtime=endtime,
        )
        master_stream += st

    # Write master stream to mSEED file
    start_str = starttime.strftime("%Y%m%d%H%M%S%f")
    end_str = endtime.strftime("%Y%m%d%H%M%S%f")
    combined_name = f"{datacenter}_{network}_{start_str}_{end_str}"
    output_filename = r_mseed_path / f"{combined_name}.mseed"
    master_stream.write(output_filename, format="MSEED")


def download_and_handle_exception(
    network,
    station,
    location,
    channel,
    starttime,
    endtime,
    datacenter,
    r_mseed_path,
    max_retries,
    retry_backoff,
):
    """Download seismic data and handle exceptions with retries."""
    # Cap the retries and backoff time
    max_retries = min(max_retries, 5)  # Maximum of 5 retries
    retry_backoff = min(retry_backoff, 180)  # Maximum of 3 minutes (180 seconds)

    attempt = 0

    while attempt <= max_retries:
        try:
            download_waveform_data(
                network,
                station,
                location,
                channel,
                starttime,
                endtime,
                datacenter,
                r_mseed_path,
            )
            break  # Break out of the loop if download is successful
        except Exception as e:
            attempt += 1
            exception_traceback = traceback.format_exc()  # Capture the traceback
            msg = (
                f"Attempt {attempt}/{max_retries}: Error downloading seismic data "
                f"from {starttime} to {endtime}:\n{e}\n{exception_traceback}"
            )
            logging.error(msg)

            if attempt <= max_retries:
                logging.info("Retrying download...")
                time.sleep(retry_backoff)
            else:
                logging.error("Retry attempts failed")


if __name__ == "__main__":
    # --- Suppress non-critical ObsPy 'event' service warnings ---
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="obspy.clients.fdsn.wadl_parser",
        lineno=107,
    )

    # --- Create directories to store raw mSEED files and logs ---
    r_mseed_path.mkdir(parents=True, exist_ok=True)
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
    log_file = log_path / f"get_{current_time}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(logger_format)
    logger.addHandler(file_handler)

    # --- Load download credentials ---
    try:
        with open(credentials_file, "r") as f:
            credentials = json.load(f)
        username = credentials["username"]
        password = credentials["password"]
    except Exception as e:
        logging.error(f"Error reading credentials: {e}")
        raise

    # --- Initializing client ---
    if username and password:
        client = Client(datacenter, user=username, password=password, timeout=120)
    else:
        client = Client(datacenter, timeout=120)

    logging.info("################################################")
    logging.info(f"Accessing data from network {network} from {datacenter}...")

    # --- Write instrument response inventory ---
    if isinstance(station_input, str):  # String
        station = station_input
    elif isinstance(station_input, list):  # Station list
        station = ",".join(f"{s}" for s in station_input)
    else:
        raise ValueError("station_input must be a string or list!")

    inv = client.get_stations(
        network=network,
        station=station,
        starttime=starttime,
        endtime=endtime,
        level="response",
    )
    inv.write(response_file, format="STATIONXML", validate=True)

    logging.info("Instrument response inventory written")
    logging.info("################################################\n")

    # --- Generate pairs of start and end times ---
    if time_type == 1:  # Regular time chunks
        time_pairs = [
            (
                starttime - time_buffer + t * chunk_size,
                endtime + time_buffer + t * chunk_size,
            )
            for t in range(time_chunks)
        ]
    elif time_type == 2:  # Custom times
        times.sort()  # Sort times chronologically
        time_pairs = [(start - time_buffer, end + time_buffer) for start, end in times]
    else:
        time_type_error = "Invalid time_type value; must be 1 or 2"
        logging.error(time_type_error)
        raise ValueError(time_type_error)

    # --- Concurrently download seismic data ---
    logging.info("Data downloads")
    logging.info("################################################")

    if not time_pairs:
        logging.warning("No seismic data to download")
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures_list = [
                executor.submit(
                    download_and_handle_exception,
                    network,
                    station_input,
                    location_input,
                    channel_input,
                    start,
                    end,
                    datacenter,
                    r_mseed_path,
                    max_retries,
                    retry_backoff,
                )
                for start, end in time_pairs
            ]
            for future in as_completed(futures_list):
                future.result()  # Raise thread exceptions

    logging.info("################################################\n")

    logging.info("################################################")
    logging.info("Seismic data downloads complete")
    logging.info("################################################")
