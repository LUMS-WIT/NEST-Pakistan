# ================================
# Groundwater Harmonization Script
# Converted from R to Python
# ================================

import os
import numpy as np
import pandas as pd
import xarray as xr
import rioxarray
import rasterio
import rasterio.mask
import geopandas as gpd
from rasterio.enums import Resampling
from rasterio.transform import from_origin

# ================================
# SETTINGS
# ================================

reg = "IRB"

base_path = r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Input"
gw_path = os.path.join(base_path, "groundwater")
basin_path = os.path.join(base_path, "Delineation\Data\delineated_basins_new")
r_output_base = os.path.join(os.path.dirname(base_path), "R Output Files")

# Demand file paths (defined early — also needed for IRB BCU key mapping)
demand_path = os.path.join(base_path, "water_demands", "harmonized", reg)
urban_demand_path = os.path.join(demand_path, "ssp2_regional_urban_withdrawal_baseline.csv")
rural_demand_path = os.path.join(demand_path, "ssp2_regional_rural_withdrawal_baseline.csv")
irr_demand_path = os.path.join(gw_path, f"hist_irrigation_withdrawals_{reg}.csv")

os.chdir(gw_path)

# ================================
# 1. CREATE BASE RASTER (1/8 deg)
# ================================

resolution = 1 / 8
xmin, xmax, ymin, ymax = -180, 180, -60, 85

width = int((xmax - xmin) / resolution)
height = int((ymax - ymin) / resolution)

transform = from_origin(xmin, ymax, resolution, resolution)

base_array = np.zeros((height, width), dtype=np.float32)

base_meta = {
    "driver": "GTiff",
    "height": height,
    "width": width,
    "count": 1,
    "dtype": "float32",
    "crs": "EPSG:4326",
    "transform": transform,
}

base_raster_path = "base_raster.tif"

with rasterio.open(base_raster_path, "w", **base_meta) as dst:
    dst.write(base_array, 1)

# Open reference raster as DataArray for rioxarray.reproject_match
ref = rioxarray.open_rasterio(base_raster_path).squeeze(drop=True)

# ================================
# 2. LOAD NETCDF (WTD)
# ================================

tile_names = ["Africa", "Australia", "Eurasia", "N_America", "S_America"]
global_raster = None

for tile in tile_names:

    nc_file = os.path.join(gw_path, "table_depth", f"{tile}_model_wtd_v2.nc")
    ds = xr.open_dataset(nc_file)

    wtd = ds["WTD"]
    wtd = wtd.squeeze()

    # Ensure CRS + spatial dims for rioxarray operations
    wtd = wtd.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=False)
    wtd.rio.write_crs("EPSG:4326", inplace=True)

    # Reproject to base grid
    wtd_reproj = wtd.rio.reproject_match(ref, resampling=Resampling.bilinear)

    if global_raster is None:
        global_raster = wtd_reproj
    else:
        global_raster = global_raster.combine_first(wtd_reproj)

# Save GeoTIFF
global_raster.rio.to_raster("global_water_table_depth_0125.tif")

# ================================
# 3. LOAD BASINS
# ================================

basins = gpd.read_file(
    os.path.join(basin_path, f"basins_by_region_{reg}.shp")
)

basins = basins.to_crs("EPSG:4326")

# Basin ID field can vary across basin shapefiles (e.g., BCU_name vs REGION).
basin_id_candidates = ["BCU_name", "BCU_NAM", "REGION", "region"]
basin_id_col = next((c for c in basin_id_candidates if c in basins.columns), None)
if basin_id_col is None:
    raise KeyError(
        "No basin ID column found. Expected one of "
        f"{basin_id_candidates}, got {list(basins.columns)}"
    )


