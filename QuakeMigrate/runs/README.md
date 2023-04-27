You have the option of running QuakeMigrate in either a 12 x 2-hour chunks day format or for a specific time window (custom format). The QuakeMigrate input data that have been prepared using the QuakeSupport preprocessing scripts work best here, and can be combined to extend the workflow. 2-hour chunks strike a good balance between the read-write speed and file optimization. Users may modify the chunk size, with corresponding script (both preprocessing and runs) modifications, to fit their needs.

Within each script, you only need to make changes to lines demarcated by two dashed lines:  
`-----------------`  
`Make changes here`  
`-----------------`

:heavy_exclamation_mark: You must have the QuakeMigrate repository downloaded on your machine/HPC AND the QuakeMigrate package installed  
:grey_exclamation: Clone the QuakeMigrate repository or download the source code from their [GitHub](https://github.com/QuakeMigrate/QuakeMigrate), which also contains installation instructions

This subfolder contains three Python scripts. If you are running in day format, you will need all three scripts. If you are running in custom format, you only need `QM_run`.
## 1. [`QM_run_day`](https://github.com/cryoilrj/QuakeSupport/blob/main/QuakeMigrate/runs/QS_QM_run_day.py) - Script to run QuakeMigrate in 12 x 2-hour chunks
:snowman: Package required: `obspy`  
:snowman: Performs 2-hour runs sequentially, modifying the run times and run name of the QuakeMigrate scripts before each run  
:snowman: Place this script in your QuakeMigrate run folder for your specific study site ([example](https://github.com/QuakeMigrate/QuakeMigrate/tree/master/examples/Icequake_Rutford))  
:snowman: Script requires the `QM_run` and `QM_reset` scripts to be present in the same run folder  
:snowman: Modifies the `detect`, `trigger`, and `locate` scripts  
:snowman: The mSEED folder(s) containing files for the corresponding time window is unlocked (i.e., renamed) for QuakeMigrate to read  
:snowman: As an example of unlocking, `012_0` is renamed to `012` for QuakeMigrate to read since it only reads files in Julian day format  
:snowman: The mSEED folder(s) is relocked after its run completion, as only one chunk folder per Julian day can be unlocked at any time  
:snowman: Relocking is similarly renaming the mSEED folder from Julian day (`012`) back to its original Julian day_chunk format (`012_0`)  
:snowman: Running multiple instances of this script to perform runs for different days concurrently is recommended to speed up your runs  
:snowman: There are conditions and restrictions to perform runs for different days concurrently:  
:snowman: 1. Each run requires its own specific copy of the three `runs` and QuakeMigrate scripts (`LUT`, `detect`, `trigger`, `locate`)  
:snowman: 2. Due to buffer folders, the runs for the first and last 2 hours of each day also require access to an adjacent Julian day folder  
:warning: If two runs try to unlock the same Julian day folder, the later run raises a `FileExistsError` exception  
:warning: There are three different solutions to avoid this problem, from easiest to hardest:  
:warning: 1. Only run non-adjacent days concurrently (e.g., run the even days together, then the odd days together)  
:warning: 2. Create separate `input` folders for each day and direct the `QM_run_day`, `detect`, `trigger`, and `locate` scripts to it  
:warning: 3. Time your runs to ensure they do not access the same Julian day folder at the same time (hard to time - not recommended)

## 2. [`QM_run`](https://github.com/cryoilrj/QuakeSupport/blob/main/QuakeMigrate/runs/QS_QM_run.py) - Script to run QuakeMigrate
:snowman: Sequentially runs all the QuakeMigrate scripts (`LUT`, `detect`, `trigger`, and `locate`)  
:snowman: If running in day format, place this script in the same run folder as `QM_run_day`  
:snowman: If running in custom format, you only need this script and can ignore the other two scripts in this subfolder  
:warning: If running this script alone, make sure to unlock (and relock after) the corresponding mSEED folder(s)  
:snowman: Script only runs the QuakeMigrate scripts, tune your QuakeMigrate scripts appropriately before running them  
:snowman: For guidance on parameter tuning for the QuakeMigrate scripts, refer to their [user manual](https://quakemigrate.readthedocs.io/_/downloads/en/stable/pdf/) (_Updated Apr 10, 2023_)

## 3. [`QM_reset`](https://github.com/cryoilrj/QuakeSupport/blob/main/QuakeMigrate/runs/QS_QM_reset.py) - Script to reset QuakeMigrate scripts
:snowman: Resets parameters in QuakeMigrate scripts after each 2-hour run in `QM_run_day` in preparation for the next iteration or another day run  
:snowman: Only required if running in day format - place this script in the same run folder as `QM_run_day`  
:snowman: The parameters being reset by this script are the run times and run name of the QuakeMigrate scripts  
:snowman: Resets the `detect`, `trigger`, and `locate` scripts  
:snowman: Script can be used/modified individually to act as a failsafe to restore QuakeMigrate scripts back to a default or "save" state
