# Script to download mSEED files for one day (12 x 2-hr chunks)

# Import modules
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Change these only
today = datetime.datetime(2019, 1, 12)  # Target day date
time_string = (
    "starttime=2019-01-11T23%3A55%3A00.000000&"
    + "endtime=2019-01-12T02%3A05%3A00.000000"
)  # Time specifications of download URL

# Modification variables
all_drivers = []
starttime = [str((t0 * 2 - 1) % 24).zfill(2) for t0 in range(12)]
endtime = [str((t1 * 2 + 2) % 24).zfill(2) for t1 in range(12)]
tmr = today + datetime.timedelta(days=1)
ytd = today - datetime.timedelta(days=1)

# Loop through the day
for c in range(12):
    url_path = (
        "user:password@"
        + "service.iris.washington.edu/ph5ws/dataselect/1/queryauth?"
        + time_string
        + "&network=5B&station=166%2A&location=--&channel=GP%2A"
    )  # Download URL
    ser = Service(ChromeDriverManager().install())
    op = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=ser, options=op)  # Use the chrome browser
    all_drivers.append(driver)  # Enable multiple download windows to run simultaneously
    driver.get(url_path)  # Access URL and download data

    # Modify download URL for next iteration
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
while True:
    pass
