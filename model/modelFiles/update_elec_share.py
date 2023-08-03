# -*- coding: utf-8 -*-
"""
This Script is use to adjust share of electricity generation technologies in model according to 
renewable or non-renewable resources. 

- Importing data for percentage of share from model files Parameters_messageix_pak excel file
- Make sure percetange of shares are added correctly in the excel file

"""
# Import required Libraries 
import pandas as pd
import numpy as np
from itertools import product

# add technology type in model for percetage of share
def new_tech_type_for_share(path, scenario, suffix):

    # add type_tec powerplants
    scenario.add_set('type_tec', 'powerplant')
    xl_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))
    sheet_tech = xl_set.parse('technology')
    df_tech1 = sheet_tech[sheet_tech['INCLUDE'] == 'y'].dropna(subset=['TECHNOLOGY'])
    # List of all powerplants technologies
    tec2 = list(set(df_tech1['TECHNOLOGY'][df_tech1['POWERPLANT'] == 'y']))

    # Add technology to powerplant list
    tec3 = ['coal_adv', 'foil_ppl', 'coal_adv_ccs']
    for i in tec3:
        tec2.append(str(i))

    # Remove technology from powerplant list
    tec4 = ['solar_th_ppl', 'solar_pv_I']
    for i in tec4:
        tec2.remove(str(i)) 

    scenario.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant','technology':tec2}))


def expand_grid(dictionary):
    return pd.DataFrame([row for row in product(*dictionary.values())], 
                        columns=dictionary.keys())

# Add percentage of shares
def shares(msgSDG, path, nodeName, suffix):
      
     # add type_tec for renewable
     type_tec = 'renewable_electr'
     msgSDG.add_set('type_tec', 'renewable_electr')
    
     # defining share for renewable
     shares = 'share_renew_electr'
     msgSDG.add_set('shares', 'share_renew_electr')
    
     # including technologies for which shares need to be defined
     tec = ('wind_res1','solar_res1','hydro_lc','hydro_hc', 'bio_ppl')
   
     # defining technologing in cateogry of technologies 
     msgSDG.add_set('cat_tec',pd.DataFrame({'type_tec':'renewable_electr','technology':tec}))
     # msgSDG.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant','technology':tec2}))
    
     # mapping total share from which share is intended 
     dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
            'type_tec': [str('powerplant')],
            'mode': [str('M1')],
            'commodity': [str('electr')],
            'level': [str('secondary')]}
     df = expand_grid(dic)
     msgSDG.add_set('map_shares_commodity_total', df)
        
     # mapping share from total 
     dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
            'type_tec': [type_tec],
            'mode': [str('M1')],
            'commodity': [str('electr')],
            'level': [str('secondary')]}
     df = expand_grid(dic)
     msgSDG.add_set('map_shares_commodity_share', df)
    
    
     # Importing required shares from excel files    
     xls_par = pd.ExcelFile(path + '/Parameters_messageix'+suffix+'.xlsx')
     sheet_shares = xls_par.parse('share_comodity_lo')
  
     msgSDG.add_par('share_commodity_lo', sheet_shares)

