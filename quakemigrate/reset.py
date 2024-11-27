"""
Script to reset QuakeMigrate scripts with template run name and times

Inputs:
    - QuakeMigrate run scripts
"""

# --- Import modules ---
import re
import time
from pathlib import Path

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Detect, trigger, and locate QuakeMigrate script names (in order)
reset_scripts = [
    Path("./sample_detect.py"),  # Detect
    Path("./sample_trigger.py"),  # Trigger
    Path("./sample_locate.py"),  # Locate
]

# QuakeMigrate run name, match qm_run_name in runs.py
qm_run_name = "sampleQM"

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################

if __name__ == "__main__":
    # --- Regex patterns and template lines dictionary ---
    patterns = {
        re.compile(
            r"^run_name\s*=\s*(?!run_name$).*$", re.MULTILINE
        ): f'run_name = "{qm_run_name}"',  # Matches 'run_name = <not run_name>'
        re.compile(
            r"^starttime\s*=.*$", re.MULTILINE
        ): 'starttime = "yyyy-mm-ddT00:00:00.000000Z"',  # Matches 'starttime ='
        re.compile(
            r"^endtime\s*=.*$", re.MULTILINE
        ): 'endtime = "yyyy-mm-ddT00:00:00.000001Z"',  # Matches 'endtime ='
    }

    # --- Reset QuakeMigrate scripts with template lines ---
    for rs in reset_scripts:
        content = rs.read_text(encoding="utf-8")  # Read script content

        # Apply pattern replacements
        for pattern, template in patterns.items():
            content = pattern.sub(template, content)

        # Write updated content back to file
        rs.write_text(content, encoding="utf-8")
        time.sleep(1.0)  # Ensure sequential script resets

    print("################################################")
    print("Detect, trigger, and locate scripts reset")
    print("################################################\n")
