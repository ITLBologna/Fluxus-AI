from datetime import datetime, timedelta
from typing import Dict
import numpy as np


def build_histogram(query_dict, csv_array, bin_width=15):
    # type: (Dict, np.ndarray, int) -> list
    """
    :param query_dict: query dictionary
        >> se the attached example (query_dict.py)
    :param csv_array: array containing the data read from the CSV file
        >> see the attached example csv file (sample.csv)
    :param bin_width: width (in minutes) of each bin of the histogram
    :return: output array of size (N,) where N is the number histogram bins
        based on the input query; the i-th element of this array is an
        int value representing the height of the i-th bin
    """

    # read classes and time from the query dict
    query_vclass = [kc for kc, kv in query_dict["vclass"].items() if kv]
    query_time_init = query_dict["timestamp"]["start"]
    query_time_end = query_dict["timestamp"]["end"]
    # handle the textbox problem
    query_time_init = None if query_time_init in ['', None] else query_time_init
    query_time_end = None if query_time_end in ['', None] else query_time_end

    # get first and last time to have the complete range
    time_range = [csv_array[0, 0], csv_array[-1, 0]]

    # convert two time range into datetime format
    time_range = [datetime.strptime(d, '%H:%M:%S') for d in time_range]

    # bins creations
    bins = []
    bins.append(time_range[0])
    x = time_range[0]
    while True:
        x = x + timedelta(minutes=bin_width)
        if x >= time_range[1]:
            break
        bins.append(x)
    bins.append(time_range[1])
    bins = [b.time() for b in bins]

    # copy of the original
    query_accumulator = csv_array.copy()

    # query by timestamp
    if query_time_init is not None and len(query_accumulator) > 0:
        query_accumulator = query_accumulator[query_accumulator[:, 0] >= query_time_init]
    if query_time_end is not None and len(query_accumulator) > 0:
        query_accumulator = query_accumulator[query_accumulator[:, 0] <= query_time_end]

    # query by lane
    # tmp = []
    # for ci, cv in query_dict["lane"].items():
    #     if cv:
    #         tmp.append(query_accumulator[query_accumulator[:, 3] == ci])
    #
    # if len(tmp) > 0:
    #     query_accumulator = np.asarray(sorted(np.concatenate(tmp), key=lambda x: int(x[1])))
    # else:
    #     query_accumulator = np.empty(shape=0, dtype=np.object)

    # query by vclass
    tmp = []
    for vc in query_vclass:
        if len(query_accumulator) > 0:
            tmp.append(query_accumulator[query_accumulator[:, 2] == vc])

    if len(tmp) > 0:
        query_accumulator = np.asarray(sorted(np.concatenate(tmp), key=lambda x: int(x[1])))
    else:
        query_accumulator = np.empty(shape=0, dtype=np.object)

    # clusters into bins
    bins_out = [0 for i in range(len(bins) - 1)]
    idx_bins_out = 0
    idx_accum = 0
    b0 = bins[0]

    for b1 in bins[1:]:
        for i in range(idx_accum, len(query_accumulator)):
            if str(b0) <= query_accumulator[i][0] <= str(b1):
                bins_out[idx_bins_out] += 1
                idx_accum += 1
            else:
                idx_bins_out += 1
                b0 = b1
                idx_accum = i
                break

    return bins_out
