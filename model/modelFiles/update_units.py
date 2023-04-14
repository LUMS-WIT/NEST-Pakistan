'''
This script uniforms the units'
'''


def unit_correction(mp, msgSC):

    par_list = msgSC.par_list()

    unit_dict = {'demand': 'GWa/a',
                 'level_cost_new_capacity_soft_up': '-',
                 'bound_extraction_up': '???',
                 'relation_new_capacity': '???',
                 'relation_total_capacity': '???',
                 'soft_new_capacity_up': '???',
                 'resource_remaining': '-',
                 'resource_volume': 'GWa',
                 'technical_lifetime': 'year',
                 'capacity_factor': '-',
                 'min_utilization_factor': '-',
                 'inv_cost': 'USD',
                 'fix_cost': 'USD',
                 'var_cost': 'USD',
                 'output': '-',
                 'input': '-',
                 'bound_new_capacity_up': 'GW/a',
                 'bound_new_capacity_lo': 'GW/a',
                 'bound_total_capacity_up': 'GW',
                 'bound_activity_up': 'GWa/a',
                 'bound_activity_lo': 'GWa/a',
                 'initial_new_capacity_up': 'GW/a',
                 'initial_new_capacity_lo': 'GW/a',
                 'growth_new_capacity_up': '-',
                 'growth_new_capacity_lo': '-',
                 'initial_activity_up': 'GWa/a',
                 'initial_activity_lo': 'GWa/a',
                 'growth_activity_up': '-',
                 'growth_activity_lo': '-',
                 'emission_factor': 'MtCO2eq/GWa',
                 'construction_time': 'year',
                 'renewable_potential': 'GWa/a',
                 'renewable_capacity_factor': '-',
                 'reliability_factor': '-',
                 'peak_load_factor': '-',
                 'flexibility_factor': '-',
                 'rating_bin': '-',
                 'emission_scaling': '-',
                 'tax_emission': 'USD/tCO2',
                 'relation_cost': 'USD',
                 'resource_cost': 'USD',
                 'relation_activity': 'GWa/a',
                 'duration_period': 'year',
                 'duration_time': '-',
                 'interestrate': '-',
                 'historical_new_capacity': 'GW/a',
                 'historical_activity': 'GWa/a',
                 'historical_gdp': 'TUSD',
                 'MERtoPPP': '-',
                 'aeei': '-',
                 'cost_MESSAGE': 'MUSD/a',
                 'demand_MESSAGE': 'GWa/a',
                 'depr': '-',
                 'drate': '-',
                 'esub': '-',
                 'gdp_calibrate': 'TUSD',
                 'grow': '-',
                 'kgdp': '-',
                 'kpvs': '-',
                 'lakl': '-',
                 'lotol': '-',
                 'p_ref': '-',
                 'prfconst': '-',
                 'price_MESSAGE': 'USD',
                 'abs_cost_activity_soft_up': '-',
                 'abs_cost_activity_soft_lo': '-',
                 'level_cost_activity_soft_lo': '-',
                 'level_cost_activity_soft_up': '-',
                 'soft_activity_up' : '-',
                 'soft_activity_lo' : '-',
                 'emission_factor' : '-',
                 'relation_upper' : '-',
                 'relation_lower' : '-',
                 }

    msgSC.check_out()
    for p in par_list:
        _par = msgSC.par(p)
        if not _par.empty:
            if not unit_dict[p] in mp.units():
                mp.add_unit(unit_dict[p])
            _par = _par.assign(unit=unit_dict[p])
            msgSC.add_par(p, _par)
    #msgSC.commit('update units')

    #msgSC.solve(model='MESSAGE-MACRO')
    print('- Units were corrected.')