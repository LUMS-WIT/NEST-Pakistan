# Pakistan Energy Data Calibration

Before MESSAGEix-Pakistan can be solved for future scenarios, it must reproduce observed historical energy flows and infrastructure. Calibration is applied in two stages. First, the Pakistan node is downscaled from the South Asia region (R11_SAS) of MESSAGEix-GLOBIOM using country-level global datasets. Second, a detailed calibration is applied for 2015, 2020, and 2025 using national data sources to ensure consistency with officially reported domestic data.

## Calibration overview

Calibration fixes or bounds model variables in historical years so that the optimisation does not rewrite the past. Calibration targets include:

- Installed capacity and power generation by technology
- Energy extraction, production, and imports
- Sectoral energy consumption across industry, residential, commercial, and transport
- Transmission and distribution electricity throughput
- Variable renewable energy (VRE) capacity factors
- Reserve margin requirements for the Pakistan grid
- Consumer-driven distributed solar capacity

In the power sector, 2024 values were used to calibrate the 2025 base year.

## Data sources by sector

| Sector / metric | Primary source |
|---|---|
| Power sector capacity and generation | NEPRA State of Industry Report |
| Energy extraction, imports, consumption | Pakistan Economic Survey 2024–25 |
| Distributed solar capacity | Ember; PRIED-TransitionZero |
| Sectoral energy consumption | Pakistan Economic Survey 2024–25 |
| Transport activity | Pakistan Economic Survey 2024–25 |
| Industrial energy | Pakistan Economic Survey 2024–25 |

Distributed solar is calibrated using Ember and PRIED-TransitionZero estimates due to the limited representation of rooftop solar in official national statistics. Pakistan's installed distributed solar capacity is estimated at 22–32 GW by 2025.

## Transmission and distribution calibration

**Script:** `MESSAGEix-Pakistan/scripts/calibrate_t_d.py`

Historical electricity throughput for the `elec_t_d` technology is fixed in historical years using data from NEPRA's State of Industry Reports. The script reads historical activity levels and writes `historical_activity` parameters to the scenario, ensuring the model's T&D infrastructure matches observed utilisation before the optimisation horizon begins.

| Parameter | Description |
|---|---|
| `historical_activity` | Observed T&D throughput (GWa) by historical year |
| `bound_activity_lo` / `_up` | Bounds to lock historical years against re-optimisation |

## VRE calibration

**Script:** `MESSAGEix-Pakistan/scripts/add_rooftop_solar_pv.py`  
**Data file:** `MESSAGEix-Pakistan/data/VRE_calibration_SSP_dev_v14.xlsx`

Capacity factors and historical activity bounds for variable renewable technologies (utility-scale solar, rooftop solar, wind) are calibrated using the `VRE_calibration_SSP_dev_v14.xlsx` workbook. The `v14` suffix denotes the calibration version used in the published study. Calibration values are downscaled from the South Asia (SAS) region of MESSAGEix-GLOBIOM and applied to the Pakistan node (R12_PAK).

## Reserve margin

**Script:** `MESSAGEix-Pakistan/scripts/reserve_margin.py`

Pakistan's grid reliability standard requires that dispatchable installed capacity exceeds peak demand by a specified margin. The `reserve_margin.py` script sets the `res_marg` parameter on `elec_t_d` to enforce this constraint across optimisation years.

**Data source:** NEPRA State of Industry Report

## Near-term policy constraints

In addition to calibration, near-term technology policies are implemented as hard bounds in all scenarios. These include:

- Committed power sector capacity additions (hydropower mega-projects, CPEC coal plants)
- Consumer-driven rooftop solar growth
- New Energy Vehicle Policy: 30% EV share of new vehicle sales by 2030

See Table S4 of the Supplementary Information for the full policy list.
