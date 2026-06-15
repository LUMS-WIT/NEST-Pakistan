############################################################
# NEST – WATER DEMAND PROCESSING (PYTHON VERSION)
# FULL SINGLE SCRIPT – STABLE & CLEAN
############################################################

import os
import gc
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import rasterio
import pyreadr
from shapely.geometry import Point

print("Starting NEST Water Demand Processing...")

# =========================
# BASE PATH (EDIT ONLY THIS)
# =========================
BASE = r"C:/Users/User/Desktop/lums/3rd semester/Thesis"

# =========================
# GLOBAL SETTINGS
# =========================
ssp = 2
rcp = 3
yrs = list(range(2010, 2100, 10))
crs_ll = "EPSG:4326"

# =========================
# COUNTRY–REGION MAP
# =========================
country_region_map = pd.read_csv(
    os.path.join(BASE, "Input Files/country_delineation/country_region_map_key.csv")
)

country_region_map["country_code"] = country_region_map["country_code"].astype(str)

# =========================
# LOAD & AGGREGATE SSP DATA
# =========================
print("Loading SSP Data...")

dfs = []

for y in yrs:
    pkl_path = os.path.join(
        BASE,
        f"Input Files/harmonized_rcp_ssp_data/water_use_ssp{ssp}_rcp{rcp}_{y}_data.pkl"
    )
    rda_path = os.path.join(
        BASE,
        f"Input Files/harmonized_rcp_ssp_data/water_use_ssp{ssp}_rcp{rcp}_{y}_data.Rda"
    )

    if os.path.exists(pkl_path):
        d = pd.read_pickle(pkl_path)
    elif os.path.exists(rda_path):
        rda_obj = pyreadr.read_r(rda_path)
        d = next(iter(rda_obj.values()))
    else:
        raise FileNotFoundError(
            f"Missing SSP input for {y}. Checked:\n- {pkl_path}\n- {rda_path}"
        )

    df_year = pd.DataFrame({
        "country_id": d["country_id"],
        "xloc": d[f"xloc.{y}"],
        "yloc": d[f"yloc.{y}"],
        f"urban_pop.{y}": d[f"urban_pop.{y}"],
        f"rural_pop.{y}": d[f"rural_pop.{y}"],
        f"urban_gdp.{y}": d[f"urban_gdp.{y}"],
        f"rural_gdp.{y}": d[f"rural_gdp.{y}"],
    })

    # Monthly aggregation
    df_year[f"urban_withdrawal.{y}"] = d[
        [f"urban_withdrawal.{y}.{m}" for m in range(1, 13)]
    ].sum(axis=1)

    df_year[f"rural_withdrawal.{y}"] = d[
        [f"rural_withdrawal.{y}.{m}" for m in range(1, 13)]
    ].sum(axis=1)

    df_year[f"urban_return.{y}"] = d[
        [f"urban_return.{y}.{m}" for m in range(1, 13)]
    ].sum(axis=1)

    df_year[f"rural_return.{y}"] = d[
        [f"rural_return.{y}.{m}" for m in range(1, 13)]
    ].sum(axis=1)

    dfs.append(df_year)

# Merge all years
dat_df = dfs[0]
for df in dfs[1:]:
    dat_df = dat_df.merge(df, on=["country_id", "xloc", "yloc"], how="outer")

dat_df = dat_df.fillna(0)
dat_df["country_id"] = dat_df["country_id"].astype(str)

# =========================
# ADD COUNTRY / REGION INFO
# =========================
dat_df = dat_df.merge(
    country_region_map[["country_code", "macro_region", "continent"]],
    left_on="country_id",
    right_on="country_code",
    how="left"
)

dat_df.rename(columns={
    "country_id": "country",
    "macro_region": "region"
}, inplace=True)

# =========================
# CONVERT TO GEODATAFRAME
# =========================
geometry = gpd.points_from_xy(dat_df["xloc"], dat_df["yloc"])
dat_gdf = gpd.GeoDataFrame(dat_df, geometry=geometry, crs=crs_ll)

# =========================
# WATER STRESS (NETCDF)
# =========================
print("Extracting Water Stress Index...")

wsi_path = os.path.join(BASE, "Thesis II/Input/wsi_memean_ssp2_rcp6p0.nc")
ds = xr.open_dataset(wsi_path)

# Identify year variables automatically
for var in ds.data_vars:
    year_digits = ''.join(filter(str.isdigit, var))
    if year_digits.isdigit():
        year_val = int(year_digits)
        if year_val in yrs:
            print(f"Processing WSI {year_val}")

            raster = ds[var]

            with rasterio.open(wsi_path) as src:
                coords = [(x, y) for x, y in zip(dat_gdf["xloc"], dat_gdf["yloc"])]
                sampled = list(src.sample(coords))

            dat_gdf[f"WSI.{year_val}"] = np.array(sampled).flatten()
            dat_gdf[f"WSI.{year_val}"] = dat_gdf[f"WSI.{year_val}"].fillna(0)

