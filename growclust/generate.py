"""
Script to generate GrowClust xcordata input file from QuakeMigrate outputs

Inputs:
    - QuakeMigrate event ID file
    - QuakeMigrate outputs runs files

Outputs:
    - GrowClust xcordata input file
    - Run log
"""

# --- Import modules ---
import sys, time, logging, datetime
from pathlib import Path
from multiprocessing import Pool, cpu_count, Manager
import numpy as np
import pandas as pd
from obspy import read, UTCDateTime

# ##############################################################################
#                                Configurations                                #
# ##############################################################################

# Input paths
evID_file = Path("./evID.txt")  # QuakeMigrate event ID file
runs_path = Path("./outputs/runs")  # QuakeMigrate outputs runs directory

# Output paths
xcordata_file = Path("./xcordata.txt")  # GrowClust xcordata input file

# Seismic phases
unique_phases = ["P", "S"]

# Stations channels (align with the order of phases in unique_phases)
channels = ["GPZ", "GP1", "GP2"]  # [Vertical, Horizontal1, Horizontal2]

# Start time of the initial time chunk in the processing window
# Match starttime in get.py
starttime = UTCDateTime("2023-01-06T00:00:00.000000Z")

# Size of time chunks (in seconds)
chunk_size = 2 * 60 * 60  # 2 hours (7200 seconds)

# Differential time sign convention for event pairs (matching GrowClust)
tdif_fmt = 12  # 12: t1 - t2, 21: t2 - t1

# Trace sampling frequency (in Hz)
fs = 1000

# Cross-correlation window length before and after the pick times
# Units are in samples (1/fs), based on the sampling frequency (fs) of your data
xcor_P_window = (-10, 30)  # P phase
xcor_S_window = (-8, 64)  # S phase

# Decimal precision for xcordata outputs (consistent with GrowClust defaults)
ttddp = 5  # Travel-time differential
xcordp = 4  # Cross-correlation value

# Progress threshold for pairwise event computations
# Indicates the nth event has been pairwise computed with all subsequent events
prog_threshold = 100

# Define the number of workers, default to the number of available CPU cores
num_workers = cpu_count()

# Specify a different number of workers, if needed
user_defined_workers = None
if user_defined_workers:
    num_workers = user_defined_workers

# ##############################################################################
#                            End of Configurations                             #
# ##############################################################################


