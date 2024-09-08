"""
This function implements tax on GHG emissions post 2030  
"""

import pandas as pd
from itertools import product

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())], 
                       columns=dictionary.keys())


def tax_emissions(msgSDG, nodeName):
    
    year_df = [2035, 2040 ,2045 ,2050 ,2055 ,2060 ]
 
    
    dic = {
        'node': [nodeName],
        'type_emission':[str('TCE')],
        'type_tec':[str('all')],
        'type_year': [2035, 2040, 2045, 2050, 2055, 2060],
        'value': [ 30,30,30,30,30,30],# 34.78, 40.32, 46.74, 54.18,62.81],
        'unit':[str('USD/tCO2')]}
  
    df = expand_grid(dic)
    df = df.iloc[0:6]
    df['type_year'] = year_df
    msgSDG.add_par('tax_emission', df)
   
