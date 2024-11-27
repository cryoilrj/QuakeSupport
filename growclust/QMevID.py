"""
Script to write QuakeMigrate event ID file

Inputs:
    - QuakeMigrate event files

Outputs:
    - QuakeMigrate event ID file
"""

# --- Import modules ---
from pathlib import Path

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
runs_path = Path("./outputs/runs")  # QuakeMigrate outputs runs directory

# Output paths
evID_file = Path("./evID.txt")  # QuakeMigrate event ID file

# Wildcard pattern to match event files
events_pattern = "*.event"

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Retrieve and sort event IDs ---
    events = sorted(f.stem for f in runs_path.rglob(events_pattern))

    if events:
        print("################################################")
        print("Writing QuakeMigrate event IDs...")
        print("################################################\n")

        # Create sequential ID mapping
        seq_mapping = [f"{i:07d} {event}" for i, event in enumerate(events, 1)]

        # Write sequentially mapped event IDs
        evID_file.write_text("\n".join(seq_mapping))

        print("################################################")
        print(f"{len(events)} QuakeMigrate event IDs written")
        print("################################################")
    else:
        raise ValueError("No events found")