def correlate_events(args):
    """Compute travel-time differentials and cross-correlation between event pairs."""
    (
        idx1,
        event_list,
        available_events,
        ev_dict,
        t0,
        prog_threshold,
        log_messages,
        tdif_fmt,
        ttddp,
        xcordp,
    ) = args
    results = []

    # Validate tdif_fmt input
    if tdif_fmt not in (12, 21):
        error_msg = "tdif_fmt must be either 12 or 21"
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Evaluate every event pair
    for idx2 in range(idx1 + 1, len(event_list)):
        ev2_dict = ev_dict[idx2]

        # Find waveform pairs with common station and channel
        common_wfs = [
            [
                x[0],  # Station
                x[2],  # Phase
                (
                    (x[3] - y[3]) if tdif_fmt == 12 else (y[3] - x[3])
                ),  # Travel-time differential
                x[-1],  # Event 1 cross-correlation window data
                y[-1],  # Event 2 cross-correlation window data
            ]
            for x in available_events[idx1]
            if (key := (x[0], x[1])) in ev2_dict
            for y in [ev2_dict[key]]
        ]

        if common_wfs:
            # Extract waveform data
            wf1_data = np.array([wf[-2] for wf in common_wfs], dtype=object)
            wf2_data = np.array([wf[-1] for wf in common_wfs], dtype=object)

            # Compute data lengths, means, and standard deviations
            wf1_len = np.array([len(wf) for wf in wf1_data])
            wf1_mean = np.array([np.mean(wf) for wf in wf1_data])
            wf1_std = np.array([np.std(wf) for wf in wf1_data])

            wf2_mean = np.array([np.mean(wf) for wf in wf2_data])
            wf2_std = np.array([np.std(wf) for wf in wf2_data])

            # Apply broadcasting for 2D arrays
            if wf1_data.ndim == 2:
                wf1_len = wf1_len[:, np.newaxis]
                wf1_mean = wf1_mean[:, np.newaxis]
                wf1_std = wf1_std[:, np.newaxis]

            if wf2_data.ndim == 2:
                wf2_mean = wf2_mean[:, np.newaxis]
                wf2_std = wf2_std[:, np.newaxis]

            # Normalize data
            a = (wf1_data - wf1_mean) / (wf1_std * wf1_len)
            b = (wf2_data - wf2_mean) / wf2_std

            # Compute full cross-correlation for each waveform pair [-1, 1]
            xcorr_full = [np.correlate(a_wf, b_wf, "full") for a_wf, b_wf in zip(a, b)]

            # Capture highest similarity by taking the maximum absolute value [0, 1]
            xcor = [max(abs(corr)) for corr in xcorr_full]

            # Create DataFrame to store waveform pairs info
            df = pd.DataFrame(
                {
                    "Stat": [i[0] for i in common_wfs],  # Station
                    "tDif": [j[2] for j in common_wfs],  # Travel-time differential
                    "xCor": xcor,  # Cross-correlation value
                    "Phse": [k[1] for k in common_wfs],  # Phase
                }
            )

            # Group DataFrame by phase, then station
            phase_station_groups = df.groupby(["Phse", "Stat"])

            # Format pairwise event waveform info
            seq_id1, _ = event_list[idx1]
            seq_id2, _ = event_list[idx2]
            pairing = f"# {seq_id1} {seq_id2} 0.000"
            ttdwidth = ttddp + 3
            xcorwidth = xcordp + 2
            match_lines = [
                (
                    f"  {stat} "
                    f"{grp['tDif'].iloc[0]:{ttdwidth}.{ttddp}f} "
                    f"{np.mean(grp['xCor']):{xcorwidth}.{xcordp}f} "
                    f"{phase}"
                )
                for (phase, stat), grp in phase_station_groups
            ]  # Iterates in order of keys (phase, then station)
            results.append((pairing, match_lines))

    # Log message when progress threshold is reached
    if (idx1 + 1) % prog_threshold == 0:
        elapsed_minutes = (time.time() - t0) / 60
        log_messages.append(
            f"Event {idx1 + 1} complete, {elapsed_minutes:.2f} minutes elapsed"
        )

    return results


