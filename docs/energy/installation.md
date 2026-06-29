# Installation

MESSAGEix-Pakistan is not a self-contained Python package. Reproducing results requires the full MESSAGEix toolchain.

## Prerequisites

### GAMS

GAMS (General Algebraic Modelling System) is required to solve the optimisation model. It is **not** a pip package and must be installed separately with a valid licence.

- Version used: **GAMS 40**
- Download and licence instructions: <https://www.gams.com/download/>

### MESSAGEix toolchain

| Package | Version used |
|---|---|
| `message_ix` | 3.9.0 |
| `ixmp` | 3.9.0 |
| Python | 3.12.7 |

The complete installation guide for the MESSAGEix toolchain (GAMS, Java, conda environment) is at:
<https://docs.messageix.org/en/latest/install.html>

## Python dependencies

Once GAMS and the MESSAGEix toolchain are installed, install the remaining Python dependencies:

```bash
pip install -r requirements.txt
```

The `requirements.txt` at the repository root lists all pinned versions used in the study.

## Cloning the repository

```bash
git clone https://github.com/<org>/NEST-Pakistan.git
cd NEST-Pakistan
```

## Documentation dependencies

To build this documentation locally:

```bash
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```
