"""
Script to automate QuakeMigrate runs

Inputs:
    - QuakeMigrate run scripts
"""

# --- Import modules ---
import sys
import subprocess
from pathlib import Path

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# QuakeMigrate script names (in order)
qm_scripts = [
    Path("./sample_lut.py"),  # LUT
    Path("./sample_detect.py"),  # Detect
    Path("./sample_trigger.py"),  # Trigger
    Path("./sample_locate.py"),  # Locate
]

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Dynamic Python interpreter selection ---
    python_interpreter = sys.executable

    # --- Run QuakeMigrate scripts ---
    for script in qm_scripts:
        subprocess.run([python_interpreter, str(script)], check=True)

    print("\n################################################")
    print("All QuakeMigrate scripts have been executed")
    print("################################################\n")
