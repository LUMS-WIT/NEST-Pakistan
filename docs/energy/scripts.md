# Scripts

The `MESSAGEix-Pakistan/scripts/` directory contains Python modules that apply model modifications to a `message_ix.Scenario` object. They are called from within the scenario notebooks after the base scenario is loaded from the Excel workbook.

## `add_rooftop_solar_pv.py`

Adds a rooftop solar PV technology to the scenario using calibration data from `data/VRE_calibration_SSP_dev_v14.xlsx`. This script encodes the capacity factors, costs, and availability windows for distributed rooftop generation and links it to the residential and commercial demand nodes.

## `calibrate_t_d.py`

Applies historical-activity calibration for transmission and distribution (T&D) technologies. Historical electricity throughput data is used to fix or bound the activity of `elec_t_d` in historical years, ensuring the model reproduces observed infrastructure utilisation before the optimisation horizon begins.

## `reserve_margin.py`

Implements a reserve-margin constraint on `elec_t_d`. The reserve margin requires that dispatchable installed capacity exceeds peak demand by a specified fraction, reflecting reliability standards for the Pakistan grid.

## `emissions.py`

Defines emission bounds for the three mitigation scenarios:

- **NDC-U and NDC-C** — reads annual CO₂ targets from `data/emissionAllocation.xlsx` and writes them as `bound_emission` parameters.
- **Net Zero** — the `net_zero_emissions()` function generates a programmatic emission trajectory that reaches net zero by the target year.

## `utilities/`

Shared helper modules imported by the scripts above:

| Module | Purpose |
|---|---|
| `utilities.py` | General-purpose model utilities |
| `get_nodes.py` | Retrieve node lists from a scenario |
| `get_historical_years.py` | Return historical year set from a scenario |
| `get_optimization_years.py` | Return optimisation year set from a scenario |
