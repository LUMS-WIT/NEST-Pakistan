# -*- coding: utf-8 -*-
"""
This function adds resource constraints from the data 

"""
import ixmp as ix
import pandas as pd
import numpy as np
import pycountry
from geotext import GeoText
from itertools import product

def resource_constraints(msgSC, msgWSC, path, nodeName, regionName, iso):
    

    ### Step 1: add the oil, gas and coal resource volumes
    
    # Oil reserves estimated for 2017 from BP Statistical Review 2018
    oil_df = pd.read_excel(
        str(path) + str('/') + str('bp_stats_review_2018_all_data.xlsx'), 
        'Oil - Proved reserves history', 
        header = 2,
        skip_blank_lines = True)
    oil_df = oil_df.dropna()
    oil_df = oil_df[['Thousand million barrels',2017]]   
    oil_df['units'] = str('Thousand million barrels')  
    oil_df['country'] = oil_df['Thousand million barrels']
    oil_df['reserves'] = oil_df[2017]
    oil_df = oil_df[['country','reserves','units']]
    for j in oil_df.index:
        places = list( GeoText(oil_df['country'][j]).country_mentions.keys() )
        if places:
            places = places[0]
            places = pycountry.countries.get(alpha_2=places)
            places = places.alpha_3
        else:
            places = float('NaN') 
        if oil_df['country'][j] == 'Papua New Guinea':
            places = 'PNG'
        oil_df['country'][j] = places
    oil_df = oil_df.dropna()
    
    # Coal reserves estimated for 2017 from BP statistical review 2018
    coal_df = pd.read_excel(
        str(path) + str('/') + str('bp_stats_review_2018_all_data.xlsx'), 
        'Coal - Reserves', 
        header = 3,
        skip_blank_lines = True)
    coal_df = coal_df.dropna()
    coal_df = coal_df[['Million tonnes','and bituminous','and lignite']]   
    coal_df['units'] = str('Million tonnes')  
    coal_df['country'] = coal_df['Million tonnes']
    coal_df['reserves1'] = coal_df['and bituminous']
    coal_df['reserves2'] = coal_df['and lignite']
    coal_df = coal_df[['country','reserves1','reserves2','units']]
    for j in coal_df.index:
        places = list( GeoText(coal_df['country'][j]).country_mentions.keys() )
        if places:
            places = places[0]
            places = pycountry.countries.get(alpha_2=places)
            places = places.alpha_3
        else:
            places = float('NaN') 
        if coal_df['country'][j] == 'Papua New Guinea':
            places = 'PNG'
        coal_df['country'][j] = places
    coal_df = coal_df.dropna()
    lignite_df = coal_df[['country','reserves1','units']]
    lignite_df.columns=['country','reserves','units']
    coal_df = coal_df[['country','reserves1','units']]
    coal_df.columns=['country','reserves','units']
    
    # Natural gas reserves for 2017 from bp statistical review 2018
    gas_df = pd.read_excel(
        str(path) + str('/') + str('bp_stats_review_2018_all_data.xlsx'), 
        'Gas - Proved reserves history ', 
        header = 2,
        skip_blank_lines = True)
    gas_df = gas_df.dropna()
    gas_df = gas_df[['Trillion cubic metres',2017]]   
    gas_df['units'] = str('Trillion cubic metres')  
    gas_df['country'] = gas_df['Trillion cubic metres']
    gas_df['reserves'] = gas_df[2017]
    gas_df = gas_df[['country','reserves','units']]
    for j in gas_df.index:
        places = list( GeoText(gas_df['country'][j]).country_mentions.keys() )
        if places:
            places = places[0]
            places = pycountry.countries.get(alpha_2=places)
            places = places.alpha_3
        else:
            places = float('NaN') 
        if gas_df['country'][j] == 'Papua New Guinea':
            places = 'PNG'
        gas_df['country'][j] = places
    gas_df = gas_df.dropna()
    
    # Copy the existing resource volume settings from the global model
    parname = 'resource_volume'
    par_res = msgWSC.par(parname, {'node':regionName})       # BZ: taking the data of the respective region from global MESSAGE
    par_new = par_res.copy()
    par_new.index = zip(par_new['commodity'],par_new['grade'])
    # loop through the resourve volumes and multiple by the fraction estimated from the historical data
    for i in par_new.index:
        
        if str('crude') in str(par_new['commodity'][i]):
            df = oil_df
        elif str('coal') in str(par_new['commodity'][i]):
            df = coal_df
        elif str('lignite') in str(par_new['commodity'][i]):
            df = lignite_df
        elif str('gas') in str(par_new['commodity'][i]): 
            df = gas_df
        
        # country potential
        ccc = df[df['country'] == iso]
        if not ccc.empty:
            ccc = ccc['reserves'].values[0]
        else:
            ccc = 0
        
        # region potential
        reg_df = pd.read_excel( str(path) + str('/') + str('iso_reg.xlsx'), 'Sheet1')
        reg_df['node'] = str('R14_') + reg_df['node'].astype(str) 
        isoreg = reg_df[reg_df['node']==regionName]
        isoreg = isoreg['iso'].tolist()
        rrr = df[df.country.isin(isoreg)]
        if rrr.empty:
            rrr = 0
        else:
            rrr = rrr['reserves'].sum()
        # fraction
        if ccc > 0:
            frac = ccc / rrr
        else:    
            frac = 0
        par_new['value'][i] = par_new['value'][i] * frac
    
    # reset node name to match the country
    par_new['node'] = nodeName
    par_new = par_new.dropna(axis=0, how='any', thresh=None, subset=['value'])
    par_new.index = range(0, len(par_new))
    
    # make sure all commodities initialized in the model
    res_cmdty = par_new['commodity'].unique()
    exs_cmdty = msgSC.set('commodity')
    for j in res_cmdty:
        if str(j) not in str(exs_cmdty):
            msgSC.add_set('commodity', j)
    
    # add the fossil resource volume parameter to the model
    msgSC.add_set('grade', list(par_new.grade.unique()))
    msgSC.add_par('resource_volume', par_new)
    
    # fossil resource costs
    par_name = 'resource_cost'
    
    # par_new = msgWSC.par(par_name, {
    #     'node':regionName,
    #     'commodity':res_cmdty})
    # par_new['node'] = iso
    # par_new = par_new.dropna(axis=0, how='any', thresh=None, subset=['value'])
    # par_new.index = range(0, len(par_new))
    # par_new['node'] = par_new['node'].str.replace('PAK',nodeName)
    # msgSC.add_par(par_name, par_new)
    
    #
    # add the ISO country code
