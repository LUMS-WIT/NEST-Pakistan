# -*- coding: utf-8 -*-
"""
This function imports historical new capacities from IIASA database

"""
import ixmp as ix
import pandas as pd
from colorama import Fore

def add_platts_capacity(msgSC, plattsName, nodeName, remove_tec=[]):

#%% 1) Making the mapping of technologies
    data_cat = 'New installed capacity'

    name_dict = {data_cat + '|Gas-fired power plant|Standard': 'gas_ct',
                 data_cat + '|Gas-fired power plant|Combined cycle': 'gas_cc',
                 data_cat + '|Gas-fired power plant|Heatplant': 'gas_hpl',
                 data_cat + '|Biomass-fired power plant|Standard': 'bio_ppl',
                 data_cat + '|Coal-fired power plant|Standard': 'coal_ppl',
                 data_cat + '|Coal-fired power plant|No abatement': 'coal_ppl_u',
                 data_cat + '|Fuel-oil power plant|Standard': 'foil_ppl',
                 data_cat + '|Fuel-oil power plant|Heatplant': 'foil_hpl',
                 data_cat + '|Light-oil power plant|Standard': 'loil_ppl',
                 data_cat + '|Light-oil power plant|Heatplant': 'loil_hpl',
                 data_cat + '|Light-oil power plant|Combined cycle': 'loil_cc',
                 data_cat + '|Hydro power plant|High cost': 'hydro_lc',
                 data_cat + '|Hydro power plant|Low cost': 'hydro_hc',     # Assuming the already installed hydro is mainly low cost (?)
                 data_cat + '|Nuclear power plant': 'nuc_lc',
                 data_cat + '|Solar PV': 'solar_pv_ppl',
                 data_cat + '|Wind turbine': 'wind_ppl',
                 data_cat + '|Municipal waste power plant': 'waste_ppl',
                 data_cat + '|Geothermal power plant': 'geo_ppl'}

#%% 2) Loading the data from database
 # Launching the IX modeling platform using the local default database
    mp = ix.Platform()
    #('CARMA', 'powerplant capacity data')
    data = ix.Scenario(mp, 'IIASA',
                       'historical powerplant capacity data').timeseries()
    df_region = data[(data['region'] == plattsName)]
    hist_cap = pd.DataFrame(columns=msgSC.par(
                            'historical_new_capacity').columns,
                            index=df_region.index)
    hist_cap['node_loc'] = nodeName
    hist_cap['unit'] = 'GW'
    for i in hist_cap.index:
        hist_cap.loc[i, 'technology'] = name_dict[df_region['variable'][i]]
        hist_cap.loc[i, 'value'] = df_region['value'][i] / 1000
        hist_cap.loc[i, 'year_vtg'] = df_region['year'][i]

    miss_tec = [x for x in set(hist_cap['technology'].tolist()
                               ) if x not in set(msgSC.set('technology'))]
    if miss_tec:
        print(Fore.RED +'> WARNING: There is data for {} in the database, but'
              ' these technologies are not present in the model!!'.format(miss_tec))
    # Removing extra technologies
    hist_cap = hist_cap.loc[~hist_cap['technology'].isin(remove_tec + miss_tec)]

#%% 3) Adding historical new capacity data and commiting it
    if hist_cap.empty:
        print(Fore.RED +'> WARNING: Power plant database has no data for' + str(plattsName) + ' !!')
    else:
        msgSC.check_out()
        msgSC.add_par('historical_new_capacity', hist_cap)
        msgSC.commit('Added historical new capacity from IIASA Database!')
        print(Fore.RESET + '> Historical vintage capacity data of "{}" imported'
              ' from Power Plant (CARMA) database!'.format(nodeName))
