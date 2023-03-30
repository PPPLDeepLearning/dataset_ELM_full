#!/bin/bash

# Driver script to instatiate ELM-test dataset

# 1. Download necessary files
python download.py --dataset_def dataset.yaml --destination dataset

# 2. Generate TTELM target
python generate_ttelm_targets.py --dataset_def dataset.yaml --destination dataset

# 3. Calculate mean and std averaged over signals
python calculate_mean_std.py --dataset_def dataset.yaml --destination dataset

# 4. Compile tmin from HDF5 files / dataset definition and write to yaml file
python compile_tmin.py --dataset_def dataset.yaml  --destination dataset
