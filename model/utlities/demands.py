import numpy as np
import pandas as pd

from scipy.optimize import linprog
from pathlib import Path
from model.utlities.pop_gdp import process_gdp_population_data


def adjust_demands(model_obj):
		"""
		Adjust demands in the scenario based on population and GDP data.

		Args:
						None

		Returns:
						pd.DataFrame: DataFrame containing updated demand data.
		"""

		# Define directories for data storage
		script_dir = Path(__file__).resolve().parent
		data_dir = script_dir / "../../data"

		# File paths for GDP and population data
		gdp_data = data_dir / "gdp/gdp_messageca_prov.csv"
		population_data = data_dir / "population/pop_messageca_prov.csv"

		# Process GDP and population data for use in the scenario
		ssp_df = process_gdp_population_data(gdp_data, population_data)

		# Retrieve demand data from the scenario
		demand = model_obj.ctx.source_scenario['scenario'].par("demand")

		# Group demand data by specific columns and aggregate it at the 'Canada' level
		df_ca = (
			demand.groupby(["year", "commodity", "level", "time", "unit"])
			.sum()
			.reset_index()
		)
		df_ca["node"] = "Canada"

		# Calculate the percentage change in demand year-over-year for each commodity
		pc = df_ca.groupby("commodity").apply(
			lambda x: x.sort_values("year").assign(
				pct_change=lambda y: y["value"].pct_change().fillna(0)
			)
		)
		pc = pc.reset_index(drop=True)  # Flatten the DataFrame
		pc = pc[["year", "commodity", "pct_change"]]  # Keep only relevant columns

		# Retrieve historical activity data from the scenario
		hist_act_df = model_obj.ctx.source_scenario['scenario'].par("historical_activity")

		# Initialize dictionary and lists for storing demands and relevant years
		dmds_dict = {}
		historical_years = hist_act_df["year_act"].unique().tolist()
		demand_years = demand["year"].unique().tolist()
		cmdtys = demand["commodity"].unique().tolist()

		# Extract historical demand data for each commodity and province
		historical_demand = []
		for cmdty in cmdtys:
			for province in ssp_df["iso"].unique():
				for year in demand_years:
					if year in historical_years:
						historical_demand.append(
							demand[
								(demand["year"] == year)
								& (demand["commodity"] == cmdty)
								& (demand["node"] == province)
							]
						)

		# Concatenate all historical demand DataFrames into one
		historical_demand_df = pd.concat(historical_demand, ignore_index=True)

		# Initialize lists for storing final demand data
		ha = historical_demand_df
		dmds = []

		# Iterate through each commodity, province, and year to adjust demand
		for cmdty in cmdtys:
			for province in ssp_df["iso"].unique():
				for year in demand_years:
					if year in historical_years:
						# Process historical demands
						dm = ha.loc[
							(ha["year"] == year)
							& (ha["node"] == province)
							& (ha["commodity"] == cmdty)
						]
						dm = dm[["node", "value"]]

						# Initialize GDP and GDP per capita lists
						gdp = [ssp_df.gdp.to_numpy()[0]]
						gdpc = [ssp_df.gdpc.to_numpy()[0]]

						# Create DataFrame for historical demand with additional economic indicators
						dm = pd.DataFrame(
							{
								"node": dm.node.to_numpy(),
								"commodity": cmdty,
								"level": "useful",
								"year": year,
								"time": "year",
								"value": dm.value.to_numpy(),
								"unit": "GWa",
								"ei": dm.value.to_numpy() / gdp,
								"gdp": gdp,
								"gdpc": gdpc,
								"year": year,
							}
						)
						dmds.append(dm)

						# Update variables for the next iteration
						dt = dm.value
						dm0 = dm

					else:
						# Calculate future demand based on percentage change
						pct_change = pc.loc[
							(pc["year"] == year) & (pc["commodity"] == cmdty),
							"pct_change",
						].values[0]
						dt = dm.value * (1 + pct_change)

						dm0 = dm
						gdpf = []
						gdpcf = []

						# Retrieve future GDP and GDP per capita
						inds = ssp_df["year"] == year
						gdpf.append(ssp_df.loc[inds, "gdp"].to_numpy()[0])
						gdpcf.append(ssp_df.loc[inds, "gdpc"].to_numpy()[0])

						# Unload some variables and call LP downscaling algorithm
						names = dm0.node.to_numpy()
						vl = dm0.value.to_numpy()
						gdpco = dm0.gdpc.to_numpy()

						# Avoid 0 intensities in future time steps for non-biomass technologies
						if "biomass" not in cmdty:
							ei = vl / gdpco
							vl = ei * gdpco

						# Simplifying parameters for LP solver
						beta = gdpco * vl / gdpco
						phi = gdpcf / gdpco - 1

						# Define LP objective function coefficients
						cobj = [1] + [0] * len(names)
						cobj = np.array(cobj)

						# Define inequality constraints for LP solver
						a = np.array([-1] * len(names)).reshape((len(names), 1))
						b = np.identity(len(names))

						Aub1 = np.concatenate((a, b), axis=1)
						bub1 = phi.reshape((len(names), 1))

						Aub2 = np.concatenate((a, -b), axis=1)
						bub2 = (-1 * phi).reshape((len(names), 1))

						Aub3 = np.array([-1] + [0] * len(names)).reshape(
							(1, len(names) + 1)
						)
						bub3 = np.array([[0]])

						Aub = np.concatenate((Aub1, Aub2, Aub3), axis=0)
						bub = np.concatenate((bub1, bub2, bub3), axis=0)

						# Define equality constraints for LP solver
						Aeq = np.append([0], beta).reshape((1, len(names) + 1))
						beq = np.array([[dt - sum(beta)]]).reshape((1, 1))

						# Call LP solver to minimize the maximum difference in growth rates
						res = linprog(
							c=cobj,
							A_ub=Aub,
							b_ub=bub,
							A_eq=Aeq,
							b_eq=beq,
							bounds=(-np.inf, np.inf),
							options={"disp": False, "tol": 3.6e-10},
						)

						# Calculate the updated demand values based on the LP results
						val = [
							(gdpcf[i] * (vl[i] / gdpco[i]) * (1 + res.x[i + 1]))
							for i in range(len(names))
						]

						# Create DataFrame for future demand with updated values
						dmf = pd.DataFrame({"node": names, "value": val})

						dm = pd.DataFrame(
							{
								"node": dmf.node.to_numpy(),
								"commodity": cmdty,
								"level": "useful",
								"year": year,
								"time": "year",
								"value": dmf.value.to_numpy(),
								"unit": "GWa",
								"ei": dmf.value.to_numpy() / gdpf,
								"gdp": gdpf,
								"gdpc": gdpcf,
								"commodity": cmdty,
								"year": year,
							}
						)

						# Append updated demand to the list
						dmds.append(dm)

		# Concatenate all demand DataFrames into a single DataFrame
		dmds = pd.concat(dmds, ignore_index=True)

		# Drop unnecessary columns before updating the scenario
		dmds.drop(columns=["ei", "gdp", "gdpc"], inplace=True)

		# Update the scenario with the new demand data
		model_obj.ctx.source_scenario['scenario'].check_out()
		df = model_obj.ctx.source_scenario['scenario'].par("demand")
		model_obj.ctx.source_scenario['scenario'].remove_par("demand", df)
		model_obj.ctx.source_scenario['scenario'].add_par("demand", dmds)

		print('demands adjusted based on historical data')
		# Commit the changes to the scenario
		model_obj.ctx.source_scenario['scenario'].commit("Updated demands")