dat_df = pd.DataFrame(dat_gdf.drop(columns="geometry"))

# =========================
# GOVERNANCE
# =========================
print("Processing Governance...")

gov_df = pd.read_csv(
    os.path.join(BASE, "Thesis II/Input/governance/governance_obs_project.csv")
)

gov_df = gov_df[
    (gov_df["scenario"] == f"SSP{ssp}") &
    (gov_df["year"].isin(yrs))
][["countrycode", "year", "governance"]]

gov_df = gov_df.pivot(index="countrycode", columns="year", values="governance")
gov_df.columns = [f"gov.{c}" for c in gov_df.columns]
gov_df.reset_index(inplace=True)

mean_gov = gov_df.drop(columns="countrycode").mean().mean()

dat_df = dat_df.merge(
    gov_df,
    left_on="country",
    right_on="countrycode",
    how="left"
)

for col in dat_df.columns:
    if col.startswith("gov."):
        dat_df[col] = dat_df[col].fillna(mean_gov)

# =========================
# MANUFACTURING DEMANDS
# =========================
print("Processing Manufacturing Data...")

mf_w = pd.read_csv(
    os.path.join(BASE, "Thesis II/Input/national/IIASA_water_withdrawal_manufacturing_Static.csv")
)
mf_r = pd.read_csv(
    os.path.join(BASE, "Thesis II/Input/national/IIASA_water_return_manufacturing_Static.csv")
)

mf_w = mf_w[mf_w["Scenario"] == "SSP2"]
mf_r = mf_r[mf_r["Scenario"] == "SSP2"]
mf_w["Country_Code"] = mf_w["Country_Code"].astype(str)
mf_r["Country_Code"] = mf_r["Country_Code"].astype(str)


def _year_col(df, yy):
    yy_str = str(yy)
    x_yy = f"X{yy}"
    if x_yy in df.columns:
        return x_yy
    if yy_str in df.columns:
        return yy_str
    raise KeyError(f"Year column not found for {yy}. Tried '{x_yy}' and '{yy_str}'.")

for yy in yrs:
    dat_df[f"mf_withdrawal.{yy}"] = 0
    dat_df[f"mf_return.{yy}"] = 0

    for cc in dat_df["country"].unique():
        idx = dat_df["country"] == cc
        pop = dat_df.loc[idx, f"urban_pop.{yy}"].sum()

        if pop == 0:
            continue

        year_col_w = _year_col(mf_w, yy)
        year_col_r = _year_col(mf_r, yy)
        mw = mf_w.loc[mf_w["Country_Code"] == cc, year_col_w]
        mr = mf_r.loc[mf_r["Country_Code"] == cc, year_col_r]

        mw = mw.iloc[0] if not mw.empty else 0
        mr = mr.iloc[0] if not mr.empty else 0

        dat_df.loc[idx, f"mf_withdrawal.{yy}"] = \
            (dat_df.loc[idx, f"urban_pop.{yy}"] / pop) * mw

        dat_df.loc[idx, f"mf_return.{yy}"] = \
            (dat_df.loc[idx, f"urban_pop.{yy}"] / pop) * mr

# =========================
# REGIONAL AGGREGATION
# =========================
print("Running Regional Aggregation...")

for reg in ["IRB"]:

    basin_path = os.path.join(
        BASE,
        "Thesis II/Input/Delineation/Data/delineated_basins_new",
        f"basins_by_region_{reg}.shp"
    )

    basins = gpd.read_file(basin_path).to_crs(crs_ll)

    gdf = gpd.GeoDataFrame(
        dat_df,
        geometry=gpd.points_from_xy(dat_df.xloc, dat_df.yloc),
        crs=crs_ll
    )

    joined = gpd.sjoin(gdf, basins, how="inner", predicate="intersects")

    for yy in yrs:

        out = joined.groupby("BCU_name").agg({
            f"urban_withdrawal.{yy}": "sum",
            f"rural_withdrawal.{yy}": "sum",
            f"mf_withdrawal.{yy}": "sum"
        }).reset_index()

        out.columns = [
            "BCU_name",
            "urban_withdrawal",
            "rural_withdrawal",
            "manufacturing_withdrawal"
        ]

        output_dir = os.path.join(
            BASE,
            "Thesis II/R Output Files/water_demands/harmonized",
            reg
        )

        os.makedirs(output_dir, exist_ok=True)

        out.to_csv(
            os.path.join(output_dir, f"ssp{ssp}_withdrawals_{yy}.csv"),
            index=False
        )

        print(f"Saved {reg} - {yy}")

gc.collect()

print("✅ SCRIPT FINISHED SUCCESSFULLY")
