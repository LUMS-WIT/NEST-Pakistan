# Overview

## Study context

This repository supports the study *Decarbonization Pathways and Equity Implications of Pakistan's Climate Ambition* (Yaseen et al.). The study presents the first multi-model assessment of Pakistan's energy transition, using MESSAGEix-Pakistan (cost-optimisation) and GCAM-Pakistan (market-equilibrium) to evaluate technology pathways, investment requirements, and equity implications across four scenarios: Current Measures, NDC Unconditional, NDC Conditional, and Net Zero.

Key findings:

- Under Current Measures, fossil fuels in primary energy increase 2.1–3.6× by 2050.
- Meeting the unconditional NDC requires only a 6% increase above Current Measures in energy supply investment ($37 billion above a $596 billion baseline), making it a no-regrets pathway.
- Net Zero requires a 160% increase in cumulative energy supply investment ($1,553 billion).
- Both models converge on solar providing 55–56% of electricity under Net Zero.
- Transport electrification reaches 62–80% under Net Zero; buildings 52–75%.
- Pakistan's per-capita emissions remain within most fair-share allocations of the global carbon budget through the 2030s under the unconditional NDC.

## MESSAGEix-Pakistan

MESSAGEix-Pakistan is a national energy system application developed within the open-source [`message_ix`](https://docs.messageix.org) and [`ixmp`](https://docs.messageix.org/projects/ixmp) framework maintained by IIASA. It is a bottom-up, linear-programming model that solves for least-cost configurations of the full energy supply chain — from resource extraction through conversion, transmission, and end-use — subject to exogenous energy service demands and technical, economic, and environmental constraints.

The model represents Pakistan as a single node (R12_PAK), developed by downscaling the South Asia region (R11_SAS) of MESSAGEix-GLOBIOM. It represents seven useful-energy service demands: residential and commercial thermal, residential and commercial specific electricity, industrial thermal, industrial specific electricity, industrial feedstock, transport, and non-commercial biomass. The optimisation is implemented in GAMS; scenario and data management uses the ix modelling platform (ixmp).

| Property | Value |
|---|---|
| Base year | 2025 |
| Time horizon | 2025–2070 (results reported to 2050) |
| Time step | 5 years |
| Spatial resolution | Single national node (R12_PAK) |
| Solver | GAMS |

Both models are driven by SSP2 socioeconomic assumptions: Pakistan's population grows from 249 million in 2025 to 370 million by 2050, and GDP (PPP) from USD 1,396 billion to USD 3,975 billion (2017 USD).

## Scenarios

Four scenarios are developed, each solved through the GAMS optimisation solver:

| Scenario | Short name | Mitigation level |
|---|---|---|
| Current Measures | CM | No additional constraints; fossil fuel baseline |
| NDC-Unconditional | NDC-U | 15% reduction below CM emissions (17% under NDC 3.0) |
| NDC-Conditional | NDC-C | 50% reduction below CM emissions, contingent on international finance |
| Net Zero | NZ | Net zero energy-sector emissions |

NDC targets are applied to the modelled CM emissions trajectory rather than to Pakistan's official high-growth NDC baseline projections.
