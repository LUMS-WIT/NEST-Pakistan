# Import required Libraries 
from message_ix import make_df

# Adjustment for elec transport
def adjust_elec(scenario,years):
    # Adjust growth_activity_up
    growth_elec = make_df('growth_activity_up', node_loc = 'Pakistan', technology = 'elec_trp'
                         , year_act = years, time = 'year', value = 0.8, unit = '-' )
    # Adjust intial_activity_up
    initial_elec = make_df('initial_activity_up', node_loc = 'Pakistan', technology = 'elec_trp', 
                      year_act = years, time = 'year', value = 0.1, unit = 'GWa/a' )

    scenario.add_par('initial_activity_up', initial_elec)
    scenario.add_par('growth_activity_up', growth_elec)
def adjust_eth(scenario,years):
    # Adjust growth_activity_up
    growth_eth = make_df('growth_activity_up', node_loc = 'Pakistan', technology = 'eth_ic_trp'
                         , year_act = years, time = 'year', value = 0.000001, unit = '-' )
    # Adjust intial_activity_up
    initial_eth = make_df('initial_activity_up', node_loc = 'Pakistan', technology = 'eth_ic_trp', 
                      year_act = years, time = 'year', value = 0.000015, unit = 'GWa/a' )

    scenario.add_par('initial_activity_up', initial_eth)
    scenario.add_par('growth_activity_up', growth_eth)
    
def adjust_transport(scenario):

    # Filter years from 2020-2050
    years = [x for x in scenario.set('year') if x >2015]
    
    # Run All functions to adjust values for all power plant
    adjust_elec(scenario, years)
    adjust_eth(scenario, years)

    print("-- Hydro Adjusted --")