# ==========================================================
# DESALINATION PROJECTION MODEL (Python version of R script)
# ==========================================================

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.formula.api import ols
from linearmodels.panel import PanelOLS
from linearmodels.panel.utility import AbsorbingEffectError
from statsmodels.stats.outliers_influence import variance_inflation_factor
from country_converter import convert as coco

# ==========================================================
# PATHS (DIRECTLY FROM YOUR R FILE)
# ==========================================================

BASE = r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Input"
PROJECT_ROOT = os.path.dirname(BASE)

DESAL1 = os.path.join(BASE, r"Desalination\Hanasaki_et_al_2015\desal_data_Hanasaki_et_al_2015.csv")
DESAL2 = os.path.join(BASE, r"Desalination\DESALCAPACITYDATA\DesalData-2016-06-15.csv")
GDP_FILE = os.path.join(BASE, r"governance\governance_2021\input\navigate_ssp.csv")
WSI_FILE = os.path.join(BASE, r"wsi_memean_ssp2_rcp6p0.nc")
BASIN_FILE = os.path.join(BASE, r"Delineation\Data\delineated_basins_new\basins_by_region_IRB.shp")
BASIN_META_FILE = os.path.join(PROJECT_ROOT, r"Indus Shape Files\basins_by_region_simpl_IRB.csv")
BASIN_COUNTRY_FILE = os.path.join(PROJECT_ROOT, r"Indus Shape Files\basins_country_IRB.csv")

OUTPUT_PROJ = os.path.join(BASE, r"Desalination\projected_desalination_potential_km3_year_IRB_python.csv")

# ==========================================================
# 1️⃣ LOAD & CLEAN DESAL DATA
# ==========================================================

desal = pd.read_csv(DESAL1)
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

# Convert to ISO3
desal["iso3"] = coco(desal["country"], to="ISO3")

# Aggregate new capacity by country/year
desal_year = (
    desal.groupby(["iso3", "online"])["m3_per_day"]
    .sum()
    .reset_index()
    .rename(columns={"online": "year", "m3_per_day": "desal_cap"})
)

desal_year = desal_year.dropna()
desal_year = desal_year.sort_values(["iso3", "year"])

desal_year["cum_desal"] = desal_year.groupby("iso3")["desal_cap"].cumsum()

# Convert to km3/year
desal_year["cum_desal"] = desal_year["cum_desal"] * 365 / 1e9

# ==========================================================
# 2️⃣ LOAD GDP PROJECTIONS (SSP2)
# ==========================================================

gdp = pd.read_csv(GDP_FILE)

gdp = gdp[(gdp["scenario"] == "WDI_2021") &
          (gdp["variable"] == "gdppc")]

# Keep only year columns (supports both "X2020" and "2020" styles)
year_cols = [col for col in gdp.columns if col.startswith("X") or col.isdigit()]

gdp = gdp[["region"] + year_cols]

gdp = gdp.melt(id_vars=["region"],
               var_name="year",
               value_name="gdp")

gdp["year"] = (
    gdp["year"].astype(str)
    .str.replace("X", "", regex=False)
    .astype(int)
)
gdp["gdp"] = pd.to_numeric(gdp["gdp"], errors="coerce")

gdp = gdp.rename(columns={"region": "iso3"})


# ==========================================================
# 3️⃣ LOAD WATER STRESS (WSI)
# ==========================================================

ds = xr.open_dataset(WSI_FILE)
wsi_var = list(ds.data_vars)[0]

# Extract mean WSI per period globally (simplified)
wsi_df = ds[wsi_var].mean(dim=["lat", "lon"]).to_dataframe().reset_index()
wsi_df = wsi_df.rename(columns={wsi_var: "wsi"})

# File uses "period" labels (e.g. "2010s"), not datetime "time"
if "time" in wsi_df.columns:
    wsi_df["year"] = pd.to_datetime(wsi_df["time"], errors="coerce").dt.year
elif "period" in wsi_df.columns:
    wsi_df["year"] = (
        wsi_df["period"].astype(str)
        .str.extract(r"(\d{4})", expand=False)
        .astype(float)
        .astype("Int64")
    )
else:
    raise KeyError("WSI dataset must contain either 'time' or 'period'.")

wsi_df = wsi_df.dropna(subset=["year", "wsi"])
wsi_df["year"] = wsi_df["year"].astype(int)

# ==========================================================
# 4️⃣ MERGE MASTER DATASET
# ==========================================================

master = desal_year.merge(gdp, on=["iso3", "year"], how="left")
master = master.merge(wsi_df, on="year", how="left")

master = master.dropna()
master["cum_desal"] = pd.to_numeric(master["cum_desal"], errors="coerce")
master["gdp"] = pd.to_numeric(master["gdp"], errors="coerce")
master["wsi"] = pd.to_numeric(master["wsi"], errors="coerce")
master = master[(master["cum_desal"] > 0) & (master["gdp"] > 0) & (master["wsi"] > 0)]

master["log_desal"] = np.log(master["cum_desal"])
master["log_gdp"] = np.log(master["gdp"])
master["log_wsi"] = np.log(master["wsi"])

master = master.replace([np.inf, -np.inf], np.nan).dropna()

# ==========================================================
# 5️⃣ OLS MODEL
# ==========================================================

lm1 = ols("log_desal ~ log_gdp + log_wsi", data=master).fit()
print(lm1.summary())

# ==========================================================
# 6️⃣ FIXED EFFECT MODEL
# ==========================================================

