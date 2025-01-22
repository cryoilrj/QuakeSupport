"""
Script to read and plot seismic waveforms

Inputs:
    - Seismic file (accepts common formats such as mSEED, SAC, SEGY, etc.)

Outputs:
    - Seismic waveform plots, using ObsPy's `plot()` method
"""

# --- Import modules ---
from pathlib import Path
from obspy import read

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
seismic_file = Path("./sample.mseed")  # Seismic file

# Stream station and channel filters
station = "11*"  # Matches stations starting with "11"
channel = "GPZ"  # Matches the "GPZ" channel

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Read seismic file ---
    st = read(seismic_file)

    # --- Apply filters to stream ---
    filtered_stream = st.select(station=station, channel=channel)
    filtered_stream.traces.sort(
        key=lambda tr: (tr.stats.station, 0 if tr.stats.channel.endswith("Z") else 1)
    )  # Sort traces by station, then channel (prioritizing Z)

    # --- Stream information ---
    # Check if filtered stream is empty
    if len(filtered_stream) == 0:
        # No traces found; no plot
        print("No traces found matching the specified filters")
    else:
        # Print filtered stream information
        print(filtered_stream.__str__(extended=True))

        # Plot filtered stream
        filtered_stream.plot(method="full")  # No data downsampling
