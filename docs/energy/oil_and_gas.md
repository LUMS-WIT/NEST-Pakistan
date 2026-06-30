# Oil and Gas

Oil and gas are central to Pakistan's current energy system: natural gas supplies industry, power generation, and residential cooking; imported oil products fuel transport and backup power. This section documents how upstream and downstream oil and gas supply chains are represented in MESSAGEix-Pakistan.

## Sector overview

Pakistan is a natural gas producer but depends heavily on LNG imports and crude oil imports to meet demand. Key features of the sector:

- Declining indigenous gas production from mature fields (Sui, Mari, Qadirpur)
- Growing LNG import capacity (FSRU terminals at Port Qasim)
- Refinery capacity well below domestic demand; petroleum product imports are large
- Furnace oil (fuel oil) used in power generation, declining under policy pressure
- Heavy exposure to international fuel price volatility; global energy price shocks in 2022 severely stressed Pakistan's import bill

Under Current Measures, natural gas accounts for approximately 31% of primary energy in MESSAGEix-Pakistan, rising to 39% under NDC-Unconditional as gas partially replaces coal. Under Net Zero, gas declines to 16% of primary energy by 2050 in MESSAGEix-Pakistan, and from 27% to 1% in GCAM-Pakistan, as electrification and efficiency displace direct fossil combustion.

**Data sources:** Pakistan Economic Survey 2024–25; HDIP Pakistan Energy Yearbook; OGRA Annual Report

## Natural gas

### Indigenous production

Pakistan's domestic gas fields are in decline. The model represents indigenous production as a resource-constrained supply technology with an exogenous depletion trajectory calibrated to historically reported output levels.

| Field / region | Production status |
|---|---|
| Sui (Balochistan) | Declining |
| Mari (Sindh) | Declining |
| Qadirpur | Declining |

Technology names for gas fields are defined in the scenario input workbooks (`MESSAGEix-Pakistan-CurrentMeasures-SSP2.xlsx` and shared workbooks).

**Data sources:** OGRA Annual Report; Pakistan Economic Survey 2024–25; HDIP Pakistan Energy Yearbook

### LNG imports

Pakistan has rapidly expanded LNG import capacity since 2015. LNG is represented as an import commodity with an international price trajectory based on World Bank commodity projections.

| Terminal | Location |
|---|---|
| PGPCL FSRU | Port Qasim, Karachi |
| ETPL FSRU | Port Qasim, Karachi |

**Data sources:** GIIGNL LNG Report; World Bank Commodity Markets Outlook

### Gas distribution

The national gas transmission and distribution network (SNGPL serving Punjab and KPK; SSGC serving Sindh and Balochistan) is modelled as a single T&D technology node. System losses and unaccounted-for gas (UFG) are calibrated from SNGPL and SSGC annual reports.

**Data sources:** SNGPL Annual Report; SSGC Annual Report

## Oil

### Crude oil and refined products

Pakistan imports the majority of its crude oil and petroleum products. Indigenous crude production is small and declining. Refinery capacity is insufficient to meet domestic demand, so petroleum product imports fill the gap.

| Commodity | Notes |
|---|---|
| Crude oil imports | Primary import for domestic refining |
| Petrol (motor spirit) | Import + domestic refining |
| Diesel (high speed diesel, HSD) | Import + domestic refining; primary freight fuel |
| Furnace oil | Domestic refining; used in thermal power plants |
| LPG | Domestic refining + imports; residential cooking |

**Data sources:** HDIP Oil Companies Advisory Council (OCAC) data; Pakistan State Oil (PSO) Annual Report; Pakistan Economic Survey 2024–25

### Refineries

Pakistan has several refineries — PARCO, NRL, PRL, ARL, and Byco. The model aggregates these into a single refinery technology with calibrated throughput and efficiency parameters.

**Data sources:** OGRA refinery licensing data; HDIP Pakistan Energy Yearbook

## Phasedown in mitigation scenarios

| Scenario | Gas trajectory | Oil trajectory |
|---|---|---|
| CM | +31% → 39% of primary energy by 2050 | Steady with demand growth |
| NDC-U | Gas rises as coal substitute (39% by 2050) | Moderate reduction |
| NDC-C | Gas peaks, begins decline | Oil product decline accelerates |
| NZ | Gas falls to 16% (MESSAGEix) / 1% (GCAM) by 2050 | Petroleum phased out in transport |

Furnace oil phaseout is an early mitigation measure across NDC scenarios. Natural gas demand peaks and declines as the power sector shifts to renewables and end-use electrification progresses. Domestic solar expansion and CPEC coal overcapacity together reduce the electricity system's reliance on gas even under Current Measures. LNG import volumes are sensitive to the pace of gas demand reduction.

## Key references

- OGRA — Annual Report (natural gas and petroleum)
- HDIP — Pakistan Energy Yearbook
- SNGPL / SSGC — Annual Reports
- Pakistan Economic Survey 2024–25 (Energy chapter)
- World Bank — Commodity Markets Outlook