def _build_irb_bcu_key_from_demand(urban_csv_path):
    """
    Build {numeric_id: 'num|COUNTRY'} map using demand CSV column headers as
    the authoritative source.  The numeric part of the shapefile ID field
    (UNK_14 → 14) is matched against the numeric prefix of each 'num|COUNTRY'
    demand column (14|PAK → 14).  This avoids relying on the shapefile REGION
    label, which can differ from the model's country assignment (e.g. UNK_14
    has REGION=india_west but the model assigns it to PAK).
    """
    try:
        hdr = pd.read_csv(urban_csv_path, nrows=0)
    except Exception:
        return {}
    mapping = {}
    for col in hdr.columns:
        col_s = str(col)
        if "|" in col_s:
            try:
                num = int(col_s.split("|")[0])
                mapping[num] = col_s   # e.g. {14: '14|PAK'}
            except ValueError:
                pass
    return mapping


basin_key_col = basin_id_col
basins["BCU_key"] = basins[basin_id_col].astype(str).str.strip()
if reg == "IRB" and "ID" in basins.columns:
    bcu_key_map = _build_irb_bcu_key_from_demand(urban_demand_path)
    if bcu_key_map:
        basins["_basin_num"] = (
            basins["ID"].astype(str).str.extract(r"(\d+)")[0].astype(int)
        )
        basins["BCU_key"] = basins["_basin_num"].map(bcu_key_map)
        basins = basins.drop(columns="_basin_num")
        unmapped = basins["BCU_key"].isna().sum()
        if unmapped:
            print(f"[WARNING] {unmapped} basin(s) could not be mapped to a "
                  "demand BCU key — check ID field vs demand CSV columns.")
    basin_key_col = "BCU_key"

# ================================
# 4. EXTRACT MEAN TABLE DEPTH
# ================================

table_depth_values = []

with rasterio.open("global_water_table_depth_0125.tif") as src:
    for geom in basins.geometry:
        try:
            out_image, _ = rasterio.mask.mask(src, [geom], crop=True)
            mean_val = np.nanmean(out_image)
        except Exception:
            mean_val = np.nan
        table_depth_values.append(mean_val)

basins["table_depth_m"] = table_depth_values

# Replace NA with mean
basins["table_depth_m"] = basins["table_depth_m"].fillna(
    basins["table_depth_m"].mean()
)

# Energy calculations
basins["GW_per_MCM_per_day"] = (
    0.85 * 9.81 / 86400 * basins["table_depth_m"]
)

basins["GW_per_km3_per_year"] = (
    basins["GW_per_MCM_per_day"] * 1000 / 365
)

basins.drop(columns="geometry").to_csv(
    f"gw_energy_intensity_depth_{reg}.csv",
    index=False
)

# ================================
# 5. GROUNDWATER FRACTION
# ================================

def load_2010_sum(nc_path, var_name, aliases=None):
    ds = xr.open_dataset(nc_path)
    aliases = aliases or []
    candidates = [var_name, *aliases]

    selected_name = None
    for candidate in candidates:
        if candidate in ds.data_vars:
            selected_name = candidate
            break

    if selected_name is None:
        raise KeyError(
            f"No variable matched {candidates} in {nc_path}. "
            f"Available variables: {list(ds.data_vars)}"
        )

    da = ds[selected_name]
    da_2010 = da.sel(time=slice("2010-01-01", "2010-12-31"))
    return da_2010.sum(dim="time")


def set_spatial_dims_auto(da):
    x_candidates = ["lon", "longitude", "x"]
    y_candidates = ["lat", "latitude", "y"]

    x_dim = next((d for d in x_candidates if d in da.dims), None)
    y_dim = next((d for d in y_candidates if d in da.dims), None)

    if x_dim is None or y_dim is None:
        raise KeyError(
            f"Could not infer spatial dims from {da.dims}. "
            "Expected one of lon/longitude/x and lat/latitude/y."
        )

    return da.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim, inplace=False)

# File paths
gw_abstract_nc = os.path.join(
    gw_path,
    "wada_groundwater_abstraction",
    "waterdemand_30min_groundwaterabstraction_million_m3_month.nc",
)

irrigation_nc = os.path.join(
    gw_path,
    "wada_groundwater_abstraction",
    "pcrglobwb_WFDEI_historical_PIrrWW_monthly_1960_2010.nc4",
)

