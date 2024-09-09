# -*- coding: utf-8 -*-
"""
This Script is use to adjust share of transport technologies in model 
- Importing data for percentage of share from model files Parameters_messageix_pak excel file
- Make sure percetange of shares are added correctly in the excel file

"""
# Import required Libraries 
import pandas as pd
import numpy as np
from itertools import product

# add technology type in model for percetage of share
def new_tech_type_for_transport_share(path, scenario, suffix):

    # add type_tec powerplants
    scenario.add_set('type_tec', 'transport')
    xl_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))
    sheet_tech = xl_set.parse('technology')
    df_tech1 = sheet_tech[sheet_tech['INCLUDE'] == 'y'].dropna(subset=['TECHNOLOGY'])
    # List of all powerplants technologies
    tec2 = list(set(df_tech1['TECHNOLOGY'][df_tech1['OUTPUT'] == 'transport']))
    #technologies in this category include:
    #['eth_fc_trp', 'loil_trp', 'elec_trp', 'coal_trp', 'eth_ic_trp', 'h2_fc_trp', 'meth_ic_trp', 'meth_fc_trp', 'foil_trp', 'gas_trp']

    # Remove technology from transport list
    tec4 = ['h2_fc_trp','meth_ic_trp','meth_fc_trp']
    for i in tec4:
        tec2.remove(str(i)) 

    scenario.add_set('cat_tec',pd.DataFrame({'type_tec':'transport','technology':tec2}))
    print(tec2)

def expand_grid(dictionary):
    return pd.DataFrame([row for row in product(*dictionary.values())], 
                        columns=dictionary.keys())


# Add percentage of shares
def shares_elec_trp(msgSDG, path, nodeName, suffix):
      
     # add type_tec for transport
     type_tec = 'transport'
     msgSDG.add_set('type_tec', 'transport')
    
     # defining share for transport
     shares = 'share_elec_trp'
     msgSDG.add_set('shares', 'share_elec_trp')
    
     # including technologies for which shares need to be defined
     tec = ['elec_trp']
   
     # defining technologing in cateogry of technologies 
     msgSDG.add_set('cat_tec',pd.DataFrame({'type_tec':'transport','technology':tec}))
    
     # mapping total share from which share is intended 
     dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
            'type_tec': [str('transport')],
            'mode': [str('M1')],
            'commodity': [str('transport')],
            'level': [str('useful')]}
     df = expand_grid(dic)
     msgSDG.add_set('map_shares_commodity_total', df)
        
     # mapping share from total 
     dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
            'type_tec': [type_tec],
            'mode': [str('M1')],
            'commodity': [str('transport')],
            'level': [str('useful')]}
     df = expand_grid(dic)
     msgSDG.add_set('map_shares_commodity_share', df)
    
    
     # Importing required shares from excel files    
     xls_par = pd.ExcelFile(path + '/Parameters_messageix'+suffix+'.xlsx')
     sheet_shares = xls_par.parse('share_comodity_lo_trp')
  
     msgSDG.add_par('share_commodity_lo', sheet_shares)

def shares_eth_trp(msgSDG, path, nodeName, suffix):
      
     # add type_tec for transport
     type_tec = 'transport'
     msgSDG.add_set('type_tec', 'transport')
    
     # defining share for transport
     shares = 'share_eth_trp'
     msgSDG.add_set('shares', 'share_eth_trp')
    
     # including technologies for which shares need to be defined
     tec = ('eth_fc_trp','eth_ic_trp')
   
     # defining technologing in cateogry of technologies 
     msgSDG.add_set('cat_tec',pd.DataFrame({'type_tec':'transport','technology':tec}))
    
     # mapping total share from which share is intended 
     dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
            'type_tec': [str('transport')],
            'mode': [str('M1')],
            'commodity': [str('transport')],
            'level': [str('useful')]}
     df = expand_grid(dic)
     msgSDG.add_set('map_shares_commodity_total', df)
        
     # mapping share from total 
     dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
            'type_tec': [type_tec],
            'mode': [str('M1')],
            'commodity': [str('transport')],
            'level': [str('useful')]}
     df = expand_grid(dic)
     msgSDG.add_set('map_shares_commodity_share', df)
    
    
     # Importing required shares from excel files    
     xls_par = pd.ExcelFile(path + '/Parameters_messageix'+suffix+'.xlsx')
     sheet_shares = xls_par.parse('share_comodity_lo_ethtrp')
  
     msgSDG.add_par('share_commodity_lo', sheet_shares)
