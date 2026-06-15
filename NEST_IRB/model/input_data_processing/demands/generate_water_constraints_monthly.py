############################################################
# NEST – WATER DEMAND PROCESSING (PYTHON VERSION)
# FULL SINGLE SCRIPT – CLEAN & COMPATIBLE
############################################################

import os
import gc
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import rioxarray as rxr
import pyreadr
from shapely.geometry import Point

print("Starting Script...")

# Allow GDAL to reconstruct missing .shx for shapefiles when possible.
os.environ.setdefault("SHAPE_RESTORE_SHX", "YES")


def _build_irb_bcu_key_from_shapefile(shapefile_path):
    """
    Build {UNK_X: 'num|COUNTRY'} map by reading the IRB basin shapefile.

    The shapefile ID field (UNK_1, UNK_14 …) provides the numeric part of the
    key.  The country code is derived from the REGION field using the standard
    Indus Basin country assignment.  UNK_14 is a known exception: its shapefile
    REGION is india_west but the model assigns it to PAK (it covers disputed
    Kashmir territory allocated to Pakistan in the demand model).
    """
    REGION_TO_COUNTRY = {
        "afghan_south": "AFG",
        "afghan_north": "AFG",
        "china":        "CHN",
        "india_west":   "IND",
        "india_east":   "IND",
        "pakistan":     "PAK",
    }
    # Basin-level overrides where REGION label differs from model assignment.
    OVERRIDES = {
        "UNK_14": "14|PAK",   # shapefile says india_west, model assigns PAK
    }
    try:
        import geopandas as _gpd
        gdf = _gpd.read_file(shapefile_path)
    except Exception:
        return {}
    if "ID" not in gdf.columns or "REGION" not in gdf.columns:
        return {}
    mapping = {}
    for _, row in gdf[["ID", "REGION"]].dropna().iterrows():
        src_id = str(row["ID"]).strip()
        region = str(row["REGION"]).strip().lower()
        if src_id in OVERRIDES:
            mapping[src_id] = OVERRIDES[src_id]
            continue
        ccode = REGION_TO_COUNTRY.get(region)
        if ccode is None:
            continue
        try:
            num = int(src_id.split("_")[-1])
            mapping[src_id] = f"{num}|{ccode}"
        except ValueError:
            pass
    return mapping


# =========================
# BASE PATH (EDIT ONLY THIS)
# =========================
BASE = r"C:/Users/User/Desktop/lums/3rd semester/Thesis"

_irb_shapefile = os.path.join(
    BASE,
    "Thesis II/Input/Delineation/Data/delineated_basins_new",
    "basins_by_region_IRB.shp",
)
irb_bcu_label_map = _build_irb_bcu_key_from_shapefile(_irb_shapefile)
print(f"IRB BCU label map: {len(irb_bcu_label_map)} entries built from shapefile.")

# =========================
# GLOBAL SETTINGS
# =========================
ssp = 2
yrs = list(range(2010, 2100, 10))
crs_ll = "EPSG:4326"

# =========================
# COUNTRY–REGION MAP
# =========================
country_region_map_key = pd.read_csv(
    os.path.join(BASE, "Input Files/country_delineation/country_region_map_key.csv")
)

country_region_map_key["country_code"] = country_region_map_key["country_code"].astype(str)

# =========================
# LOAD & AGGREGATE SSP DATA
# =========================
print("Loading SSP data...")

dfs = []

