# Scenarios

Four scenarios are developed in MESSAGEix-Pakistan, spanning the range from a no-new-policy baseline to full net zero.

## Summary

| Scenario | Short name | Notebook | `ixmp` scenario name | Input workbook | Emission treatment |
|---|---|---|---|---|---|
| Current Measures | CM | `current_measures.ipynb` | `current-measures` | `MESSAGEix-Pakistan-CurrentMeasures-SSP2.xlsx` | None (baseline) |
| NDC-Unconditional | NDC-U | `ndc-u.ipynb` | `ndc-u` | `MESSAGEix-Pakistan-NDC-U-SSP2.xlsx` | Emission bounds from `emissionAllocation.xlsx` |
| NDC-Conditional | NDC-C | `ndc-c.ipynb` | `ndc-c` | `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | Emission bounds from `emissionAllocation.xlsx` |
| Net Zero | NZ | `net-zero.ipynb` | `net-zero` | `MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx` | Emission bounds from `net_zero_emissions()` |

All scenarios use the SSP2 socioeconomic pathway as the activity driver.

## Current Measures (CM)

The baseline scenario. It reflects only currently implemented policies and planned capacity as of the modelling base year. No additional emission constraints are imposed. This scenario serves as the reference against which mitigation scenarios are measured.

## NDC-Unconditional (NDC-U)

Implements Pakistan's unconditional NDC target — the mitigation commitment that Pakistan will undertake regardless of international climate finance. Emission bounds are read from `data/emissionAllocation.xlsx` and applied as annual `emission_factor` constraints in the model.

## NDC-Conditional (NDC-C)

Implements Pakistan's conditional NDC target — a deeper mitigation level contingent on receiving international climate finance and technology transfer. This scenario shares its base input workbook with Net Zero (`MESSAGEix-Pakistan-NDC-C_NZ-SSP2.xlsx`). Emission bounds come from `data/emissionAllocation.xlsx`.

## Net Zero (NZ)

The most ambitious scenario, targeting net zero emissions. Emission bounds are generated programmatically by the `net_zero_emissions()` function defined in `scripts/emissions.py` rather than read from a static file. This scenario shares its base input workbook with NDC-C.
