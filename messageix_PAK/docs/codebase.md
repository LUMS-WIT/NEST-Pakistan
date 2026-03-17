# **📂 Codebase Documentation**

This page provides an **overview of the repository structure** and **automatically includes function docstrings from all scripts**.

---

## **📌 Repository Structure**
| **Directory**        | **Description** |
|----------------------|----------------|
| `model/`            | Core model execution scripts |
| `model/policies/`   | Scripts related to policy constraints (carbon tax, renewables, emissions) |
| `model/scenarios/`  | Scripts defining different energy transition scenarios |
| `model/pre_process/`| Scripts for data preprocessing and transformation |
| `model/utilities/`  | Helper scripts for data processing and execution |
| `model/report/`     | Scripts for visualization and post-processing |
| `docs/`             | Documentation files |
| `data/`             | Input datasets for running the model |

---

## **🛠 Model Core**
::: model.Model

---

## **📜 Policies**
The following scripts define policy constraints such as **carbon tax, emissions limits, renewable targets, and investment incentives**.

::: model.policies.apply_renewable_potential
::: model.policies.bound_emissions
::: model.policies.bound_renewables
::: model.policies.coal_phase_out
::: model.policies.demand_reduction
::: model.policies.emissions
::: model.policies.federal_carbon_tax
::: model.policies.general_policies
::: model.policies.hydrogen_shares
::: model.policies.investment_tax_credit
::: model.policies.provincial_carbon_tax
::: model.policies.share_constraints

---

## **📊 Scenarios**
This folder  define **different scenarios** such as **baseline, net-zero, and DAC (Direct Air Capture)**.The user can define instructions in the `yaml` configuration files and run the scenarios. 



---

## **🔍 Preprocessing**
Scripts used for **data preprocessing, cleaning, and preparing model inputs**.



---

## **🧰 Utilities**
Helper scripts for **data processing, model execution, and report generation**.

<!-- ::: model.utilities.add_demand
::: model.utilities.cleanup_rel_tec
::: model.utilities.get_historical_years
::: model.utilities.get_nodes
::: model.utilities.pop_gdp
::: model.utilities.report
::: model.utilities.utils -->

---

## **📈 Reporting & Visualization**
Scripts used for **post-processing results and generating reports**.

<!-- ::: model.report.Plotter
::: model.report.Reporting_Postprocess_Workflow
::: model.report.message_processing
::: model.report.output_mapping_gen
::: model.report.process_idea
::: model.report.process_to_idea
::: model.report.tech_tables -->

---

