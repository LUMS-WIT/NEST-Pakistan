# Model Input & Assumptions

Each scenario file includes sets and parameters used in the model. Many of these input data points are already reported in the output files, such as **efficiency, technical lifetime, and operation & maintenance (O&M) costs for technologies**.

For certain sheets where data sources and assumptions are required, they are documented below. For a detailed explanation of each set or parameter used in the core model formulation, refer to the following documentation:

- **Sets**: [MESSAGE Sets and Mappings](https://docs.messageix.org/en/latest/model/MESSAGE/sets_maps_def.html#)
- **Parameters**: [MESSAGE Parameters](https://docs.messageix.org/en/latest/model/MESSAGE/sets_maps_def.html#)

For the name and descrion of the MESSAGE commodities, technologies and relations:

* [Technologies](https://docs.messageix.org/projects/models/en/latest/pkg-data/codelists.html#technologies-technology-yaml)
  * For new technologies that are added in the model. See below.
* [Commodities](https://docs.messageix.org/projects/models/en/latest/pkg-data/codelists.html#commodities-commodity-yaml)
* [Relations](https://docs.messageix.org/projects/models/en/latest/pkg-data/relation.html)
* [Emission Species](https://docs.messageix.org/projects/models/en/latest/pkg-data/codelists.html#emission-species-emission-yaml)

# **📊 Data Sources and Assumptions**

The table below summarizes the data sources used for different input parameters:

| **Data Type**                       | **Sheet Name(s)**                                                                                                                     | **Description**                                                                                                                                                                                                                                                                                                                                             |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Costs**                           | `inv_cost`, `fix_cost`, `var_cost`                                                                                                    | Cost data is sourced from**WEO data**, fuel blending, and energy demands. For more details, refer to the MESSAGEix-GLOBIOM documentation [page](https://docs.messageix.org/projects/global/en/latest/energy/tech.html). At this point, there is no provinciial differentiation in technology costs but future work will explore varying technological costs.  |
| **Energy Resources**                | `historical_activity`                                                                                                                     | Historical oil and gas production data is sourced from**[Canada Energy Future](https://www.cer-rec.gc.ca/en/index.html)**. Data and processing scripts are available in `data/oil_gas_production`.                                                                                                                                                                 |
| **Energy End-Use**                  | `initial_activity_lo`, `growth_activity_lo`, `growth_activity_up`, `initial_activity_up`                                            | Eneergy end use asumptions growth rates and diffusion rates are based on SSP2 assumptions. For more details on the assumptions and how end-use technologies are mapped to useful demands refer to the documentation[page](https://docs.messageix.org/projects/global/en/latest/energy/enduse/index.html).                                                           |
| **Population and GDP**              | `bound_activity_lo`, `bound_activity_up`                                                                                                | Population projections for provinces are sourced from**Statistics Canada** (till 2048) and projected till 2060 using linear regression. GDP projections apply federal growth rate predictions to current provincial GDP values.                                                                                                                             |
| **Energy Service Demands**          | `demand`                                                                                                                                  | Energy demands are calculated using population and GDP data (`data/population` and `data/gdp`).                                                                                                                                                                                                                                                               |
| **Power Plant Capacity**            | `historical_new_capacity`, `bound_new_capacity_lo`, `bound_new_capacity_up`, `bound_total_capacity_lo`, `bound_total_capacity_up` | Data is collected and pre-processed from**[CODERS](https://coders.cme-emh.ca/login)**. Vintage years are used to bound new capacity installations based on the technical lifetime of each technology.                                                                                                                                                                |
| **Renewable Energy Potentials**     | `renewable_potential`                                                                                                                     | Based on**gridded capacity factors** from [CODERS](https://coders.cme-emh.ca/login) data. The maximum producible solar, onshore wind, and offshore wind energy are multiplied by capacity factors.                                                                                                                                                             |
| **Historical Generation & End-Use** | `historical_activity`                                                                                                                     | Calibrated using **CER current measures**, mapped appropriately to individual technologies.                                                                                                                                                                                                                                                                |
|                                           |                                                                                                                                             |                                                                                                                                                                                                                                                                                                                                                                   |

---

## 🛢️Oil & Gas Resource

MESSAGEix represents fossil-fuel resources via the parameter `resource_volume`, enforcing both cumulative and annual extraction limits so that total withdrawals never exceed the estimated reserves.For details on the mathemartical forumulation for resource, see the `message_ix` equation [here](https://docs.messageix.org/en/latest/model/MESSAGE/model_core.html#equation-resource-constraint). More details on the fossil fuel implementation and resource supply curves are also mentioned in the global model documentation [here](https://docs.messageix.org/projects/global/en/latest/energy/resource/fossilfuel.html). For Canada, we begin with SSP2 global availability figures and scale them to national totals reported by Natural Resources Canada. We then partition the country-level resource volumes into technology-specific “categories” of oil and gas extraction. Where provincial data on resource volumes are sparse or inconsistent, resources are allocated across provinces in proportion to historical extraction data from the [Canada Energy Regulator (CER)](https://www.cer-rec.gc.ca/en/data-analysis/canada-energy-future/).We also used the Natural Resources Canada [Fossil Fuels database ](https://natural-resources.canada.ca/energy-sources/fossil-fuels)to adjust the maximum constraints based on the resource availability in each province. 

Oil extraction is divided into six primary categories (I–VI) plus a market-penetration factor; methane-reduction variants (`_ch4`) are defined for the first four categories. Historical CER production categories are mapped to these model codes (e.g., “CONVENTIONAL LIGHT” → `oil_extr_1`). The table below summarizes each oil extraction category, its input/output commodities, and the CER mapping.

### Oil Extraction Categories

A schematic showing how the oil extraction is mapped from supply till end use;
![](include/oil_res.png)

| Category                 | Code               | Description                                                         | Input Resource       | Output Commodity | CER Mapping         |
| ------------------------ | ------------------ | ------------------------------------------------------------------- | -------------------- | ---------------- | ------------------- |
| Conventional Light       | `oil_extr_1`     | Cat I: conventional light crude                                     | `crude 1 resource` | `crude oil`    | CONVENTIONAL LIGHT  |
| CH₄ reduction (Cat I)   | `oil_extr_1_ch4` | Methane-reduction in Cat I extraction                               | `crude 1 resource` | `crude oil`    | CONVENTIONAL LIGHT  |
| Pentanes plus (NGL)      | `oil_extr_2`     | Cat II: undiscovered conventional (incl. NGL)                       | `crude 2 resource` | `crude oil`    | C5+ (PENTANES PLUS) |
| CH₄ reduction (Cat II)  | `oil_extr_2_ch4` | Methane-reduction in Cat II extraction                              | `crude 2 resource` | `crude oil`    | C5+ (PENTANES PLUS) |
| Conventional Heavy       | `oil_extr_3`     | Cat III: “Masters 5 %–50 %” of conventional heavy                | `crude 3 resource` | `crude oil`    | CONVENTIONAL HEAVY  |
| CH₄ reduction (Cat III) | `oil_extr_3_ch4` | Methane-reduction in Cat III extraction                             | `crude 3 resource` | `crude oil`    | CONVENTIONAL HEAVY  |
| Field Condensate         | `oil_extr_4`     | Cat IV: recoverable non-conventional reserves (condensate)          | `crude 4 resource` | `crude oil`    | FIELD CONDENSATE    |
| CH₄ reduction (Cat IV)  | `oil_extr_4_ch4` | Methane-reduction in Cat IV extraction                              | `crude 4 resource` | `crude oil`    | FIELD CONDENSATE    |
| In Situ Bitumen          | `oil_extr_5`     | Cat V: in situ bitumen (shale, tarsands/bitumen, heavy oils)        | `crude 5 resource` | `crude oil`    | IN SITU BITUMEN     |
| Mined Bitumen            | `oil_extr_6`     | Cat VI: mined bitumen (20 % of remaining non-conventional reserves) | `crude 6 resource` | `crude oil`    | MINED BITUMEN       |
| Market penetration       | `oil_extr_mpen`  | Common market-penetration factor for all oil extraction (exports)   | —                   | `exports`      | —                  |

### Gas Extraction Categories

Natural gas extraction follows a similar six-category structure plus market penetration. Categories I–III cover conventional reserves and undiscovered volumes; IV captures enhanced recovery plus a share of historical production; V–VII represent non-conventional resources split across coal-bed methane, shale, and tight formations. CER reports gas production uses five labels—`CONVENTIONAL`, `COAL BED METHANE`, `SHALE`, `TIGHT`, `SOLUTION`—which are mapped into the model as shown below.

| Category                   | Code              | Description                                                                     | Input Resource | Output Commodity | CER Mapping                    |
| -------------------------- | ----------------- | ------------------------------------------------------------------------------- | -------------- | ---------------- | ------------------------------ |
| Conventional (Cat I)       | `gas_extr_1`    | Identified conventional reserves (“Master et al.”)                            | `resource`   | `primary`      | CONVENTIONAL                   |
| Undiscovered mode (Cat II) | `gas_extr_2`    | Mode undiscovered conventional gas                                              | `resource`   | `primary`      | SOLUTION                       |
| Diff. mode–5 % (Cat III)  | `gas_extr_3`    | Difference between “mode” and 5 % undiscovered gas                            | `resource`   | `primary`      | SOLUTION                       |
| Enhanced recovery (Cat IV) | `gas_extr_4`    | 30 % of resources I–III + 15 % of historical production                        | `resource`   | `primary`      | CONVENTIONAL                   |
| Non-conventional (Cat V)   | `gas_extr_5`    | 20 % coal bed; 15 % fractured shale; 15 % tight formation                       | `resource`   | `primary`      | COAL BED METHANE, SHALE, TIGHT |
| Remainder (Cat VI–VII)    | `gas_extr_6`    | Remaining non-conventional (80 % coal bed; 85 % shale; 85 % tight), split 40/60 | `resource`   | `primary`      | COAL BED METHANE, SHALE, TIGHT |
| Market penetration         | `gas_extr_mpen` | Common market-penetration factor for all gas extraction (exports)               | —             | `exports`      | —                             |

### Refineries

Two refinery technologies—“Existing (low yield)” and “New Deeply upgraded”—are defined. Both consume `crude oil` and produce refined petrochemical products. Refinery capacities and efficiencies are calibrated at provincial scale to historical throughput data.

### Trade Assumptions

* **Exogenous trade** : Oil & gas imports/exports are exogenous and set equal to historical provincial flows.
* **No explicit bounds** : No capacity or tariff constraints in the current version.
* **Province-level** : Only provinces with refinery technologies may export refined products; others must import.
* **Future work** : Endogenous trade constraints (transport costs, tariffs, capacity limits) will be introduced in later model versions.

## Electricity Supply

### Renewable Potentials

Renewable potentials for solar and wind are estimated using gridded capacity factors from the [CODERS](https://coders.cme-emh.ca/login) database. For each grid cell, we calculate the maximum power generation potential from solar and wind based on historical capacity factors. These grid‐level potentials are then aggregated to the provincial scale, grouped into capacity‐factor bins. In MESSAGEix, each bin defines a maximum renewable potential for a given capacity factor range. For more information on grid integration and reliability, see the [Systems Integrtaions &amp; Reliability](https://docs.messageix.org/projects/global/en/v2020/energy/conversion/grid.html#systems-integration-and-reliability) section of the MESSAGEix documentation.

### Historical Power Plant Capacity & Generation

Historical installed capacity and generation data come from CODERS. CODERS provides both capacity factors and the installed capacity for each power plant. We convert these values into historical generation (MWh) and validate them against publicly available Canada Energy Regulator (CER) data by province. Retirement schedules and vintaging of thermal power plants are calibrated using the[ technical_lifetime parameter](https://docs.messageix.org/en/latest/model/MESSAGE/parameter_def.html). Future installations of new power plants are constrained by provincial dynamics (e.g., resource availability, policy targets).

For detailed information on how MESSAGEix handles historical capacity and activity values, refer to the [Historical Capacity and Activity Values](https://docs.messageix.org/en/latest/model/MESSAGE/parameter_def.html#historical-capacity-and-activity-values) documentation.

## Energy Demand & End Use

Baseline energy service demands are provided exogenously to MESSAGEix. In this version, we project future demands by scaling historical final-energy consumption using provincial population and GDP growth rates, and then reconcile any year-to-year discrepancies via a minimax LP formulation. Specifically, we introduce a variable \(M\) representing the largest absolute deviation between population-driven and GDP-driven growth rates over the entire projection period and minimize \(M\), thereby enforcing consistency between these two socioeconomic drivers.

Once consistency is ensured, these exogenous service-demand trajectories are converted into final-energy demands (by fuel type) using the model’s relative efficiency assumptions. In future work, we will link these inputs dynamically to MESSAGEix through the [MESSAGEix–MACRO linkage](https://docs.messageix.org/projects/global/en/latest/macro.html) so that demand can respond to iterative price feedback.

### Demand-Projection Workflow

1. **Historical Baseline**

   - Compile provincial final-energy consumption (by end-use technology and fuel) from [CER](https://www.cer-rec.gc.ca/en/data-analysis/canada-energy-future/), [NRCan](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm), and [Statistics](https://www.statcan.gc.ca/en/subjects-start/energy) Canada.
2. **Socioeconomic Scaling & Consistency**

   - Apply province-level population and GDP projections to scale historical consumption.
   - Solve a small LP that minimizes the maximum absolute deviation—across all projection years—between population-driven and GDP-driven growth rates to produce a single, internally consistent demand forecast per province.
3. **Useful-Final Energy Mapping**

   - Those forecasted service demands into MESSAGEix final-energy demands using fixed efficiency factors.

For full details on data sources, SSP-related assumptions, and demand-projection methodologies, see the [Energy Demand documentation](https://docs.messageix.org/projects/global/en/latest/energy/demand.html).

## Energy End Use

MESSAGEix-Canada represent three primary end‐use sectors—transport, buildings, and industrial—each with distinct service demands and fuel‐switching options.

#### Transport

- **Stylized Sector Representation**
  - The transport sector is modeled with stylized “vehicle‐time” or “vehicle‐distance” technologies that allow fuel switching based on relative efficiencies.
- **Fuel Switching & Electrification**
  - Transport technologies can switch between liquid fuels (gasoline, diesel) and electricity. A maximum electrification rate (50% assumed for SSP2) ensures results remain realistic and aligned with socioeconomic assumptions for vehicle electrification.
- **Service Demand**
  - Transport demand is expressed in the total energy service demand which includes transport individual demand side parameters such as passenger‐kilometers or ton‐kilometers converted to energy demand via technology‐specific energy intensities.

For more detailed explanation, refer to the transport documentation [page](https://docs.messageix.org/projects/global/en/latest/energy/enduse/transport.html) of global model.

#### Residential & Commercial

Residential & Commercial demands are represented through thermal and specific technologies.

- **Thermal Demand**Both residential and commercial sectors have a thermal service demand (space heating and hot water). Fuel‐switching options include natural gas, propane, fuel oil, biomass, and district heating. Switching decisions are based on relative efficiency and cost.
- **Specific (Electric) Demand**
  Specific electricity demand (lighting, appliances, electronics) is satisfied either by grid‐supplied electricity or decentralized options (e.g., fuel cells, combined heat and power). Rooftop/off‐grid solar PV is _not_ included in this model version.

For more detailed explanation, refer to the transport documentation [page](https://docs.messageix.org/projects/global/en/latest/energy/enduse/resid_commerc.html) of global model.

#### Industrial

Industrial demands are represented through thermal and specific technologies.

- **Thermal Demand**Industrial thermal demand (process heat) can be met by natural gas, coal, biomass, or process‐heat electricity, depending on cost and efficiency.
- **Specific Demand**
  Industrial specific electricity demand (motors, drives, etc.) is met by grid electricity. On‐site generation (e.g., gas‐turbine CHP) is also allowed if economically favorable.

For more detailed explanation, refer to the transport documentation [page](https://docs.messageix.org/projects/global/en/latest/energy/enduse/industrial.html) of global model.

## **📉 Emissions Accounting**

The model employs **two types of emissions accounting**:

### **1️⃣ Top-Down (Extraction-Level) Accounting**

- Used for **carbon pricing** and **emission constraints**.
- Parameterized in the relation **`CO2_emission`**.
- **Positive values** correspond to **extraction and import technologies**.
- **Negative values** correspond to **mitigation technologies** (e.g., **CCS**).
- The `CO2_emission` relation assigns an **`emission_factor`** to technologies, categorized under the **emission type `TCE`**.
- By applying an upper **bound on `TCE`**, the model determines which technologies contribute to emissions.

### **2️⃣ Bottom-Up (Process-Level) Accounting**

- Tracks emissions at the **process level** within the system.
- Includes **technological groupings** for:
  - **CH₄ (Methane)**
  - **N₂O (Nitrous Oxide)**
  - **HFCs (Hydrofluorocarbons)**
- **Land-use emissions** are **not parameterized** in this model.

---

### **📊 Emission Factors and Calculations**

- The **emission factors** for fuels are mentioned alongwith references in the [MESSAGEix-GLOBIOM documnentation](https://docs.messageix.org/projects/global/en/latest/emissions/message/index.html)
- In **MESSAGEix-Canada**, the **emission factor** for each power plant is based on **fuel input values**.
  - Example: For a **coal power plant**, the **CO₂_CC** relation value needs to be **multiplied by the fuel input** (`coal_ppl`) to determine emissions.

### **📉 Emissions Calculation**

The model employs **two types of emissions accounting**:

### **1️⃣ Top-Down (Extraction-Level) Accounting**

- Used for **carbon pricing** and **emission constraints**.
- Parameterized in the relation **`CO2_emission`**.
- **Positive values** correspond to **extraction and import technologies**.
- **Negative values** correspond to **mitigation technologies** (e.g., **CCS**).
- The `CO2_emission` relation assigns an **`emission_factor`** to technologies, categorized under the **emission type `TCE`**.
- By applying an upper **bound on `TCE`**, the model determines which technologies contribute to emissions.

### **2️⃣ Bottom-Up (Process-Level) Accounting**

- Tracks emissions at the **process level** within the system.
- Includes **technological groupings** for:
  - **CH₄ (Methane)**
  - **N₂O (Nitrous Oxide)**
  - **HFCs (Hydrofluorocarbons)**
- **Land-use emissions** are **not parameterized** in this model.

---

### **📊 Emission Factors and Calculations**

- The **emission factors** for fuels are available in the MESSAGEix documentation:🔗 [MESSAGEix Emission Factors](https://docs.messageix.org/projects/global/en/latest/emissions/message/index.html)
- In **MESSAGEix-Canada**, the **emission factor** for each power plant is based on **fuel input values**.
  - Example: For a **coal power plant**, the **CO₂_CC** relation value needs to be **multiplied by the fuel input** (`coal_ppl`) to determine emissions.

---

### **📌 Example: Coal Power Plant Emissions Calculation**

To compute **fuel-related emission factors** for a coal power plant:

| **Relation**                            | **Value**                                      |
| --------------------------------------------- | ---------------------------------------------------- |
| `CO2_cc` (CO₂ emission factor)             | **2.11979**                                    |
| Coal power plant efficiency                   | **\(1 / 2.63158 = 0.379\)**                    |
| **Emission factor of coal power plant** | **\(2.11979 \times 0.379 = 0.8044\) MtC/GWyr** |

> **🔹 Note:** The `CO2_cc` relation is **not used for emission constraints**. Instead, emission constraints are applied through **`CO2_emission`** and `TCE`.

# **⚡ Hydrogen Representation**

- Hydrogen technologies are included in the model with a focus on:

  - **Hydrogen production**
  - **Hydrogen storage**
  - **Hydrogen transportation**
  - **Hydrogen trade**

Hydrogen production is modeled with specific **conversion efficiencies** and **emission factors** based on feedstock type (e.g., electrolysis, SMR with or without CCS).

Aside from documneted MESSAGEix Hydrogen technologies, the following list of technologies have been incorporated in respect to the Canadian context:

| **Technology** | **Description**                                         |
| -------------------- | ------------------------------------------------------------- |
| h2_atr               | Auto Thermal Reforming                                        |
| h2_atr_ccs           | Auto Thermal Reforming With CCS                               |
| gas_h2               | Hydrogen Methanation                                          |
| liq_h2               | Fischer Tropsch Synthesis - Lightoil Production From Hydrogen |
| h2_stor_geo          | Geological Hydrogen Storage                                   |
| meth_h2              | Methanol Production From Hydrogen                             |
| h2_gas_fc_trp        | Hydrogen Gas fuel Cell Transportation                         |
| h2_pyrolysis         | Methane Pyrolysis to produce Hydorgen                         |

# **🌍 Direct Air Capture (DAC)**

- **DAC (Direct Air Capture)** is modeled as a **negative emissions technology**.
- It extracts CO₂ directly from the atmosphere and is parameterized in the relation:

  - `DAC_CO2_removal`
- The DAC process requires:

  - **Energy input**
  - **CO₂ separation and compression**
  - **Storage or utilization of captured CO₂**
- The effectiveness of DAC depends on:

  - **Technology efficiency**
  - **Energy requirements**
  - **CO₂ capture rate**
- The net-zero scenario that incorporates direct air capture technologies as part of  emission-mitigating technology. The infrastructure for accomodating such technologies counts on CO2 storage facilities paired with the extraction technologies, as examplified by the figure below.

![](include/DAC_infrastructure.svg)

# Unit Conversion Tables

This section contains a table of unit conversions for the most used units in the MESSAGE-ix model

<html>

<body>
<table>
  <thead>
    <tr>
      <th>From Unit</th>
      <th>To Unit</th>
      <th>Conversion Factor</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Cubic Metres per day of natural gas [m³/d]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>4.32 e-10</td>
      <td>Volume conversion for natural gas to gigawatt annual</td>
    </tr>
    <tr>
      <td>Cubic metres per day of heavy crude oil [m³/d]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>4.73 e-4</td>
      <td>Volume conversion for heavy crude oil to gigawatt annual</td>
    </tr>
    <tr>
      <td>Cubic metres per day of light crude oil [m³/d]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>4.46 e-4</td>
      <td>Volume conversion for light crude oil to gigawatt annual</td>
    </tr>
    <tr>
      <td>Tonnes of bitumenous coal [t]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>8.75 e-7</td>
      <td>Mass conversion for bitumenous coal to gigawatt annual</td>
    </tr>
    <tr>
      <td>Tonnes of subbitumenous coal [t]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>5.96 e-7</td>
      <td>Mass conversion for subbitumenous coal to gigawatt annual</td>
    </tr>
    <tr>
      <td>Tonnes of lignite coal [t]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>4.56 e-7</td>
      <td>Mass conversion for lignite coal to gigawatt annual</td>
    </tr>
    <tr>
      <td>Megatonnes of Hydrogen [Mt]</td>
      <td>Gigawatt annual [GWa]</td>
      <td>3.81</td>
      <td>Mass conversion for Hydrogen</td>
    </tr>
    <tr>
      <td>Peta-joules [PJ]</td>
      <td>Tonnes [t]</td>
      <td>120</td>
      <td>Hydrogen gravimetric energy density</td>
    </tr>
    <tr>
      <td>Gigawatt-hour [GWh]</td>
      <td>Peta-joules [PJ]</td>
      <td>0.0036</td>
      <td>Gigawatt-hour to peta-joules</td>
    </tr>
    <tr>
      <td>Cubic metre of heavy crude oil [m³]</td>
      <td>Peta-joules [PJ]</td>
      <td>40.9 e-6</td>
      <td>Volumetric energy of heavy crude oil</td>
    </tr>
  </tbody>
</table>
</body>
</html>

## References

[1] [Energy conversion tables - CER](https://apps.cer-rec.gc.ca/Conversion/conversion-tables.aspx?GoCTemplateCulture=en-CA)
