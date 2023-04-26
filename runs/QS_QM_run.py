# Script to run all QuakeMigrate scripts

# Import module
import subprocess

# Change these only
# -----------------------------------------
# Names of QuakeMigrate scripts (in order)
all_qm_scripts = [
    "penguin_lut.py",  # LUT script
    "penguin_detect.py",  # Detect script
    "penguin_trigger.py",  # Trigger script
    "penguin_locate.py",  # Locate script
]
# -----------------------------------------

# Execute QuakeMigrate scripts
[subprocess.run(["python", script]) for script in all_qm_scripts]
