# Renewables

Pakistan has significant renewable energy potential — solar, wind, and large hydropower — that is central to all mitigation scenarios. Under Net Zero, solar provides 55–56% of electricity and 26–43% of primary energy in both MESSAGEix-Pakistan and GCAM-Pakistan, making it the single largest energy source.

## Solar PV

### Utility-scale solar

Utility-scale ground-mounted solar PV is included in the scenario input workbooks. Pakistan's high-irradiance regions (Balochistan, southern Punjab, Sindh) offer some of the best solar resources in Asia. Calibrated using national data sources for 2025.

**Data sources:** Pakistan Economic Survey 2024–25; NEPRA State of Industry Report; Ember

### Rooftop solar PV

Rooftop solar PV is added programmatically via a dedicated script using calibrated capacity factors from the VRE calibration dataset. Pakistan has undergone a rapid consumer-driven rooftop solar expansion, with distributed capacity estimated at 22–32 GW by 2025. This has resulted in declining grid electricity generation since 2022.

**Script:** `MESSAGEix-Pakistan/scripts/add_rooftop_solar_pv.py`  
**Calibration data:** `MESSAGEix-Pakistan/data/VRE_calibration_SSP_dev_v14.xlsx`

The rooftop solar technology is linked to residential and commercial demand nodes. Historical capacity and activity are calibrated using Ember and PRIED-TransitionZero estimates, given limited coverage in official statistics.

**Data sources:** Ember; PRIED-TransitionZero; AEDB

### Solar in mitigation scenarios

| Scenario | Solar share of electricity (2050) | Solar share of primary energy (2050) |
|---|---|---|
| CM | — | — |
| NDC-U | Partial expansion | — |
| NDC-C | Dominant source | — |
| NZ | 55–56% | 26–43% |

Under NZ, 515 GW of solar is integrated, requiring substantial grid and storage investment (T&D and storage together account for 29% of long-term NZ investment).

## Wind

Pakistan's wind corridor along the Sindh coast (Gharo–Kati Bandar) and in Balochistan offers substantial potential. Wind is included in the scenario input workbooks and contributes to the NDC-C and NZ electricity mix. Under NZ, MESSAGEix-Pakistan integrates approximately 70 GW of wind capacity by 2050.

**Data sources:** AEDB Wind Resource Map; NEPRA State of Industry Report

## Hydropower

Large hydropower dominates Pakistan's current installed renewable capacity. Run-of-river and storage plants on the Indus system are included in the model. Committed hydropower mega-projects are included as near-term policy constraints in all scenarios. Under NZ (near-term, 2025–2035), hydropower accounts for 27% of cumulative investment ($111 billion).

Hydropower availability is sensitive to seasonal flow variation and long-term glacier and snowmelt changes. The model uses calibrated capacity factors; climate-adjusted hydropower is a planned extension.

**Data sources:** WAPDA; NEPRA State of Industry Report; Pakistan Economic Survey 2024–25

## Nuclear

Pakistan operates nuclear power plants at Karachi (KANUPP) and Chashma (CHASNUPP). Nuclear is included as a dispatchable baseload technology. Under NZ, nuclear contributes 17% of electricity in MESSAGEix-Pakistan by 2050 — comparable to Pakistan's recent nuclear share of approximately 18% in fiscal year 2024, but at nearly double the absolute generation volume.

**Data sources:** PAEC (Pakistan Atomic Energy Commission); NEPRA State of Industry Report
