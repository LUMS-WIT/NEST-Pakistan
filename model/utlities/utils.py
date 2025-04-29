#### MESSAGE_IX CANADA ####

# --- This script contains all the auxiliary functions to the model ---#

import os
import sys
import toml
import message_ix
import numpy as np
import pandas as pd
import yaml

from typing import Optional, Tuple
from math import prod

#import models.data.report
#from models.data.report.legacy import default_units as def_units

def read_config_ctx(ctx, config_file="ModelSetup_CA.yaml", dir_path="model/scenarios/baseline", verbose=False):
	path = os.path.join(os.getcwd(), dir_path, config_file)
	ctx["config_path"] = path
    
	if verbose:
		print(f"Reading configuration from {path}")
    
    # Load YAML file
	with open(path, "r") as file:
		config = yaml.safe_load(file)
    
    # -----------------------
    # Read paths to data file
    # -----------------------
	ctx["path"] = config.get("path_config", {})
    
    # # ------------------
    # # Configure scenario
    # # ------------------
	for section, values in config.get("scenario_config", {}).items():
		ctx[section] = values


def config_validation(config_path: str):
    """
    Function to verify the MESSAGE config file

    Input: path to the config file
    Output: Error, or success messages

    Logic: only checking for missing fields, since additional settings won't hinder
    model execution, only missing settings will cause the model to fail
    """
    validated = False

    try:
        with open(config_path, "r") as config_file:
            check_config_file = yaml.safe_load(config_file)
            print("Config file read successfully!")
    except FileNotFoundError:
        print(f"YAML config file not found in path {config_path}")
        sys.exit()
    
    # Using baseline scenario as a basis for validation
    sample_path = os.path.join(os.getcwd(), "model/scenarios/baseline", "ModelSetup_CA_sample.yaml")
    try:
        with open(sample_path, "r") as sample_file:
            sample_config = yaml.safe_load(sample_file)
    except FileNotFoundError:
        print(f"Sample YAML config file not found in path {sample_path}")
        sys.exit()

    # Extract path config
    sample_items_path = list(sample_config.get("path_config", {}).keys())
    given_items_path = list(check_config_file.get("path_config", {}).keys())

    # Extract scenario config
    sample_scenario_config = sample_config.get("scenario_config", {})
    given_scenario_config = check_config_file.get("scenario_config", {})

    # Check for missing fields
    for path in sample_items_path:
        if path not in given_items_path:
            raise Exception(f"Missing path '{path}' in config file '{config_path}'")
    
    
    for item, sub_items in sample_scenario_config.items():
        if item not in given_scenario_config:
            raise Exception(f"Missing section '{item}' in config file '{config_path}'")
        for sub_item in sub_items:
            if sub_item not in given_scenario_config[item]:
                raise Exception(f"Missing field '{sub_item}' in section '{item}'")

    print(f"{'#' * 100}\nConfig file '{config_path}' passed format verification!\n{'#' * 100}")
    validated = True
    return validated

def clone_scenario(scenario_name: str, scenario_params: list, keep_solution=False) -> tuple:
		"""
		Clone an existing scenario
		Parameters:
			scenario_name (str): name of scenario to be cloned
			scenario_params: list of the necessary MESSAGE parameters to clone a scenario
				[0]: mp
				[1]: modelName
				[2]: scenarioName
				[3]: version
				[4]: annotation
		Returns: a copy of the input MESSAGE scenario
		"""

		scenario = message_ix.Scenario(
			scenario_params[0], scenario_params[1], scenario_params[2],
			version=scenario_params[3], annotation=scenario_params[4]
		)
		scenario_copy = scenario.clone(
			scenario_params[0],
			scenario_name,
			keep_solution=keep_solution,
		)

		return scenario_copy

def map_yv_ya_lt(
		periods: Tuple[int, ...], lt: int, ya: Optional[int] = None
	) -> pd.DataFrame:
		"""All meaningful combinations of (vintage year, active year) given periods.
		Parameters
		----------
		labels : pandas.DataFrame
						Each column (dimension) corresponds to one in df. Each row represents one
						matched set of labels for those dimensions.
		lt : int, lifetime
		"""
		if not ya:
			ya = periods[0]
			print(f"First active year set as {ya!r}")
		if not lt:
			raise ValueError("Add a fixed lifetime parameter 'lt'")
		# The following lines are the same as
		# message_ix.tests.test_feature_vintage_and_active_years._generate_yv_ya
		# - Create a mesh grid using numpy built-ins
		# - Take the upper-triangular portion (setting the rest to 0)
		# - Reshape
		data = np.triu(np.meshgrid(periods, periods, indexing="ij")).reshape((2, -1))
		# Filter only non-zero pairs
		def filter_func(pair):
			#print(pair, (abs(pair[1] - pair[0]) < lt) and (pair != (0,0)), lt)
			return (abs(pair[1] - pair[0]) < lt) and (pair != (0,0))
		df = pd.DataFrame(
			filter(filter_func, zip(data[0, :], data[1, :])),
			columns=["year_vtg", "year_act"],
			dtype=np.int64,
		)
		# Select values using the ya and lt parameters
		return df#[(ya <= df.year_act) & (df.year_act - df.year_vtg <= lt)]

