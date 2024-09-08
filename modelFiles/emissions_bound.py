"""
This function bounds emissions in an extreme climate mitigation scenario 
"""


import pandas as pd
import numpy as np
#import pycountry
#from geotext import GeoText
from itertools import product

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())], 
                       columns=dictionary.keys())


def bound_emissions(msgSDG, nodeName):

    #msgSDG.check_out()   
    
    year_df = [2035, 2040, 2045 ,2050 ,2055 ,2060]
 
    
    dic = {
        'node': [nodeName],
        'type_emission':[str('TCE')],
        'type_tec':[str('all')],
        'type_year': [2035,2040,2045 ,2050 ,2055 ,2060],
        'value':     [120, 110, 100,  90,   80,  70],#, 59.0182956, 63.18147765,63.44854928,33.89831257, 33.10522112], 
        #'value': [43.761, 45.8525 , 50.251],
        'unit':[str('MtCO2')]}
  
    df = expand_grid(dic)
    df = df.iloc[0:6]
    df['type_year'] = year_df
    
    #msgSDG.add_par('bound_emission',df)
    msgSDG.add_par('bound_emission', df)
   
