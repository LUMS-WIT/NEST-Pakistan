#require(reshape)
#require(rgdal)
require(raster)
#require(rgeos)
#require(tidyr)
#require(dplyr)
#require(maptools)
require(ncdf4)
library(sp)
library(tibble)
#library(countrycode)
#library(ggmap)
library(sf)
library(exactextractr)

nc = nc_open(
    paste0(
        "ssp2_population_total.nc"
    ),
    verbose=FALSE,
)

nc.brick = brick(
    "ssp2_total_gdp0.125.nc")#, varname = "total-population"
#)


basin <-read.csv(
    "Canada_shape_file.csv"
)

# load shapefile
basin_by_region.spdf = read_sf(
    paste0("georef-canada-province-millesime.shp"),
)


agg <-exact_extract(nc.brick, basin_by_region.spdf, "sum")


output <-cbind(basin, agg)

write.csv(
    output,
    "Canada_GDP.csv",
)