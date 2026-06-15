# ============================================
# Groundwater Harmonization - Visual Diagnostics
# ============================================

import os
import pandas as pd
import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")


def _pick_col(columns, candidates, label):
    for c in candidates:
        if c in columns:
            return c
    raise KeyError(
        f"Could not find {label} column. Tried {candidates}; "
        f"available: {list(columns)}"
    )


# ================================
# SETTINGS
# ================================

reg = "IRB"

base_path = r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Input"
gw_path = os.path.join(base_path, "groundwater")

# Output files created by your pipeline
depth_csv = os.path.join(gw_path, f"gw_energy_intensity_depth_{reg}.csv")
gw_fraction_shp = os.path.join(gw_path, f"gw_fraction_{reg}.shp")
capacity_csv = os.path.join(gw_path, f"historical_new_cap_gw_sw_km3_year_{reg}.csv")
depth_raster = os.path.join(gw_path, "global_water_table_depth_0125.tif")

# ================================
# 1. WATER TABLE DEPTH RASTER
# ================================

print("\nPlotting water table depth raster...")

with rasterio.open(depth_raster) as src:
    raster = src.read(1)

plt.figure(figsize=(12, 6))
plt.imshow(raster, cmap="viridis")
plt.colorbar(label="Water Table Depth (m)")
plt.title("Global Water Table Depth")
plt.xlabel("Longitude Index")
plt.ylabel("Latitude Index")
plt.show()

# ================================
# 2. BASIN MAP WITH GW FRACTION
# ================================

print("Plotting groundwater fraction per basin...")

basins = gpd.read_file(gw_fraction_shp)
gw_frac_col = _pick_col(
    basins.columns,
    ["gw_fraction", "gw_fractio", "gw_frac"],
    "groundwater fraction",
)

plt.figure(figsize=(10, 8))
basins.plot(
    column=gw_frac_col,
    cmap="YlGnBu",
    legend=True,
    edgecolor="black",
)

plt.title("Groundwater Fraction by Basin")
plt.axis("off")
plt.show()

# ================================
# 3. GW FRACTION DISTRIBUTION
# ================================

print("Plotting gw fraction distribution...")

plt.figure(figsize=(8, 5))
sns.histplot(basins[gw_frac_col], bins=30)
plt.xlabel("Groundwater Fraction")
plt.ylabel("Number of Basins")
plt.title("Distribution of Groundwater Fraction")
plt.show()

# ================================
# 4. WATER TABLE DEPTH DISTRIBUTION
# ================================

depth_df = pd.read_csv(depth_csv)
depth_col = _pick_col(
    depth_df.columns,
    ["table_depth_m", "table_dept"],
    "table depth",
)
energy_col = _pick_col(
    depth_df.columns,
    ["GW_per_km3_per_year", "GW_per_km3"],
    "GW energy intensity",
)

plt.figure(figsize=(8, 5))
sns.histplot(depth_df[depth_col], bins=40)
plt.xlabel("Water Table Depth (m)")
plt.ylabel("Basins")
plt.title("Distribution of Basin Water Table Depth")
plt.show()

# ================================
# 5. ENERGY INTENSITY VS DEPTH
# ================================

plt.figure(figsize=(7, 5))
sns.scatterplot(
    x=depth_df[depth_col],
    y=depth_df[energy_col],
)
plt.xlabel("Water Table Depth (m)")
plt.ylabel("Energy Intensity (GW/km3/year)")
plt.title("Energy Needed vs Water Table Depth")
plt.show()

# ================================
# 6. HISTORICAL CAPACITY
# ================================

cap_df = pd.read_csv(capacity_csv)

print("Plotting groundwater vs surface water capacity...")

plt.figure(figsize=(10, 6))
plt.bar(
    cap_df["BCU_name"],
    cap_df["hist_cap_gw_km3_year"],
    label="Groundwater",
)
plt.bar(
    cap_df["BCU_name"],
    cap_df["hist_cap_sw_km3_year"],
    bottom=cap_df["hist_cap_gw_km3_year"],
    label="Surface Water",
)

plt.xticks(rotation=90)
plt.ylabel("km3 / year")
plt.title("Historical Water Extraction Capacity")
plt.legend()
plt.tight_layout()
plt.show()

# ================================
# 7. GW SHARE BY BASIN
# ================================

cap_df["gw_share"] = (
    cap_df["hist_cap_gw_km3_year"]
    / (cap_df["hist_cap_gw_km3_year"] + cap_df["hist_cap_sw_km3_year"])
)

plt.figure(figsize=(8, 5))
sns.histplot(cap_df["gw_share"], bins=30)
plt.xlabel("GW Share")
plt.ylabel("Basins")
plt.title("Distribution of Groundwater Share")
plt.show()

# ================================
# 8. TOTAL WATER EXTRACTION
# ================================

cap_df["total"] = (
    cap_df["hist_cap_gw_km3_year"]
    + cap_df["hist_cap_sw_km3_year"]
)

plt.figure(figsize=(8, 5))
sns.histplot(cap_df["total"], bins=30)
plt.xlabel("Total Water Extraction (km3/year)")
plt.ylabel("Basins")
plt.title("Total Water Extraction Distribution")
plt.show()

print("\nVisualization diagnostics completed.")
