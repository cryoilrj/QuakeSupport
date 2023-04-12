All scripts except QS_IRIS_DL.py are written to handle a day of data at a time in 12 x 2-hr chunks, and can be seamlessly applied in a pre-processing workflow under that condition. 2-hr chunks were used to avoid extremely large file sizes and speed up processing speed through simultaneous downloads. Users who prefer a different chunk size can make the appropriate modifications in the code.

This folder contains, in sequential running order:
1) [QS_IRIS_DL.py](https://github.com/cryoilrj/QuakeSupport/blob/main/Preprocessing/QS_IRIS_DL.py) and [QS_IRIS_dayDL.py](https://github.com/cryoilrj/QuakeSupport/blob/main/Preprocessing/QS_IRIS_dayDL.py): Scripts to download seismic data (mSEED, SEGY, SAC) from IRIS  
▸ Packages required: selenium, webdriver-manager (used with ChromeDriver, download [here](https://chromedriver.chromium.org/downloads))  
▸ Makes use of the formatted IRIS download URL and selenium package to automate downloads  
▸ webdriver-manager automatically uses the current ChromeDriver so you only need to download ChromeDriver once  
▸ Use IRIS_DL for specific time windows and IRIS_dayDL for 1 day of seismic data broken down into 12 x 2-hour chunks  
▸ To account for QuakeMigrate pre- and post-padding, add a buffer (e.g., 5 minutes) to your desired start and end times

2) [QS_stream_align.py](https://github.com/cryoilrj/QuakeSupport/blob/main/Preprocessing/QS_stream_align.py): Script to align stream trace times  
▸ Package required: obspy  
▸ If your sampling period > seconds decimal precision of your traces, your stream traces may have time offsets < sampling period  
▸ These time offsets do not affect your results, as the stream trace times remain in the same time window with similar data lengths   
▸ QuakeMigrate performs its own stream trace alignment during runs, but outputs a long message for each trace that is re-aligned  
▸ To prevent these messages from clogging up your output logs, use this script to nominally align your stream trace times  
▸ Script assumes all traces in a single run have the same sampling frequency  
▸ Below is an example of a misaligned stream, with original start time of `2019-01-03T23:55:00.000000`, being re-aligned using this script

Before running the script:
![Screenshot of a misaligned stream](https://github.com/cryoilrj/QuakeSupport/blob/main/Preprocessing/misaligned_stream.png)  
After running the script:
![Screenshot of an aligned stream](https://github.com/cryoilrj/QuakeSupport/blob/main/Preprocessing/aligned_stream.png)

3) [QS_mSEED2QM.py](https://github.com/cryoilrj/QuakeSupport/blob/main/Preprocessing/QS_mSEED2QM.py): Script to center data and reformat mSEED files for QuakeMigrate input  
▸ Packages required: numpy, obspy  
▸ QuakeMigrate input traces are separated by station and component, with a specific filename format  
▸ Sample filename (yearjd_starttime_station_component): `2019003_235500_16611_GP1.mseed`  
▸ Centering data prevents underestimation/overestimation of QuakeMigrate's computed coalescence values  
▸ Script assumes the standard 3 components (1 x vertical, 2 x horizontals), comment out unused components if < 3 components  
▸ A trace's channel and component can be found using tr.stats.channel and tr.stats.component, respectively
