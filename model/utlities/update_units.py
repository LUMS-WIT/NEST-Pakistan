'''
This script uniforms the units'
'''


def unit_correction(mp, msgSC):

    print(' Notice: after this unit correction, you will have erorrs/issues'
          ' if you use "old reporting" scripts!')
    unit_dict = {'demand': 'GWa/a',
                 'resource_remaining': '-',
                 'resource_volume': 'GWa',
                 'technical_lifetime': 'year',
                 'capacity_factor': '-',
                 'min_utilization_factor': '-',
                 'inv_cost': 'USD/kW',
                 'fix_cost': 'USD/kW',
                 'var_cost': 'USD/kW',
                 'abs_cost_activity_soft_up': 'USD/kW',
                 'abs_cost_activity_soft_lo': 'USD/kW',
                 'level_cost_activity_soft_up': '-',
                 'level_cost_activity_soft_lo': '-',
                 'soft_activity_up': '-',
                 'soft_activity_lo': '-',
                 'resource_cost': 'USD/kW',
                 'output': 'GWa',
                 'input': 'GWa',
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
                 # 'emission_factor': 'MtCO2eq/GWa',
                 'construction_time': 'year',
                 'renewable_potential': 'GWa/a',
                 'renewable_capacity_factor': '-',
                 'reliability_factor': '-',
                 'peak_load_factor': '-',
                 'flexibility_factor': '-',
                 'rating_bin': '-',
                 'emission_scaling': '-',
                 # 'tax_emission': 'USD/tCO2',
                 'relation_cost': 'USD/kW',
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
                 # 'p_ref': '-',
                 'prfconst': '-',
                 'price_MESSAGE': 'USD/kW'
                 }

    msgSC.check_out()
    print('- Unit was corrected for:')
    for p in unit_dict.keys():
        if p in msgSC.par_list():
            _par = msgSC.par(p)
            if not _par.empty:
                if not unit_dict[p] in mp.units():
                    mp.add_unit(unit_dict[p])
                _par = _par.assign(unit=unit_dict[p])
                msgSC.add_par(p, _par)
                print(p)
    msgSC.commit('update units')
    print('- Units were corrected.')