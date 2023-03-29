#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
"""Instantiates 
This script downloads a list of signals for a given shot.
The data is stored in HDF5 format with a layout compatible
with the data loading logic of the d3d loader."""

import h5py
import MDSplus as mds
import numpy as np
import os
from os.path import join

import logging
import yaml

import argparse

import d3d_signals
resource_path = importlib.resources.files("d3d_signals")


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


# Set the environment variable to connect to the correct MDS server
# 
os.environ["main_path"] = "atlas.gat.com::"

# Load dataset definitions into file
with open(args.dataset_def, "r") as stream:
    dataset_def = yaml.safe_load(stream)



# Separate between three kinds of data. Each kind requires separate download logic, 
# to pull from from either MDS or PTDATA, and handle 0d vs 1d

# The first and second kind are scalar time series, i.e. 0d time series.
# These live either in MDS or PTdata.
# For MDS, each entry is a dict with 
#   Tree - The name of the MDS tree the data is stored in
#   Node - The name of the MDS node the data is stored in
#   map_to - The group in the HDF5 file the data will be stored in

resource_path = importlib.resources.files("d3d_signals")

with open(join(resource_path, "signals_0d.yaml"), "r") as fp:
    signals_0d = yaml.safe_load(fp)

# The second kind are profiles. These are 1d time series from MDS.
with open(join(resource_path, "signals_1d.yaml"), "r") as fp:
    signals_1d = yaml.safe_load(fp)


# Open Connection to D3D atlas server
conn = mds.Connection("atlas.gat.com")

shotlist = list(dataset_def["shots"].keys())

logging.info(f"Processing shots {shotlist}")


