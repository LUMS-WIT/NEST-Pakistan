"""
This function bounds emissions in an extreme climate mitigation scenario 
"""

import pandas as pd
import numpy as np
import pycountry
from geotext import GeoText
from itertools import product

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())], 
                       columns=dictionary.keys())

def bound_emissions(msgSDG, nodeName):

    msgSDG.check_out()   
    
    year_df = [2025, 2030, 2035, 2040 ,2045 ,2050 ,2055 ,2060 ,2070]
 
    
    dic = {
        'node': [nodeName],
        'type_emission':[str('TCE')],
        'type_tec':[str('all')],
        'type_year': [2025, 2030, 2035, 2040 ,2045 ,2050 ,2055 ,2060 ,2070],
        'value': [100, 90, 72.79 , 50, 45, 40,35, 30, 30],
        'unit':[str('MtCO2')]}
  
    df = expand_grid(dic)
    df = df.iloc[0:9]
    df['type_year'] = year_df
    
    #msgSDG.add_par('bound_emission',df)
    msgSDG.add_par('bound_emission', df)
    msgSDG.commit('emissions bounded ')
   