industrial_nc = os.path.join(
    gw_path,
    "wada_groundwater_abstraction",
    "pcrglobwb_WFDEI_historical_PIndWW_monthly_1960_2010.nc4",
)

domestic_nc = os.path.join(
    gw_path,
    "wada_groundwater_abstraction",
    "pcrglobwb_WFDEI_historical_PDomWW_monthly_1960_2010.nc4",
)

gwabstract = load_2010_sum(
    gw_abstract_nc,
    "groundwater_abstraction",
    aliases=["gwab"],
)
irrigation = load_2010_sum(irrigation_nc, "PIrrWW")
industrial = load_2010_sum(industrial_nc, "PIndWW")
domestic = load_2010_sum(domestic_nc, "PDomWW")

total_demand = irrigation + industrial + domestic

gwfraction = gwabstract / total_demand
gwfraction = gwfraction.fillna(0)
gwfraction = xr.where(gwfraction > 1, 1, gwfraction)
gwfraction = xr.where(gwfraction < 0, 0, gwfraction)

# ================================
# 6. EXTRACT GW FRACTION PER BASIN
# ================================

gwfraction.rio.write_crs("EPSG:4326", inplace=True)
gwfraction = set_spatial_dims_auto(gwfraction)

gw_values = []

for geom in basins.geometry:
    try:
        clipped = gwfraction.rio.clip([geom])
        val = float(clipped.mean())
    except:
        val = 0
    gw_values.append(round(val, 3))

basins["gw_fraction"] = gw_values
basins["gw_fraction"] = basins["gw_fraction"].replace(
    to_replace=0, value=basins["gw_fraction"].mean()
)

# Save shapefile
basins.to_file(f"gw_fraction_{reg}.shp")

# ================================
# 7. HISTORICAL CAPACITY
# ================================

urban_dem = pd.read_csv(urban_demand_path)
rural_dem = pd.read_csv(rural_demand_path)
irr_dem_raw = pd.read_csv(irr_demand_path)


def demand_wide_to_long_2010(df, value_name):
    year_col = "year" if "year" in df.columns else df.columns[0]
    tmp = df.copy()
    tmp[year_col] = pd.to_numeric(tmp[year_col], errors="coerce")
    tmp = tmp[tmp[year_col] == 2010]

    if tmp.empty:
        raise ValueError(f"No 2010 row found in demand table for {value_name}.")

    out = tmp.drop(columns=[year_col]).melt(
        var_name="REGION", value_name=value_name
    )
    out[value_name] = pd.to_numeric(out[value_name], errors="coerce").fillna(0)
    return out


def irrigation_to_bcu_2010(df, basins_df, basin_key_col_name):
    if "year" in df.columns and "REGION" in df.columns and "irr_dem" in df.columns:
        irr = df[df["year"] == 2010][["REGION", "irr_dem"]].copy()
    elif "node" in df.columns and "2010" in df.columns:
        irr = df[["node", "2010"]].rename(
            columns={"node": "REGION", "2010": "irr_dem"}
        )
    else:
        return basins_df[[basin_key_col_name]].assign(irr_dem=0.0).rename(
            columns={basin_key_col_name: "REGION"}
        )

    irr["irr_dem"] = pd.to_numeric(irr["irr_dem"], errors="coerce").fillna(0)
    irr["REGION"] = irr["REGION"].astype(str).str.strip()

    # If irrigation is already on BCU ids (e.g., "1|AFR"), use it directly.
    if irr["REGION"].str.contains(r"\|").any():
        return irr[["REGION", "irr_dem"]]

    # Otherwise assume macro-regional ids (e.g., "R12_AFR") and distribute
    # equally across BCUs in each macro-region to obtain BCU-level values.
    irr["macro"] = irr["REGION"].str.extract(r"([A-Z]+)$")
    irr["macro"] = irr["macro"].fillna(
        irr["REGION"].str.extract(r"^([A-Z]{3,})")[0]
    )

    bcu_map = basins_df[[basin_key_col_name]].copy()
    bcu_map["macro"] = (
        bcu_map[basin_key_col_name].astype(str).str.split(r"\|").str[-1]
    )
    bcu_counts = bcu_map.groupby("macro", as_index=False).size().rename(
        columns={"size": "bcu_count"}
    )

    irr_macro = irr.groupby("macro", as_index=False)["irr_dem"].sum()
    irr_macro = irr_macro.merge(bcu_counts, on="macro", how="left")
    irr_macro["bcu_count"] = irr_macro["bcu_count"].replace(0, np.nan)
    irr_macro["irr_per_bcu"] = (
        irr_macro["irr_dem"] / irr_macro["bcu_count"]
    ).fillna(0)

    irr_bcu = bcu_map.merge(
        irr_macro[["macro", "irr_per_bcu"]], on="macro", how="left"
    )
    irr_bcu["irr_per_bcu"] = irr_bcu["irr_per_bcu"].fillna(0)
    return irr_bcu.rename(
        columns={basin_key_col_name: "REGION", "irr_per_bcu": "irr_dem"}
    )[["REGION", "irr_dem"]]