def map_learning_rate(provinces, l_rate: float, initial_cost: float, cost_type: str, years: list, tech_lifetime, input_df=None,) -> pd.DataFrame:
	'''
	Function to apply learning rate to costs using the technology.yaml file.
	
	Parameters
		----------
		l_rate : float
			Learning rate.
		initial_cost : float
			Initial cost to propagate through time-series
		cost_type : string
			Type of cost to which the learning rate is applied (investment, fixed, or variable)
		years :  list
			Time-series of years included in the model
	Returns
		-----
		df : pandas DataFrame
			Resulting dataframe after the learning rate is applied
	'''
	values = np.zeros(len(years))
	values[0] = initial_cost

	if cost_type == "investment":
		
		for i in range(1, len(years)):
			values[i] = values[i-1] * l_rate
		df = pd.DataFrame({"year_vtg": years, "value": values}, dtype=np.float64)
	
	elif cost_type == "fixed":
		
		input_df["value"] = values_calculation(years, provinces, l_rate, initial_cost, tech_lifetime)
		
		filtered_input_df = input_df[input_df['value'].notna()]

		df = filtered_input_df

	return df

def values_calculation(years, provinces, learning_rate, initial_value, tech_lifetime):
	"""
	Calculates the fixed cost values for each province and year based on the given learning rate.
 
	Args:
		years (list of int): List of years to calculate the values for
		provinces (list of str): List of province names to calculate the values for
		learning_rate (float): The learning rate to use for calculating the fixed costs
		initial_value (float): The initial value to use as a base for calculation
		tech_lifetime (int): The lifetime of technology in years

	Returns:
		list: A list of calculated values, one for each province and year combination
		
    Description:
        This auxelary function for map_learning_rate calculates the fixed cost values for each province and year based on the given learning rate.
        It starts by initializing a dictionary with the initial value for each province-year combination.
        Then it iterates over each year and updates the values using the learning rate, assuming that the previous year's value is the base.
        Finally, it calculates the fixed costs for each province-year combination within a certain technology lifetime (tech_lifetime).
        The function returns a list of calculated values.
	"""

	dictionary_vals = {f"{prov}.{year}": initial_value for year in years for prov in provinces}
	for year_index, year in enumerate(years):
		for prov in provinces:
			if year_index != 0:
				previous_value = dictionary_vals[f"{prov}.{years[year_index-1]}"]
				dictionary_vals[f"{prov}.{years[year_index]}"] = previous_value * learning_rate
	#value_col = [dictionary_vals[f"{prov}.{year}"] for year in years for prov in provinces]
	value_col = []
	final_result_dict = {}
	for year in years:
		for i in range(len(years) - years.index(year)):
			for prov in provinces:
				act_year = years[years.index(year)+i]
				if (act_year - year) < tech_lifetime:
					value_col.append(dictionary_vals[f"{prov}.{act_year}"])
					final_result_dict[f"{prov}.{year}.{act_year}"] = dictionary_vals[f"{prov}.{act_year}"]

	return value_col

def expand_grid(dictionary):
	"""
	Create a DataFrame from all combinations of dictionary values.
	Args:
		dictionary (dict): A dictionary where each key is a column name and the value is a list of column values.
	Returns:
		pd.DataFrame: A DataFrame containing all combinations of the provided values.
	"""
	return pd.DataFrame([row for row in prod(*dictionary.values())], columns=dictionary.keys())


