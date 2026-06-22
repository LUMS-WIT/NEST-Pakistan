# Running the Notebooks

Each scenario has a dedicated Jupyter notebook in `MESSAGEix-Pakistan/notebooks/`. Every notebook is self-contained and follows the same three-phase workflow:

1. **Build** — load the scenario from the Excel workbook into an `ixmp` platform database, apply scripts, and check data integrity.
2. **Solve** — call `scenario.solve()`, which submits the linear programme to the GAMS backend.
3. **Report** — invoke the IAMC reporting pipeline and write a timestamped Excel file to `output/`.

## Prerequisites

Before running any notebook, ensure:

- GAMS is installed and the licence is active (see [Installation](installation.md)).
- The MESSAGEix toolchain and all `requirements.txt` dependencies are installed.
- Jupyter is available in your environment (`pip install jupyter` or via conda).

## Workflow

```bash
cd MESSAGEix-Pakistan/notebooks
jupyter notebook
```

Open the notebook for the scenario you want to run and execute all cells in order. The notebooks are intended to be run sequentially from top to bottom.

## Notebooks

| Notebook | Scenario | `ixmp` model name |
|---|---|---|
| `current_measures.ipynb` | Current Measures (CM) | `current-measures` |
| `ndc-u.ipynb` | NDC-Unconditional (NDC-U) | `ndc-u` |
| `ndc-c.ipynb` | NDC-Conditional (NDC-C) | `ndc-c` |
| `net-zero.ipynb` | Net Zero (NZ) | `net-zero` |

## Output

Solved scenarios produce timestamped IAMC-format Excel files in `MESSAGEix-Pakistan/output/`. These files follow the IAMC data template and can be loaded with `pyam` for analysis and visualisation.

```python
import pyam
df = pyam.IamDataFrame("output/current-measures_YYYYMMDD_HHMMSS.xlsx")
```
