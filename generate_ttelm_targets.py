#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import h5py
import logging
import numpy as np
from os.path import join
import yaml



def find_elm_events_tar(time, y, threshold=None, scheme=None, maxi=500):
   """Generate ELM targets.
   
   Taken from stellar:/projects/FRNN/gdong-temp/2021-LM-tune/n1rms-2021-02-08-23-43/7/find_elms.py

   Args:
    time: np.ndarray
        timebse of the signal
    y: np.ndarray
        signal to calulcate ELM target from. Should by fs07 signal.
    threshold: float
        Value a peak has to exceed to count as an ELM.
    scheme:
        Not used
    maxi:
        Not used.
   """
   res=[]
   assert(len(time)==len(y))
   if len(time)==0:
      return []
   tar = np.ones(len(time))*500
   if threshold==None:
      if scheme==None:
         threshold=np.mean(y)*3
   previous_end = -100
   during_elm = False
   current_elm={}
   for i,yi in enumerate(y):
       if yi>threshold:
          if during_elm == False:
             if time[i]-previous_end>5 or len(res)==0:
                current_elm['begin']=time[i]
                current_elm['begin_index']=i
                current_elm['max']=yi
                during_elm=True
             else:

                current_elm=res.pop()
                during_elm=True
                current_elm['max']=yi
    
          else:
             current_elm['max'] = max(yi,current_elm['max'])
       else:
          if during_elm == True:
             during_elm = False
             current_elm['end']=time[i]
             current_elm['end_index']=i
             res.append(current_elm)
             current_elm={}
             previous_end=time[i]
    
   if during_elm == True:
             during_elm = False
             current_elm['end']=time[i]
             current_elm['end_index']=i
             res.append(current_elm)
             current_elm={}
             previous_end=time[i]
   
   #print(len(res),'ELM events detected~~~!!!')
   previous_end =0
   for e in res:
       index_begin = e['begin_index']
       index_end = e['end_index']
       tar[previous_end:index_begin] = time[index_begin]-time[previous_end:index_begin]
       tar[index_begin:index_end] = 0 #during ELM
       previous_end = index_end

   #print(tar.shape)
   return res,tar

logging.basicConfig(filename="instantiate.log",
                    format="%(asctime)s    %(message)s",
                    encoding="utf-8",
                    level=logging.INFO)

parser = argparse.ArgumentParser(
    prog="generat_ttd_targets.py",
    description="Generate time-to-disruption target for each shot in the dataset")
parser.add_argument("--dataset_def", type=str,
    help="YAML file that contains definition of the dataset")
parser.add_argument("--destination", type=str,
    help="Destination for Dataset HDF5 files")

args = parser.parse_args()


with open(args.dataset_def, 'r') as fp:
    dataset_def = yaml.safe_load(fp)


for shotnr in dataset_def["shots"][-10:]:
    # Iterate over the target variables and find the longest time base
    # of the signals. Use this timebase to generate a ttd target
    with h5py.File(join(args.destination, f"{shotnr}.h5"), "a") as df:
        fs07 = df["/fs07/zdata"][:]
        tb = df["/fs07/xdata"][:]

        # Generate ttelm:
        _, ttelm = find_elm_events_tar(tb, fs07)

        # See if TTELM already exists. If yes, we don't overwrite it.
        try:
            df["/target_ttelm/xdata"]
            logging.info(f"TTELM for shot {shotnr} already exists. Skipping shot")
            continue
        except KeyError:
            pass

        grp_t = df.create_group("target_ttelm")
        grp_t.create_dataset("xdata", data=tb.astype(np.float32))
        grp_t.create_dataset("zdata", data=ttelm.astype(np.float32))



    