for y in yrs:
    pkl_path = os.path.join(
        BASE,
        f"Input Files/harmonized_rcp_ssp_data/water_use_ssp2_rcp2_{y}_data.pkl"
    )
    rda_path = os.path.join(
        BASE,
        f"Input Files/harmonized_rcp_ssp_data/water_use_ssp2_rcp2_{y}_data.Rda"
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

    # Aggregate monthly values
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
# ADD COUNTRY / REGIONS
# =========================
dat_df = dat_df.merge(
    country_region_map_key[["country_code", "macro_region", "continent"]],
    left_on="country_id",
    right_on="country_code",
    how="left"
)

dat_df = dat_df.rename(columns={
    "country_id": "country",
    "macro_region": "region"
})

# =========================
# CONVERT TO GEODATAFRAME
# =========================
geometry = [Point(xy) for xy in zip(dat_df["xloc"], dat_df["yloc"])]
dat_gdf = gpd.GeoDataFrame(dat_df, geometry=geometry, crs=crs_ll)

# =========================
# WATER STRESS (NETCDF)
# =========================
print("Extracting WSI...")

wsi_nc = os.path.join(BASE, "Thesis II/Input/wsi_memean_ssp2_rcp6p0.nc")
ds = xr.open_dataset(wsi_nc)

for y in yrs:
    if str(y) in ds:
        raster = ds[str(y)]
        raster = raster.rio.write_crs(crs_ll)

        values = raster.rio.sample(dat_gdf.geometry).to_pandas()
        dat_gdf[f"WSI.{y}"] = values.iloc[:, 0].fillna(0).values

dat_df = pd.DataFrame(dat_gdf.drop(columns="geometry"))

# =========================
# GOVERNANCE
# =========================
gov_df = pd.read_csv(
    os.path.join(BASE, "Thesis II/Input/governance/governance_obs_project.csv")
)

gov_df = gov_df[
    (gov_df["scenario"] == f"SSP{ssp}") &
    (gov_df["year"].isin(yrs))
][["countrycode", "year", "governance"]]

gov_df = gov_df.pivot(
    index="countrycode",
    columns="year",
    values="governance"
)

gov_df.columns = [f"gov.{col}" for col in gov_df.columns]
gov_df = gov_df.reset_index()

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
print("Processing manufacturing...")

mf_w = pd.read_csv(
    os.path.join(BASE, "Thesis II/Input/national/IIASA_water_withdrawal_manufacturing_Static.csv")
)
mf_w = mf_w[mf_w["Scenario"] == "SSP2"]
mf_w["Country_Code"] = mf_w["Country_Code"].astype(str)

mf_r = pd.read_csv(
    os.path.join(BASE, "Thesis II/Input/national/IIASA_water_return_manufacturing_Static.csv")
)
mf_r = mf_r[mf_r["Scenario"] == "SSP2"]
mf_r["Country_Code"] = mf_r["Country_Code"].astype(str)


def _year_col(df, yy):
    yy_str = str(yy)
    x_yy = f"X{yy}"
    if x_yy in df.columns:
        return x_yy
    if yy_str in df.columns:
        return yy_str
    raise KeyError(f"Year column not found for {yy}. Tried '{x_yy}' and '{yy_str}'.")

# dat_df["country"] holds the raw country_id from SSP data, which is the
# numeric UN country code (float, e.g. 4.0=AFG, 586.0=PAK).  The
# manufacturing CSVs have Country_Code (alpha, "AFG") AND UN_Code (numeric
# float).  We match on UN_Code so the lookup actually finds rows.
for yy in yrs:
    dat_df[f"mf_withdrawal.{yy}"] = 0.0
    dat_df[f"mf_return.{yy}"] = 0.0

    year_col_w = _year_col(mf_w, yy)
    year_col_r = _year_col(mf_r, yy)

    for cc in dat_df["country"].unique():
        idx = dat_df["country"] == cc
        pop = dat_df.loc[idx, f"urban_pop.{yy}"].sum()

        if pop == 0:
            continue

        cc_num = pd.to_numeric(cc, errors="coerce")
        mw_rows = mf_w.loc[mf_w["UN_Code"] == cc_num, year_col_w]
        mr_rows = mf_r.loc[mf_r["UN_Code"] == cc_num, year_col_r]

        mw = pd.to_numeric(mw_rows.values[0], errors="coerce") if len(mw_rows) else 0
        mr = pd.to_numeric(mr_rows.values[0], errors="coerce") if len(mr_rows) else 0
        if pd.isna(mw):
            mw = 0
        if pd.isna(mr):
            mr = 0

        dat_df.loc[idx, f"mf_withdrawal.{yy}"] = (
            dat_df.loc[idx, f"urban_pop.{yy}"] / pop
        ) * mw

        dat_df.loc[idx, f"mf_return.{yy}"] = (
            dat_df.loc[idx, f"urban_pop.{yy}"] / pop
        ) * mr

# =========================
# REGIONAL AGGREGATION
# =========================
print("Running regional aggregation...")

for reg in ["IRB"]:

    basins_path = os.path.join(
        BASE,
        "Thesis II/Input/Delineation/Data/delineated_basins_new",
        f"basins_by_region_{reg}.shp"
    )

    basins = gpd.read_file(basins_path).to_crs(crs_ll)

    if "BCU_name" in basins.columns:
        basin_key_col = "BCU_name"
    elif "ID" in basins.columns:
        basin_key_col = "ID"
    else:
        raise KeyError(
            f"No basin key column found for {reg}. "
            f"Available columns: {list(basins.columns)}"
        )

    gdf = gpd.GeoDataFrame(
        dat_df,
        geometry=gpd.points_from_xy(dat_df.xloc, dat_df.yloc),
        crs=crs_ll
    )

    joined = gpd.sjoin(gdf, basins, how="inner")

    for yy in yrs:
        out = joined.groupby(basin_key_col).agg({
            f"urban_withdrawal.{yy}": "sum",
            f"rural_withdrawal.{yy}": "sum",
            f"mf_withdrawal.{yy}":    "sum",
            f"urban_return.{yy}":     "sum",
            f"rural_return.{yy}":     "sum",
            f"mf_return.{yy}":        "sum",
        }).reset_index()

        out.columns = [
            "BCU_name",
            "urban_withdrawal",
            "rural_withdrawal",
            "manufacturing_withdrawal",
            "urban_return",
            "rural_return",
            "manufacturing_return",
        ]

        if reg == "IRB" and irb_bcu_label_map:
            out["BCU_name"] = out["BCU_name"].replace(irb_bcu_label_map)

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

        print(f"Saved: {reg} - {yy}")

gc.collect()

# ============================================================
# GENERATE WIDE-FORMAT ssp2_regional_*_baseline.csv
# add_sectoral_demands() reads these files from the model
# data directory. Rows = years, columns = basin IDs.
# ============================================================
print("Generating wide-format ssp2_regional_*_baseline.csv files...")

MODEL_YEARS = list(range(2010, 2080, 10))   # 2010 … 2070

# Source: per-year files written in the loop above
irb_yearly_dir = output_dir   # output_dir was set during the IRB loop

# Destination: model data directory that add_sectoral_demands() reads
model_demands_dir = os.path.join(
    BASE,
    "Hydro-Energy Model/message-ix-models/message_ix_models"
    "/data/water/demands/harmonized/IRB"
)
os.makedirs(model_demands_dir, exist_ok=True)

# ------------------------------------------------------------------
# Build basin-number → authoritative BCU_name mapping from the model
# delineation CSV.  The demand CSVs must use exactly these names so
# add_sectoral_demands() isin(context.valid_basins) passes correctly.
#
#   delineation format : "14|PAKISTAN", "1|AFGHAN_SOUTH", "3|CHINA"
#   shapefile label    : "14|PAK",      "1|AFG",          "3|CHN"
# ------------------------------------------------------------------
_delineation_csv = os.path.join(
    BASE,
    "Hydro-Energy Model/message-ix-models/message_ix_models"
    "/data/water/delineation/basins_by_region_simpl_IRB.csv"
)
_delineation_df = pd.read_csv(_delineation_csv)
_num_to_bcu = {}
for _bcu in _delineation_df["BCU_name"].astype(str):
    _parts = _bcu.split("|")
    if len(_parts) == 2:
        try:
            _num_to_bcu[int(_parts[0])] = _bcu
        except ValueError:
            pass
_valid_bcu_set = set(_num_to_bcu.values())
print(f"  Loaded {len(_num_to_bcu)} basin mappings from delineation CSV.")


def _rename_to_delineation(columns):
    """Map shapefile-style names ('14|PAK') → delineation names ('14|PAKISTAN')."""
    rename = {}
    for col in columns:
        parts = str(col).split("|")
        if len(parts) == 2:
            try:
                num = int(parts[0])
                if num in _num_to_bcu:
                    rename[col] = _num_to_bcu[num]
            except ValueError:
                pass
    return rename


# Map: output filename → column name in per-year CSV
# Note: urban files use the "2" suffix that add_sectoral_demands() expects
WIDE_FILES = {
    "ssp2_regional_urban_withdrawal2_baseline.csv":        "urban_withdrawal",
    "ssp2_regional_rural_withdrawal_baseline.csv":         "rural_withdrawal",
    "ssp2_regional_urban_return2_baseline.csv":            "urban_return",
    "ssp2_regional_rural_return_baseline.csv":             "rural_return",
    "ssp2_regional_manufacturing_withdrawal_baseline.csv": "manufacturing_withdrawal",
    "ssp2_regional_manufacturing_return_baseline.csv":     "manufacturing_return",
}

irb_basin_ids = None   # collected on first successful read (delineation names)

for fname, col in WIDE_FILES.items():
    rows = {}
    for yy in MODEL_YEARS:
        fpath = os.path.join(irb_yearly_dir, f"ssp{ssp}_withdrawals_{yy}.csv")
        if not os.path.exists(fpath):
            continue
        df_yr = pd.read_csv(fpath)
        if col not in df_yr.columns:
            continue
        ser = df_yr.set_index("BCU_name")[col]
        rows[yy] = ser

    if rows:
        wide = pd.DataFrame(rows).T

        # Rename columns: shapefile format → delineation format
        wide = wide.rename(columns=_rename_to_delineation(wide.columns))
        # Keep only basins that exist in the model delineation
        wide = wide[[c for c in wide.columns if c in _valid_bcu_set]]

        if irb_basin_ids is None:
            irb_basin_ids = list(wide.columns)

        wide.index.name = None   # unnamed index → "Unnamed: 0" on reload
        out_path = os.path.join(model_demands_dir, fname)
        wide.to_csv(out_path)
        print(f"  Saved: {fname}  shape={wide.shape}  "
              f"sample cols: {list(wide.columns[:3])}")
    else:
        print(f"  SKIPPED (no per-year data found): {fname}")

# ============================================================
# GENERATE RATE FILES FROM R12 REFERENCE DATA
# For each IRB basin the rate is taken as the median of all
# R12 basins in the same MSG region:
#   AFG / PAK / IND → SAS (South Asia)
#   CHN             → CHN (China)
# Rows = years, columns = IRB basin IDs (same layout as above).
# ============================================================
print("Generating rate files from R12 reference data...")

r12_rates_dir = os.path.join(
    BASE,
    "Hydro-Energy Model/message-ix-models/message_ix_models"
    "/data/water/demands/harmonized/R12"
)

COUNTRY_TO_R12_REGION = {
    # Keys are the region suffix in the delineation BCU_name (after '|')
    # Values are the R12 MSG region code used in the R12 rate file columns
    "AFGHAN_SOUTH": "SAS",
    "AFGHAN_NORTH": "SAS",
    "PAKISTAN":     "SAS",
    "INDIA_WEST":   "SAS",
    "INDIA_EAST":   "SAS",
    "CHINA":        "CHN",
}

RATE_FILES = [
    "ssp2_regional_urban_connection_rate_baseline.csv",
    "ssp2_regional_rural_connection_rate_baseline.csv",
    "ssp2_regional_urban_treatment_rate_baseline.csv",
    "ssp2_regional_rural_treatment_rate_baseline.csv",
    "ssp2_regional_urban_recycling_rate_baseline.csv",
]


def _country_from_basin(basin_id):
    """Extract region suffix from '14|PAKISTAN' → 'PAKISTAN'."""
    parts = str(basin_id).split("|")
    return parts[1] if len(parts) == 2 else None


if irb_basin_ids is None:
    print("  WARNING: No IRB basin IDs collected — rate files skipped.")
else:
    for fname in RATE_FILES:
        r12_path = os.path.join(r12_rates_dir, fname)
        if not os.path.exists(r12_path):
            print(f"  WARNING: R12 source not found: {fname}")
            continue

        r12 = pd.read_csv(r12_path, index_col=0)
        # Index may be quoted strings like '"2010"'; normalise to int
        r12.index = r12.index.astype(str).str.strip('"').astype(int)
        r12 = r12[r12.index.isin(MODEL_YEARS)]

        irb_cols = {}
        for basin in irb_basin_ids:
            region_name = _country_from_basin(basin)
            region      = COUNTRY_TO_R12_REGION.get(region_name)
            if region is None:
                continue
            # All R12 columns in the same MSG region
            region_cols = [c for c in r12.columns if str(c).endswith(f"|{region}")]
            if not region_cols:
                continue
            # Use median — representative for the country without basin-level lookup
            irb_cols[basin] = r12[region_cols].median(axis=1)

        if irb_cols:
            rate_wide = pd.DataFrame(irb_cols)   # index = MODEL_YEARS from Series
            rate_wide.index.name = None
            out_path = os.path.join(model_demands_dir, fname)
            rate_wide.to_csv(out_path)
            sample_mean = rate_wide.iloc[0].mean()
            print(f"  Saved: {fname}  shape={rate_wide.shape}  "
                  f"(mean rate {rate_wide.index[0]}: {sample_mean:.3f})")
        else:
            print(f"  SKIPPED (no matching R12 region columns): {fname}")

# ============================================================
# GENERATE all_rates_SSP2.csv
# Long-format file read by get_rates_data() in report.py and
# by demands.py for SDG scenario rate comparisons.
# Columns: node, year, variable, value, time
# Contains baseline rates for all IRB basins across all years.
# To extend for SDG scenarios, add SDG-rate rows with variable
# names like "urban_connection_rate_SDG" etc.
# ============================================================
print("Generating all_rates_SSP2.csv...")

# Map each rate file → the variable name it represents
RATE_VAR_MAP = {
    "ssp2_regional_urban_connection_rate_baseline.csv": "urban_connection_rate_baseline",
    "ssp2_regional_rural_connection_rate_baseline.csv": "rural_connection_rate_baseline",
    "ssp2_regional_urban_treatment_rate_baseline.csv":  "urban_treatment_rate_baseline",
    "ssp2_regional_rural_treatment_rate_baseline.csv":  "rural_treatment_rate_baseline",
    "ssp2_regional_urban_recycling_rate_baseline.csv":  "urban_recycling_rate_baseline",
}

all_rates_parts = []

for fname, varname in RATE_VAR_MAP.items():
    fpath = os.path.join(model_demands_dir, fname)
    if not os.path.exists(fpath):
        print(f"  WARNING: {fname} not found — skipping from all_rates.")
        continue

    # Wide format: index=year, columns=basin IDs
    wide = pd.read_csv(fpath, index_col=0)
    wide.index = wide.index.astype(str).str.strip('"').astype(int)
    wide.index.name = "year"

    # Melt to long format: one row per (basin, year)
    long = wide.reset_index().melt(id_vars="year", var_name="node", value_name="value")
    long["variable"] = varname
    long["time"] = "year"

    all_rates_parts.append(long[["node", "year", "variable", "value", "time"]])

if all_rates_parts:
    all_rates_df = pd.concat(all_rates_parts, ignore_index=True)
    all_rates_df = all_rates_df.sort_values(
        ["variable", "year", "node"]
    ).reset_index(drop=True)

    out_path = os.path.join(model_demands_dir, "all_rates_SSP2.csv")
    all_rates_df.to_csv(out_path, index=False)
    print(f"  Saved: all_rates_SSP2.csv  ({len(all_rates_df):,} rows, "
          f"{all_rates_df['node'].nunique()} basins, "
          f"{all_rates_df['variable'].nunique()} variables)")
else:
    print("  WARNING: No rate files found — all_rates_SSP2.csv not created.")

print("✅ SCRIPT FINISHED SUCCESSFULLY")
