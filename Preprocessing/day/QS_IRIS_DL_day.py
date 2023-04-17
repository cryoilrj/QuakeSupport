# Script to download a day of seismic data from IRIS in 12 x 2-hr chunks

# Import modules
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Change these
# -------------------------------------------------------------------------------------
user, pw = (
    "penguin@psu.edu",
    "1234567890",
)  # Username and password
source = "service.iris.washington.edu/ph5ws/dataselect/1/queryauth?"  # Download source
today = datetime.datetime(2019, 1, 12)  # Target day date
# Start and end times of first chunk with ±5 min buffer
# Start time = 2019-01-12T00:00:00.000000, End time = 2019-01-12T02:00:00.000000
time_string = (
    "starttime=2019-01-11T23%3A55%3A00.000000&"
    + "endtime=2019-01-12T02%3A05%3A00.000000"
)  # "%3A" is url encoding for ":"
# Download specifications
network, station, loc, channel, fmt = (
    "5B",
    "166%2A",  # "%2A" is url encoding for "*", to get all stations starting with "166"
    "--",
    "GP%2A",  # Get all channels starting with "GP"
    "mseed",  # Other options are "segy1", "segy2", and "sac"
)
# -------------------------------------------------------------------------------------

all_drivers = []  # Enable multiple drivers

# Time chunks (modify only if using a different chunk size)
# ---------------------------------------------------------------
starttime = [str((t0 * 2 - 1) % 24).zfill(2) for t0 in range(12)]
endtime = [str((t1 * 2 + 2) % 24).zfill(2) for t1 in range(12)]
tmr = today + datetime.timedelta(days=1)
ytd = today - datetime.timedelta(days=1)
# ---------------------------------------------------------------

# Loop through the day
for c in range(12):
    # Generate download URL
    url_path = (
        "http://"
        + user
        + ":"
        + pw
        + "@"
        + source
        + time_string
        + "&network="
        + network
        + "&station="
        + station
        + "&location="
        + loc
        + "&channel="
        + channel
        + "&format="
        + fmt
    )

    # Download data
    ser = Service(ChromeDriverManager().install())
    op = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=op)  # Use the chrome browser
    all_drivers.append(driver)  # Enable multiple download windows to run simultaneously
    driver.get(url_path)  # Access URL and download data

    # Start and end times for next iteration (modify only if using a different chunk size)
    # ------------------------------------------------------------------------------------
    if c < 11:
        s0 = "T" + starttime[c] + "%"
        s1 = "T" + starttime[c + 1] + "%"
        e0 = "T" + endtime[c] + "%"
        e1 = "T" + endtime[c + 1] + "%"
        time_string = time_string.replace(s0, s1).replace(e0, e1)
        if c == 0:
            time_string = time_string.replace(
                ytd.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
            )
        elif c == 10:
            time_string = time_string.replace(
                "endtime=" + today.strftime("%Y-%m-%d"),
                "endtime=" + tmr.strftime("%Y-%m-%d"),
            )
    # ------------------------------------------------------------------------------------

# Close browsers that have completed downloads
for dv in all_drivers:
    dv.get("chrome://downloads")
    while True:
        downloads = dv.execute_script(
            "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList').items;"
        )
        all_complete = all(d.get("state") == "COMPLETE" for d in downloads)
        if all_complete:
            break

    # Close the browser
    dv.quit()
