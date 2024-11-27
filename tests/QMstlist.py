"""
Script to write GrowClust stlist input file from QuakeMigrate station file

Inputs:
    - QuakeMigrate station file

Outputs:
    - GrowClust stlist input file
"""

# --- Import modules ---
import pandas as pd
from pathlib import Path

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
station_file = Path("./inputs/rutfordIL_stations.txt")  # QuakeMigrate station file

# Output paths
stlist_file = Path("./stlist.txt")  # GrowClust stlist input file

# Unit of elevation in QuakeMigrate station file ('m' or 'km')
elev_unit = "km"

# Decimal precision for stlist outputs (consistent with GrowClust defaults)
latdp = 4  # Latitude
londp = 4  # Longitude
elevdp = 0  # Elevation

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Read QuakeMigrate station file ---
    st = pd.read_csv(station_file, skipinitialspace=True)

    # --- Remove whitespace from station names if string ---
    st["Name"] = st["Name"].apply(lambda x: x.strip() if isinstance(x, str) else x)

    # --- Convert station elevations to meters if in kilometers ---
    if elev_unit == "km":
        st["Elevation"] = st["Elevation"] * 1000
    elif elev_unit != "m":
        raise ValueError("Invalid elev_unit ('m' or 'km' only)")

    print("################################################")
    print("Writing GrowClust stlist input file...")
    print("################################################\n")

    # --- Write stations to stlist input file ---
    with open(stlist_file, "w") as f:
        latwidth = 4 + latdp
        lonwidth = 5 + londp

        for _, row in st.iterrows():
            # Convert station name to integer if whole number
            name = row["Name"]
            if isinstance(name, float) and name.is_integer():
                name = int(name)

            f.write(
                (
                    f"{name:<5} "  # Station name
                    f"{row['Latitude']:{latwidth}.{latdp}f} "  # Latitude
                    f"{row['Longitude']:{lonwidth}.{londp}f} "  # Longitude
                    f"{row['Elevation']:.{elevdp}f}\n"  # Elevation
                )
            )
            print(f"Station {name} written")

    print("\n################################################")
    print("GrowClust stlist input file written")
    print("################################################")
