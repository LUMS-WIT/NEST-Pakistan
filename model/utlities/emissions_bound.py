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
 
    nodeName = 'your_node_name_here'  # Replace with the actual node name

    dic = {
        'node': [nodeName],
        'type_emission': [str('TCE')],
        'type_tec': [str('all')],
        'type_year': [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060],
        'value': [
            66000000000,
            63000000000,
            60000000000,
            58000000000,
            57000000000,
            57000000000,
            57000000000,
            57000000000
        ],
        'unit': [str('MtCO2')]
    }

  
    df = expand_grid(dic)
    df = df.iloc[0:9]
    df['type_year'] = year_df
    
    #msgSDG.add_par('bound_emission',df)
    msgSDG.add_par('bound_emission', df)
    msgSDG.commit('emissions bounded ')
   