urban_2010 = demand_wide_to_long_2010(urban_dem, "urb_dem")
rural_2010 = demand_wide_to_long_2010(rural_dem, "rur_dem")
irr_2010 = irrigation_to_bcu_2010(irr_dem_raw, basins, basin_key_col)

tot_dem = urban_2010.merge(rural_2010, on="REGION", how="outer").merge(
    irr_2010, on="REGION", how="left"
)
tot_dem[["urb_dem", "rur_dem", "irr_dem"]] = tot_dem[
    ["urb_dem", "rur_dem", "irr_dem"]
].fillna(0)
tot_dem["tot_dem"] = tot_dem["urb_dem"] + tot_dem["rur_dem"] + tot_dem["irr_dem"]

hist_cap = basins[[basin_key_col, "gw_fraction"]].merge(
    tot_dem, left_on=basin_key_col, right_on="REGION", how="left"
)
hist_cap[["urb_dem", "rur_dem", "irr_dem", "tot_dem"]] = hist_cap[
    ["urb_dem", "rur_dem", "irr_dem", "tot_dem"]
].fillna(0)

hist_cap["hist_cap_gw_km3_year"] = (
    hist_cap["tot_dem"] * hist_cap["gw_fraction"]
)

hist_cap["hist_cap_sw_km3_year"] = (
    hist_cap["tot_dem"] * (1 - hist_cap["gw_fraction"])
)

# Diagnostics: confirm gw/sw split and scale after harmonization.
hist_cap["balance_err_km3_year"] = (
    hist_cap["hist_cap_gw_km3_year"]
    + hist_cap["hist_cap_sw_km3_year"]
    - hist_cap["tot_dem"]
)

print("\n=== Historical Capacity Diagnostics ===")
print(
    "GW fraction stats (min/mean/max): "
    f"{basins['gw_fraction'].min():.4f} / "
    f"{basins['gw_fraction'].mean():.4f} / "
    f"{basins['gw_fraction'].max():.4f}"
)
print(
    "Demand sums (km3/yr) - "
    f"tot_dem={hist_cap['tot_dem'].sum():.6f}, "
    f"gw={hist_cap['hist_cap_gw_km3_year'].sum():.6f}, "
    f"sw={hist_cap['hist_cap_sw_km3_year'].sum():.6f}"
)
print(
    "Balance check |gw+sw-tot_dem| max (km3/yr): "
    f"{hist_cap['balance_err_km3_year'].abs().max():.10f}"
)

hist_cap[[
    basin_key_col,
    "hist_cap_gw_km3_year",
    "hist_cap_sw_km3_year",
]].rename(columns={basin_key_col: "BCU_name"}).to_csv(
    f"historical_new_cap_gw_sw_km3_year_{reg}.csv",
    index=False
)

print("Groundwater harmonization completed successfully.")
