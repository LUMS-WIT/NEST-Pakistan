
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union


def process_gdp_population_data(
		path_to_gdp: Union[str, Path], path_to_pop: Union[str, Path]
	):
		"""
		Process GDP and population data for the model.

		Args:
			path_to_pop (str or Path): Path to the CSV file containing raw population data.
			path_to_gdp (str or Path): Path to the CSV file containing raw GDP data.

		Returns:
			pd.DataFrame: DataFrame containing processed GDP, population, and GDP per capita data for each province.
		"""
		# Resolve the full paths to the GDP and population data files
		path_to_gdp = Path(path_to_gdp).resolve()
		path_to_pop = Path(path_to_pop).resolve()

		# Read the CSV files containing GDP and population data into DataFrames
		ssp_gdp_df = pd.read_csv(path_to_gdp)
		ssp_gdp_df.rename(columns={"node_loc": "Province","year_act":"Year","value":"GDP"}, inplace=True)
		ssp_gdp_df = ssp_gdp_df[["Province", "Year", "GDP"]]
		# Convert GDP figures to consistent units (billions to single units)
		ssp_gdp_df['GDP'] = ssp_gdp_df['GDP'] * 1e9
		ssp_gdp_df = ssp_gdp_df[ssp_gdp_df["Year"] != 2020]
		ssp_pop_df = pd.read_csv(path_to_pop)

		# Convert population figures to consistent units (thousands to single units)
		ssp_pop_df["Population"] = ssp_pop_df["Population"] * 1000

		# Remove spaces from province names to ensure consistency
		ssp_pop_df["Province"] = ssp_pop_df["Province"].str.replace(" ", "")

		# Adjust specific province names for consistency
		province_mapping = {
			"Newfoundland and Labrador": "NewfoundlandandLabrador",
			"Prince Edward Island": "PrinceEdwardIsland",
		}
		ssp_pop_df["Province"] = ssp_pop_df["Province"].replace(province_mapping)

		# List of unique provinces from the GDP data
		provinces = ssp_gdp_df["Province"].unique()

		ssp_df = (
			[]
		)  # Initialize an empty list to store the processed data for each province

		# Process each province's GDP and population data
		for province in provinces:
			# Filter GDP and population data for the current province
			c_ssp_gdp_df = ssp_gdp_df.loc[ssp_gdp_df.Province == province]
			c_ssp_pop_df = ssp_pop_df.loc[ssp_pop_df.Province == province]

			# Initialize empty lists to store GDP, population, and GDP per capita for each year
			gdp = []
			pop = []
			gdpc = []

			# Iterate over the years of interest to extract and calculate GDP per capita
			for jjj in [2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060]:
				if (
					not c_ssp_gdp_df.loc[c_ssp_gdp_df.Year == jjj].empty
					and not c_ssp_pop_df.loc[c_ssp_pop_df.Year == jjj].empty
				):
					gdp.append(
						c_ssp_gdp_df.loc[c_ssp_gdp_df.Year == jjj, "GDP"].values[0]
					)
					pop.append(
						c_ssp_pop_df.loc[c_ssp_pop_df.Year == jjj, "Population"].values[
							0
						]
					)
					gdpc.append(gdp[-1] / pop[-1])  # Calculate GDP per capita
				else:
					# If data is missing, append NaN to maintain the structure
					gdp.append(np.nan)
					pop.append(np.nan)
					gdpc.append(np.nan)

			# Append the processed data for the current province to the list
			ssp_df.append(
				pd.DataFrame(
					{
						"year": [2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060],
						"gdp": gdp,
						"pop": pop,
						"gdpc": gdpc,
						"iso": province,
					}
				)
			)

		# Concatenate the data from all provinces into a single DataFrame
		ssp_df = pd.concat(ssp_df)
		return ssp_df  # Return the processed DataFrame

def add_population_gdp_to_scenario(
		scenario, population_data: pd.DataFrame, gdp_data: pd.DataFrame
	):
		"""
		Add processed population and GDP data to the scenario.

		Args:
						population_data (pd.DataFrame): DataFrame containing processed population data.
						gdp_data (pd.DataFrame): DataFrame containing processed GDP data.

		Logic:
						Adds the processed population and GDP data to the scenario's 'bound_activity_lo' parameter.
		"""
		# Rename columns in the population DataFrame to match the expected format in the scenario
		population_data.rename(
			columns={"Population": "value", "Province": "node_loc", "Year": "year_act"},
			inplace=True,
		)
		population_data["technology"] = "Population"  # Add a column for technology type
		population_data["mode"] = "P"  # Add a column for mode
		population_data["time"] = "year"  # Add a column for time
		population_data["unit"] = "GWa/a"  # Add a column for unit

		# Rename columns in the GDP DataFrame to match the expected format in the scenario
		gdp_data.rename(
			columns={"GDP": "value", "Province": "node_loc", "Year": "year_act"},
			inplace=True,
		)
		gdp_data["technology"] = "GDP"  # Add a column for technology type
		gdp_data["mode"] = "P"  # Add a column for mode
		gdp_data["time"] = "year"  # Add a column for time
		gdp_data["unit"] = "GWa/a"  # Add a column for unit

		# Concatenate the processed population and GDP data into a single DataFrame
		concatenated_df_socio = pd.concat([population_data, gdp_data])

		# Retrieve the current 'bound_activity_lo' parameter from the scenario
		df = model_obj.scenario.par("bound_activity_lo")

		# Filter out any existing 'Population' and 'GDP' technologies to avoid duplication
		df_filtered = df[~df["technology"].isin(["Population", "GDP"])]

		# Combine the filtered existing data with the new population and GDP data
		df_bound_new = pd.concat([df_filtered, concatenated_df_socio])

		# Update the scenario with the new bounds
		model_obj.scenario.check_out()
		model_obj.scenario.add_par("bound_activity_lo", df_bound_new)
		model_obj.scenario.commit(
			"Added population and GDP bounds"
		) 