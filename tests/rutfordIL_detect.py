# -*- coding: utf-8 -*-
"""
This script runs the detect stage for the Rutford icequake example.

"""

# Stop numpy using all available threads (these environment variables must be
# set before numpy is imported for the first time).
import os

os.environ.update(
    OMP_NUM_THREADS="1",
    OPENBLAS_NUM_THREADS="1",
    NUMEXPR_NUM_THREADS="1",
    MKL_NUM_THREADS="1",
)

from quakemigrate import QuakeScan
from quakemigrate.io import Archive, read_lut, read_stations
from quakemigrate.signal.onsets import STALTAOnset

# --- i/o paths ---
station_file = "./inputs/rutfordIL_stations.txt"
data_in = "./inputs/mSEED"
lut_out = "./outputs/lut/rutfordIL.LUT"
run_path = "./outputs/runs"
run_name = "rutfordIL_test_run"

# --- Set time period over which to run detect ---
starttime = "yyyy-mm-ddT00:00:00.000000Z"
endtime = "yyyy-mm-ddT00:00:00.000001Z"

# --- Read in station file ---
stations = read_stations(station_file)

# --- Create new Archive and set path structure ---
archive = Archive(
    archive_path=data_in, stations=stations, archive_format="YEAR/JD/*_STATION_*"
)

# --- Load the LUT ---
lut = read_lut(lut_file=lut_out)

# --- Create new Onset ---
onset = STALTAOnset(position="centred", sampling_rate=500)
onset.phases = ["P", "S"]
onset.bandpass_filters = {"P": [20, 200, 4], "S": [10, 125, 4]}
onset.sta_lta_windows = {"P": [0.01, 0.25], "S": [0.05, 0.5]}

# --- Create new QuakeScan ---
scan = QuakeScan(
    archive,
    lut,
    onset=onset,
    run_path=run_path,
    run_name=run_name,
    log=True,
    loglevel="info",
)

# --- Set detect parameters ---
scan.timestep = 1.0
scan.threads = 4  # NOTE: increase as your system allows to increase speed!

# --- Run detect ---
scan.detect(starttime, endtime)
