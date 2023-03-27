# ELM training dataset

This dataset tries to reproduce the data used for ELM prediction.
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
