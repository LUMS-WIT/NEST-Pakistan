"""
This script aggregates the global gridded data to any
scale and also adjust unit conversions. The following
script specifically aggregates global gridded hydrological
data onto the basin mapping used in the nexus module.
"""

import glob
import os
from datetime import datetime as dt

import dask
import numpy as np
import xarray as xr

start = dt.now()

# Configuration
variables = ["qtot", "dis", "qr"]  # All variables to process
isimip = "3b"
data = "future"  # "future" or "historical"

# Updated to use local paths
input_dir = os.path.join(".", "Input Files") + os.sep
output_dir = os.path.join(".", "Output Files") + os.sep

# Climate models available in your Input Files folder
climmodels = [
    "gfdl-esm4",
    "ipsl-cm6a-lr",
    "mpi-esm1-2-hr",
    "mri-esm2-0",
    "ukesm1-0-ll",
]

# Scenarios available in your Input Files folder
scenarios = ["ssp126", "ssp370"]

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("="*80)
print("ISIMP Water Model - Hydrological Data Aggregation")
print("="*80)
print(f"Variables: {variables}")
print(f"Data type: {data}")
print(f"Climate models: {len(climmodels)}")
print(f"Scenarios: {scenarios}")
print(f"Input directory: {input_dir}")
print(f"Output directory: {output_dir}")
print("="*80)

# Configuration parameters
monthlyscale = True  # Define if monthly aggregation is required
quant = 0.1  # Define quantile for statistical aggregation
multimodelensemble = True  # Define if multi climate models mean
latchunk = 120  # Define lat and long chunk for reducing computational load
lonchunk = 640

# TO AVOID ERROR WHEN OPENING AND SLICING INPUT DATA
dask.config.set({"array.slicing.split-large-chunks": False})

# Open raster area file
# The file landareamaskmap0.nc can be found under
# P:\ene.model\NEST\delineation\data\delineated_basins_new
area_file = input_dir + "landareamaskmap0.nc"
if not os.path.exists(area_file):
    print(f"ERROR: Missing required file: {area_file}")
    print("Please add 'landareamaskmap0.nc' to the Input Files folder.")
    print("This file is needed for area calculations.")
    exit(1)

print(f"Loading area mask file...")
area = xr.open_dataarray(area_file)

