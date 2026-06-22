# Data

All input data for MESSAGEix-Pakistan lives in `MESSAGEix-Pakistan/data/`.

## Scenario input workbooks

Each Excel workbook encodes the full parameterisation of a scenario — technologies, capacities, costs, demands, and constraints — in the structured format expected by the `message_ix` Excel importer.

| File | Used by |
|---|---|
| `MESSAGEix-Pakistan-CurrentMeasures-SSP2.xlsx` | CM scenario |
| `MESSAGEix-Pakistan-NDC-U-SSP2.xlsx` | NDC-U scenario |
| `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | NDC-C and NZ scenarios (shared) |

## Auxiliary data files

**`VRE_calibration_SSP_dev_v14.xlsx`** — Variable renewable energy (VRE) calibration data used by `scripts/add_rooftop_solar_pv.py`. The `v14` suffix denotes the calibration version used in the published study.

**`emissionAllocation.xlsx`** — Annual emission trajectories (CO₂ bounds) for the NDC-U and NDC-C scenarios, derived from Pakistan's NDC targets and allocated to the energy system.

## Legacy data

`data/legacy/` contains configuration files and default tables inherited from the MESSAGEix-GLOBIOM ENGAGE project (SSP2 v4.1.7 run) and adapted for the Pakistan node:

| File | Purpose |
|---|---|
| `ENGAGE_SSP2_v417_run_config.yaml` | ENGAGE run configuration reference |
| `default_run_config.yaml` | Adapted run configuration for Pakistan |
| `default_aggregates.csv` | IAMC variable aggregation rules |
| `default_kyoto_hist.csv` | Historical Kyoto gas emissions |
| `default_lu_co2_hist.csv` | Historical land-use CO₂ |
| `default_pop_urban_rural.csv` | Urban/rural population splits |
| `default_units.yaml` | Unit definitions for IAMC reporting |
| `default_variable_definitions.csv` | IAMC variable metadata |
