#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import numpy as np
import logging
import multiprocessing as mp
import yaml
from os.path import join
import h5py

import importlib.resources
import d3d_signals


"""
This script calculates max, min, mean, and std individually for all signals in a dataset definition.
Max, min, mean, and std are calculated over all shots, and for each signal individually.
For 1d signals, all channels in the signal are used. That is, the calculation is over all shots
and all channels.
The results are stored in the file `normalization.yaml` as follows
predictor_name:
    max:
    mean:
    min:
    std:
"""


# Each task fetches a single variable from all shots and calculates the 
# mean and standard deviation.


def process_variable(args):
    """Fetch a single variable from all shots and calculate the channel-wise min, max, mean and std.
    args:
        datadir (string): Directory to HDF5 files
        group_name (string, string) : Tuple (predictor_name, map_to). This is used to find the HDF5
                                      group name for the predictor. 
        shotlist (list[Int]): List of shots to process
    """
    datadir, group_name, shotlist = args    # Unpack the arguments
    pred_name, map_to = group_name          # Unpack predictor name and map_to
    # 1. Cache the relevant data from list of hdf5 files
    cache_data = []
    for shotnr in shotlist:
        with h5py.File(join(datadir, f"{shotnr}.h5"), "r") as df:
            cache_data.append(df[map_to]["zdata"][:].flatten())

    all_signals = np.hstack(cache_data)
    # try:
    #     all_signals = np.hstack(cache_data)
    # except:
    #     print(f"Error in shot {shotnr}")


    # 2. Calculate min, max, mean and std. Convert numpy datatypes to float. Otherwise yaml.safe_dump
    #    throws an error
    return {pred_name: {"min": float(all_signals.min()),
                        "max": float(all_signals.max()),
                        "mean": float(all_signals.mean()), 
                        "std": float(all_signals.std())}}

    
if __name__ == "__main__":
    print("main")

    logging.basicConfig(filename="instantiate.log",
                    format="%(asctime)s    %(message)s",
                    encoding="utf-8",
                    level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog="downloader.py",
        description="Downloads D3D datasets according to yaml description")
    parser.add_argument("--dataset_def", type=str,
        help="YAML file that contains definition of the dataset")
    parser.add_argument("--destination", type=str,
        help="Destination for Dataset HDF5 files")

    args = parser.parse_args()

    # Load dataset definition
    with open(args.dataset_def, "r") as stream:
        dataset_def = yaml.safe_load(stream)

    # The MDS/PTdata signals are stored under the field `map_to` in signals?.yaml
    # Load the yaml files and find the map_to names that correspond to the field 'predictors' in the
    # dataset definition

    resource_path = importlib.resources.files("d3d_signals")

    with open(join(resource_path, "signals_0d.yaml"), "r") as fp:
        signals_0d = yaml.safe_load(fp)
    with open(join(resource_path, "signals_1d.yaml"), "r") as fp:
        signals_1d = yaml.safe_load(fp)


    # Gather the name of the predictor and the corresponding HDF5 group names 
    # of the predictors listed in the definition of the dataset.
    # The result is a list of tuples (predictor, map_to)
    group_list_0d = [(k, signals_0d[k]["map_to"]) for k in dataset_def["predictors"] if k in signals_0d.keys()]
    group_list_1d = [(k, signals_1d[k]["map_to"]) for k in dataset_def["predictors"] if k in signals_1d.keys()]
    group_list = group_list_0d + group_list_1d


    # Generate list from shots in the dataset
    shot_list = list(dataset_def["shots"][-10:])

    pool = mp.Pool(4)
    res_mean_std = pool.map(process_variable,  [(args.destination, grp, shot_list) for grp in group_list])

    # all_mean_std is a list of dicts: [{"var1": (min, max, mean, std)}, {"var2": (min, max, mean, std)}, ...]
    # combine them into a single dict
    dict_mean_std = {}
    for i in res_mean_std:
        dict_mean_std.update(i)
    # Serialize the dictionary to file
    with open("normalization.yaml", "w") as fp:
        fp.write(yaml.safe_dump(dict_mean_std))

# end of file calculate_mean_std.py