if __name__ == "__main__":
    # --- Set up root logger ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # --- Console logging handler ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logger_format)
    logger.addHandler(console_handler)

    # --- Configure file logging ---
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = f"generate_{current_time}.log"
    file_handler = logging.FileHandler(log_file, mode="w")
    file_handler.setFormatter(logger_format)
    logger.addHandler(file_handler)

    # --- Log messages from multiprocessed computations ---
    manager = Manager()
    log_messages = manager.list()

    logging.info("################################################")
    logging.info("Generating GrowClust xcordata input file...")

    # --- Start timer ---
    t0 = time.time()

    # --- Read in QuakeMigrate event ID list ---
    with open(evID_file, "r") as f:
        event_list = sorted(line.strip().split() for line in f)

    # --- Get list of available QuakeMigrate runs ---
    parent_runs = sorted(fol.name for fol in runs_path.glob("*/"))

    # --- Pre-read event data ---
    streams, picks, event_times = [], [], []

    for _, event_id in event_list:
        # Find runs directory with matching start date and chunk time
        event_timestamp = event_id[:14]
        event_dt = UTCDateTime(
            datetime.datetime.strptime(event_timestamp, "%Y%m%d%H%M%S")
        )
        remainder = (event_dt - starttime) % chunk_size
        floor_dt = event_dt - remainder
        start_str = floor_dt.strftime("%Y%m%d%H%M%S")

        runs_dir = next(
            (
                dir
                for dir in parent_runs
                if "_" in dir and dir.split("_")[-2].startswith(start_str)
            ),
            None,
        )

        if runs_dir is None:
            error_msg = f"Event {event_id} runs directory not found"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Construct base path
        base_path = runs_path / runs_dir

        # QuakeMigrate outputs runs sub-directories
        rcwfs_path = Path("locate/raw_cut_waveforms")  # raw_cut_waveforms
        picks_path = Path("locate/picks")  # picks
        event_path = Path("locate/events")  # events

        # Retrieve event's QuakeMigrate outputs runs files
        rcwfs_file = (base_path / rcwfs_path / event_id).with_suffix(".m")
        picks_file = (base_path / picks_path / event_id).with_suffix(".picks")
        event_file = (base_path / event_path / event_id).with_suffix(".event")

        # Check for missing files
        missing_files = [
            path for path in [rcwfs_file, picks_file, event_file] if not path.is_file()
        ]

        if missing_files:
            missing_files_str = ",\n".join(map(str, missing_files))
            error_msg = f"Event {event_id} missing files:\n{missing_files_str}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Read QuakeMigrate outputs and store in lists
        streams.append(read(rcwfs_file))
        picks.append(pd.read_csv(picks_file))
        event_times.append(UTCDateTime(pd.read_csv(event_file)["DT"][0]))

    # --- Check if any streams were loaded ---
    if not streams:
        error_msg = "No streams were loaded"
        logging.error(error_msg)
        raise ValueError(error_msg)

    # --- Record pre-reading completion time ---
    elapsed_minutes = (time.time() - t0) / 60
    logging.info(f"Data pre-reading complete, {elapsed_minutes:.2f} minutes elapsed")

    # --- Pre-load available events and picks ---
    available_events = []

    for stream, pick, event_time, stream_start in zip(
        streams, picks, event_times, [s[0].stats.starttime for s in streams]
    ):
        # Trace information
        traces = []
        for tr in stream:
            if tr.stats.channel == channels[0]:
                phase = unique_phases[0]  # P phase
            elif tr.stats.channel in channels[1:]:
                phase = unique_phases[1]  # S phase
            else:
                error_msg = f"Channel {tr.stats.channel} not defined in channels"
                logging.error(error_msg)
                raise ValueError(error_msg)

            # Station, Channel, Phase, Data
            traces.append((tr.stats.station, tr.stats.channel, phase, tr))

        # Pick information
        picked = [  # Station Phase Picktime PicktimeIndex
            f"{p[0]} {p[1]} {p[3]} {round((UTCDateTime(p[3]) - stream_start) * fs)}"
            for p in pick.itertuples(index=False)
            if p[3] != "-1"
        ]

        # Event information
        available_event = []
        for trc in traces:
            match_str = f"{trc[0]} {trc[2]}"  # Station-phase identifier
            match = next((pk for pk in picked if match_str in pk), None)

            if match:
                pkInfo = match.split(" ")
                pkTime = UTCDateTime(pkInfo[-2])  # Pick time
                pkIdx = int(pkInfo[-1])  # Pick time index
                minus, plus = (
                    xcor_P_window if pkInfo[1] == "P" else xcor_S_window
                )  # Cross-correlation window length

                available = [
                    trc[0],  # Station
                    trc[1],  # Channel
                    pkInfo[1],  # Phase
                    pkTime - event_time,  # Event-station travel-time
                    trc[-1][
                        pkIdx + minus : pkIdx + plus + 1
                    ],  # Cross-correlation window data
                ]
                available_event.append(available)
        available_events.append(available_event)

    # --- Record pre-loading completion time ---
    elapsed_minutes = (time.time() - t0) / 60
    logging.info(f"Data pre-loading complete, {elapsed_minutes:.2f} minutes elapsed")
    logging.info("################################################\n")

    # --- Generate dictionary of station-channel pairs for all events ---
    ev_dict = {
        num: {(x[0], x[1]): x for x in ev} for num, ev in enumerate(available_events)
    }

    # --- Pairwise computations using multiprocessing ---
    logging.info("Pairwise event computation:")
    logging.info("################################################")

    args = [
        (
            idx1,
            event_list,
            available_events,
            ev_dict,
            t0,
            prog_threshold,
            log_messages,
            tdif_fmt,
            ttddp,
            xcordp,
        )
        for idx1 in range(len(event_list) - 1)
    ]

    with Pool(num_workers) as pool:
        all_results = pool.map(correlate_events, args)

    # --- Write results ---
    with open(xcordata_file, "w") as f:
        pair_count = 0
        for results in all_results:
            for pairing, match_lines in results:
                f.write(f"{pairing}\n")
                [f.write(f"{line}\n") for line in match_lines]
                pair_count += 1

    # --- Sort log messages based on event order ---
    sorted_messages = sorted(log_messages, key=lambda msg: int(msg.split()[1]))

    # --- Write log messages ---
    for message in sorted_messages:
        logging.info(message)
    logging.info("################################################\n")

    logging.info("################################################")
    logging.info(f"{pair_count} total pairwise event computations")
    logging.info("GrowClust xcordata input file generated")
    logging.info("################################################")