master_panel = master.set_index(["iso3", "year"])

fe_model = None
try:
    fe_model = PanelOLS.from_formula(
        "log_desal ~ log_gdp + log_wsi + EntityEffects",
        data=master_panel,
        drop_absorbed=True
    ).fit()
    print(fe_model.summary)
except AbsorbingEffectError:
    print("FE model could not be estimated due absorbed regressors. Using OLS coefficients for projection.")

# ==========================================================
# 7️⃣ PROJECTION SSP2 (2020–2090)
# ==========================================================

proj_years = range(2020, 2095, 5)

gdp_future = pd.read_csv(GDP_FILE)
gdp_future = gdp_future[
    (gdp_future["scenario"] == "SSP2") &
    (gdp_future["variable"] == "gdppc")
]

year_cols_future = [col for col in gdp_future.columns if col.startswith("X") or col.isdigit()]
gdp_future = gdp_future[["region"] + year_cols_future]
gdp_future = gdp_future.melt(id_vars=["region"], var_name="year", value_name="gdp")
gdp_future["year"] = (
    gdp_future["year"].astype(str)
    .str.replace("X", "", regex=False)
    .astype(int)
)
gdp_future["gdp"] = pd.to_numeric(gdp_future["gdp"], errors="coerce")
gdp_future = gdp_future.rename(columns={"region": "iso3"})
gdp_future = gdp_future[gdp_future["year"].isin(proj_years)]

future = gdp_future.merge(wsi_df, on="year", how="left")
future["gdp"] = pd.to_numeric(future["gdp"], errors="coerce")
future["wsi"] = pd.to_numeric(future["wsi"], errors="coerce")
future = future[(future["gdp"] > 0) & (future["wsi"] > 0)]
future["log_gdp"] = np.log(future["gdp"])
future["log_wsi"] = np.log(future["wsi"])

# Extract coefficients (prefer FE when estimable, otherwise OLS)
params = fe_model.params if fe_model is not None else lm1.params
beta_gdp = params.get("log_gdp", 0.0)
beta_wsi = params.get("log_wsi", 0.0)
intercept = params.get("Intercept", 0.0)

future["log_desal_pred"] = (
    intercept +
    beta_gdp * future["log_gdp"] +
    beta_wsi * future["log_wsi"]
)

future["desal_km3_year"] = np.exp(future["log_desal_pred"])

# ==========================================================
# 8️⃣ BASIN AGGREGATION
# ==========================================================

if os.path.exists(BASIN_COUNTRY_FILE):
    basin_meta = pd.read_csv(BASIN_COUNTRY_FILE)
else:
    basin_meta = pd.read_csv(BASIN_META_FILE)

required_cols = {"BCU_name", "REGION", "area_km2"}
missing_cols = required_cols.difference(basin_meta.columns)
if missing_cols:
    raise KeyError(
        f"Basin metadata is missing required columns {sorted(missing_cols)}. "
        f"Available columns: {list(basin_meta.columns)}"
    )

basin_meta = basin_meta[list(required_cols)].dropna().copy()
basin_meta["REGION"] = basin_meta["REGION"].astype(str).str.strip().str.upper()
basin_meta["BCU_name"] = basin_meta["BCU_name"].astype(str).str.strip()
basin_meta["area_km2"] = pd.to_numeric(basin_meta["area_km2"], errors="coerce")
basin_meta = basin_meta.dropna(subset=["area_km2"])

# Map each ISO3 to the IRB MESSAGE regions represented in the supplied basin files.
iso_region_groups = {
    "AFG": ["AFGHAN_NORTH", "AFGHAN_SOUTH"],
    "CHN": ["CHINA"],
    "IND": ["INDIA_EAST", "INDIA_WEST"],
    "PAK": ["PAKISTAN"],
}

region_weights = []
for iso3, regions in iso_region_groups.items():
    region_subset = basin_meta[basin_meta["REGION"].isin(regions)].copy()
    if region_subset.empty:
        continue

    total_area = region_subset["area_km2"].sum()
    region_subset["allocation_weight"] = region_subset["area_km2"] / total_area
    region_subset["iso3"] = iso3
    region_weights.append(region_subset[["iso3", "BCU_name", "allocation_weight"]])

if not region_weights:
    raise ValueError("No ISO3-to-basin allocation weights could be built from the IRB basin files.")

allocation_weights = pd.concat(region_weights, ignore_index=True)
allocation_weights = (
    allocation_weights.groupby(["iso3", "BCU_name"], as_index=False)["allocation_weight"]
    .sum()
)

future_basin = future.merge(allocation_weights, on="iso3", how="inner")
future_basin["desal_km3_year"] = (
    future_basin["desal_km3_year"] * future_basin["allocation_weight"]
)
future_basin = (
    future_basin.groupby(["BCU_name", "year"], as_index=False)["desal_km3_year"]
    .sum()
    .sort_values(["year", "BCU_name"])
)

# ==========================================================
# 9️⃣ SAVE OUTPUT
# ==========================================================

try:
    future_basin.to_csv(OUTPUT_PROJ, index=False)
    output_written = OUTPUT_PROJ
except PermissionError:
    root, ext = os.path.splitext(OUTPUT_PROJ)
    output_written = f"{root}_latest{ext}"
    future_basin.to_csv(output_written, index=False)
    print(f"Primary output file is locked. Wrote fallback file instead: {output_written}")

print("\nProjection complete. File saved to:")
print(output_written)

# ==========================================================
# END SCRIPT
# ==========================================================
