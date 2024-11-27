# -*- coding: utf-8 -*-
"""
This script generates the traveltime look-up table (LUT) for the Rutford
icequake example.

"""

from obspy.core import AttribDict
from pyproj import Proj

from quakemigrate.io import read_stations
from quakemigrate.lut import compute_traveltimes

station_file = "./inputs/rutfordIL_stations.txt"
lut_out = "./outputs/lut/rutfordIL.LUT"

# --- Read in the station information file ---
stations = read_stations(station_file)

# --- Define the input and grid projections ---
gproj = Proj(
    proj="lcc",
    units="km",
    lon_0=-84.038,
    lat_0=-78.168,
    lat_1=-78.18,
    lat_2=-78.16,
    datum="WGS84",
    ellps="WGS84",
    no_defs=True,
)
cproj = Proj(proj="longlat", datum="WGS84", ellps="WGS84", no_defs=True)

# --- Define the grid specifications ---
# AttribDict behaves like a Python dict, but also has '.'-style access.
grid_spec = AttribDict()
grid_spec.ll_corner = [-84.10, -78.185, 1.6]
grid_spec.ur_corner = [-83.97, -78.15, 2.4]
grid_spec.node_spacing = [0.05, 0.05, 0.05]
grid_spec.grid_proj = gproj
grid_spec.coord_proj = cproj

# --- Homogeneous LUT generation ---
lut = compute_traveltimes(
    grid_spec,
    stations,
    method="homogeneous",
    phases=["P", "S"],
    vp=3.841,
    vs=1.970,
    log=True,
    save_file=lut_out,
)
