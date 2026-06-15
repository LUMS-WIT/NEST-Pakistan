import os

# Set GAMS path
os.environ["PATH"] += os.pathsep + r"C:\GAMS\50"

# Optional: print to verify
print("✅ GAMS path added:", os.environ["PATH"])


import ixmp

mp = ixmp.Platform()


import message_ix

scenario = message_ix.Scenario(
    mp, model="Westeros Electrified", scenario="baseline", version="new"
)

history = [690]
model_horizon = [700, 710, 720]
scenario.add_horizon(year=history + model_horizon, firstmodelyear=model_horizon[0])

country = "Westeros"
scenario.add_spatial_sets({"country": country})

scenario.add_set("commodity", ["electricity", "light"])
scenario.add_set("level", ["secondary", "final", "useful"])
scenario.add_set("technology", ["coal_ppl", "wind_ppl", "grid", "bulb"])
scenario.add_set("mode", "standard")

"""##Building Sypply and Demand for Enery"""

import pandas as pd

gdp_profile = pd.Series([1.0, 1.5, 1.9], index=pd.Index(model_horizon, name="Time"))
gdp_profile.plot(title="GDP profile")

"""##Building demand model - All parameter are in format used by messagix"""

demand_per_year = 40 * 12 * 1000 / 8760
light_demand = pd.DataFrame(
    {
        "node": country,
        "commodity": "light",
        "level": "useful",
        "year": model_horizon,
        "time": "year",
        "value": (demand_per_year * gdp_profile).round(),
        "unit": "GWa",
    }
)

light_demand

# We use `add_par` for adding data to a MESSAGEix parameter
scenario.add_par("demand", light_demand)

light_demand

"""##define the technical_lifetime of technologies."""

from message_ix import make_df

# Define technical lifetime in years
lifetime = {
    "coal_ppl": 20,
    "wind_ppl": 20,
    "bulb": 1,
    "grid": 30,
}

for tec, val in lifetime.items():
    df = make_df(
        "technical_lifetime",
        node_loc=country,
        year_vtg=history + model_horizon,
        unit="y",
        technology=tec,
        value=val,
    )
    scenario.add_par("technical_lifetime", df)

# Let's see the content
scenario.par("technical_lifetime")

"""##Here we are parametrizing bulb on on final stage and going reverse"""

year_df = scenario.vintage_and_active_years((country, "bulb"), in_horizon=False)
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

# Some common values to be used for both the "input" and "output" parameters
base = dict(
    node_loc=country,
    year_vtg=vintage_years,
    year_act=act_years,
    technology="bulb",
    mode="standard",
    time="year",
    unit="-",
)

# Use the message_ix utility function make_df() to create a base data frame for
# different "input" parameter values
base_input = make_df("input", **base, node_origin=country, time_origin="year")

# Create a base data frame for different "output" parameter values
base_output = make_df("output", **base, node_dest=country, time_dest="year")

# Extend `base_output` by filling in some of the other columns, using the
# pandas.DataFrame.assign() method
bulb_out = base_output.assign(commodity="light", level="useful", value=1.0)
scenario.add_par("output", bulb_out)

bulb_in = base_input.assign(commodity="electricity", level="final", value=1.0)
scenario.add_par("input", bulb_in)

scenario.idx_names("input")

"""##Next, we parameterize the electrical "grid"
"""

grid_efficiency = 0.9
year_df = scenario.vintage_and_active_years((country, "grid"), in_horizon=False)
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

base.update(
    year_vtg=vintage_years,
    year_act=act_years,
    technology="grid",
    commodity="electricity",
    level="final",
    value=1.0,
)
grid_out = make_df("output", **base, node_dest=country, time_dest="year")
scenario.add_par("output", grid_out)

base.update(commodity="electricity", level="secondary", value=1.0 / grid_efficiency)
grid_in = make_df("input", **base, node_origin=country, time_origin="year")
scenario.add_par("input", grid_in)

"""##Now power plants"""

year_df = scenario.vintage_and_active_years((country, "coal_ppl"), in_horizon=False)
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

base.update(
    year_vtg=vintage_years,
    year_act=act_years,
    technology="coal_ppl",
    commodity="electricity",
    level="secondary",
    value=1.0,
)
coal_out = make_df("output", **base, node_dest=country, time_dest="year")
scenario.add_par("output", coal_out)

