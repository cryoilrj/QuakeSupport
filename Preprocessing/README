This folder contains:

1) IRIS_DL.py and IRIS_mass_DL.py: Scripts to download seismic data (mSEED, SEGY, SAC) from IRIS
  - Packages required: selenium, webdriver-manager
  - Download ChromeDriver here: https://chromedriver.chromium.org/downloads
  - Makes use of the formatted IRIS download URL and selenium package to automate downloads
  - IRIS_DL is for a specified time window, IRIS_mass_DL is for a day of seismic data broken down into 12 x 2-hr chunks
  - webdrive-manager automatically uses the correct ChromeDriver so you do not have to re-download the latest version each Chrome update
  - Selected 2-hr chunks for IRIS_mass_DL to avoid extremely large file sizes and to speed up the process through simultaneous downloads

2) stAlign.py: Script to align stream trace times
  - Package required: obspy
  - If your sampling period > seconds decimal precision specified for your traces, the stream traces can have various time offsets < sampling period
  - These time offsets will not change your results, as the stream trace times are still considered in the same time window with similar data length
  - QuakeMigrate runs perform automatic trace alignment on unaligned traces, but each alignment shift generates a message which can clog up the logs
  - Run this script on your raw downloaded data to nominally align the stream trace times to avoid those messages
  - Modify lines 20 and 21 depending on how you want to align your stream traces relative to a "master" starttime
  - TODO: Example of stream trace offsets

3) mSEED_ReformatQM.py: Script to center data and reformat miniSEED (mSEED) files for QuakeMigrate input
  - Packages required: numpy, obspy
  - QuakeMigrate requires the input traces to be separated by station-component and have specific filename formats (date_starttime_station_component)
  - Centering applied to the data to prevent underestimation/overestimation of QM's coalescence value
  - Complements the IRIS_mass_DL.py script by reformatting a day of mSEED seismic data in 2-hr chunks
  - Again, selected 2-hr chunks to avoid extremely large file sizes. Increase the chunk size, or remove altogether if your data size is small
  - Script assumes the standard 3 components (one vertical, two horizontals), comment out/remove unused component variables if < 3 components
  - A trace's channel and component can be found using tr.stats.channel and tr.stats.component, respectively
  - Suppressed "userwarning" when the processing converts data dtype from integer to float; obspy automatically chooses the suitable encoding
  
  
