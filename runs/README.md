You have the option of running QuakeMigrate in either a 12 x 2-hour chunks day format or for a specific time window (custom format). The QuakeMigrate input data that have been prepared using the QuakeSupport preprocessing scripts work best here, and can be combined to extend the workflow. 2-hour chunks strike a good balance between the read-write speed and file optimization. Users may modify the chunk size, with corresponding script (both preprocessing and runs) modifications, to fit their needs.

Within each script, you only need to make changes to lines demarcated by two dashed lines:  
`------------------`  
`Makes changes here`  
`------------------`  

If you are running in day format, you will need all three scripts. If you are running in custom format, you only need QM_run.

:heavy_exclamation_mark: You must have the QuakeMigrate repository on your machine/HPC cluster AND have installed the QuakeMigrate package  
:grey_exclamation: Clone the QuakeMigrate repository or download the source code from their [GitHub](https://github.com/QuakeMigrate/QuakeMigrate), which also contains installation instructions

This QuakeSupport subfolder contains three Python scripts:
## 1) [QM_run_day](https://github.com/cryoilrj/QuakeSupport/blob/main/runs/QS_QM_run_day.py) - Script to run QuakeMigrate in 12 x 2-hour chunks
:snowman: Package required: obspy  
:snowman: Performs 2-hour runs sequentially, modifying the QuakeMigrate scripts run times and output run name before each run  
:snowman: Modifies the `detect`, `trigger`, and `locate` scripts  
:snowman: Place this script in your QuakeMigrate examples folder for your study site ([like this](https://github.com/QuakeMigrate/QuakeMigrate/tree/master/examples/Icequake_Rutford))  
:snowman: Script requires the QM_run and QM_reset scripts to be present in that same folder  
:snowman: The appropriate mSEED folder(s) is unlocked and relocked (i.e., renamed) to accomodate the corresponding run time window  
:snowman: Only one chunk folder per Julian day can be unlocked at any time (e.g., `012_0` and `012_1` both cannot be renamed to `012`)  
:snowman: Running multiple instances of this script to perform runs for different days concurrently is recommended to speed up your runs  
:warning: There are however conditions/restrictions to perform runs for different days concurrently:  
:warning: Each run requires its own specific copy of the three run scripts and QuakeMigrate scripts (`LUT`, `detect`, `trigger`, `locate`)  
:warning: Due to buffer folders, the first and last 2 hours of each run will require access to an adjacent Julian day folder in addition to its own    
:warning: If two runs try to access/unlock the same Julian day folder the later run will raises a `FileExistsError` exception and stop running  
:green_book: There are three different solutions to avoid this problem, from easiest to hardest:  
:green_book: 1. Only run non-adjacent days concurrently (e.g., run the even days together, then the odd days together)  
:green_book: 2. Create separate `input` folders for each day and direct the `QM_run_day`, `detect`, `trigger`, and `locate` scripts to it  
:green_book: 3. Time your runs to ensure they do not access the same Julian day folder at the same time (difficult to time - not recommended)  
:snowman: Modifying QuakeMigrate source code to work with chunk folders (`012_0`, `012_1`) is possible, but beyond the scope of this package

## 2) [QM_run](https://github.com/cryoilrj/QuakeSupport/blob/main/runs/QS_QM_run.py) - Script to run QuakeMigrate
:snowman: Sequentially runs all the QuakeMigrate scripts (`LUT`, `detect`, `trigger`, and `locate`) in one script  
:snowman: If running in day format, ensure this script is in the same folder as QM_run_day  
:snowman: If running in custom format, you only need this script and can ignore the other two scripts in this subfolder  
:snowman: Script only runs the QuakeMigrate scripts, and assumes you have tuned your QuakeMigrate scripts appropriately before running them  
:snowman: For guidance on parameter tuning for the QuakeMigrate scripts, refer to their highly comprehensive [user manual](https://quakemigrate.readthedocs.io/_/downloads/en/stable/pdf/) (_Updated Apr 10, 2023_)

## 3) [QM_reset](https://github.com/cryoilrj/QuakeSupport/blob/main/runs/QS_QM_reset.py) - Script to reset QuakeMigrate scripts
:snowman: Resets key parameters in QuakeMigrate scripts after each 2-hour run in QS_run_day in preparation for the next iteration or another day run  
:snowman: Resets the `detect`, `trigger`, and `locate` scripts  
:snowman: Only required if running in day format, ensure this script is in the same folder as QM_run_day  
:snowman: Can also be used/modified individually to act as a failsafe to restore QuakeMigrate scripts back to a default or "save" state
