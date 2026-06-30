# Scenarios

Four scenarios are developed in MESSAGEix-Pakistan, spanning the range from a no-new-policy baseline to full net zero. NDC targets are applied to the modelled Current Measures emissions trajectory rather than to Pakistan's official NDC baseline projections (which assume ~9.5% annual GHG growth, substantially above Pakistan's historical rate of ~4%).

## Summary

| Scenario | Short name | Notebook | `ixmp` scenario name | Input workbook | Emission treatment |
|---|---|---|---|---|---|
| Current Measures | CM | `current_measures.ipynb` | `current-measures` | `MESSAGEix-Pakistan-CurrentMeasures-SSP2.xlsx` | None (baseline) |
| NDC-Unconditional | NDC-U | `ndc-u.ipynb` | `ndc-u` | `MESSAGEix-Pakistan-NDC-U-SSP2.xlsx` | Emission bounds from `emissionAllocation.xlsx` |
| NDC-Conditional | NDC-C | `ndc-c.ipynb` | `ndc-c` | `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | Emission bounds from `emissionAllocation.xlsx` |
| Net Zero | NZ | `net-zero.ipynb` | `net-zero` | `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | Emission bounds from `net_zero_emissions()` |

All scenarios use the SSP2 socioeconomic pathway as the activity driver (population 249M→370M; GDP PPP USD 1,396B→3,975B by 2050 in 2017 USD). Energy service demands are exogenous and identical across all four scenarios; only the supply configuration is optimised.

Emission constraints are applied to Kyoto gases in the energy sector, matching the percentage reductions specified for the whole economy in Pakistan's NDC. The 2035 percentage reduction level is held constant in subsequent periods.

## Current Measures (CM)

The baseline scenario. It reflects only currently implemented policies and committed capacity as of the modelling base year (2025). No additional emission constraints are imposed. This scenario serves as the reference against which mitigation scenarios are measured.

Under CM, fossil fuels in primary energy increase 2.1–3.6× by 2050. Energy-sector Kyoto greenhouse gas emissions rise from 246–259 MtCO₂-eq in 2025 to 555–860 MtCO₂-eq by 2050.

## NDC-Unconditional (NDC-U)

Implements Pakistan's unconditional NDC target — the mitigation commitment that Pakistan will undertake regardless of international climate finance. Pakistan's NDC (2021) pledges a 15% unconditional reduction; NDC 3.0 (2025) increases this to 17%.

Emission bounds are read from `data/emissionAllocation.xlsx`. This scenario requires only a 6% increase above CM in long-term cumulative energy supply investment ($37 billion additional above $596 billion), making it a no-regrets pathway. Consumer electricity prices remain within 6% above CM.

## NDC-Conditional (NDC-C)

Implements Pakistan's conditional NDC target — a 50% reduction below CM emissions contingent on receiving international climate finance and technology transfer. This scenario shares its base input workbook with Net Zero (`MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx`). Emission bounds come from `data/emissionAllocation.xlsx`.

NDC-C requires higher near-term investment than Net Zero ($446 billion vs $408 billion over 2025–2035) because the 50% target forces rapid near-term deployment. Consumer electricity prices peak at 28% above CM in 2035. By 2035, NDC-C and NZ converge in MESSAGEix; thereafter NZ continues to decline while NDC-C emissions rise as the 50% target is defined relative to the growing CM baseline.

## Net Zero (NZ)

The most ambitious scenario, targeting net zero energy-sector emissions. Emission bounds are generated programmatically by the `net_zero_emissions()` function in `scripts/emissions.py`. This scenario shares its base input workbook with NDC-C.

Under NZ, the power sector fully decarbonises by 2050 in MESSAGEix-Pakistan. Solar provides 55–56% of electricity and 26–43% of primary energy. Electricity's share of total final energy rises from 14–17% in 2025 to 52–57% under NZ. Hydrogen fills the gap for hard-to-electrify end uses, reaching 13% of final energy. Cumulative long-term investment (2025–2050) is $1,553 billion, approximately 2.6× CM.
