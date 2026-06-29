# Oil and Gas

Oil and gas are central to Pakistan's current energy system: natural gas supplies industry, power generation, and residential cooking; imported oil products fuel transport and backup power. This section documents how upstream and downstream oil and gas supply chains are represented in MESSAGEix-Pakistan.

## Sector overview

Pakistan is a natural gas producer but depends heavily on LNG imports and crude oil imports to meet demand. Key features of the sector:

- Declining indigenous gas production from mature fields (Sui, Mari, Qadirpur)
- Growing LNG import capacity (FSRU terminals at Port Qasim)
- Refinery capacity well below domestic demand; petroleum product imports are large
- Furnace oil (fuel oil) used in power generation, declining under policy pressure

**Data sources:**

- [ ] To be documented — OGRA (Oil and Gas Regulatory Authority) Annual Report
- [ ] To be documented — HDIP Pakistan Energy Yearbook (Oil and Gas chapters)

## Natural gas

### Indigenous production

Pakistan's domestic gas fields are in decline. The model represents indigenous production as a resource-constrained supply technology with an exogenous depletion trajectory.

| Field / region | Production status | Model name |
|---|---|---|
| Sui (Balochistan) | Declining | To be documented |
| Mari (Sindh) | Declining | To be documented |
| Qadirpur | Declining | To be documented |

**Data sources:**

- [ ] To be documented — OGRA / PPIS (Pakistan Petroleum Information System)

### LNG imports

Pakistan has rapidly expanded LNG import capacity. LNG is represented as an import commodity with an international price trajectory.

| Terminal | Capacity (MMTPA) | Model name |
|---|---|---|
| PGPCL FSRU (Port Qasim) | — | To be documented |
| ETPL FSRU (Port Qasim) | — | To be documented |

**Price assumptions:**

- [ ] To be documented — LNG spot price trajectory used in scenarios

**Data sources:**

- [ ] To be documented — GIIGNL LNG Report, World Bank commodity projections

### Gas distribution

The national gas transmission and distribution network (SNGPL, SSGC) is modelled as a single T&D technology node.

**Data sources:**

- [ ] To be documented — SNGPL / SSGC Annual Reports

## Oil

### Crude oil and refined products

Pakistan imports the majority of its crude oil and petroleum products. Indigenous crude production is small and declining. Refinery capacity is insufficient to meet domestic demand.

| Commodity | Import/domestic | Model name |
|---|---|---|
| Crude oil imports | Import | To be documented |
| Petrol (motor spirit) | Import + domestic refining | To be documented |
| Diesel (HSD) | Import + domestic refining | To be documented |
| Furnace oil | Domestic refining | To be documented |
| LPG | Domestic refining + import | To be documented |

**Data sources:**

- [ ] To be documented — HDIP Oil Companies Advisory Council (OCAC) data
- [ ] To be documented — Pakistan State Oil (PSO) Annual Report

### Refineries

Pakistan has several refineries (PARCO, NRL, PRL, ARL, Byco). The model aggregates these into a single refinery technology.

**Data sources:**

- [ ] To be documented — OGRA refinery licensing data

## Phasedown in mitigation scenarios

Furnace oil phaseout is an early mitigation measure across NDC scenarios. Natural gas demand peaks and declines as the power sector shifts to renewables and end-use electrification progresses. LNG import volumes are sensitive to the pace of gas demand reduction.

## Key references

- [ ] OGRA — Annual Report (natural gas and petroleum)
- [ ] HDIP — Pakistan Energy Yearbook (Oil and Gas)
- [ ] SNGPL / SSGC — Annual Reports
- [ ] IEA — World Energy Outlook (Natural Gas chapter)
- [ ] IRENA — World Energy Transitions Outlook