# Process each variable
for var in variables:
    print("\n" + "="*80)
    print(f"Processing variable: {var}")
    print("="*80)
    
    # Define spatial method to aggregate
    if var == "dis":
        spatialmethod = "meansd"
    else:
        spatialmethod = "sum"
    
    # Process each climate model and scenario
    for cl in climmodels:
        for scen in scenarios:
            print(f"\nProcessing: {cl} - {scen}")
            
            # Set paths for local setup
            wd = input_dir  # Directory for input NetCDF files
            wd2 = output_dir  # Directory for output files
            
            # Build file pattern
            if data == "historical":
                hydro_data = wd + f"*{cl}*{var}*monthly*.nc"
            elif data == "future":
                # Pattern to match files like: cwatm_gfdl-esm4_w5e5_ssp126_..._qr_global_monthly_2015_2100.nc
                hydro_data = wd + f"*{cl}*{scen}*{var}*monthly*.nc"
            
            files = glob.glob(hydro_data)
            print(f"  Looking for pattern: {os.path.basename(hydro_data)}")
            print(f"  Found {len(files)} file(s)")
            
            if len(files) == 0:
                print(f"  WARNING: No files found for {cl} + {scen} + {var}")
                continue
            
            # Open hydrological data as a combined dataset
            print(f"  Opening dataset...")
            da = xr.open_mfdataset(files)
            print(f"  Dataset shape: {da.dims}")
            
            years = np.arange(2010, 2105, 5)
            
            # Process based on monthlyscale setting
            if monthlyscale:
                if var == "dis":
                    # Convert the discharge into km3/year
                    da = da * 0.031556952
                    da["dis"] = da.dis.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.dis.time)}
                    )
                    da.dis.attrs["unit"] = "km3/year"
                    
                    output_file = wd2 + f"{var}_monthly_{cl}_{scen}.nc"
                    print(f"  Saving to: {os.path.basename(output_file)}")
                    da.to_netcdf(output_file)
                    print(f"  Completed: {cl} - {scen}")
                    
                elif var == "qtot":
                    # Convert to total runoff per grid cell into km3/year
                    # 1kg/m2/sec = 86400 mm/day
                    # 86400 mm/day X Area (mm2) = 86400 mm3/day
                    # 86400 mm3/day = 86400 X 1000000 3.65e-16 km3/year
                    da = da * 86400 * area * 3.65e-16 * 1000000
                    
                    output_file = wd2 + f"{var}_monthly_{cl}_{scen}_{data}.nc"
                    print(f"  Saving to: {os.path.basename(output_file)}")
                    da.to_netcdf(output_file)
                    print(f"  Completed: {cl} - {scen}")
                    
                elif var == "qr":
                    # Convert groundwater recharge into km3/year
                    # 1kg/m2/sec = 86400 mm/day
                    # 86400 mm/day X Area (mm2) = 86400 mm3/day
                    # 86400 mm3/day = 86400 X 1000000 3.65e-16 km3/year
                    da = da * 86400 * area * 3.65e-16 * 1000000
                    da.qr.attrs["unit"] = "km3/year"
                    
                    output_file = wd2 + f"{var}_monthly_{cl}_{scen}_{data}.nc"
                    print(f"  Saving to: {os.path.basename(output_file)}")
                    da.to_netcdf(output_file)
                    print(f"  Completed: {cl} - {scen}")
            
            else:
                # Annual aggregation path (not used with current settings)
                if var == "dis":
                    da["dis"] = da.dis.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.dis.time)}
                    )
                    # Resample daily data to annual (by taking mean)
                    da = da.resample(time="Y").mean()
                    da["dis"] = da.dis.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.dis.time)}
                    )
                    # Take 20 year rolling average to make the time scale consistent
                    da = da.rolling(time=20).mean()
                    # Convert the discharge into km3/year
                    da = da * 0.031556952
                    da.dis.attrs["unit"] = "km3/year"
                    
                    # Long term Mean annual discharge
                    davg = da.resample(time="30Y", loffset="4Y").mean()
                    davg["dis"] = davg.dis.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(davg.dis.time)}
                    )
                    davg.to_netcdf(wd2 + f"{var}_90Y_avg_5y_{cl}_{scen}_temp_agg.nc")
                    
                    # Now resample to an average value for each 5-year block, and
                    # offset by 2 years so that the value is centered to start 2101
                    da = da.resample(time="5Y", loffset="4Y").mean()
                    da.to_netcdf(wd2 + f"{var}_5y_{cl}_{scen}_temp_agg.nc")
                    print(f"  Completed: {cl} - {scen}")
                    
                elif var == "qtot":
                    da["qtot"] = da.qtot.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qtot.time)}
                    )
                    # Resample daily data to annual (by taking mean)
                    da = da.resample(time="Y").mean()
                    da["qtot"] = da.qtot.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qtot.time)}
                    )
                    da = da.rolling(time=20, min_periods=1).mean()
                    da["qtot"] = da.qtot.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qtot.time)}
                    )
                    # Convert to total runoff per grid cell into km3/year
                    da = da * 86400 * area * 3.65e-16 * 1000000
                    da.qtot.attrs["unit"] = "km3/year"
                    da["qtot"] = da.qtot.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qtot.time)}
                    )
                    # Now resample to an average value for each 5-year block
                    da = da.resample(time="5Y", loffset="4Y").mean()
                    da.to_netcdf(wd2 + f"{var}_monthly_{cl}_{scen}_temp_agg.nc")
                    print(f"  Completed: {cl} - {scen}")
                    
                elif var == "qr":
                    da["qr"] = da.qr.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qr.time)}
                    )
                    # Resample daily data to annual (by taking mean)
                    da = da.resample(time="Y").mean()
                    da["qr"] = da.qr.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qr.time)}
                    )
                    da = da.rolling(time=20, min_periods=1).mean()
                    da["qr"] = da.qr.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qr.time)}
                    )
                    # Convert groundwater recharge into km3/year
                    da = da * 86400 * area * 3.65e-16 * 1000000
                    da.qr.attrs["unit"] = "km3/year"
                    da["qr"] = da.qr.chunk(
                        {"lat": latchunk, "lon": lonchunk, "time": len(da.qr.time)}
                    )
                    # Now resample to an average value for each 5-year block
                    da = da.resample(time="5Y", loffset="4Y").mean()
                    output_file = wd2 + f"{var}_5y_{cl}_{scen}.nc"
                    print(f"  Saving to: {os.path.basename(output_file)}")
                    da.to_netcdf(output_file)
                    print(f"  Completed: {cl} - {scen}")

print("\n" + "="*80)
print("Processing complete!")
print(f"Total processing time: {dt.now() - start}")
print("="*80)