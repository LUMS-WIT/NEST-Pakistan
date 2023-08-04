# -*- coding: utf-8 -*-
"""
This Script is use to adjust electricity generation values output from the model according
to the scope and governemt policies.

- Adjustment of electricity generation in baseline model
- Assume current energy system and governemt policies

"""
# Import required Libraries 
from message_ix import make_df

# Adjustment for coal power plant
def adjust_coal(scenario):

    # Adjust growth_activity_lo
    growth_coal_lo = scenario.par('growth_activity_lo')
    growth_coal_lo= growth_coal_lo[growth_coal_lo['technology'].str.contains('coal',regex = True)]
    scenario.remove_par('growth_activity_lo', growth_coal_lo)
    growth_coal_lo['value'] = growth_coal_lo['value'] * 10
    scenario.add_par('growth_activity_lo', growth_coal_lo)

    # Adjust growth_acitiviy_up - Coal_adv and coal_ppl
    growth_coal_up = scenario.par('growth_activity_up')
    coal_adv = growth_coal_up[growth_coal_up['technology'] == 'coal_adv']
    coal_ppl = growth_coal_up[growth_coal_up['technology'] == 'coal_ppl']
    coal_adv['value'] = coal_adv['value'] *1/100
    coal_ppl['value'] = 0.000800000000000001
    coal = coal_adv.append(coal_ppl)
    scenario.add_par('growth_activity_up', coal)

# Adjustment for bio power plant
def adjust_bio(scenario, years):

    # Adjust growth_activity_up
    growth_bio = make_df('growth_activity_up', node_loc = 'Pakistan', technology = 'bio_ppl'
                         , year_act = years, time = 'year', value = 0.05, unit = '-' )
    # Adjust intial_activity_up
    initial_bio = make_df('initial_activity_up', node_loc = 'Pakistan', technology = 'bio_ppl', 
                      year_act = years, time = 'year', value = 0.015, unit = 'GWa/a' )

    scenario.add_par('initial_activity_up', initial_bio)
    scenario.add_par('growth_activity_up', growth_bio)

# Adjustment for solar power plant
def adjust_solar(scenario, years):

    # minimize the gorwth of technologies which init due to putting constraint on solar_res1
    tec = ["solar_res2", "solar_res3", "solar_res4", "solar_res5", "solar_res6", "solar_res7",
           "solar_res8", "solar_res_hist_2020", "solar_res_hist_2015", "solar_res_hist_2010"]
    
    for i in tec:
        growth_solar = make_df('growth_activity_up',node_loc = 'Pakistan', technology = i, 
                             year_act = years, time = 'year', value = 0.005, unit = '-' )  
        scenario.add_par('growth_activity_up', growth_solar)

    # Adjust intial activity up for solar_res1
    initial_bio = make_df('initial_activity_up', node_loc = 'Pakistan', technology = 'solar_res1', 
                      year_act = years, time = 'year', value = 0.0185, unit = 'GWa/a' )
    scenario.add_par('initial_activity_up', initial_bio)

# Adjustment hydro power plant
def adjust_hydro(scenario, years):

    # adjust hydro_lc and hydro_hc
    tec = ["hydro_lc", "hydro_hc"]
    
    # loop over both technologies
    for i in tec:
        
        # Adjust growht_activity_up
        growth_hydro = make_df('growth_activity_up',node_loc = 'Pakistan', technology = i, 
                             year_act = years, time = 'year', value = 0.9, unit = '-' )  
        scenario.add_par('growth_activity_up', growth_hydro)
       
       # Adjust growht_activity_lo
        growth_hydro = make_df('growth_activity_lo',node_loc = 'Pakistan', technology = i, 
                             year_act = years, time = 'year', value = -0.001, unit = '-' )  
        scenario.add_par('growth_activity_lo', growth_hydro)

        # Adjust intial_activity_lo
        initial_hydro = make_df('initial_activity_up', node_loc = 'Pakistan', technology = i, 
                      year_act = years, time = 'year', value = 0.5, unit = 'GWa/a' )
        scenario.add_par('initial_activity_up', initial_hydro)

    # Remova initial_activity_lo form model
    initial_hydro = make_df('initial_activity_lo', node_loc = 'Pakistan', technology = "hydro_lc", 
                    year_act = years, time = 'year', value = 2, unit = 'GWa/a' )
    scenario.remove_par('initial_activity_lo', initial_hydro)

    # hydro_lc - intial_new_capacity_up
    initial_cap_up_hydro = make_df("initial_new_capacity_up", node_loc = 'Pakistan', technology = 'hydro_lc', 
                            year_vtg = years, value = 0.3, unit = 'GW/a' )
    scenario.add_par('initial_new_capacity_up', initial_cap_up_hydro)

    # hydro_lc - intial_new_capacity_lo
    initial_cap_lo_hydro = make_df("initial_new_capacity_lo", node_loc = 'Pakistan', technology = 'hydro_lc', 
                            year_vtg = years, value = 0.0005, unit = 'GW/a' )
    scenario.add_par('initial_new_capacity_lo', initial_cap_lo_hydro)

    # hydro_lc - growth_new_capacity_up
    growth_hydro = make_df("growth_new_capacity_up", node_loc = 'Pakistan', technology = 'hydro_lc', 
                      year_vtg = years, value = 0.3, unit = '-' )
    scenario.add_par('growth_new_capacity_up', growth_hydro)

    # hydro_lc - growth_new_capacity_lo
    growth_hydro = make_df("growth_new_capacity_lo", node_loc = 'Pakistan', technology = 'hydro_lc', 
                      year_vtg = years, value = -0.0005, unit = '-' )
    scenario.add_par('growth_new_capacity_lo', growth_hydro)

