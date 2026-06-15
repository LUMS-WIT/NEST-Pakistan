############################################################
# NEST – WATER DEMAND VISUALIZATION SCRIPT
# Helps understand outputs from water demand processing
############################################################

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")

print("Starting visualization script...")

# =========================
# BASE PATH
# =========================
BASE = r"C:/Users/User/Desktop/lums/3rd semester/Thesis"

OUTPUT_DIR = os.path.join(
    BASE,
    "Thesis II/R Output Files/water_demands/harmonized/IRB"
)

PLOT_DIR = os.path.join(BASE, "Thesis II/plots")
os.makedirs(PLOT_DIR, exist_ok=True)

yrs = list(range(2010, 2100, 10))

# =========================
# LOAD OUTPUT FILES
# =========================
print("Loading generated withdrawal files...")

dfs = []

for y in yrs:
    file_path = os.path.join(OUTPUT_DIR, f"ssp2_withdrawals_{y}.csv")

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df["year"] = y
        dfs.append(df)

data = pd.concat(dfs, ignore_index=True)

# =========================
# TOTAL WATER DEMAND TREND
# =========================
print("Plotting total withdrawals trend...")

totals = data.groupby("year")[[
    "urban_withdrawal",
    "rural_withdrawal",
    "manufacturing_withdrawal"
]].sum()

totals.plot(figsize=(10,6))

plt.title("Total Water Withdrawals by Sector")
plt.ylabel("Water Withdrawal")
plt.xlabel("Year")

plt.savefig(os.path.join(PLOT_DIR, "withdrawal_trend.png"))
plt.close()

# =========================
# STACKED SECTOR COMPOSITION
# =========================
print("Plotting sector composition...")

totals.plot(
    kind="bar",
    stacked=True,
    figsize=(10,6)
)

plt.title("Sector Contribution to Water Withdrawals")
plt.ylabel("Water Withdrawal")
plt.xlabel("Year")

plt.savefig(os.path.join(PLOT_DIR, "sector_composition.png"))
plt.close()

# =========================
# DISTRIBUTION OF WITHDRAWALS
# =========================
print("Plotting distribution...")

plt.figure(figsize=(8,6))
sns.histplot(data["urban_withdrawal"], bins=40)
plt.title("Distribution of Urban Withdrawals")
plt.savefig(os.path.join(PLOT_DIR, "urban_distribution.png"))
plt.close()

# =========================
# TOP BCUs WATER USERS
# =========================
print("Plotting top basins...")

latest_year = max(yrs)

latest_data = data[data["year"] == latest_year]

top_bcu = (
    latest_data
    .assign(total=lambda x:
        x["urban_withdrawal"]
        + x["rural_withdrawal"]
        + x["manufacturing_withdrawal"]
    )
    .sort_values("total", ascending=False)
    .head(10)
)

plt.figure(figsize=(10,6))

sns.barplot(
    data=top_bcu,
    x="total",
    y="BCU_name"
)

plt.title(f"Top 10 BCUs by Water Withdrawal ({latest_year})")

plt.savefig(os.path.join(PLOT_DIR, "top_bcu.png"))
plt.close()

# =========================
# SPATIAL MAP
# =========================
print("Generating spatial map...")

basins_path = os.path.join(
    BASE,
    "Thesis II/Input/Delineation/Data/delineated_basins_new",
    "basins_by_region_IRB.shp"
)

basins = gpd.read_file(basins_path)

latest_data = latest_data.copy()

latest_data["total"] = (
    latest_data["urban_withdrawal"]
    + latest_data["rural_withdrawal"]
    + latest_data["manufacturing_withdrawal"]
)

map_df = basins.merge(
    latest_data,
    left_on="ID",
    right_on="BCU_name",
    how="left"
)

fig, ax = plt.subplots(figsize=(10,10))

map_df.plot(
    column="total",
    cmap="Blues",
    legend=True,
    ax=ax
)

plt.title(f"Spatial Distribution of Water Demand ({latest_year})")

plt.savefig(os.path.join(PLOT_DIR, "spatial_water_demand.png"))
plt.close()

print("All plots saved to:", PLOT_DIR)
print("Visualization script finished.")