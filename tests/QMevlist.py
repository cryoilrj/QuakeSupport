"""
Script to write GrowClust evlist input file from QuakeMigrate event files

Inputs:
    - QuakeMigrate event ID file
    - QuakeMigrate event files

Outputs:
    - GrowClust evlist input file
"""

# --- Import modules ---
import pandas as pd
from pathlib import Path
from datetime import datetime

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
evID_file = Path("./evID.txt")  # QuakeMigrate event ID file
runs_path = Path("./outputs/runs")  # QuakeMigrate outputs runs directory

# Output paths
evlist_file = Path("./evlist.txt")  # GrowClust evlist input file

# Decimal precision for evlist outputs (consistent with GrowClust defaults)
latdp = 5  # Latitude
londp = 5  # Longitude
depdp = 3  # Depth
magdp = 2  # Magnitude

# Unit of depth in QuakeMigrate event files ('m' or 'km')
dep_unit = "km"

# Verbose output flag (includes each event written if True)
verbose = True

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Read in QuakeMigrate event IDs ---
    with open(evID_file, "r") as f:
        event_list = sorted(line.strip().split() for line in f)

    # --- Retrieve QuakeMigrate event files ---
    event_files = {file.stem: file for file in runs_path.rglob("*.event")}

    print("################################################")
    print("Writing GrowClust evlist input file...")
    print("################################################\n")

    # --- Write events to evlist input file ---
    with open(evlist_file, "w") as evlist_f:
        event_count = 0  # Initialize event counter
        latwidth = 4 + latdp
        lonwidth = 5 + londp
        depwidth = 4 + depdp
        magwidth = 5 + magdp

        # Locate and process target event files
        for seq_id, event_id in event_list:
            event_file = event_files.get(event_id)

            if event_file:
                event_info = pd.read_csv(event_file)
                dt = event_info["DT"].iloc[0]  # Event arrival datetime
                dt_obj = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%fZ")

                # Convert event depth to kilometers if in meters
                if dep_unit == "m":
                    dep = event_info["Z"].iloc[0] / 1000
                elif dep_unit == "km":
                    dep = event_info["Z"].iloc[0]
                else:
                    raise ValueError("Invalid dep_unit ('m' or 'km' only)")

                row = [
                    f"{dt_obj.year}",  # Year
                    f"{dt_obj.month:>2}",  # Month
                    f"{dt_obj.day:>2}",  # Day
                    f"{dt_obj.hour:>2}",  # Hour
                    f"{dt_obj.minute:>2}",  # Minute
                    f"{dt_obj.second + dt_obj.microsecond / 1_000_000:6.3f}",  # Second
                    f"{event_info['Y'].iloc[0]:{latwidth}.{latdp}f}",  # Latitude
                    f"{event_info['X'].iloc[0]:{lonwidth}.{londp}f}",  # Longitude
                    f"{dep:{depwidth}.{depdp}f}",  # Depth
                    f"{event_info['ML'].iloc[0]:{magwidth}.{magdp}f}",  # Magnitude
                    "0.000",  # Horizontal error (ignored by GrowClust)
                    "0.000",  # Vertical error (ignored by GrowClust)
                    "0.000",  # RMS error (ignored by GrowClust)
                    f"{seq_id}",  # Sequential event ID
                ]

                # Write row to evlist_file
                evlist_f.write(" ".join(map(str, row)) + "\n")
                event_count += 1  # Increment event counter for each written event

                if verbose:
                    print(f"Event {event_id} written")

            else:
                raise FileNotFoundError(f"Event {event_id} event file not found")

    print("\n################################################")
    print(f"{event_count} total events written")
    print("GrowClust evlist input file written")
    print("################################################")
