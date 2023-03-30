#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import numpy as np
import logging
import multiprocessing as mp
import yaml
from os.path import join
import h5py


# Compile tmin from HDF5 files into yaml files
def get_tmin_tmax(shotnr, datadir):
    """Return tmax attribute from HDF5 file.
    shotnr (int) : Shot number file
    datadir (str) : Directory of the HDF5 files.
    """
    with h5py.File(join(datadir, f"{shotnr}.h5"), 'r') as df:
        tmin = df.attrs["tmin"]
        tmax = df.attrs["tmax"]
        
    # Cast to float so that yaml can pickle this item later on.
    return float(tmin), float(tmax)


if __name__ == "__main__":
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


    with open(args.dataset_def, "r") as stream:
        dataset_def = yaml.safe_load(stream)

    # Generate list from shots in the dataset
    shot_list = dataset_def["shots"][-10:]

    t_min_max_dict = {}
    for shotnr in shot_list:
        tmin, tmax = get_tmin_tmax(shotnr, args.destination)
        print(f"========== {shotnr} ========")
        #if dataset_def["shots"][shotnr]["ttd"] > 0.0:
        #    tmax = float(dataset_def["shots"][shotnr]["ttd"])
        print(f"    tmin={tmin}, tmax={tmax}")    


        t_min_max_dict.update({shotnr: {"tmin": float(tmin), "tmax": float(tmax)}})


    with open("shots_t_min_max.yaml", "w") as fp:
        fp.write(yaml.safe_dump(t_min_max_dict))
    

# end of file compile_tmin.py