for shotnr in shotlist[:5]:
    logging.info(f"{shotnr} - Processing")

    # File mode needs to be append! Otherwise we delete the file contents every time we
    # execute this script.
    with h5py.File(join(args.destination, f"{shotnr}.h5"), "a") as df:
        assert(df.mode == "r+")
        # Handle each of the three data kinds separately.
        # Second scalar data
        for pred in dataset_def["predictors"]:
            if pred in scalars_dict.keys():
                if scalars_dict[pred]["type"] == "MDS":
                    tree = scalars_dict[pred]["tree"]
                    node = scalars_dict[pred]["node"]
                    map_to = scalars_dict[pred]["map_to"]
                    # Skip the download if there already is data in the HDF5 file
                    try:
                        df[map_to]
                        logging.info(f"Signal {map_to} already exists. Skipping download")
                        continue
                    except KeyError:
                        pass

                    try:
                        logging.info(f"Trying to download {tree}::{node} from MDS")
                        conn.openTree(tree, shotnr)

                        zdata = conn.get(f"_s ={node}").data()
                        zunits = conn.get('units_of(_s)').data()
                        logging.info(f"Downloaded zdata. shape={zdata.shape}")

                        xdata = conn.get('dim_of(_s)').data()
                        xunits = conn.get('units_of(dim_of(_s))').data()
                        logging.info(f"Downloaded xdata. shape={xdata.shape}")
                    except Exception as err:
                        logging.error(f"Failed to download {tree}::{node} from MDS - {err}")
                        raise err

                    # Data is now downloaded. Store them in HDF5
                    try:
                        grp = df.create_group(map_to)
                        grp.attrs.create("origin", f"MDS {tree}::{node}")
                        # Store data in arrays and set units as an attribute
                        for ds_name, ds_data, u_name, u_data in zip(["xdata", "zdata"],
                                                                    [xdata, zdata],
                                                                    ["xunits", "zunits"],
                                                                    [xunits, zunits]):
                            dset = grp.create_dataset(ds_name, ds_data.shape, dtype='f')
                            dset[:] = ds_data[:]
                            dset.attrs.create(u_name, u_data.encode())
                    except Exception as err:
                        logging.error(f"Failed to write {tree}::{node} to HDF5 - {err}")
                        raise(err)

                    logging.info(f"Stored {tree}::{node} into {grp}")

                elif scalars_dict[pred]["type"] == "PTDATA":
                    node = scalars_dict[pred]["node"]
                    map_to = scalars_dict[pred]["map_to"]
                    # Skip the download if there already is data in the HDF5 file
                    try:
                        if df[map_to]["zdata"].size > 0:
                            logging.info(f"Signal {map_to} already exists. Skipping download")
                            continue
                    except KeyError:
                        pass

                    try:
                        logging.info(f"Trying to download {node} from PTDATA")
                        zdata = conn.get(f"""_s = ptdata2('{node}', {shotnr})""").data()
                        xdata = conn.get("dim_of(_s)")
                        logging.info(f"Downloaded zdata. shape={zdata.shape}")
                        logging.info(f"Downloaded xdata. shape={xdata.shape}")
                    except Exception as err:
                        logging.error(f"Failed to download {node} from PTDATA - {err}")
                        continue
                # Data is downloaded. Store them in HDF5
                    try:
                        grp = df.create_group(f"{scalars_dict[pred]['map_to']}")
                        grp.attrs.create("origin", f"PTDATA {node}")
                        for ds_name, ds_data in zip(["xdata", "zdata"],
                                                    [xdata, zdata]):
                            dset = grp.create_dataset(ds_name, ds_data.shape, dtype='f')
                            dset[:] = ds_data[:]
                    except Exception as err:
                        logging.error(f"Failed to write {node} to HDF5 group {grp} - {err}")
                        raise(err)

                    logging.info(f"Stored PTDATA {node} into {grp}")

            elif pred in profile_dict.keys():
                    tree = profile_dict[pred]["tree"]
                    node = profile_dict[pred]["node"]
                    map_to = profile_dict[pred]["map_to"]
                    # Skip the download if there already is data in the HDF5 file
                    try:
                        df[map_to]
                        logging.info(f"Signal {map_to} already exists. Skipping download")
                        continue
                    except KeyError:
                        pass

                    try:
                        logging.info(f"Trying to download {tree}::{node} from MDS")
                        conn.openTree(tree, shotnr)

                        # This is the profile. Remember to transpose to have dim0 being time consistently across
                        # scalars and profiles
                        zdata = conn.get(f"_s ={node}").data().T
                        zunits = conn.get('units_of(_s)').data()
                        logging.info(f"Downloaded zdata. shape={zdata.shape} units={zunits}")

                        # Remember that dim0 in MDS is rho for the profiles. 
                        # This here should be rho/psi in mm
                        ydata = conn.get('dim_of(_s)').data()
                        yunits = conn.get('units_of(dim_of(_s))').data()
                        logging.info(f"Downloaded xdata. shape={ydata.shape}, xunits={yunits}")

                        xdata = conn.get('dim_of(_s, 1)').data()
                        xunits = conn.get('units_of(dim_of(_s, 1))').data()
                        logging.info(f"Downloaded ydata. shape={xdata.shape}, yunits={xunits}")


                    except Exception as err:
                        logging.error(f"Failed to download {tree}::{node} from MDS - {err}")
                        raise err

                    # Data is now downloaded. Store them in HDF5
                    try:
                        grp = df.create_group(map_to)
                        grp.attrs.create("origin", f"MDS {tree}::{node}")
                        # Store data in arrays and set units as an attribute
                        for ds_name, ds_data, u_name, u_data in zip(["xdata", "ydata", "zdata"],
                                                                    [xdata, ydata, zdata],
                                                                    ["xunits", "yunits", "zunits"],
                                                                    [xunits, yunits, zunits]):
                            dset = grp.create_dataset(ds_name, ds_data.shape, dtype='f')
                            dset[:] = ds_data[:]
                            dset.attrs.create(u_name, u_data.encode())
                    except Exception as err:
                        logging.error(f"Failed to write {tree}::{node} to HDF5 - {err}")
                        raise(err)

                    logging.info(f"Stored {tree}::{node} into {grp}")
            else:
                raise ValueError("Couldn't find {pred} in either scalar of profile data description.")

        # # Iterate over all predictors and find the shortest time-base
        # tmax = 100_000
        # for k in df.keys():
        #     if k == "target_ttd":
        #         continue
        #     t_k = df[k]["xdata"][-1]
        #     if t_k < tmax:
        #         tmax = t_k
        # logging.info(f"{shotnr}: tmax = {tmax} ms")
        # df.attrs.create("tmax", tmax)


        # tmin = -100.0
        # for k in df.keys():
        #     if k == "target_ttd":
        #         continue
        #     t_k = df[k]["xdata"][0]
        #     if t_k > tmin:
        #         tmin = t_k
        # logging.info(f"{shotnr}: tmin = {tmin} ms")
        # df.attrs.create("tmin", tmin)

        #break

    
# # end of file downloading.py