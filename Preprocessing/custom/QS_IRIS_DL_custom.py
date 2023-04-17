# Script to download seismic data for a specific time window

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
time_string = (
    "starttime=2023-01-08T12%3A00%3A00.000000&"
    + "endtime=2023-01-08T12%3A01%3A00.000000"
)  # Start and end times (±5 min buffer recommended), "%3A" is url encoding for ":"
# Download specifications
network, station, loc, channel, fmt = (
    "Y2",
    "71%2A",  # "%2A" is url encoding for "*", to get all stations starting with "71"
    "--",
    "GP%2A",  # Get all channels starting with "GP"
    "mseed",  # Other options are "segy1", "segy2", and "sac"
)
# -----------------------------------------------------------------------------------

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
driver.get(url_path)  # Access URL and download data

# Check if download has completed
driver.get("chrome://downloads")
while True:
    downloads = driver.execute_script(
        "return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList').items;"
    )
    all_complete = all(d.get("state") == "COMPLETE" for d in downloads)
    if all_complete:
        break

# Close the browser
driver.quit()
