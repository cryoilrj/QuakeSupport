I have provided the option of preparing your data for QuakeMigrate input in either a 12 x 2-hr chunks daily format (day folder) or for a specific time window(s) (custom folder) - either option can be seamlessly applied in a preprocessingly workflow. 2-hr chunks were used to avoid extremely large file sizes to speed up processing. Users may modify the chunk size, with corresponding script modifications, to fit their needs.

Within each script, you only need to make changes to lines demarcated by  
`------------------`  
`Makes changes here`  
`------------------`  

This QuakeSupport subfolder contains three Python scripts each for day and custom formats, in sequential running order:
## 1) IRIS_DL [day](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/day/QS_IRIS_DL_day.py) and [custom](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/custom/QS_IRIS_DL_custom.py) - Script to download seismic data from IRIS
:snowflake: Packages required: selenium, webdriver-manager (used with ChromeDriver, download [here](https://chromedriver.chromium.org/downloads))  
:snowflake: Makes use of the formatted IRIS download URL and selenium package to automate downloads  
:snowflake: webdriver-manager automatically uses the current ChromeDriver so you only need to download ChromeDriver once     
:snowflake: To account for QuakeMigrate pre- and post-padding, add a buffer (e.g., 5 minutes) to your start and end times  
:snowflake: Works for mSEED, SEGY, and SAC files

## 2) mSEED_streamAlign [day](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/day/QS_mSEED_streamAlign_day.py) and [custom](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/custom/QS_mSEED_streamAlign_custom.py) - Script to align mSEED stream trace times
:snowflake: Package required: obspy  
:snowflake: If your sampling period > seconds decimal precision of your traces, your stream traces may have time offsets < sampling period  
:snowflake: These time offsets will not change your results as all the stream trace times remain within the same time window  
:snowflake: QuakeMigrate performs its own stream trace alignment during runs, but outputs a long message for each trace that is realigned  
:snowflake: To prevent these messages from clogging up your output logs, use this script to nominally align your stream trace times  
:snowflake: Script assumes all traces in a single run have the same sampling frequency (e.g., 1000 Hz)   
:snowflake: If you have modified this script to work with SEGY and/or SAC files, please submit a pull request to help others!  
:snowflake: Below is an example of a misaligned stream being realigned using this script (original start time `2019-01-03T23:55:00.000000`)

Before running the script:
![Screenshot of a misaligned stream](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/misaligned_stream.png)  
After running the script:
![Screenshot of an aligned stream](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/aligned_stream.png)

## 3) mSEED_prepQM [day](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/day/QS_mSEED_prepQM_day.py) and [custom](https://github.com/cryoilrj/QuakeSupport/blob/main/preprocessing/custom/QS_mSEED_prepQM_custom.py) - Script to prepare mSEED files (zero-center and reformat) for QuakeMigrate input  
:snowflake: Packages required: numpy, obspy  
:snowflake: QuakeMigrate input streams are separated by station and channel, with a specific filename format  
:snowflake: Sample QuakeMigrate input stream filename (yearjd_starttime_station_channel): `2019003_235500_16611_GP1.mseed`  
:snowflake: Each trace is zero-centered to avoid inaccurate coalescence values in QuakeMigrate  
:snowflake: Script outputs the prepared QuakeMigrate input mSEED files into the QuakeMigrate input year folder (`input_path_QM`)  
:snowflake: The QuakeMigrate input year folder (`input_path_QM`) assumes you have the QuakeMigrate repository on your machine  
:snowflake: Clone the QuakeMigrate repository or download the source code from their [GitHub](https://github.com/QuakeMigrate/QuakeMigrate)  
:snowflake: Sample QuakeMigrate input year folder path: `"Home/QuakeMigrate/examples/PenguinGlacier/inputs/mSEED/2023/"`  
:snowflake: Script assumes the standard 3 channels (1 x vertical, 2 x horizontal), comment out unused channels if < 3 channels  
:snowflake: A trace's channel can be found using `tr.stats.channel`  
:snowflake: If you have modified this script to work with SEGY and/or SAC files, please submit a pull request to help others!
