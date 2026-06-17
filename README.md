This repository contains the integrated assessment model setups used to develop the scenarios informing the study *Decarbonization Pathways and Equity Implications of Pakistan's Climate Ambition*. 

## Repository structure

```
Multi-IAM-Pakistan/
├── MESSAGEix-Pakistan/
│   ├── data/
│   │   ├── MESSAGEix-Pakistan-CurrentMeasures-SSP2.xlsx   # CM scenario input
│   │   ├── MESSAGEix-Pakistan-NDC-U-SSP2.xlsx             # NDC-U scenario input
│   │   ├── MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx          # shared input for NDC-C and NZ
│   │   ├── emissionAllocation.xlsx                        # emission trajectories for the NDC scenarios
│   │   └── legacy/                                        # inherited ENGAGE_SSP2_v417 run configuration and default tables for reporting
│   ├── notebooks/
│   │   ├── current_measures.ipynb                         # build → solve → report --- one notebook per scenario
│   │   ├── ndc-u.ipynb
│   │   ├── ndc-c.ipynb
│   │   └── net-zero.ipynb
│   ├── scripts/
│   │   ├── calibrate_t_d.py                               # historical-activity calibration for transmission/distribution technologies
│   │   ├── reserve_margin.py                              # reserve-margin (res_marg) constraint on elec_t_d
│   │   └── emissions.py                                   # emission-bounds for NDC-U, NDC-C and Net Zero
│   ├── report/
│   │   ├── __init__.py
│   │   └── legacy/                                        # inherited MESSAGEix-GLOBIOM ENGAGE reporting code (IAMC output)
│   └── output/                                            # generated IAMC report files (timestamped)
└── GCAM-Pakistan/                                         # git submodule → https://github.com/hassaniazi/gcam-pakistan @ 4f7e219
```

## MESSAGEix-Pakistan

MESSAGEix-Pakistan directory contains the input excel workbooks, the scenario notebooks,  and the reporting files. The `data/legacy/` and `report/legacy/` directories are inherited from the MESSAGEix-GLOBIOM ENGAGE reporting routines and adapted for the Pakistan node. Reporting is invoked from `report/legacy/iamc_report_hackathon.py`. Four scenarios are developed: Current Measures (CM), NDC-Unconditional (NDC-U), NDC-Conditional (NDC-C), and Net Zero (NZ). Each is solved through GAMS, and reported in an IAMC format by a dedicated notebook.

### Prerequisites

This is not a self-contained Python package; reproducing requires the full MESSAGEix toolchain:

- **GAMS** with a valid academic licence. The `scenario.solve()` step calls the GAMS backend. We used version 40.
- **`message_ix` and `ixmp`** version 3.9.0 were used.
- **Python** version 3.12.7 was used.

GAMS must be installed separately. Please consult https://docs.messageix.org/en/latest/install.html for the complete MESSAGEix installation guide. The Python dependencies are listed in `requirements.txt`.

### Scenarios

| Scenario | Notebook | Scenario name (`ixmp`) | Input workbook | Emission treatment |
| --- | --- | --- | --- | --- |
| Current Measures | `current_measures.ipynb` | `current-measures` | `MESSAGEix-Pakistan-CurrentMeasures-SSP2.xlsx` | none (baseline) |
| NDC-Unconditional | `ndc-u.ipynb` | `ndc-u` | `MESSAGEix-Pakistan-NDC-U-SSP2.xlsx` | emission bounds from `emissionAllocation.xlsx` |
| NDC-Conditional | `ndc-c.ipynb` | `ndc-c` | `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | emission bounds from `emissionAllocation.xlsx` |
| Net Zero | `net-zero.ipynb` | `net-zero` | `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | emission bounds from `net_zero_emissions()`|

### Provenance and attribution

MESSAGEix-Pakistan is built on the `message_ix` and `ixmp` framework developed by IIASA. Please cite `message_ix` (Huppmann et al., 2019, *Environmental Modelling & Software*) and acknowledge GAMS alongside any use of this repository.

## GCAM-Pakistan

`GCAM-Pakistan/` is a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) pointing to [`hassaniazi/gcam-pakistan`](https://github.com/hassaniazi/gcam-pakistan), pinned to commit [`4f7e219`](https://github.com/hassaniazi/gcam-pakistan/commit/4f7e219ac6bfe0a6fa4caf0d4dc87c1b3d55ffea).

After cloning this repository, initialise and populate the submodule with:

```bash
git submodule update --init --recursive
```

