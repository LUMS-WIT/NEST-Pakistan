<<<<<<< HEAD:model/modelFiles/Update_historical_activity.py
# -*- coding: utf-8 -*-
"""
This Script is use to update historical activity data based on the new demand updated
from downscale demand script. 

"""
import pandas as pd
import os

# update historical activity data
def historical_activity(path_files, scenario):
    
    path2 = os.path.join(path_files + "/modelData")
    suffix = '_PAK'
    
    # Get the historical demands for country in the region from excel sheet
    xls_par = pd.ExcelFile(path2 + '/Parameters'+suffix+'.xlsx')
    hist_act_df = xls_par.parse('historical_activity').dropna(axis =1)
    
    hist_act_df2 = hist_act_df[(hist_act_df['technology'] != 'bio_extr_a') 
                        & (hist_act_df['technology'] != 'coal_exp')
                           & (hist_act_df['technology'] != 'eth_exp')
                            & (hist_act_df['technology'] != 'gas_exp')
                             & (hist_act_df['technology'] != 'solar_th_ppl')]

=======
# -*- coding: utf-8 -*-
"""
This Script is use to update historical activity data based on the new demand updated
from downscale demand script. 

"""
import pandas as pd
import os

# update historical activity data
def historical_activity(path_files, scenario):
    
    path2 = os.path.join(path_files + "/modelData")
    suffix = '_PAK'
    
    # Get the historical demands for country in the region from excel sheet
    xls_par = pd.ExcelFile(path2 + '/Parameters'+suffix+'.xlsx')
    hist_act_df = xls_par.parse('historical_activity').dropna(axis =1)
    
    hist_act_df2 = hist_act_df[(hist_act_df['technology'] != 'bio_extr_a') 
                        & (hist_act_df['technology'] != 'coal_exp')
                           & (hist_act_df['technology'] != 'eth_exp')
                            & (hist_act_df['technology'] != 'gas_exp')
                             & (hist_act_df['technology'] != 'solar_th_ppl')]

>>>>>>> master:modelFiles/Update_historical_activity.py
    scenario.add_par("historical_activity", hist_act_df2)