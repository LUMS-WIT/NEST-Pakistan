# =============================================
# Load Required Libraries
# =============================================
library(terra)
library(sf)
library(dplyr)
library(ncdf4)
library(exactextractr)

# =============================================
# Define Paths
# =============================================
base_path <- "C:/Users/User/Desktop/lums/3rd semester/Thesis/ISIMP Water Model/Output Files"
shape_path <- "C:/Users/User/Desktop/lums/3rd semester/Thesis/Thesis II/Indus Shape Files/Indus_bcu_cleaned.shp"
output_dir <- "C:/Users/User/Desktop/lums/3rd semester/Thesis/ISIMP Water Model/Output"

# Create output directory if it doesn't exist
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# =============================================
# Define Variables, Models, and Scenarios
# =============================================
variables <- c("dis", "qr", "qtot")
models <- c("gfdl-esm4", "ipsl-cm6a-lr", "mpi-esm1-2-hr", "mri-esm2-0", "ukesm1-0-ll")
scenarios <- c("ssp126", "ssp370")

# =============================================
# Load Shapefile
# =============================================
shp <- st_read(shape_path)

# Add an index column if it doesn't exist
if (!"id" %in% names(shp)) {
  shp$id <- 0:(nrow(shp) - 1)
}

# =============================================
# Loop Through Variable-Model-Scenario Combinations
# =============================================
for (var in variables) {
  for (model in models) {
    for (scenario in scenarios) {
      
      # Add "_future" suffix only for qr and qtot
      if (var %in% c("qr", "qtot")) {
        nc_filename <- paste0(var, "_monthly_", model, "_", scenario, "_future.nc")
      } else {
        nc_filename <- paste0(var, "_monthly_", model, "_", scenario, ".nc")
      }
      
      nc_path <- file.path(base_path, nc_filename)
      
      # Skip if file not found
      if (!file.exists(nc_path)) {
        cat("⚠️ Skipping missing file:", nc_filename, "\n")
        next
      }
      
      cat("✅ Processing:", nc_filename, "\n")
      
      # Load NetCDF file as a SpatRaster
      r <- rast(nc_path)
      
      # Get time information from the raster
      time_dates <- time(r)
      
      # If time information is not available, try to extract from NetCDF
      if (is.null(time_dates) || length(time_dates) == 0) {
        nc <- nc_open(nc_path)
        time_var <- ncvar_get(nc, "time")
        time_units <- ncatt_get(nc, "time", "units")$value
        
        # Parse time units (e.g., "days since 1970-01-01")
        if (grepl("days since", time_units)) {
          origin <- as.Date(sub("days since ", "", time_units))
          time_dates <- origin + time_var
        } else if (grepl("months since", time_units)) {
          origin <- as.Date(sub("months since ", "", time_units))
          time_dates <- seq(origin, by = "month", length.out = length(time_var))
        }
        nc_close(nc)
      }
      
      # Extract mean values for each basin polygon and each time step
      extracted_data <- exact_extract(r, shp, "mean", progress = TRUE)
      
      # Convert to data frame
      result_df <- as.data.frame(extracted_data)
      
      # Format dates as column names (YYYY-MM-DD format)
      if (!is.null(time_dates) && length(time_dates) > 0) {
        colnames(result_df) <- format(as.Date(time_dates), "%Y-%m-%d")
      } else {
        # If no time info available, use generic time step names
        colnames(result_df) <- paste0("time_", 1:ncol(result_df))
      }
      
      # Add basin ID as first column
      result_df <- cbind(basin_id = shp$id, result_df)
      
      # Define output path
      out_filename <- paste0(var, "_", model, "_", scenario, "_output.csv")
      out_path <- file.path(output_dir, out_filename)
      
      # Save CSV
      write.csv(result_df, out_path, row.names = FALSE)
      cat("💾 Saved:", out_filename, "\n")
      cat("   Dimensions:", nrow(result_df), "basins x", ncol(result_df)-1, "time steps\n\n")
    }
  }
}

cat("🎯 All NetCDF files processed successfully!\n")