def unit_conversion(input_df, techs_map):
	"""
	Function to convert units from tonnes of CO2 emissions per a specific quantity 
	to tonnes of CO2 emissions per GW
	
	"""
	unit_map = {"variable": [], "region": [], "technology": [], "time": [], "value": [], "unit [tCO2/-]": [], "comments": []}
	#merged_df = input_df.merge(techs_map, how="outer", right_on="variable", left_on="variable")
	
	for tmap_rows in techs_map.iterrows():
		for inp_rows in input_df.iterrows():
			if tmap_rows[1].loc["variable"] in inp_rows[1].loc["variable"]:
				unit_map["variable"].append(inp_rows[1].loc["variable"])
				unit_map["region"].append(inp_rows[1].loc["region"])
				unit_map["technology"].append(tmap_rows[1].loc["technology"])
				unit_map["time"].append(inp_rows[1].loc["time"])
				unit_map["value"].append(inp_rows[1].loc["value"])
				unit_map["unit [tCO2/-]"].append(inp_rows[1].loc["unit [tCO2/-]"])
				unit_map["comments"].append(tmap_rows[1].loc["comments"])
	
	units_df = pd.DataFrame.from_dict(unit_map)
	units_df.fillna("-")
	
	units_df["unit [tCO2/-]"].replace({"megawatt hour" : "MWh", "Megawatt hours (MWh)": "MWh", "Energy (expressed in gigajoules)": "GJ", 
							"gigawatt hours (GWh)" : "GWh", "Energy (expressed in gigawatt hours)": "GWh", 
							"Mass (expressed in tonnes)" : "tonnes", "Mass (expressed in kg)": "kg", 
							"gigajoules (GJ)": "GJ", "gigajoule": "GJ", "tonnes": "tonne"}, inplace=True)
	
	with open("model/data/default_units.yaml", "r") as file:
		data = yaml.safe_load(file)
		for k,v in data['conversion_factors']['Kwa'].items():
			for idx, row in units_df.iterrows():
				if k == row["unit [tCO2/-]"]:
					units_df.at[idx, "value"] *= v
					units_df.at[idx, "unit [tCO2/-]"] = "KWa"
		print("End!")
	
	with pd.ExcelWriter(path= "model/data/obps_inputs_clean.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
		units_df.to_excel(writer, sheet_name="Merged_Sheet",index=0)

# Reporter method - Deprecated in favor of message_ix_models legacy (forked)
def report_to_pyam(scenario, directory_path, output_path):
	"""
	Function to process all .xlsx files in a directory, extract region and scenario data,
	process the data for each sheet, and save the final dataframe as a CSV.
	Args:
		directory_path (str): Path to the directory containing .xlsx files.
		output_path (str): Path to save the resulting CSV file.
	Returns:
		final_df (pd.DataFrame): The concatenated dataframe from all processed .xlsx files.
	"""

	# Automatically list all .xlsx files in the directory
	file_paths = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.endswith('.xlsx')]
	dfs = []
	# Process each file
	for file in file_paths:
	# Extract region and scenario from the file name
		file_name = os.path.basename(file)

		# Split file name using '__' to handle sections like baseline, version, and region
		parts = file_name.split('__')

		# Extract scenario, including the version, but without '__' (e.g., 'baseline v4')
		scenario = f"{parts[1]} {parts[2].split('_')[0]}"  # Extract 'baseline' and 'v4', separated by a space

		# Extract region from the part after 'v4_'
		region = parts[2].split('_')[1].split('.')[0]  # Extract region (e.g., 'PrinceEdwardIsland')

		# Open the Excel file and get sheet names
		xls = pd.ExcelFile(file)
		sheet_names = xls.sheet_names
		for sheet in sheet_names:
			df = pd.read_excel(file, sheet_name=sheet)
			# Process variable and unit from the sheet name
			variable, unit = sheet.split(' (')
			variable = variable.strip()  # Strip spaces from variable
			unit = unit.strip().rstrip(')')  # Strip spaces from unit and remove closing parenthesis
			# Rename the first column to 'time'
			df.rename(columns={df.columns[0]: 'time'}, inplace=True)
			# Melt the dataframe to have 'time' as id_vars, variable names in 'variable', and values in 'value'
			df = pd.melt(df, id_vars=['time'], var_name='variable', value_name='value')
			# Add the unit and processed variable names
			df['unit'] = unit
			df['variable'] = variable + '|' + df['variable']
			# Add region and scenario columns
			df['region'] = region
			df['scenario'] = scenario
			df['model'] = 'MESSAGEix-Canada'
			# Append the dataframe to the list
			dfs.append(df)
	# Concatenate all dataframes into a single dataframe
	final_df = pd.concat(dfs, ignore_index=True)
	# Filter the dataframe to only include data from 2020 onwards
	final_df = final_df[final_df['time'] >= 2020]
	# Save the final dataframe to a CSV file
	final_df.to_csv(output_path, index=False)
	return final_df


 


if __name__ == "__main__":
	ßß
	formatted_inputs = pd.read_excel("model/data/obps_inputs_clean.xlsx", sheet_name="formatted_inputs")
	mapped_techs = pd.read_excel("model/data/obps_inputs_clean.xlsx", sheet_name="Mapping")
	unit_conversion(formatted_inputs, mapped_techs)
