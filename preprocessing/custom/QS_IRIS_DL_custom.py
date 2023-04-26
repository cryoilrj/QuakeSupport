# Script to download seismic data from IRIS for a specific time window(s)

# Import modules
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Change these only
# -----------------------------------------------------------------------------------
user, pw = (
    "penguin@psu.edu",
    "1234567890",
)  # Username and password
source = "service.iris.edu/ph5ws/dataselect/1/queryauth?"  # Download source
# List of lists of time windows, with each sublist containing a start and end time
time_windows = [
    ["2019-01-03T23:55:00.000000", "2019-01-04T02:05:00.000000"],
    ["2023-05-05T01:00:00.000000", "2023-05-05T01:20:00.000000"],
    ["2019-01-23T09:23:00.000000", "2019-01-23T10:00:00.000000"],
]  # Remember to add a buffer (e.g., 5 minutes) to the start and end times
# Download specifications
network, station, loc, channel, fmt = (
    "Y2",
    "71%2A",  # "%2A" is url encoding for "*", to get all stations starting with "71"
    "--",
    "GP%2A",  # Get all channels starting with "GP"
    "mseed",  # Other options are "segy1", "segy2", and "sac"
)
# -----------------------------------------------------------------------------------

all_drivers = []  # Enable multiple drivers

# Loop through the time windows
for tw in time_windows:
    time_string = (
        "starttime="
        + tw[0].replace(":", "%3A")
        + "&endtime="
        + tw[1].replace(":", "%3A")
    )

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