def adjust_wind(scenario, years):

    # minimize the gorwth of technologies which init due to putting constraint on wind_res1
    tec = ["wind_ref1", "wind_ref2", "wind_ref3", "wind_ref4", "wind_ref5", "wind_res2",
           "wind_res3", "wind_res4", "wind_res_hist_2005", "wind_res_hist_2010",
           "wind_res_hist_2015", "wind_res_hist_2020", "csp_sm3_res", "igcc"]
    
    for i in tec:
        growth_solar = make_df('growth_activity_up',node_loc = 'Pakistan', technology = i, 
                             year_act = years, time = 'year', value = 0.005, unit = '-' )  
        scenario.add_par('growth_activity_up', growth_solar)

    # Intial_activity_up - wind_res1
    initial_wind = make_df('initial_activity_up', node_loc = 'Pakistan', technology = 'wind_res1', 
                      year_act = years, time = 'year', value = 0.0652, unit = 'GWa/a' )
    scenario.add_par('initial_activity_up', initial_wind)

# Adjustment gas power plant
def adjust_gas(scenario, years):

    # adjust gas_cc and gas_ct
    tec = ["gas_cc", "gas_ct"]
    
    # loop over both technologies
    for i in tec:

    # Adjust growth_activity_up for gas_cc and gas_ct
        growth_gas = make_df('growth_activity_up', node_loc = 'Pakistan', technology = i, 
                      year_act = years, time = 'year', value = 0.01, unit = '-' )
        scenario.add_par('growth_activity_up', growth_gas)

        initial_gas = make_df('initial_activity_up', node_loc = 'Pakistan', technology = i, 
                      year_act = years, time = 'year', value = 0.0005, unit = 'GWa/a' )
        scenario.add_par('initial_activity_up', initial_gas)

    # Adjust growth_acitivy_up for gas_ppl
    initial_gas = make_df('initial_activity_up', node_loc = 'Pakistan', technology = 'gas_ppl', 
                      year_act = years, time = 'year', value = 0.05, unit = 'GWa/a' )
    scenario.add_par('initial_activity_up', initial_gas)

    growth_gas = make_df('growth_activity_up', node_loc = 'Pakistan', technology = 'gas_ppl', 
                      year_act = years, time = 'year', value = 0.17, unit = '-' )
    scenario.add_par('growth_activity_up', growth_gas)

# Adjustment nuclear power plant
def adjust_nuclear(scenario, years):

    # Set constraint on nuc_lc for growht_activity_up
    growth_nuc = make_df('growth_activity_up', node_loc = 'Pakistan', technology = 'nuc_lc', year_act = years, 
                   time = 'year', value = 0.5, unit = '-' )
    scenario.add_par('growth_activity_up', growth_nuc)

    # Set constraint on nuc_lc for growht_activity_lo
    growth_nuc = make_df('growth_activity_lo', node_loc = 'Pakistan', technology = 'nuc_lc', year_act = years, 
                   time = 'year', value = -0.00001, unit = '-' )
    scenario.add_par('growth_activity_lo', growth_nuc)

    # nuc_lc - intial_new_capacity_up
    initial_cap_lo_nuc = make_df("initial_new_capacity_lo", node_loc = 'Pakistan', technology = 'nuc_lc', 
                      year_vtg = years, value = 0.00001, unit = 'GW/a' )
    scenario.add_par('initial_new_capacity_lo', initial_cap_lo_nuc)

    # nuc_lc - growth_new_capacity_up
    growth_cap_lo_nuc = make_df("growth_new_capacity_lo", node_loc = 'Pakistan', technology = 'nuc_lc', 
                      year_vtg = years, value = -0.0005, unit = '-' )
    scenario.add_par('growth_new_capacity_lo', growth_cap_lo_nuc)

    initial_gas = make_df('initial_activity_lo', node_loc = 'Pakistan', technology = 'nuc_lc', 
                      year_act = years, time = 'year', value = 0.00005, unit = 'GWa/a' )
    scenario.add_par('initial_activity_lo', initial_gas)



def adjust_electricity(scenario):

    # Filter years from 2020-2050
    years = [x for x in scenario.set('year') if x >2015]
    
    # Run All functions to adjust values for all power plant
    adjust_hydro(scenario, years)
    print("-- Hydro Adjusted --")
    adjust_solar(scenario, years)
    print("-- Solar Adjusted --")
    adjust_bio(scenario, years)
    print("-- Bio Adjusted --")
    adjust_coal(scenario)
    print("-- Coal Adjusted --")
    adjust_wind(scenario, years)
    print("-- Wind Adjusted --")
    adjust_gas(scenario, years)
    print("-- Gas Adjusted --")
    adjust_nuclear(scenario, years)
    print("-- Nuclear Adjusted --")
    print("Great !! End")


    
