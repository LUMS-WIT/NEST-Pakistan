#### MESSAGE_IX CANADA ####

# --- This script contains the Main model's class ---#


# Including all necessary imports
import message_ix
import ixmp
import toml
import yaml
import os
import time
import warnings
import pandas as pd
from datetime import datetime
import pyam
import numpy as np


from model.utlities.pop_gdp import process_gdp_population_data, add_population_gdp_to_scenario
from model.utlities.demands import adjust_demands
from model.utlities.report import generate_report
from model.utlities.historical_activity import balance_import_export, update_historical_activity

from model.utlities.utils import (read_config_ctx, map_yv_ya_lt, config_validation, map_learning_rate)


from message_ix_models.util import (
	broadcast,
	make_matched_dfs,
	same_node,
	same_time,
)
from message_ix_models import Context
from pathlib import Path
from model.report.legacy.iamc_report_hackathon import report

warnings.filterwarnings("ignore")  # Ignore warnings to keep the output clean

class model_MSG:
	"""
	model_MSG class provides methods to process and validate configuration files,
	map vintage and active years, add technologies, adjust demands, and handle
	GDP and population data for a MESSAGEix scenario.

	Methods
	-------
	__init__(self, scenario_name: str)
			Initializes the model_MSG class with the given scenario name and loads
			configuration files.

	config_validation(self, validated=False)
			Validates the MESSAGE config file by checking for missing fields.

	map_yv_ya_lt(self, periods: Tuple[int, ...], lt: int, ya: Optional[int] = None) -> pd.DataFrame
			Generates all meaningful combinations of (vintage year, active year) given periods.

	add_technology(self, techs_file: str)
			Adds new technologies to the model based on the provided technology YAML file.

	add_hydrogen_shares(self, path: Union[str, Path])
			Adds hydrogen shares to a MESSAGEix scenario using data from an Excel file.

	process_gdp_population_data(self, path_to_gdp: Union[str, Path], path_to_pop: Union[str, Path]) -> pd.DataFrame
			Processes GDP and population data for the model and returns a DataFrame with
			processed data.

	adjust_demands(self)
			Adjusts demands in the scenario based on population and GDP data.

	add_population_gdp_to_scenario(self, population_data: pd.DataFrame, gdp_data: pd.DataFrame)
			Adds processed population and GDP data to the scenario.
	"""

	def __init__(self, scenario_name: str, config: str, report: bool = False, solve: bool = True):
		"""
		Initialize the scenario with the given name.

		Args:
				scenario_name (str): The name of the scenario to initialize.

		Attributes:
				scenario (str): The name of the scenario.
				sample_config (dict): The configuration loaded from the baseline config.toml file.
				scenario_path (str): The path to the scenario directory.
				config_path (str): The path to the scenario's config.toml file.
				config (dict): The configuration loaded from the scenario's config.toml file.
		"""
		ctx = Context.get_instance()

		if config:
			self.scenario_path = config #"data/sample_0"
		else:
			self.scenario_path = os.path.join("model/scenarios", scenario_name)

		read_config_ctx(ctx, dir_path=self.scenario_path)


		self.ctx = ctx
		
		self.ctx.source_scenario['scenario'] = scenario_name
		self.ctx.source_scenario['scenario'] = self.ctx.source_scenario['scenario_name']

		self.ctx.mp = ixmp.Platform(name=self.ctx.platform['name'], jvmargs=[self.ctx.platform['jvmargs']])
		self.ctx.mp.add_unit('USD/(tC/yr)') # Addiing cost unit for DAC technologies to the database
		if report:
			self.ctx.post_process_config['legacy_reporter'] = True
		if solve:
			self.ctx.source_scenario['solve'] = True

	## Scenario creation functions ##
	#TODO move it to separate technology.py file
	def add_technology(
		self,
		techs_file: str,
	):
		"""
		Function to add new technologies to the model

		Input: path to technology YAML file
		Output: None

		Logic: Creates the corresponding technology inside MESSAGE
		"""
		self.ctx.source_scenario['scenario'].check_out()

		tech_list = self.ctx['policy_config']['add_technology_techs']

		years = self.ctx.source_scenario['scenario'].set("year").astype(int).to_list()[14:]
		first_year = self.ctx.source_scenario['scenario'].firstmodelyear

		# Read file from path and convert to dictionary
		with open(techs_file) as data:
			technologies = yaml.safe_load(data)
			for tech, tech_data in technologies.items():
				if tech in tech_list:
					self.ctx.source_scenario['scenario'].add_set("technology", tech)

					if tech_data["node_select"] == "all":
						provinces = self.ctx.source_scenario['scenario'].set("node").to_list()[2:]
					elif tech_data["node_select"] == "custom":
						provinces = tech_data["provinces"]
					else:
						raise Exception(
							f"Option {tech_data['node_select']} not recognized."
							+ "Options for node_selct in technology.yaml is either 'all' or 'custom'"
						)

					# Creating DFs

					# input dataframe
					input_df = (
						message_ix.make_df(
							"input",
							# node_loc=provinces,
							technology=tech,
							mode=tech_data["mode"],
							commodity=tech_data["commodity"][0]["input"][0]["com_name"],
							level=tech_data["commodity"][0]["input"][2]["com_level"],
							time=tech_data["time"],
							time_origin=tech_data["time"],
							value=tech_data["commodity"][0]["input"][1]["com_value"],
							unit=tech_data["unit"][1]["energy"],
						)
						.pipe(
							broadcast,
							map_yv_ya_lt(
								years, tech_data["tec_lifetime"], first_year
							),
							# time=tech_data["time"],
							node_loc=provinces,
						)
						.pipe(same_node)
						.pipe(same_time)
					)
					self.ctx.source_scenario['scenario'].add_par("input", input_df)

					# output dataframe
					output_df = (
						message_ix.make_df(
							"output",
							# node_loc=provinces,
							technology=tech,
							mode=tech_data["mode"],
							commodity=tech_data["commodity"][1]["output"][0][
								"com_name"
							],
							level=tech_data["commodity"][1]["output"][2]["com_level"],
							time=tech_data["time"],
							time_origin=tech_data["time"],
							value=tech_data["commodity"][1]["output"][1]["com_value"],
							unit=tech_data["unit"][1]["energy"],
						)
						.pipe(
							broadcast,
							map_yv_ya_lt(
								years, tech_data["tec_lifetime"], first_year
							),
							# time=tech_data["time"],
							node_loc=provinces,
						)
						.pipe(same_node)
						.pipe(same_time)
					)
					self.ctx.source_scenario['scenario'].add_par("output", output_df)

					# variable cost
					var_cost_df = message_ix.make_df(
						"var_cost",
						node_loc=provinces,
						technology=tech,
						mode=tech_data["mode"],
						value=tech_data["var_cost_2020"][1]["cost_value"],
						time=tech_data["time"],
						unit=tech_data["unit"][0]["cost"],
					).pipe(
						broadcast,
						map_yv_ya_lt(years, tech_data["tec_lifetime"], first_year),
					)
					self.ctx.source_scenario['scenario'].add_par("var_cost", var_cost_df)

										# fixed cost
					fix_cost_df = message_ix.make_df(
						"fix_cost",
						node_loc=provinces,
						technology=tech,
						#value=tech_data["fix_cost_2020"][1]["cost_value"],
						time=tech_data["time"],
						unit=tech_data["unit"][0]["cost"],
					).pipe(broadcast, map_yv_ya_lt(years, 
                                    tech_data["tec_lifetime"], first_year),
					).pipe((map_learning_rate, 'input_df'),
							provinces=provinces,
            				l_rate=tech_data["fixed_cost_lr"], 
							initial_cost=tech_data["fix_cost_2020"][1]["cost_value"], 
    						cost_type="fixed", years=years, tech_lifetime=tech_data["tec_lifetime"]
        			)
					self.ctx.source_scenario['scenario'].add_par("fix_cost", fix_cost_df)

					# investment cost
					inv_cost_df = message_ix.make_df(
						"inv_cost",
						node_loc=provinces,
						technology=tech,
						#year_vtg=years,
						level=tech_data["inv_cost_2020"][0]["cost_level"],
						#value=tech_data["inv_cost_2020"][1]["cost_value"],
						time=tech_data["time"],
						unit=tech_data["unit"][0]["cost"],
					).pipe(broadcast, map_learning_rate(provinces=provinces,initial_cost=tech_data["inv_cost_2020"][1]["cost_value"], l_rate=tech_data["investment_lr"], cost_type="investment", years=years, tech_lifetime=tech_data["tec_lifetime"]))
					inv_cost_df["year_vtg"] = inv_cost_df["year_vtg"].astype(int)
					self.ctx.source_scenario['scenario'].add_par("inv_cost", inv_cost_df)

				
					dfs = []

					# Emission factor
					for year in years:
						emission_factor_df = message_ix.make_df(
							"relation_activity",
							node_rel=provinces,
							node_loc=provinces,
							technology=[tech]*len(provinces),
							mode=tech_data["mode"],
							value=tech_data["emission_factor"]*len(provinces),
							relation=tech_data["emission_type"],
							unit=["-"]*len(provinces),
							year_rel=[year]*len(provinces),
							year_act=[year]*len(provinces),
						)
						dfs.append(emission_factor_df)

						combined_df = pd.concat(dfs, ignore_index=True)
						self.ctx.source_scenario['scenario'].add_par("relation_activity", combined_df)


						# construction time
						for i, j in zip(
							tech_data["commodity"][1]["output"][1]["com_value"],
							tech_data["commodity"][0]["input"][1]["com_value"],
						):
							tec_construction_df = make_matched_dfs(
								input_df,
								capacity_factor=tech_data["capacity_factor"],
								technical_lifetime=tech_data["tec_lifetime"],
								construction_time=tech_data["construction_time"],
							)
							self.ctx.source_scenario['scenario'].add_par(
								"capacity_factor", tec_construction_df["capacity_factor"]
							)
							self.ctx.source_scenario['scenario'].add_par(
								"technical_lifetime",
								tec_construction_df["technical_lifetime"],
							)
							self.ctx.source_scenario['scenario'].add_par(
								"construction_time",
								tec_construction_df["construction_time"],
							)

			self.ctx.source_scenario['scenario'].commit("Technologies added successfully")

	# def write_gdx(self, scenario, step_name=None):
    #      """Write scenario to gdx
    #     The modified scenario is written to a gdx file,
    #     therefore checking for compilation errors.
    #     The scenarios are not solved as they are incomplete and therefore
    #     infeasible.
    #     """

    #     output_name = (
    #         f"MsgData_{scenario.model}_{scenario.scenario}.gdx"
    #         if step_name is None
    #         else f"MsgData_{scenario.model}_{scenario.scenario}_{step_name}.gdx"
    #     )
		
	# 	self.mp._backend.write_file(
    #         path=ctx.path_gdx / output_name,
    #         item_type=ItemType.SET | ItemType.PAR,
    #         filters={"scenario": scenario},
    #     )

	def generate_report(
		self,
		output_path="scenarios/baseline/MESSAGE_test.csv",
		min_year=2015,
		max_year=2060,
		from_excel=False,
		unit_correct=True,
	):
		"""
		Generate a report from the MESSAGEix scenario and save it to a CSV file.

		Args:
						output_path (str): The path where the output CSV file will be saved.
						min_year (int): The minimum year for the report.
						max_year (int): The maximum year for the report.
						from_excel (bool): Whether to read the report from an Excel file.
						unit_correct (bool): Whether to correct units in the report.
		"""
		generate_report(
			self,
			output_path,
			min_year,
			max_year,
			from_excel,
			unit_correct)

	#TODO move to policies/
	def change_technology_cost(self):
		"""
		Change the cost of technologies in a MESSAGEix scenario     
		This function modifies the provided MESSAGEix scenario to change the costs of specified technologies. 
		The specific implementation details, such as the technologies affected, the new cost values, 
		and the time periods for the cost changes, should be added within this function     
		Args:
			scenario (MESSAGEix.Scenario): The MESSAGEix scenario for which the technology costs will be changed        
		Returns:
			None
		"""
		pass 
	def validate_scenario(self, path_name):
		df_correction = pd.read_excel(path_name)

		# Replace empty values in the 'region' column with 'Unknown'
		df_correction['Region'] = df_correction['Region'].replace(np.nan, 'Unkown')
		duplicates = df_correction[df_correction.duplicated()]

		print("Duplicated rows:")
		print(duplicates)

		num_duplicates = duplicates.shape[0]
		print(f"Number of duplicated rows: {num_duplicates}")

		df_correction = df_correction.drop_duplicates()
		

		data = pyam.IamDataFrame(df_correction)
		ranges_df = pd.read_csv('source_data.csv')

		ranges_df = ranges_df.dropna(how='all')
		# Define the acceptable lower limit for each variable, year, region, and scenario
		acceptable_ranges = {}
		for _, row in ranges_df.iterrows():
			region = row['Region']
			variable = row['Variable']
			year = int(row['Year'])
			scenario = row['Scenario']
			lower = float(row['Lower'])
			unit = row['Unit'] 

			if region not in acceptable_ranges:
				acceptable_ranges[region] = {}
			if variable not in acceptable_ranges[region]:
				acceptable_ranges[region][variable] = {}
			if year not in acceptable_ranges[region][variable]:
				acceptable_ranges[region][variable][year] = {}
			acceptable_ranges[region][variable][year][scenario] = {'lower': lower, 'unit': unit}

		# Define acceptable deviation percentages
		deviation_percentage = {
			2020: 0.10,
			2030: 0.20,
			2040: 0.20,
			2050: 0.20
		}

		# Filter for specific years of interest
		years_of_interest = [2020, 2030, 2040, 2050]

		results = []

		within_deviation_count = 0
		outside_deviation_count = 0

		for year in years_of_interest:
			for region in data.region:
				for variable in data.variable:
					for scenario in data.scenario:
						if region in acceptable_ranges and variable in acceptable_ranges[region]:
							if year in acceptable_ranges[region][variable]:
								if scenario in acceptable_ranges[region][variable][year]:
									acceptable_range = acceptable_ranges[region][variable][year][scenario]
									lower_limit = acceptable_range['lower']
									lower_unit = acceptable_range['unit'] 

									df_filtered = data.filter(year=year, region=region, variable=variable, scenario=scenario)
									
									if not df_filtered.empty:
										row = df_filtered.data.iloc[0]
										value = row['value']
										unit = row['unit']  
										
										# Unit check
										if unit != lower_unit:
											print(f"Warning: Unit mismatch for {variable} in {region}, {year}, {scenario}. "
												f"Message output unit: {unit}, Expected source unit: {lower_unit}.")

										deviation = 0
										if lower_limit == 0:
											if value==0:
												deviation = 0
											else:
												deviation = 100
										elif value < lower_limit:
											deviation = (lower_limit - value) / lower_limit * 100
										elif value > lower_limit:
											deviation = (value - lower_limit) / lower_limit * 100
											
										acceptable_dev = deviation_percentage.get(year, 0) * 100
										
										if deviation > acceptable_dev:
											results.append({
												'Year': year,
												'Region': region,
												'Variable': variable,
												'Scenario': scenario,  
												'Value': value,
												'Deviation %': deviation,
												'Unit': lower_unit,  
												'Source-value': lower_limit
											})
											outside_deviation_count += 1
										else:
											within_deviation_count += 1

		pwd = os.getcwd()
		path_name_no_ext = os.path.splitext(path_name)[0]
		val_name = str(path_name_no_ext) + "_Validation result.xlsx"
		filename = os.path.join(pwd, val_name)
		results_df = pd.DataFrame(results)
		results_df.to_csv(filename, index=False)
		print(f"Values within acceptable deviation: {within_deviation_count}")
		print(f"Values outside acceptable deviation: {outside_deviation_count}")

	# Full scenario set-up
	def setup_scenario(self) -> tuple:
		"""
		Set up, initialize, and solve a MESSAGEix scenario based on the provided configuration.

		This function reads a configuration file for a given scenario, initializes a
		MESSAGEix scenario object, and performs pre-processing steps as defined in the
		configuration. The function returns the platform and scenario objects for further use.

		Args:
						None

		Returns:
						tuple: A tuple containing the ixmp.Platform object and the message_ix.Scenario object.

		"""

		# Config verification:
		#config_validation(self.ctx.config_path)

		# Scenario set-up
		# from datetime import datetime

		start = time.time()
		
		# TODO add option for SSP
		# ssp = 'SSP2'

		self.ctx.source_scenario['scenario'] = message_ix.Scenario(
		self.ctx.mp, self.ctx.source_scenario['model'], self.ctx.source_scenario['scenario'], version=self.ctx.source_scenario['version'], annotation=self.ctx.source_scenario['annotation']
		)

		caseName = (
			self.ctx.source_scenario['scenario'].model
			+ "__"
			+ self.ctx.source_scenario['scenario'].scenario
			+ "__v"
			+ str(self.ctx.source_scenario['scenario'].version)
		)

		script_dir = Path(__file__).resolve().parent
		scenario_folder = script_dir /  self.ctx['path']['scenario_folder']
		excel_path = script_dir / self.ctx['path']['provincial_input_file']
		# Update message scenario
		#TODO: Print statement

		print('\nModel Logs: Setting up scenario\n')
		self.ctx.source_scenario['scenario'].read_excel(
			excel_path, add_units=True, commit_steps=False, init_items=True
		)

		# self.ctx.source_scenario['scenario'].read_excel(
		# 	"model/scenarios/baseline/model_default_v32_override.xlsx", add_units=True, commit_steps=False, init_items=False
		# )
		
		if self.ctx.policy_config['apply_renewable_potential']:
			print('Model Logs: Applying renewable potential data\n')
			apply_renewable_potential(self)

		if self.ctx.policy_config['process_historical']:
			print('Model Logs: Processing historical data\n')
			update_historical_activity(self, path=scenario_folder)

		if self.ctx.policy_config['add_hydrogen_shares_f']:
			print('Model Logs: Adding hydrogen shares\n')
			path_to_hydrogen_data = script_dir / scenario_folder
			add_hydrogen_shares(self, path=path_to_hydrogen_data)

		
		# Technologies
		if self.ctx.policy_config['add_techs']:
			print('Model Logs: Adding technology\n')
			self.add_technology(techs_file=f"{scenario_folder}/technology.yaml")

		# Setting up policies 

		# OBPS 
		if self.ctx.policy_config['apply_obps']:
			print('Model Logs: Applying OBPS\n')	
			apply_obps(self.ctx)
		
		if self.ctx.policy_config['investment_tax_credit']:
			print('Model Logs: Applying Investment Tax Credit\n')	
			add_investment_tax_credit(self)
			
		#remove this later
		#demand_reduction(scenario=self.ctx.source_scenario['scenario'])

  
		end = time.time()
		print(
			f"\n==================================================\n\
		Model creation time: {round((end - start) / 60)} Min and {round((end - start) % 60)} Sec \
		\n=================================================="
		)
		
		if self.ctx.source_scenario['solve']:
			start = time.time()
			try:
				print("Model Logs: Solving the model...\n")
				self.ctx.source_scenario['scenario'].solve(
					solve_options={"write_model_to_file":"true", "writelp":"true", "write_model_file":"true", "lpmethod":2}, case=caseName
				)
				end = time.time()
				print(
					f"\n==================================================\n\
				Solving process time: {round((end - start) / 60)} Min and {round((end - start) % 60)} Sec\
				\n=================================================="
				)

			except Exception as solve_error:
				print(f"Scenario {caseName} did not solve because of the following exception:\n{solve_error}\n")


			if self.ctx.post_process_config['new_reporter']:
				timestamp = f"{str(datetime.now().strftime('%Y-%m-%d--%H-%M'))}"
				self.ctx.generate_report(
					output_path=f"reporting_output/{caseName}_{timestamp}_new_reporter.csv",
					min_year=2020,
					max_year=2060,
					from_excel=False,
					unit_correct=True,
				)
				end = time.time()
				print(
					f"\n==================================================\n\
				Reporting with NEW reporter. Process time: {round((end - start) / 60)} Min and {round((end - start) % 60)} Sec\
				\n=================================================="
				)
			elif self.ctx.post_process_config['legacy_reporter']:
				timestamp = f"{str(datetime.now().strftime('%Y-%m-%d--%H-%M'))}"
				start = time.time()
				df, path_name= report(mp=self.ctx.mp, scen=self.ctx.source_scenario['scenario'], out_dir="reporting_outputs", out_file_timestamp = timestamp, IDEA_format=self.ctx.post_process_config['IDEA_format'])
				end = time.time()
				print(
					f"\n==================================================\n\
				Reporting with LEGACY reporter. Process time: {round((end - start) / 60)} Min and {round((end - start) % 60)} Sec\
				\n=================================================="
				)
				if os.path.exists(path_name):
					self.validate_scenario(path_name)
				


		if self.ctx.post_process_config['to_excell']:
			start = time.time()
			self.ctx.source_scenario['scenario'].to_excel(f"{caseName}.xlsx")
			print(f"Exported Scenario to Excel: {caseName}.xlsx")
			end = time.time()
			print(
					f"\n==================================================\n\
				Exported results to Excel in: {round((end - start) / 60)} Min and {round((end - start) % 60)} Sec\
				\n=================================================="
				)

		return self.ctx.mp, self.ctx.source_scenario['scenario'], scenario_folder
		
