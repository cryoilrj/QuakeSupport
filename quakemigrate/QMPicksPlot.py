"""
Script to plot QuakeMigrate modeled and observed picks

Inputs:
    - QuakeMigrate picks files
    - QuakeMigrate waveform files

Outputs:
    - QuakeMigrate picks plots
"""

# --- Import modules ---
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from obspy import read, UTCDateTime
from pathlib import Path
from datetime import timedelta
from matplotlib.backends.backend_pdf import PdfPages

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
runs_path = Path("./outputs/runs")  # QuakeMigrate outputs runs directory

# Output paths
plot_path = runs_path / "QMPicksPlot"  # Plot directory

# Wildcard patterns to match picks and waveform files
picks_pattern = "*.picks"  # Picks
wf_pattern = "*.m"  # Waveform

# Channel(s) to plot
channels = ["GPZ", "GP1", "GP2"]

# Vertical and horizontal components (leave empty if not applicable)
vertical_comp = ["GPZ"]
horizontal_comp = ["GP1", "GP2"]

# Enable zoom in around observed pick time
pick_zoom = True

# Time window (± seconds) around observed pick time if pick_zoom is True
pick_window = 0.5

# Custom y-axis limits for amplitude (use if data is noisy or other events are nearby)
ylims_flag = False  # True to apply custom y-axis limits, False for automatic scaling
ymin, ymax = -1000, 1000  # Minimum and maximum y-axis limits

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################


def format_time(x, _pos=None):
    """Format time for x-axis with two decimal places."""
    dt = mdates.num2date(x)
    return f"{dt:%H:%M:%S}.{dt.microsecond // 10000:02d}"


if __name__ == "__main__":
    # --- Retrieve and sort picks and waveform files ---
    picks_files = sorted(runs_path.rglob(picks_pattern))
    wf_files = sorted(runs_path.rglob(wf_pattern))

    # --- Create dictionaries mapping events to file paths ---
    picks_files_dict = {f.stem: f for f in picks_files}
    wf_files_dict = {f.stem: f for f in wf_files}

    # --- Find common event names ---
    common_events = sorted(set(picks_files_dict.keys()) & set(wf_files_dict.keys()))

    # --- Check for events present in one directory but not the other ---
    picks_only = set(picks_files_dict.keys()) - set(wf_files_dict.keys())
    wf_only = set(wf_files_dict.keys()) - set(picks_files_dict.keys())

    if picks_only:
        print(f"Picks without waveforms: {picks_only}\n")
    if wf_only:
        print(f"Waveforms without picks: {wf_only}\n")

    # --- Proceed if there are common events ---
    if not common_events:
        raise ValueError("No matching picks and waveform files found")

    print("################################################")
    print("Plotting QuakeMigrate picks...")
    print("################################################\n")

    # --- Ensure plot directory exists ---
    plot_path.mkdir(parents=True, exist_ok=True)

    # --- Plot picks and waveform file pairs ---
    for event_name in common_events:
        picks_file = picks_files_dict[event_name]
        waveform_file = wf_files_dict[event_name]

        # Plot event picks grouped by channel
        for chanl in channels:

            # Read, sort, and filter waveforms
            st = read(waveform_file).sort(
                [
                    "station",  # Sort by station first
                    "component",  # Sort by component second
                ]
            )
            wf = st.select(channel=chanl)

            # Read and filter picks by phase
            picks = pd.read_csv(picks_file)
            if chanl in vertical_comp:
                phase = "P"
            elif chanl in horizontal_comp:
                phase = "S"
            phase_picks = picks[picks["Phase"] == phase]

            # Initialize plot
            fig, axes = plt.subplots(
                len(wf), 1, figsize=(10, len(wf) * 2), squeeze=False
            )
            axes = axes.flatten()  # Flatten the axes array to 1D

            # Figure title
            fig.suptitle(
                f"Event {Path(waveform_file).stem} {chanl} Picks",
                fontsize=11.5,
                fontweight="bold",
                y=0.997,
            )

            # Plot QuakeMigrate picks and uncertainties
            for i, tr in enumerate(wf):

                # Convert relative times to absolute times
                start_time = tr.stats.starttime.datetime
                abs_times = [start_time + timedelta(seconds=t) for t in tr.times()]

                # Plot waveform
                axes[i].plot(abs_times, tr.data, label=f"{tr.stats.station} {chanl}")

                # Retrieve pick information
                station = tr.stats.station
                pick_info = phase_picks[phase_picks["Station"].astype(str) == station]
                pick_time = pick_info["PickTime"].values[0]
                modeled_time = pick_info["ModelledTime"].values[0]
                pick_error = pick_info["PickError"].values[0]

                # Plot modeled pick time
                modeled_time = UTCDateTime(
                    modeled_time
                ).datetime  # Convert to UTCDateTime
                axes[i].axvline(
                    modeled_time,
                    color="r",
                    linestyle="--",
                    label=f"Modeled {phase}",
                    linewidth=1,
                )

                # Plot observed pick time and uncertainty, if available
                if pick_time != "-1":
                    pick_time = UTCDateTime(
                        pick_time
                    ).datetime  # Convert to UTCDateTime
                    axes[i].axvline(
                        pick_time,
                        color="springgreen",
                        linestyle="--",
                        label=f"Observed {phase}",
                        linewidth=2,
                    )
                    axes[i].axvspan(
                        pick_time - timedelta(seconds=pick_error),
                        pick_time + timedelta(seconds=pick_error),
                        color="yellow",
                        alpha=0.5,
                        label="Pick uncertainty",
                    )
                else:
                    # Observed pick time and uncertainty unavailable
                    axes[i].axvline(
                        abs_times[0],
                        color="k",
                        label=f"Observed {phase} unavailable",
                        alpha=0,
                    )

                # Zoom in around observed pick time, if applicable
                if pick_zoom and (pick_time != "-1"):
                    axes[i].set_xlim(
                        pick_time - timedelta(seconds=pick_window),
                        pick_time + timedelta(seconds=pick_window),
                    )

                if ylims_flag:
                    axes[i].set_ylim(ymin, ymax)
                if i == len(wf) - 1:
                    axes[i].set_xlabel("Time (UTC)")
                axes[i].set_ylabel("Amplitude")
                axes[i].xaxis.set_major_formatter(ticker.FuncFormatter(format_time))
                axes[i].xaxis.set_major_locator(mdates.AutoDateLocator())
                axes[i].legend(loc="upper left", bbox_to_anchor=(1, 1))

            # Adjust layout
            plt.tight_layout()

            # Save figure to PDF
            pdf_plot = plot_path / f"{Path(waveform_file).stem}_{chanl}.pdf"
            with PdfPages(pdf_plot) as pdf:
                pdf.savefig(fig)
            plt.close(fig)  # Close figure to free memory

            print(f"Event {Path(waveform_file).stem} {chanl} picks plotted")

    print("\n################################################")
    print("QuakeMigrate picks plotted")
    print("################################################")
