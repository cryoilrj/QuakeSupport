# Script to reset QuakeMigrate scripts to default times and run name

# Import modules
import time
import fileinput

# Change these only
# ---------------------------------------------------------
reset_run_name = "penguin_example"  # QuakeMigrate run name
# Names of QuakeMigrate scripts (in order)
reset_scripts = [
    "penguin_detect.py",  # Detect script
    "penguin_trigger.py",  # Trigger script
    "penguin_locate.py",  # Locate script
]
# ---------------------------------------------------------

# Reset keywords
keywords = ["run_name =", "starttime =", "endtime ="]

# Default QuakeMigrate replacement lines
r_name = 'run_name = "' + reset_run_name + '"\n'  # Run name
s_time = 'starttime = "2023-01-30T00:00:00.000000Z"\n'  # Start time
e_time = 'endtime = "2023-01-30T00:00:01.000000Z"\n'  # End time
replacements = [r_name, s_time, e_time]

# Reset scripts with default lines
for rs in reset_scripts:
    with fileinput.FileInput(rs, inplace=True) as file:
        for line in file:
            for k, keyword in enumerate(keywords):
                if keyword in line:
                    line = replacements[k]
            print(line, end="")
    time.sleep(1)  # Enable reset scripts to be sequentially ordered

print("Detect, trigger, and locate scripts reset")
