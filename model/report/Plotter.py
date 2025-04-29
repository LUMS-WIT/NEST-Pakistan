#### MESSAGE_IX CANADA ####

# --- Script to contain classes for pre and postprocessing the model ---#

import itertools
import logging
import os
import sys
import time
import warnings
import matplotlib.pyplot as plt
import plotly.express as px 
import numpy as np
import pandas as pd


from matplotlib.backends.backend_pdf import PdfPages

warnings.filterwarnings("ignore")  # Ignore warnings to keep the output clean

# Plotter class
class plotter_MSG:

	def __init__(self, scenario):
		self.scenario = scenario  # MESSAGE scenario object
		self.color_map = {
			"CH4-AFOLU": "darkgreen",
			"CH4-Other": "lime",
			"CO2-AFOLU": "dimgrey",
			"CO2-Other": "lightgrey",
			"F-Gases": "black",
			"N2O-AFOLU": "maroon",
			"N2O-Other": "red",
			"Other": "orange",
			"TCE": "black",
			"biomass": "green",
			"biomass (modern)": "lightgreen",
			"biomass (solids)": "lightgreen",
			"biomass (traditional)": "green",
			"buildings": "green",
			"coal": "black",
			"coal (solids)": "black",
			"crudeoil": "red",
			"district heat": "red",
			"electr": "purple",
			"electricity": "purple",
			"electricity generation": "purple",
			"ethanol": "lightgreen",
			"exports": "blueviolet",
			"fuel oil": "firebrick",
			"fueloil": "firebrick",
			"gas": "aqua",
			"gas_weu": "olive",
			"gases": "aqua",
			"gasification": "aqua",
			"geothermal": "tan",
			"heat": "red",
			"heat pump (gas)": "darkturquoise",
			"heat pump (el)": "turquoise",
			"heavy fuel oil": "firebrick",
			"hydro": "royalblue",
			"hydrogen": "sienna",
			"i_feed": "green",
			"i_spec": "salmon",
			"i_therm": "red",
			"imports": "lightcoral",
			"industry": "darkred",
			"light oil": "salmon",
			"lightoil": "salmon",
			"liquids": "royalblue",
			"LNG": "yellow",
			"methanol": "darkgreen",
			"natural gas (CC)": "aqua",
			"natural gas (ST + CT)": "darkturquoise",
			"non-commercial": "darkgreen",
			"non-energy (feedstock)": "darkblue",
			"nuclear": "yellow",
			"oil": "red",
			"others": "lightgrey",
			"production": "darkblue",
			"production (unconv.)": "skyblue",
			"rc_spec": "darkblue",
			"rc_therm": "firebrick",
			"refinery": "gray",
			"solar": "gold",
			"solar CSP": "coral",
			"solar PV": "gold",
			"transport": "grey",
			"wind": "skyblue",
			"wind offshore": "dodgerblue",
			"wind onshore": "skyblue",
		}

		# Minimum value as % of max value to show in the graph
		self.min_val = 0.02
		self.min_abs = 2  # min abs value to show in the plots
		self.renaming = {
			"biomass_nc": "biomass (traditional)",
			"biomass_rc": "biomass (modern)",
			"coal_rc": "coal",
			"crudeoil": "oil",
			"d_heat": "district heat",
			"elec_rc": "electric heating",
			"elec_trp": "electric transport",
			"electr": "electricity",
			"electr_eur_afr": "electricity",
			"foil_rc": "heavy fuel oil",
			"fueloil": "heavy fuel oil",
			"gas_rc": "gas",
			"heat_rc": "district heat",
			"hp_el_rc": "heat pump (el)",
			"hp_gas_rc": "heat pump (gas)",
			"lh2": "hydrogen",
			"lightoil": "light oil",
			"loil_rc": "light oil",
			"solar_pv": "solar",
			"solar_csp": "solar",
			"solar_rc": "solar",
			"solar_th": "solar",
			"sp_el_I": "electricity",
			"sp_el_RC": "electricity",
			"stor_ppl": "storage_loss",
			"wind_onshore": "wind",
			"wind_offshore": "wind",
		}

		# Order of commodities in the results
		self.crudes = [x for x in set(self.scenario.set("commodity")) if "crude_" in x]
		self.gases = [x for x in set(self.scenario.set("commodity")) if "gas_" in x]
		self.gas_tecs = ["gas_t_d", "gas_t_d_ch4", "gas_bal"]
		self.coal_tecs = {"supply" : ["coal_t_d", "coal_bal", "coal_exp"], 
						"utilization": ["coal_t_d", "coal_bal", "coal_extr", "coal_extr_ch4"]}
		self.order = (
			["coal", "coal_rc", "coal_i", "crudeoil"]
			+ self.crudes
			+ ["fueloil", "foil_rc", "foil_i", "lightoil", "loil_rc", "loil_i"]
			+ self.gases
			+ [
				"biomass",
				"biomass_nc",
				"biomass_rc",
				"d_heat",
				"elec_rc",
				"electr",
				"ethanol",
				"gas",
				"gas_rc",
				"hp_el_rc",
				"hp_gas_rc",
				"hydro",
				"hydrogen",
				"methanol",
				"nuclear",
				"others",
				"solar_csp",
				"solar_pv",
				"solar_rc",
				"sp_el_I",
				"sp_el_RC",
				"wind_offshore",
				"wind_onshore",
			]
		)

		# Unit conversion
		self.unitc = 8.76 * 3.6  # Conversion from GWa to PJ
		self.unitname = "(PJ)"

		self.unit_el = 8760 / 1000  # Conversion from GWa to TWh
		self.unitname_el = "(TWh)"

		self.unit_cap = 1000  # Conversion from GW to MW
		self.unitname_cap = "(MW)"

		# Graphing parameters
		self.kind = "bar"
		self.dict_plot = {
			"Oil supply " + self.unitname: self.kind,
			"Oil derivative supply " + self.unitname: self.kind,
			"Oil derivative use " + self.unitname: self.kind,
			"Gas supply " + self.unitname: self.kind,
			"Gas utilization " + self.unitname: self.kind,
			"Coal supply " + self.unitname: self.kind,
			"Coal utilization " + self.unitname: self.kind,
			"Biomass supply " + self.unitname: self.kind,
			"Biomass utilization " + self.unitname: self.kind,
			"Electricity generation " + self.unitname_el: self.kind,
			"Power plant capacity " + self.unitname_cap: self.kind,
			"Power plant new capacity " + self.unitname_cap: self.kind,
			"Electricity use " + self.unitname_el: self.kind,
			"Primary energy supply " + self.unitname: self.kind,
			"Final energy consumption " + self.unitname: self.kind,
			"Energy use: Transport " + self.unitname: self.kind,
			"Energy use: Industry " + self.unitname: self.kind,
			"Energy use: Buildings " + self.unitname: self.kind,
			"Non-energy use: Feedstock " + self.unitname: self.kind,
			"Useful energy " + self.unitname: self.kind,
			"Energy exports " + self.unitname: self.kind,
			"Energy imports " + self.unitname: self.kind,
			"Total GHG emissions (MtCeq)": self.kind,
		}

		self.abbrev_prov = {
			"Alberta": "AB",
			"BritishColumbia": "BC",
			"Saskatchewan": "SK",
			"Manitoba": "MB",
			"Ontario": "ON",
			"Quebec": "QC",
			"NewBrunswick": "NB",
			"NewfoundlandandLabrador": "NL",
			"PrinceEdwardIsland": "PE",
			"NovaScotia": "NS",
			"Yukon": "YT",
			"NorthwestTerritories": "NT",
			"Nunavut": "NU",
		}

		self.fntsz = 5  # Font size
		self.fntcol = "dimgray"  # Font color
		self.lw = 0.1  # Line width
		self.ticksz = -1  # Tick size
		self.tickwdt = 0.2  # Tick width

	# Modules and functions for creating the plotting dataframes
	def group(self, df, groupby, result, limit, lyr) -> pd.DataFrame:
		"""The function groups dataframe df over an index and column."""
		df = df.groupby(groupby, as_index=False).sum()
		df = pd.pivot_table(
			df, index=groupby[0], columns=groupby[1], values=result, fill_value=0
		)
		return df

	def multiply_df(self, df1, column1, df2, column2) -> pd.DataFrame:
		"""The function merges dataframe df1 with df2 and multiplies column1 with
		column2. The function returns the new merged dataframe with the result
		of the muliplication in the column 'product'.
		"""
		index = [
			x
			for x in ["mode", "node_loc", "technology", "time", "year_act", "year_vtg"]
			if x in df1.columns
		]
		df = df1.merge(df2, how="outer", on=index)
		df["product"] = df.loc[:, column1] * df.loc[:, column2]
		return df

	def attach_history(self, tec, plotyrs):
		"""This function calculates historical data to be attached to the model
		results
		"""
		parname = "historical_activity"
		act_hist = self.scenario.par(parname, {"technology": tec, "year_act": plotyrs})
		act_hist = act_hist[["technology", "year_act", "value"]]
		act_hist = pd.pivot_table(
			act_hist, index="year_act", columns="technology"
		).fillna(0)
		act_hist = act_hist[act_hist.columns[(act_hist > 0).any()]]
		act_hist.columns = act_hist.columns.droplevel(0)
		return act_hist

	def plotdf(self, tec, com, direction, plotyrs, yr):
		"""The main function for calculating output and attaching historical data"""
		# Reading input or output coefficients based on the direction
		inputs = self.scenario.par(direction)
		inputs = inputs.loc[inputs.year_act.isin(plotyrs)]
		inputs = inputs.loc[
			(inputs.technology.isin(tec)) & (inputs.commodity.isin(com))
		][["technology", "year_act", "value"]]
		inputs = inputs.groupby(["technology", "year_act"], as_index=False).mean()
		inputs = inputs.pivot(index="year_act", columns="technology")
		inputs = inputs[inputs.columns[(inputs != 0).any()]]
		inputs.columns = inputs.columns.droplevel(0)

		# Reading output variable of activity
		act = self.scenario.var("ACT").loc[
			self.scenario.var("ACT").year_act.isin(plotyrs)
		]
		activity = act.loc[act.technology.isin(tec)][["technology", "year_act", "lvl"]]

		activity = activity.groupby(["technology", "year_act"], as_index=False).sum()
		activity = activity.pivot(index="year_act", columns="technology").fillna(0)
		activity = activity[activity.columns[(activity != 0).any()]]
		activity.columns = activity.columns.droplevel(0)

		# Addding Historical Activity (to the graphs)
		act_hist = self.attach_history(tec, plotyrs)
		activity_tot = activity.add(act_hist, fill_value=0)

		df_plot = inputs * activity_tot
		df_plot = df_plot.fillna(0)
		df_plot = df_plot[df_plot.columns[(df_plot > 0).any()]]
		return df_plot

	def plotdf_com(self, tec, com, direction, plotyrs, yr):
		"""This funcion aggregates commodities for reporting at each level"""

		df_plot_com = df_plot_el = pd.DataFrame(index=plotyrs)
		for commodities in com:

			inputs = self.scenario.par(direction)
			inputs = inputs.loc[inputs.year_act.isin(plotyrs)]
			inputs = inputs.loc[
				(inputs.technology.isin(tec)) & (inputs.commodity == commodities)
			][["technology", "year_act", "value"]]
			inputs = inputs.groupby(["technology", "year_act"], as_index=False).mean()
			inputs = inputs.pivot(index="year_act", columns="technology")
			inputs = inputs[inputs.columns[(inputs != 0).any()]]
			inputs.columns = inputs.columns.droplevel(0)
			act = self.scenario.var("ACT").loc[
				self.scenario.var("ACT").year_act.isin(plotyrs)
			]
			activity = act.loc[act.technology.isin(tec)][
				["technology", "year_act", "lvl"]
			]

			activity = activity.groupby(
				["technology", "year_act"], as_index=False
			).sum()
			activity = activity.pivot(index="year_act", columns="technology")
			activity = activity[activity.columns[(activity != 0).any()]]
			activity.columns = activity.columns.droplevel(0)

			# Attaching history
			act_hist = self.attach_history(tec, plotyrs)
			activity = activity.add(act_hist, fill_value=0)

			df_plot = inputs * activity
			df_plot = df_plot.fillna(0)
			df_plot = df_plot.loc[:, (df_plot != 0).any(axis=0)]

			cols_hydro = [col for col in df_plot.columns if "hydro" in col]
			cols_wind = [col for col in df_plot.columns if "wind" in col]
			cols_solar = [col for col in df_plot.columns if "solar" in col]
			cols_others = [
				x
				for x in df_plot.columns
				if x not in (cols_hydro + cols_wind + cols_solar)
			]
			dict_ele = {
				"cols_hydro": (cols_hydro, "hydro"),
				"cols_wind": (cols_wind, "wind"),
				"cols_solar": (cols_solar, "solar"),
				"cols_others": (cols_others, "electr"),
			}

			if commodities == "electr":
				for tecs in list(dict_ele.keys()):
					df_plot_el[dict_ele["{}".format(tecs)][1]] = (
						df_plot.filter(items=dict_ele["{}".format(tecs)][0])
						.sum(axis=1)
						.to_frame()
					)
			else:
				df_plot = df_plot.sum(axis=1).to_frame()
				df_plot[commodities] = df_plot
				df_plot_com = df_plot_com.join(df_plot[commodities])
		df_plot_com = df_plot_com.join(df_plot_el)

		return df_plot_com

	# Aggregating sectors
	def mappings(self, plotyrs, df, groupby="sector"):
		df_sec = pd.DataFrame(index=plotyrs)

		if groupby == "sector":
			cols_ind = [col for col in df.columns if "_i" in col] + [
				col for col in df.columns if "_I" in col
			]
			cols_ind = [
				x
				for x in cols_ind
				if not any(y in x for y in ["eth_ic", "meth_ic", "bio_is", "_imp"])
			]
			cols_trp = [col for col in df.columns if "_trp" in col]
			cols_rc = [
				col for col in df.columns if any(y in col for y in ["_rc", "_RC"])
			]
			cols_nc = [col for col in df.columns if "_nc" in col]
			cols_ene = [col for col in df.columns if "_fs" in col]
			cols_exp = [col for col in df.columns if "_exp" in col]
			cols_imp = [col for col in df.columns if "_imp" in col]
			cols_ppl = [
				col
				for col in df.columns
				if any(
					y in col
					for y in [
						"_ppl",
						"_adv",
						"bio_istig",
						"gas_cc",
						"gas_cc_ccs",
						"gas_ct",
						"igcc",
						"igcc_ccs",
						"loil_cc",
					]
				)
			]
			cols_eth = [
				col
				for col in df.columns
				if any(y in col for y in ["eth_bio", "liq_bio"])
			]
			cols_meth = [
				col
				for col in df.columns
				if any(y in col for y in ["meth_ng", "meth_coal"])
			]
			cols_loil = [
				col for col in df.columns if any(y in col for y in ["syn_liq"])
			]
			cols_gas = [
				col
				for col in df.columns
				if any(y in col for y in ["coal_gas", "gas_bio"])
			]
			cols_hyd = [col for col in df.columns if any(y in col for y in ["h2_"])]

			cols_prod = [
				col
				for col in df.columns
				if any(
					y in col
					for y in [
						"_extr",
						"_extr_1",
						"_extr_2",
						"_extr_3",
						"_extr_4",
						"extr_ch4",
					]
				)
			]

			cols_prod2 = [
				col
				for col in df.columns
				if any(y in col for y in ["_extr_5", "_extr_6", "_extr_7", "_extr_8"])
			]

			cols_ref = [
				col for col in df.columns if any(y in col for y in ["ref_h", "ref_l"])
			]

			dict_sectors = {
				"production": cols_prod,
				"production (unconv.)": cols_prod2,
				"refinery": cols_ref,
				"industry": cols_ind,
				"transport": cols_trp,
				"non-energy (feedstock)": cols_ene,
				"buildings": cols_rc,
				"non-commercial": cols_nc,
				"electricity generation": cols_ppl,
				"exports": cols_exp,
				"imports": cols_imp,
				"ethanol": cols_eth,
				"methanol": cols_meth,
				"light oil": cols_loil,
				"gasification": cols_gas,
				"hydrogen": cols_hyd,
				"production": cols_prod,
				"production (unconv.)": cols_prod2,
				"refinery": cols_ref,
			}
		else:
			cols_solar = [
				col
				for col in df.columns
				if any(y in col for y in ["solar_pv", "solar_res"])
			]
			cols_csp = [
				col
				for col in df.columns
				if any(y in col for y in ["csp_sm", "solar_th_ppl"])
			]
			cols_wind = [
				col
				for col in df.columns
				if any(y in col for y in ["wind_ppl", "wind_res"])
			]
			cols_windoff = [
				col
				for col in df.columns
				if any(y in col for y in ["wind_ppf", "wind_ref"])
			]
			cols_coal = [
				col
				for col in df.columns
				if any(y in col for y in ["coal_ppl", "coal_adv", "syn_liq", "igcc"])
			]
			cols_gas1 = [
				col
				for col in df.columns
				if any(y in col for y in ["gas_ppl", "gas_ct"])
			]
			cols_gas2 = [col for col in df.columns if any(y in col for y in ["gas_cc"])]
			cols_loil = [
				col
				for col in df.columns
				if any(y in col for y in ["loil_ppl", "loil_cc"])
			]
			cols_foil = [
				col
				for col in df.columns
				if any(y in col for y in ["foil_ppl", "foil_cc"]) or col == "oil_ppl"
			]
			cols_nuc = [
				col for col in df.columns if any(y in col for y in ["nuc_hc", "nuc_lc"])
			]
			cols_hyd = [
				col
				for col in df.columns
				if any(y in col for y in ["hydro_lc", "hydro_hc"])
			]
			cols_bio = [
				col
				for col in df.columns
				if any(y in col for y in ["bio_ppl", "bio_istig"])
			]
			cols_geo = [col for col in df.columns if any(y in col for y in ["geo_ppl"])]
			dict_sectors = {
				"coal": cols_coal,
				"heavy fuel oil": cols_foil,
				"light oil": cols_loil,
				"natural gas (ST + CT)": cols_gas1,
				"natural gas (CC)": cols_gas2,
				"nuclear": cols_nuc,
				"hydro": cols_hyd,
				"biomass": cols_bio,
				"wind onshore": cols_wind,
				"wind offshore": cols_windoff,
				"solar PV": cols_solar,
				"solar CSP": cols_csp,
				"geothermal": cols_geo,
			}

		# Adding everything else to others
		cols_others = [
			x
			for x in df.columns
			if x not in list(itertools.chain.from_iterable(dict_sectors.values()))
		]
		dict_sectors.update({"others": cols_others})

		# Mapping the entries (columns) to lables
		for label, tecs in dict_sectors.items():
			df[label] = df.filter(items=tecs).sum(axis=1).to_frame()
			df_sec = df_sec.join(df[label])

		return df_sec.fillna(0)

	# Aggregating results for industry and energy sectors
	def plotdf_ind(self, tec, com, direction, plotyrs, yr):
		df_plot_ind = pd.DataFrame(index=plotyrs)
		plot_year = int(yr)
		inputs = self.scenario.par(direction)
		inputs = inputs.loc[inputs.year_act.isin(plotyrs)]
		inputs = inputs.loc[
			(inputs.technology.isin(tec)) & (inputs.commodity.isin(com))
		][["technology", "year_act", "value"]]
		inputs = inputs.groupby(["technology", "year_act"], as_index=False).mean()
		inputs = inputs.pivot(index="year_act", columns="technology")
		inputs = inputs[inputs.columns[(inputs != 0).any()]]
		inputs.columns = inputs.columns.droplevel(0)
		act = self.scenario.var("ACT").loc[
			self.scenario.var("ACT").year_act.isin(plotyrs)
		]
		activity = act.loc[act.technology.isin(tec)][["technology", "year_act", "lvl"]]

		activity = activity.groupby(["technology", "year_act"], as_index=False).sum()
		activity = activity.pivot(index="year_act", columns="technology")
		activity = activity[activity.columns[(activity != 0).any()]]
		activity.columns = activity.columns.droplevel(0)

		# Attaching history
		act_hist = self.attach_history(tec, plotyrs)
		activity = activity.add(act_hist, fill_value=0)

		df_plot = inputs * activity
		df_plot = df_plot.fillna(0)
		df_plot = df_plot.loc[:, (df_plot != 0).any(axis=0)]

		fuel = {
			"biomass": ["biomass_i"],
			"coal": ["coal_i"],
			"foil": ["foil_fs", "foil_i"],
			"electr": ["elec_i", "sp_el_I", "sp_liq_I"],
			"gas": ["gas_fs", "gas_i"],
			"d_heat": ["heat_i"],
			"loil": ["loil_fs", "loil_i"],
			"solar": ["solar_i"],
		}

		for source in list(fuel.keys()):
			df_plot["{}".format(source)] = (
				df_plot.filter(items=fuel["{}".format(source)]).sum(axis=1).to_frame()
			)
			df_plot_ind = df_plot_ind.join(df_plot["{}".format(source)])

		others = df_plot_ind.loc[
			:, (df_plot_ind.loc[plot_year] <= df_plot_ind.loc[plot_year].sum() * 0.01)
		].sum(axis=1)
		df_plot_ind = df_plot_ind.loc[
			:, (df_plot_ind.loc[plot_year] > df_plot_ind.loc[plot_year].sum() * 0.01)
		]
		df_plot_ind["others"] = others

		return df_plot_ind

	# A function for adding history
	def add_history(self, tecs, nodeloc, df2, groupby):
		df1_hist = self.scenario.par(
			"historical_activity", {"technology": tecs, "node_loc": nodeloc}
		).rename({"value": "lvl"}, axis=1)
		df2_hist = (
			df2.groupby(
				["year_act", "technology", "mode", "node_loc", "commodity", "time"],
				as_index=False,
			)
			.mean(numeric_only=True)
			.drop(["year_vtg"], axis=1)
		)
		df_hist = self.multiply_df(df1_hist, "lvl", df2_hist, "value")
		df_hist = self.group(df_hist, ["year_act", groupby], "product", 0.0, None)
		return df_hist

	# A function for making model output in a compact way
	def model_output(self, tecs, nodeloc, parname, coms=None):
		df1 = self.scenario.var("ACT", {"technology": tecs, "node_loc": nodeloc})
		df2 = self.scenario.par(parname, {"technology": tecs, "node_loc": nodeloc})
		if coms:
			if isinstance(coms, str):
				coms = [coms]
			df2 = df2.loc[df2["commodity"].isin(coms)]
		df = self.multiply_df(df1, "lvl", df2, "value")
		return df, df2

	# A function for reordering the columns of a dataframe and leaving the rest
	def com_order(self, df, order):
		order = [x for x in order if x in df.columns]
		new_order = order + [x for x in set(df.columns) if x not in order]
		df = df.reindex(new_order, axis=1)
		return df

	# The main plotting function
	def plotter(
		self, case, nodeloc:list, path, yr_min, yr_max, plots="all", not_plots=[]
	) -> pd.DataFrame:
	 
		def make_tec_list(scenario, out_in, commodity=None, level=None, add_storage=False, offset=None):
			''''
			Creates a list of the technologies to be used in plotting
   			'''
	  
			if level is None:
				tecs_set = set(scenario.par(out_in, {"commodity": commodity}).technology)
			elif commodity is None:
				tecs_set = set(scenario.par(out_in, {"level": level}).technology)
			else:
				tecs_set = set(scenario.par(out_in, {"commodity": commodity,
					"level": level}).technology)
			
			if offset is not None:
				tecs_set -= offset
			tecs_list = list(tecs_set)
			
			if add_storage:
				return  tecs_list + ["stor_ppl"]
			else:
				return tecs_list 

		# 1) Initialization and importing required data
		cwd = os.getcwd()
		os.chdir(path)

		# Checking if the scenario has a solution
		if not self.scenario.has_solution():
			raise Exception("Submitted scenario has no solution to plot!")

		if not self.scenario.set("cat_year", {"type_year": "lastmodelyear"}).empty:
			last_yr = self.scenario.set("cat_year", {"type_year": "lastmodelyear"})[
				"year"
			].item()
		else:
			last_yr = max(self.scenario.set("year"))

		plotyrs = [
			int(i) for i in list(self.scenario.set("year")) if int(i) < int(last_yr)
		]
		yr = self.scenario.set("cat_year", {"type_year": "firstmodelyear"}).year.item()

		# 2) Reading and sorting solution data
		# A dictionary for saving all the results for plotting
		alldf = {}

		# 2.1) Power plant activity and capacity
		cap = self.scenario.var("CAP", {"year_vtg": plotyrs})
		cap_new = self.scenario.var("CAP_NEW", {"year_vtg": plotyrs})
		cap_hist = self.scenario.par("historical_new_capacity", {"year_vtg": plotyrs})

		tec = self.scenario.par(
			"output", {"commodity": "electr", "level": "secondary"}
		)["technology"]

		tec = tec.tolist() + ["stor_ppl"]
		# Power plant capacity
		ppl_cap = cap.loc[cap.technology.isin(tec)][["technology", "year_act", "lvl"]]
		ppl_cap = ppl_cap.groupby(["technology", "year_act"], as_index=False).sum()
		ppl_cap = ppl_cap.pivot(index="year_act", columns="technology")
		ppl_cap = ppl_cap[ppl_cap.columns[(ppl_cap != 0).any()]]
		ppl_cap.columns = ppl_cap.columns.droplevel(0)
		ppl_cap = ppl_cap.loc[:, (ppl_cap > 0).any()]

		# Power plant new capacity
		ppl_cap_new = cap_new.loc[(cap_new.technology.isin(tec)) & (cap_new.lvl > 0)][
			["technology", "year_vtg", "lvl"]
		]
		ppl_cap_new = pd.pivot_table(
			ppl_cap_new, index="year_vtg", columns="technology"
		).fillna(0)
		ppl_cap_new.columns = ppl_cap_new.columns.droplevel(0)

		# Power plant historical capacity
		ppl_cap_hist = cap_hist.loc[
			(cap_hist.technology.isin(tec)) & (cap_hist.value > 0)
		][["technology", "year_vtg", "value"]]
		ppl_cap_hist = pd.pivot_table(
			ppl_cap_hist, index="year_vtg", columns="technology"
		).fillna(0)
		ppl_cap_hist.columns = ppl_cap_hist.columns.droplevel(0)

		cap_new_tot = (ppl_cap_new.add(ppl_cap_hist, fill_value=0)).fillna(0)
		cap_new_tot = cap_new_tot[cap_new_tot.columns[(cap_new_tot > 0.001).any()]]

		# Power plant activity
		elec = self.plotdf(tec, ["electr"], "output", plotyrs, yr)

		# Treatment of storage losses
		if "stor_ppl" in elec.columns:
			d_stor = self.scenario.par("input", {"technology": "stor_ppl"})
			d_stor = d_stor.loc[d_stor["year_act"].isin(plotyrs)][
				["technology", "year_act", "value"]
			]
			d_stor = d_stor.groupby(["year_act"]).mean()
			elec["stor_ppl"] *= -d_stor["value"]
			elec.rename(self.renaming, axis=1, inplace=True)

		elec = self.mappings(plotyrs, elec, groupby="technology")
		ppl_cap = self.mappings(plotyrs, ppl_cap, groupby="technology")
		cap_new_tot = self.mappings(plotyrs, cap_new_tot, groupby="technology")

		alldf["Electricity generation " + self.unitname_el] = elec * self.unit_el
		alldf["Power plant capacity " + self.unitname_cap] = ppl_cap * self.unit_cap
		alldf["Power plant new capacity " + self.unitname_cap] = (
			cap_new_tot * self.unit_cap
		)

		# 2.2) Electricity usage

		tecs = make_tec_list(self.scenario,"input", "electr", "final", True)

		for current_node in nodeloc:
			# Prepration for Excel writings
			writer_xls = pd.ExcelWriter(f"{path}/{case}_{current_node}.xlsx", engine="xlsxwriter")

			df, df2 = self.model_output(tecs, current_node, "input", "electr")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)

			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (
				(df_hist + df)
				.fillna(0)
				.rename(
					{
						"sp_el_RC": "buildings",
						"sp_el_I": "industry",
						"elec_trp": "transport",
					},
					axis=1,
				)
			)
			alldf["Electricity use " + self.unitname_el] = df * self.unit_el

			# 2.3) Natural Gas supply (incl. import) and usage

			tecs = make_tec_list(self.scenario,"output", "gas")
			df, df2 = self.model_output(tecs, current_node, "output", "gas")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df_hist + df).fillna(0)
			alldf["Gas supply " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# Natural gas usage

			tecs = make_tec_list(self.scenario,"output", "gas", offset=set(self.gas_tecs))
			df, df2 = self.model_output(tecs, current_node, "input", "gas")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df_hist + df).fillna(0)
			alldf["Gas utilization " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# 2.4) Coal supply and utilization

			tecs = make_tec_list(self.scenario,"output", "coal", offset=set(self.coal_tecs["supply"]))
			df, df2 = self.model_output(tecs, current_node, "output", "coal")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Coal supply " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# Coal utilization

			tecs = make_tec_list(self.scenario,"input", "coal", offset=set(self.coal_tecs["utilization"]))
			df, df2 = self.model_output(tecs, current_node, "input", "coal")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Coal utilization " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# 2.5) Oil derivatives supply and use

			tecs = make_tec_list(self.scenario,"output", ["fueloil", "lightoil"], "secondary")

			df, df2 = self.model_output(
				tecs, current_node, "output", ["fueloil", "lightoil"]
			)
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Oil derivative supply " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# Oil derivatives utilisation
   		
			tecs = make_tec_list(self.scenario,"input",["fueloil", "lightoil"], offset=set(["loil_t_d", "foil_t_d"]))
			df, df2 = self.model_output(
				tecs, current_node, "input", ["fueloil", "lightoil"]
			)
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Oil derivative use " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# 2.6) Oil supply

			tecs = make_tec_list(self.scenario,"output",["crudeoil"], offset=set(["oil_bal", "oil_exp"]))
			df, df2 = self.model_output(tecs, current_node, "output", "crudeoil")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Oil supply " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# 2.7) Biomass provision

			tecs = make_tec_list(self.scenario,"output",["biomass"])
			df, df2 = self.model_output(tecs, current_node, "output")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Biomass supply " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# Biomass utilisation

			tecs = make_tec_list(self.scenario,"input",["biomass"],["primary", "final"], offset=set(["biomass_t_d"]))
			df, df2 = self.model_output(tecs, current_node, "input", "biomass")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = (df + df_hist).fillna(0)
			alldf["Biomass utilization " + self.unitname] = (
				self.mappings(plotyrs, df) * self.unitc
			)

			# 3) Sector related results
			# 3.1) Transport

			tecs = make_tec_list(self.scenario,"output",["transport"])
			df, df2 = self.model_output(tecs, current_node, "input")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Energy use: Transport " + self.unitname] = df * self.unitc

			# 3.2) Industry

			tecs = make_tec_list(self.scenario,"output",["i_spec", "i_therm"])
			df, df2 = self.model_output(tecs, current_node, "input")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Energy use: Industry " + self.unitname] = df * self.unitc

			# 3.3) Non-energy (feedstock) use in Industry

			tecs = make_tec_list(self.scenario,"output",["i_feed"])
			df, df2 = self.model_output(tecs, current_node, "input")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)

			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Non-energy use: Feedstock " + self.unitname] = df * self.unitc

			# 3.4) Residencial and commercial

			tecs = make_tec_list(self.scenario,"output",["rc_spec", "rc_therm", "non-comm"])
			df, df2 = self.model_output(tecs, current_node, "input")
			df = self.group(df, ["year_act", "technology"], "product", 0.0, yr)

			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "technology")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Energy use: Buildings " + self.unitname] = df * self.unitc

			# 4) Energy balances
			# 4.1) Primary energy : production + imports - exports

			tecs = make_tec_list(self.scenario,"output",level=["primary"])
			df, df2 = self.model_output(tecs, current_node, "output")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)

			# Renewables

			tecs = make_tec_list(self.scenario,"input",level=["renewable"])
			df_re, df2 = self.model_output(tecs, current_node, "input")
			df_re = self.group(df_re, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "commodity")
			df = df.add(
				self.com_order((df_hist + df_re).fillna(0), self.order), fill_value=0
			)

			# Import technologies
			tecs_imp = [
				x for x in set(self.scenario.set("technology")) if x.endswith("_imp")
			]
			df_imp, df2_imp = self.model_output(tecs_imp, current_node, "output")
			df_imp = self.group(df_imp, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs_imp, current_node, df2_imp, "commodity")
			df_imp = self.com_order((df_hist + df_imp).fillna(0), self.order)
			if not df_imp.empty:
				df = df.add(df_imp, fill_value=0)

				# Export technologies
			tecs_exp = [x for x in list(self.scenario.set("technology")) if "_exp" in x]
			df_exp, df2_exp = self.model_output(tecs_exp, current_node, "output")
			df_exp = self.group(df_exp, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs_exp, current_node, df2_exp, "commodity")
			df_exp = self.com_order((df_hist + df_exp).fillna(0), self.order)
			if not df_exp.empty:
				df = df.add(-df_exp, fill_value=0)

				# Production + import - exports
			alldf["Primary energy supply " + self.unitname] = (
				self.com_order(df, self.order) * self.unitc
			)

			# 4.2) Useful consumption

			tecs = make_tec_list(self.scenario,"output",level=["useful"])
			df, df2 = self.model_output(tecs, current_node, "output")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			alldf["Useful energy " + self.unitname] = df * self.unitc

			# 4.3) Final energy consumption
			# Final energy consumption by source

			tecs = make_tec_list(self.scenario,"output",level=["final"])
			df, df2 = self.model_output(tecs, current_node, "output")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Final energy consumption " + self.unitname] = df * self.unitc

			# 5) Energy trade
			# 5.1) Exports
			df, df2 = self.model_output(tecs_exp, current_node, "output")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs_exp, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Energy exports " + self.unitname] = df * self.unitc

			# 5.2) Imports
			df, df2 = self.model_output(tecs_imp, current_node, "output")
			df = self.group(df, ["year_act", "commodity"], "product", 0.0, yr)
			# adding historical data
			df_hist = self.add_history(tecs_imp, current_node, df2, "commodity")
			df = self.com_order((df_hist + df).fillna(0), self.order)
			alldf["Energy imports " + self.unitname] = df * self.unitc

			# 6) Emissions
			ems = ["TCE"]
			df1 = self.scenario.var("EMISS", {"emission": ems, "node": current_node})
			alldf["Total GHG emissions (MtCeq)"] = self.group(
				df1, ["year", "emission"], "lvl", 0.0, yr
			)

			# 7) Plotting

			plt.style.use("ggplot")

			# Setting tick width
			plt.rcParams["xtick.major.size"] = self.ticksz
			plt.rcParams["xtick.major.width"] = self.tickwdt
			plt.rcParams["ytick.major.size"] = self.ticksz
			plt.rcParams["ytick.major.width"] = self.tickwdt
			plt.rcParams["axes.linewidth"] = 0.1

			# Creating a pdf file for receiving the results
			# Selecting the plots to be plotted
			if plots != "all":
				keys = [
					x for x in self.dict_plot.keys() if any([y in x for y in plots])
				]
				self.dict_plot = {x: self.dict_plot[x] for x in keys}
			keys = [
				x for x in self.dict_plot.keys() if not any([y in x for y in not_plots])
			]
			self.dict_plot = {x: self.dict_plot[x] for x in keys}
			# Construct the full path using pathlib and the PDF filename format
			pdf_file_path = path+"/{}-msgResults.pdf".format(
				case + f"_{current_node}_" + time.strftime("%m.%d_%H.%M", time.localtime())
			)
			with PdfPages(pdf_file_path)as pdf:
				j = 0
				for subplt, item in self.dict_plot.items():
					df = alldf[subplt].copy()
					kind = item
					j = j + 1
					if df.empty:
						continue
					# Renaming
					df.rename(self.renaming, axis=1, inplace=True)

					# Adding up columns with the same name
					df = df.groupby(level=0, axis=1).sum()

					# Writing to Excel
					sh_name = (
						subplt.replace("[", "(").replace("]", ")").replace("/", "")
					)
					if len(sh_name.split(": ")) > 1:
						sh_name = sh_name.split(": ")[1]
					df.to_excel(writer_xls, sheet_name=sh_name)

					# Plotting
					fig = plt.figure(j)
					ax = fig.add_subplot(111)
					box = ax.get_position()

					if subplt in ["Power plant new capacity " + self.unitname_cap]:
						ax.set_position(
							[box.x0, box.y0, box.width * 0.8, box.height * 0.6]
						)
					else:
						df = df.loc[(df.index >= yr_min) & (df.index <= yr_max)]
						ax.set_position(
							[box.x0, box.y0, box.width * 0.6, box.height * 0.6]
						)

						# Removing those values lower than min data for plots
					df = df.loc[:, (df > max(df.max()) * self.min_val).any()]
					df = df.loc[:, (df > self.min_abs).any()]

					if df.empty:
						print(
							"> WARNING: There is no solution data in the selected"
							" years and limits to be plotted for {}!".format(subplt)
						)
						continue
					# indices = np.linspace(0, cmap.N, len(dfs.columns))
					# my_colors = [cmap(int(i)) for i in indices]
					my_colors = [self.color_map.get(x) for x in df.columns]
					my_colors = ["peru" if i == None else i for i in my_colors]
					df.index.name = None
					plt_title = f"{subplt} in {self.abbrev_prov[current_node]}"
					df.plot(
						ax=ax,
						kind=kind,
						stacked=True,
						color=my_colors,
						grid=None,
						title=plt_title,
						linewidth=self.lw,
						width=0.75,
					)

					# plt.ylabel(subplt, size=fntsz, color=fntcol)
					plt.title(plt_title, size=self.fntsz * 2, color=self.fntcol)
					handles, labels = ax.get_legend_handles_labels()

					plt.tick_params(axis="both", which="major", labelsize=self.fntsz)
					plt.grid(
						visible=True,
						which="both",
						linewidth=0.1,
						color="silver",
						linestyle="-",
					)
					ax.set_xticklabels(df.index, rotation=30)

					# Put a legend to the right of the current axis
					ax.legend(
						handles[::-1],
						labels[::-1],
						loc="center left",
						bbox_to_anchor=(1, 0.5),
						fontsize=self.fntsz * 1,
					)

					alldf[subplt] = df
					pdf.savefig()
					plt.show()
					plt.close()
			# Savig Excel file
			writer_xls.close()
		os.chdir(cwd)
		return alldf
