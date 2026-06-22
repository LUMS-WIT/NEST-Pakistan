# Renewables

Pakistan has significant renewable energy potential — particularly solar, wind, and large hydropower — that is central to all mitigation scenarios. This section documents how renewable technologies are represented in MESSAGEix-Pakistan and the data sources used to parameterise them.

## Solar PV

### Utility-scale solar

Utility-scale ground-mounted solar PV is included in the main scenario input workbooks. Capacity factors are derived from satellite-based solar resource data for Pakistan's high-irradiance regions (Balochistan, southern Punjab, Sindh).

**Model technology name:** To be documented

| Parameter | Value | Source |
|---|---|---|
| Capacity factor (annual average) | — | To be documented |
| Investment cost (USD/kW) | — | To be documented |
| Fixed O&M (USD/kW/yr) | — | To be documented |
| Lifetime (years) | — | To be documented |

**Data sources:**

- [ ] To be documented — e.g. IRENA Renewable Power Generation Costs, Global Solar Atlas

### Rooftop solar PV

Rooftop solar PV is added programmatically via a dedicated script rather than through the input workbook, using calibrated capacity factors from the VRE calibration dataset.

**Script:** `MESSAGEix-Pakistan/scripts/add_rooftop_solar_pv.py`  
**Calibration data:** `MESSAGEix-Pakistan/data/VRE_calibration_SSP_dev_v14.xlsx`

The rooftop solar technology is linked to residential and commercial demand nodes. Its potential is bounded by available rooftop area estimates for Pakistan's urban and peri-urban settlements.

| Parameter | Value | Source |
|---|---|---|
| Capacity factor | — | VRE calibration file (v14) |
| Technical potential (GW) | — | To be documented |

**Data sources:**

- [ ] To be documented — rooftop area estimates
- [ ] To be documented — AEDB (Alternative Energy Development Board) data

## Wind

Pakistan's wind corridor along the Sindh coast (Gharo–Kati Bandar) and in Balochistan offers substantial wind potential.

**Model technology name:** To be documented

| Parameter | Value | Source |
|---|---|---|
| Capacity factor (annual average) | — | To be documented |
| Investment cost (USD/kW) | — | To be documented |
| Fixed O&M (USD/kW/yr) | — | To be documented |
| Technical potential (GW) | — | To be documented |

**Data sources:**

- [ ] To be documented — e.g. AEDB Wind Resource Map, Global Wind Atlas

## Hydropower

Large hydropower dominates Pakistan's current installed renewable capacity. Run-of-river and storage plants on the Indus system are included in the model.

**Model technology names:** To be documented

| Plant type | Installed capacity (GW, base year) | Source |
|---|---|---|
| Large storage hydro | — | To be documented |
| Run-of-river | — | To be documented |
| Small hydro | — | To be documented |

Hydropower availability is sensitive to seasonal flow variation and long-term climate change impacts on glacier and snowmelt. The model uses historical capacity factors as a proxy; climate-adjusted capacity factors are a planned extension linked to the Water pillar.

**Data sources:**

- [ ] To be documented — WAPDA (Water and Power Development Authority)
- [ ] NTDC — System Operation Report

## Nuclear

Pakistan operates nuclear power plants at Karachi and Chashma. Nuclear is included as a dispatchable baseload technology.

**Model technology name:** To be documented

| Parameter | Value | Source |
|---|---|---|
| Installed capacity (GW, base year) | — | To be documented |
| Capacity factor | — | To be documented |

**Data sources:**

- [ ] To be documented — PAEC (Pakistan Atomic Energy Commission) / IAEA PRIS

## Key references

- [ ] IRENA — Renewable Energy Statistics
- [ ] AEDB — Renewable Energy Policy and Resource Data
- [ ] World Bank — Pakistan Renewable Energy Atlas
