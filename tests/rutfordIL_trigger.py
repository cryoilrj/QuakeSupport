# -*- coding: utf-8 -*-
"""
This script runs the trigger stage for the Rutford icequake example.

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

from quakemigrate import Trigger
from quakemigrate.io import read_lut

# --- i/o paths ---
lut_file = "./outputs/lut/rutfordIL.LUT"
run_path = "./outputs/runs"
run_name = "rutfordIL_test_run"

# --- Set time period over which to run trigger ---
starttime = "yyyy-mm-ddT00:00:00.000000Z"
endtime = "yyyy-mm-ddT00:00:00.000001Z"

# --- Load the LUT ---
lut = read_lut(lut_file=lut_file)

# --- Create new Trigger ---
trig = Trigger(lut, run_path=run_path, run_name=run_name, log=True, loglevel="info")

# --- Set trigger parameters ---
# For a complete list of parameters and guidance on how to choose them, please
# see the manual and read the docs.
trig.marginal_window = 0.06
trig.min_event_interval = 0.12
trig.normalise_coalescence = True

# --- Static threshold ---
trig.threshold_method = "static"
trig.static_threshold = 6.0

# --- Dynamic (Median Absolute Deviation) threshold ---
# trig.threshold_method = "dynamic"
# trig.mad_window_length = 7200.
# trig.mad_multiplier = 8.

# --- Run trigger ---
trig.trigger(starttime, endtime, interactive_plot=False)