year_df = scenario.vintage_and_active_years((country, "wind_ppl"), in_horizon=False)
vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
base.update(
    year_vtg=vintage_years,
    year_act=act_years,
    technology="wind_ppl",
    commodity="electricity",
    level="secondary",
    value=1.0,
)
wind_out = make_df("output", **base, node_dest=country, time_dest="year")
scenario.add_par("output", wind_out)

"""##Operational Constraints, specifically capacity factor"""

capacity_factor = {
    "coal_ppl": 1,
    "wind_ppl": 0.36,
    "bulb": 1,
    "grid": 1,
}

for tec, val in capacity_factor.items():
    year_df = scenario.vintage_and_active_years((country, tec), in_horizon=False)
    df = make_df(
        "capacity_factor",
        node_loc=country,
        year_vtg=year_df["year_vtg"],
        year_act=year_df["year_act"],
        time="year",
        unit="-",
        technology=tec,
        value=val,
    )
    scenario.add_par("capacity_factor", df)

"""##growth activity up mode for diffusion constrained - prediction of a technology that how long it will survive

##Note: No new energy can be spreaded in a day\

"""

growth_technologies = [
    "coal_ppl",
    "wind_ppl",
]

for tec in growth_technologies:
    df = make_df(
        "growth_activity_up",
        node_loc=country,
        year_act=model_horizon,
        time="year",
        unit="-",
        technology=tec,
        value=0.1,
    )
    scenario.add_par("growth_activity_up", df)

"""##Energy mix during demand - "historical_activity" and "historical_new_capacity" required"""

historic_demand = 0.5 * demand_per_year
historic_generation = historic_demand / grid_efficiency
coal_fraction = 0.6

old_activity = {
    "coal_ppl": coal_fraction * historic_generation,
    "wind_ppl": (1 - coal_fraction) * historic_generation,
    "grid": historic_generation,
}

for tec, val in old_activity.items():
    df = make_df(
        "historical_activity",
        node_loc=country,
        year_act=history,
        mode="standard",
        time="year",
        unit="GWa",
        technology=tec,
        value=val,
    )
    scenario.add_par("historical_activity", df)

mp.add_unit("GW/y")
for tec in old_activity:
    value = old_activity[tec] / (1 * 10 * capacity_factor[tec])  #New capacity formula
    df = make_df(
        "historical_new_capacity",
        node_loc=country,
        year_vtg=history,
        unit="GW/y",
        technology=tec,
        value=value,
    )
    scenario.add_par("historical_new_capacity", df)

"""##Working on objective function - Costs"""

scenario.add_par("interestrate", model_horizon, value=0.05, unit="-")

#Investment costs
# Add a new unit for ixmp to recognize as valid
mp.add_unit("USD/kW")

# in $ / kW (specific investment cost)
costs = {
    "coal_ppl": 500,
    "wind_ppl": 1500,
    "bulb": 5,
    "grid": 800,
}

for tec, val in costs.items():
    df = make_df(
        "inv_cost",
        node_loc=country,
        year_vtg=model_horizon,
        unit="USD/kW",
        technology=tec,
        value=val,
    )
    scenario.add_par("inv_cost", df)

"""##Fixed OM Costs - This formulation allows to include the potential cost savings from early retirement of installed capacity."""

# in $ / kW / year (every year a fixed quantity is destinated to cover part of the O&M
# costs based on the size of the plant, e.g. lighting, labor, scheduled maintenance,
# etc.)

costs = {
    "coal_ppl": 30,
    "wind_ppl": 10,
    "grid": 16,
}

for tec, val in costs.items():
    year_df = scenario.vintage_and_active_years((country, tec), in_horizon=False)
    df = make_df(
        "fix_cost",
        node_loc=country,
        year_vtg=year_df["year_vtg"],
        year_act=year_df["year_act"],
        unit="USD/kWa",
        technology=tec,
        value=val,
    )
    scenario.add_par("fix_cost", df)

"""##Variable O&M Costs"""

# In $ / kWa (costs associated with the degradation of equipment
# when the plant is functioning per unit of energy produced
# kW·year = 8760 kWh. Therefore the costs represents USD per 8760 kWh
# of energy). Do not confuse with fixed O&M units.

costs = {
    "coal_ppl": 30,
}

for tec, val in costs.items():
    year_df = scenario.vintage_and_active_years((country, tec), in_horizon=False)
    df = make_df(
        "var_cost",
        node_loc=country,
        year_vtg=year_df["year_vtg"],
        year_act=year_df["year_act"],
        mode="standard",
        time="year",
        unit="USD/kWa",
        technology=tec,
        value=val,
    )
    scenario.add_par("var_cost", df)

def get_scenario():
    return scenario

