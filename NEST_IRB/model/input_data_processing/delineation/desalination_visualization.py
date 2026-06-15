# ==========================================================
# DESALINATION MODEL VISUALIZATION SCRIPT
# ==========================================================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================================
# PATHS (same as your main script)
# ==========================================================

BASE = r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Input"

DESAL_FILE = os.path.join(BASE, r"Desalination\Hanasaki_et_al_2015\desal_data_Hanasaki_et_al_2015.csv")
OUTPUT_PROJ = os.path.join(BASE, r"Desalination\projected_desalination_potential_km3_year_R11_python.csv")

PLOT_DIR = os.path.join(BASE, r"Desalination\plots")

os.makedirs(PLOT_DIR, exist_ok=True)

sns.set_style("whitegrid")

# ==========================================================
# 1. LOAD DESAL DATA
# ==========================================================

desal = pd.read_csv(DESAL_FILE)

desal.columns = [
    "country", "location", "m3_per_day", "technology",
    "water_type", "online", "user", "price", "lat", "lon"
]

desal["m3_per_day"] = (
    desal["m3_per_day"]
    .astype(str)
    .str.replace(",", "")
    .astype(float)
)

desal["online"] = pd.to_numeric(desal["online"], errors="coerce")

# ==========================================================
# 2. GLOBAL DESAL CAPACITY TREND
# ==========================================================

desal_global = (
    desal.groupby("online")["m3_per_day"]
    .sum()
    .reset_index()
)

plt.figure(figsize=(10,6))
plt.plot(desal_global["online"], desal_global["m3_per_day"])
plt.title("Global Desalination Capacity Installed Per Year")
plt.xlabel("Year")
plt.ylabel("Capacity (m3/day)")
plt.tight_layout()

plt.savefig(os.path.join(PLOT_DIR, "global_desal_capacity_trend.png"))
plt.close()

# ==========================================================
# 3. TECHNOLOGY DISTRIBUTION
# ==========================================================

plt.figure(figsize=(8,6))
sns.countplot(data=desal, y="technology", order=desal["technology"].value_counts().index)

plt.title("Desalination Technology Distribution")
plt.tight_layout()

plt.savefig(os.path.join(PLOT_DIR, "technology_distribution.png"))
plt.close()

# ==========================================================
# 4. WATER SOURCE DISTRIBUTION
# ==========================================================

plt.figure(figsize=(8,6))
sns.countplot(data=desal, y="water_type", order=desal["water_type"].value_counts().index)

plt.title("Water Source for Desalination Plants")
plt.tight_layout()

plt.savefig(os.path.join(PLOT_DIR, "water_source_distribution.png"))
plt.close()

# ==========================================================
# 5. PLANT CAPACITY DISTRIBUTION
# ==========================================================

plt.figure(figsize=(8,6))
sns.histplot(desal["m3_per_day"], bins=50)

plt.title("Distribution of Plant Capacities")
plt.xlabel("m3/day")
plt.tight_layout()

plt.savefig(os.path.join(PLOT_DIR, "capacity_distribution.png"))
plt.close()

# ==========================================================
# 6. FUTURE PROJECTION PLOTS
# ==========================================================

proj = pd.read_csv(OUTPUT_PROJ)

plt.figure(figsize=(10,6))

for basin in proj["BCU_name"].unique()[:8]:
    subset = proj[proj["BCU_name"] == basin]
    plt.plot(subset["year"], subset["desal_km3_year"], label=basin)

plt.title("Projected Desalination Capacity by Basin")
plt.xlabel("Year")
plt.ylabel("km3/year")

plt.legend()
plt.tight_layout()

plt.savefig(os.path.join(PLOT_DIR, "future_basin_projections.png"))
plt.close()

# ==========================================================
# 7. GLOBAL FUTURE TREND
# ==========================================================

global_proj = proj.groupby("year")["desal_km3_year"].sum().reset_index()

plt.figure(figsize=(10,6))
plt.plot(global_proj["year"], global_proj["desal_km3_year"], linewidth=3)

plt.title("Global Desalination Projection (SSP2)")
plt.xlabel("Year")
plt.ylabel("km3/year")

plt.tight_layout()

plt.savefig(os.path.join(PLOT_DIR, "global_projection.png"))
plt.close()

# ==========================================================
# FINISHED
# ==========================================================

print("\nAll plots generated successfully.")
print("Location:", PLOT_DIR)