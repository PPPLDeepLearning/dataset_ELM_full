# ELM training dataset

This dataset is used for ELM prediction, it is defined in dataset.yaml.
The notebook `shots_overview.ipynb` sketches how the dataset is collected. This is forensic work
to reconstruct lost, prior knowledge. Using work from that notebook, I constructed the
definition of the dataset 'dataset.yaml'.



The definitions of the predictors are given in [d3d_signals](https://github.com/PlasmaControl/d3d_signals).
This dataset uses some more signals than the D3D_100 dataset, such as fs07 (fitlerscope data) to construct
the TTELM target (which is done in post-processing), and the pedestal info prmtan_xxxxx.



The TTELM target is calculated in post-processing.

## New: Checking signal availability in downloads.py
This dataset contains over 43,000 shots. Not all signals are available for every shot.
The file `download.py` will compile which signals could be successfully downloaded from D3D in
the csv file df_progress.csv through the use of a pandas dataframe.
The dataframe contains columns of shotnr and all the predictors in `dataset.yaml`. 
A true in a predictor column indicates that the signal is available in D3D MDS.
A false indicates that it is not available.

When building a [dataset](https://github.com/PlasmaControl/d3d_loaders), only pick the shots that
have all requested predictors available. This can be done through the dataframe loaded in
`verify_downloads.ipynb`, f.ex.:
```
df[(df["bmstinj"] == True) & (df["dusbradial"] == True)]
```
selects only the rows that have both, `bmstinj` and `dusbradial`.



## New: Notebook to verify ELM detection code.
Ge's code uses the routine `find_elm_events_tar`, in the file `find_elms.py`. Search for it:
```
[stellar]:/projects/FRNN/gdong-temp $ find . -type f -name "find_elms.py"
```

I used this notebook to visualize what it does. The TTELM is written into the shots hdf5 file,
located in `datasets/XXXXXX.h5` in the group "target". This is done in `generate_ttelm.py` and
executed in `instantiate.sh`.



## Detective work to reconstruct dataset.yaml from previous work
Below are notes how the original dataset has been reconstructed. These are working notes for the
notebook `verify_downloads.ipynb`.


As a start, I'm looking at Ge's folder `stellar:/projects/FRNN/gdong-temp/ELM/elm-d3d-data-fs07`
The `conf.yaml` lists the following folders to be parsed:
* /../../../tigress/FRNN/signal_data_ipsip/
* /../../../tigress/FRNN/signal_data_new_nov2019/
* /../../../tigress/FRNN/signal_data_new_2020/
* /../../../tigress/FRNN/signal_data_new_REAL_TIME/
* /../../../tigress/FRNN/signal_data/

The contents of these folders are the following:


* signal_data_ipsip - A folder of 40837 txt files, one for each shot
* signal_data_new_nov2019 - A folder with with subfolders
```
[rkube@stellar-intel FRNN]$ tree -d signal_data_new_nov2019/
signal_data_new_nov2019/
└── d3d
    ├── bmspinj
    ├── bmstinj
    ├── \bol_l03_p
    ├── \bol_l15_p
    ├── dssdenest
    ├── dusbradial
    ├── EFIT01
    │   └── RESULTS.AEQDSK.Q95
    ├── EFITRT1
    │   └── RESULTS.AEQDSK.Q95
    ├── efsbetan
    ├── efsli
    ├── efswmhd
    ├── ELECTRONS
    │   ├── test_ne
    │   ├── test_te
    │   ├── TS.BLESSED.CORE.DENSITY
    │   └── TS.BLESSED.CORE.TEMP
    ├── ipeecoil
    ├── ipsiptargt
    ├── ipspr15V
    ├── iptdirect
    ├── mhd
    │   └── mirnov.n1rms
    └── ZIPFIT01
        ├── PROFILES.EDENSFIT
        ├── PROFILES.ETEMPFIT
        ├── PROFILES.ITEMPFIT
        └── PROFILES.ZDENSFIT

30 directories

```

* signal_data_new_2020/

```
[rkube@stellar-intel FRNN]$ tree -d signal_data_new_2020/
signal_data_new_2020/
└── d3d
    ├── dusbradial
    ├── fs07
    ├── prmtan_neped
    ├── prmtan_newid
    ├── prmtan_peped
    ├── prmtan_teped
    └── prmtan_tewid

8 directories
```

* signal_data
```
signal_data
├── d3d
│   ├── bmspinj
│   ├── bmstinj
│   ├── \bol_l03_p
│   ├── \bol_l15_p
│   ├── dssdenest
│   ├── dusbradial
│   ├── EFIT01
│   │   ├── RESULTS.AEQDSK.Q95
│   │   └── RESULTS.GEQDSK.QPSI
│   ├── efsbetan
│   ├── efsli
│   ├── efswmhd
│   ├── ipeecoil
│   ├── ipsip
│   ├── ipsiptargt
│   ├── ipspr15V
│   ├── iptdirect
│   ├── nssampn1l
│   ├── nssampn2l
│   ├── nssfrqn1l
│   ├── nssfrqn2l
│   ├── RF
│   │   └── ECH.TOTAL.ECHPWRC
│   └── ZIPFIT01
│       ├── PROFILES.BOOTSTRAP.JBS_SAUTER
│       ├── PROFILES.BOOTSTRAP.QRHO
│       ├── PROFILES.EDENSFIT
│       ├── PROFILES.ETEMPFIT
│       ├── PROFILES.ITEMPFIT
│       ├── PROFILES.NEUTFIT
│       ├── PROFILES.PTHMFIT
│       ├── PROFILES.TROTFIT
│       └── PROFILES.ZDENSFIT
├── jet
│   ├── jpf
│   │   ├── da

[...]
```
    There is a lot of D3D data and also some jet data.
