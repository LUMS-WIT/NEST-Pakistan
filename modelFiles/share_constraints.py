# -*- coding: utf-8 -*-
"""
This function add share of different constraints technologies 

"""

import pandas as pd
import numpy as np
import pycountry
from geotext import GeoText
from itertools import product

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())], 
                       columns=dictionary.keys())

def shares(msgSDG, path, nodeName, suffix):

    msgSDG.check_out()   
    # add type_tec for renewable
    type_tec = 'renewable_electr'
    msgSDG.add_set('type_tec', 'renewable_electr')
    
    # defining share for renewable
    shares = 'share_renew_electr'
    msgSDG.add_set('shares', 'share_renew_electr')
    
    # including technologies for which shares need to be defined
    tec = ('wind_ppf','wind_ppl','solar_pv_ppl','solar_th_ppl','hydro_lc','hydro_hc')

    #tec = ('hydro_lc','hydro_hc')
   
    # defining technologing in cateogry of technologies 
    msgSDG.add_set('cat_tec',pd.DataFrame({'type_tec':'renewable_electr','technology':tec}))
    
    # mapping total share from which share is intended 
    dic = {
            'shares': [shares],
            'node_share': [nodeName],
            'node': [nodeName],
        #     'type_tec': [str('powerplant')],
            'type_tec': [type_tec],
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
    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    sheet_shares = xls_par.parse('share_comodity_lo')
  
    msgSDG.add_par('share_commodity_lo', sheet_shares)

    print("Added Shares")

    #msgSDG.commit('renewable shares defined')
    #todo: Check this which level I need to get a share, usually electricity , good level is secondary 
    # 
