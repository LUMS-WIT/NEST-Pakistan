"""
Unit correction for MESSAGEix-Pakistan scenario parameters.
"""

UNIT_DICT = {
    'demand': 'GWa/a',
    'resource_remaining': '-',
    'resource_volume': 'GWa',
    'technical_lifetime': 'year',
    'capacity_factor': '-',
    'min_utilization_factor': '-',
    'inv_cost': 'USD/kW',
    'fix_cost': 'USD/kW/a',
    'var_cost': 'USD/kW/a',
    'abs_cost_activity_soft_up': 'USD/kW/a',
    'abs_cost_activity_soft_lo': 'USD/kW/a',
    'level_cost_activity_soft_up': '-',
    'level_cost_activity_soft_lo': '-',
    'soft_activity_up': '-',
    'soft_activity_lo': '-',
    'resource_cost': 'USD/kW/a',
    'output': 'GWa',
    'input': 'GWa',
    'bound_new_capacity_up': 'GW/a',
    'bound_new_capacity_lo': 'GW/a',
    'bound_total_capacity_up': 'GW',
    'initial_new_capacity_up': 'GW/a',
    'initial_new_capacity_lo': 'GW/a',
    'growth_new_capacity_up': '-',
    'growth_new_capacity_lo': '-',
    'initial_activity_up': 'GWa/a',
    'initial_activity_lo': 'GWa/a',
    'growth_activity_up': '-',
    'growth_activity_lo': '-',
    'construction_time': 'year',
    'renewable_potential': 'GWa/a',
    'renewable_capacity_factor': '-',
    'reliability_factor': '-',
    'peak_load_factor': '-',
    'flexibility_factor': '-',
    'rating_bin': '-',
    'emission_scaling': '-',
    'relation_cost': 'USD/kW/a',
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
    'prfconst': '-',
    'price_MESSAGE': 'USD/kW/a',
}


def unit_correction(mp, scenario):
    """Apply standardised units to all parameters in *scenario*.

    Note: after this correction, old reporting scripts may raise errors.
    """
    print('Applying unit corrections...')
    scenario.check_out()
    print('Corrected units for:')
    for param, unit in UNIT_DICT.items():
        if param in scenario.par_list():
            _par = scenario.par(param)
            if not _par.empty:
                if unit not in mp.units():
                    mp.add_unit(unit)
                _par = _par.assign(unit=unit)
                scenario.add_par(param, _par)
                print(f'  {param}')
    scenario.commit('update units')
    print('Unit correction complete.')
