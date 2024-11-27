# -*- coding: utf-8 -*-
"""
This script runs the locate stage for the Rutford icequake example.

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

from obspy.core import AttribDict

from quakemigrate import QuakeScan
from quakemigrate.io import Archive, read_lut, read_stations, read_response_inv
from quakemigrate.signal.onsets import STALTAOnset
from quakemigrate.signal.pickers import GaussianPicker
from quakemigrate.signal.local_mag import LocalMag

# --- i/o paths ---
station_file = "./inputs/rutfordIL_stations.txt"
response_file = "./inputs/response.xml"
data_in = "./inputs/mSEED"
lut_out = "./outputs/lut/rutfordIL.LUT"
run_path = "./outputs/runs"
run_name = "rutfordIL_test_run"

# --- Set time period over which to run locate ---
starttime = "yyyy-mm-ddT00:00:00.000000Z"
endtime = "yyyy-mm-ddT00:00:00.000001Z"

# --- Read in station file ---
stations = read_stations(station_file)

# --- Read in response inventory ---
response_inv = read_response_inv(response_file)

# --- Specify parameters for response removal ---
response_params = AttribDict()
response_params.water_level = 60

# --- Create new Archive and set path structure ---
archive = Archive(
    archive_path=data_in,
    stations=stations,
    archive_format="YEAR/JD/*_STATION_*",
    response_inv=response_inv,
    response_removal_params=response_params,
)

# --- Specify parameters for amplitude measurement ---
amp_params = AttribDict()
amp_params.signal_window = 0

# --- Specify parameters for magnitude calculation ---
mag_params = AttribDict()
mag_params.A0 = "Hutton-Boore"

mags = LocalMag(amp_params=amp_params, mag_params=mag_params, plot_amplitudes=False)

# --- Load the LUT ---
lut = read_lut(lut_file=lut_out)

# --- Create new Onset ---
onset = STALTAOnset(position="centred", sampling_rate=500)
onset.phases = ["P", "S"]
onset.bandpass_filters = {"P": [20, 200, 4], "S": [10, 125, 4]}
onset.sta_lta_windows = {"P": [0.01, 0.25], "S": [0.05, 0.5]}

# --- Create new PhasePicker ---
picker = GaussianPicker(onset=onset)
picker.plot_picks = False

# --- Create new QuakeScan ---
scan = QuakeScan(
    archive,
    lut,
    onset=onset,
    picker=picker,
    mags=mags,
    run_path=run_path,
    run_name=run_name,
    log=True,
    loglevel="info",
)

# --- Set locate parameters ---
# For a complete list of parameters and guidance on how to choose them, please
# see the manual and read the docs.
scan.marginal_window = 0.06
scan.threads = 4  # NOTE: increase as your system allows to increase speed!

# --- Toggle plotting options ---
scan.plot_event_summary = True

# --- Toggle writing of waveforms ---
scan.write_cut_waveforms = True

# --- Run locate ---
scan.locate(starttime=starttime, endtime=endtime)
