# Reporting

MESSAGEix-Pakistan uses the inherited MESSAGEix-GLOBIOM ENGAGE reporting code to convert raw model output into IAMC-format variables.

## Pipeline

The reporting pipeline is invoked at the end of each scenario notebook. It reads solved parameter values from the `ixmp` database and aggregates them into a standard set of IAMC variables (energy supply by fuel, emissions by sector, capacity, etc.).

Entry point: `MESSAGEix-Pakistan/report/legacy/iamc_report_hackathon.py`

## Key modules

| Module | Role |
|---|---|
| `iamc_report_hackathon.py` | Main reporting entry point; orchestrates aggregation |
| `default_tables.py` | Default IAMC variable mapping tables |
| `default_tables_static.py` | Static (non-optimised) variable mappings |
| `ENGAGE_SSP2_v417_tables.py` | Variable mappings inherited from ENGAGE SSP2 run |
| `iamc_tree.py` | Hierarchical variable tree logic |
| `postprocess.py` | Post-processing (unit conversion, infilling) |
| `pp_utils.py` | Utility functions for post-processing |

## Output format

Reports are written as Excel files in the [IAMC data template](https://github.com/IAMconsortium/pyam) format with columns:

```
model | scenario | region | variable | unit | 2020 | 2025 | ... | 2100
```

Files are placed in `MESSAGEix-Pakistan/output/` with a timestamp suffix, e.g. `current-measures_20250101_120000.xlsx`.

## Working with output

Output files can be loaded and explored with [`pyam`](https://pyam-iamc.readthedocs.io):

```python
import pyam

df = pyam.IamDataFrame("MESSAGEix-Pakistan/output/current-measures_*.xlsx")
df.filter(variable="Primary Energy|*").plot()
```
