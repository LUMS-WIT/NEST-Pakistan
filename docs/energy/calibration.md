# Pakistan Energy Data Calibration

Before the MESSAGEix-Pakistan model can be solved for future scenarios, it must reproduce observed historical energy flows and infrastructure in the base year. This section documents the calibration procedures applied to align the model with Pakistan-specific historical data.

## Calibration overview

Calibration fixes or bounds model variables in historical years so that the optimisation does not rewrite the past. The main calibration targets are:

- Transmission and distribution (T&D) electricity throughput
- Variable renewable energy (VRE) capacity factors
- Reserve margin requirements for the Pakistan grid
- Base year demand levels by sector

## Transmission and distribution calibration

**Script:** `MESSAGEix-Pakistan/scripts/calibrate_t_d.py`

Historical electricity throughput for the `elec_t_d` technology is fixed in historical years using data from Pakistan's electricity supply statistics. The script reads historical activity levels and writes `historical_activity` parameters to the scenario, ensuring the model's T&D infrastructure matches observed utilisation before the optimisation horizon begins.

Key parameters set:

| Parameter | Description |
|---|---|
| `historical_activity` | Observed T&D throughput (GWa) by historical year |
| `bound_activity_lo` / `_up` | Bounds to lock historical years against re-optimisation |

**Data sources:**

- [ ] To be documented — add primary source for Pakistan T&D historical data

## VRE capacity factor calibration

**Script:** `MESSAGEix-Pakistan/scripts/add_rooftop_solar_pv.py`  
**Data file:** `MESSAGEix-Pakistan/data/VRE_calibration_SSP_dev_v14.xlsx`

Capacity factors for variable renewable technologies (solar PV, wind) are calibrated using the `VRE_calibration_SSP_dev_v14.xlsx` workbook. The `v14` suffix denotes the calibration version used in the published study. The script reads capacity factor profiles and technology cost data from this workbook and writes them as `capacity_factor` and `inv_cost` / `fix_cost` parameters in the scenario.

**Data sources:**

- [ ] To be documented — add source for solar resource data (e.g. PVGIS, Global Solar Atlas)
- [ ] To be documented — add source for wind resource data

## Reserve margin

**Script:** `MESSAGEix-Pakistan/scripts/reserve_margin.py`

Pakistan's grid reliability standard requires that dispatchable installed capacity exceed peak demand by a specified margin. The `reserve_margin.py` script sets the `res_marg` parameter on `elec_t_d` to enforce this constraint across optimisation years.

| Parameter | Value | Source |
|---|---|---|
| Reserve margin (%) | — | To be documented |

**Data sources:**

- [ ] To be documented — add NEPRA or NTDC source for reserve margin requirement

## Base year demand

Base year energy demand by sector is set directly in the scenario input workbooks. The calibration target is the Pakistan Energy Yearbook published by HDIP (Hydrocarbon Development Institute of Pakistan).

| Sector | Data source |
|---|---|
| Residential | To be documented |
| Commercial | To be documented |
| Industry | To be documented |
| Transport | To be documented |
| Agriculture | To be documented |

**Key references:**

- [ ] HDIP — Pakistan Energy Yearbook (latest edition)
- [ ] NEPRA — State of Industry Report
- [ ] NTDC — System Operation Report
