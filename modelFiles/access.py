# -*- coding: utf-8 -*-
"""
This function increases demands of biomass and electriicty to meet basic access levels      


"""
import pandas as pd
import numpy as np
from itertools import product
from modelFiles.downscale_demands import downscale_demands
from modelFiles.demands import demands
from modelFiles.ssp_data import ssp_data
from modelFiles.parameter_modifier import import_parameter, copy_parameter
from scipy.optimize import linprog

def access(msgSDG, path):

   
    dmds = msgSDG.par('demand')
    nodeName = 'Pakistan'
    iso ='PAK' 
    regionName = 'R14_SAS'

    # Increasing access to electricity
    elec_dmds = dmds.loc[dmds['commodity'] == 'rc_spec']

    # Worldbank multi-tier framework for electricity access 
    # share of population without access to electricity 
    elec_acc_df = pd.read_excel(
        str(path) + str('/') + str('WEO2019-Electricity-database.xlsx'), 
        'Developing Asia', 
        header = 2,
        skip_blank_lines = True)
    elec_acc_df = elec_acc_df.dropna().reset_index(drop= 1)
    elec_acc_df.columns = elec_acc_df.iloc[0]
    elec_acc_df = elec_acc_df.drop(elec_acc_df.index[0:1])
    elec_acc_df = elec_acc_df.loc[(elec_acc_df.Country == "Pakistan")]
    pc_elec_acc = elec_acc_df[2015]

    # Percentage of population without access to electricity in 2020 in Pakistan 
    pc_pop_2020 = 0.77

    # targets to increase electricity access 
    pc_pop_2025 = 0.9
    pc_pop_2030 = 1
    
    msg_yrs = [int(x) for x in msgSDG.set('year')]
    hist_year = 2015
    final_year = 2100
    demand_yrs = [x for x in msg_yrs if x >= hist_year and x <= final_year]    
    demand_yrs = [x for x in msg_yrs if x >= hist_year ] 
    
    # Population with acess to electricity 
    pop_df = ssp_data( msgSDG, path, iso , regionName)
    pop_df = pop_df.loc[(pop_df.Variable == "Population")]
   
    ssp_df = []
    pop = []
    pop_u = []
    pop_r = []
 
    for jjj in demand_yrs:
        if jjj < 2110:
              mmm = jjj
        else:
              mmm = 2100
            
           
            
        if mmm < 2025:
            pop_u.append(pop_df[mmm].values[0]*1e6*pc_pop_2020)
            pop_r.append(pop_df[mmm].values[0]*1e6*(1-pc_pop_2020))
        elif  mmm == 2025:
            pop_u.append(pop_df[mmm].values[0]*1e6*pc_pop_2025)
            pop_r.append(pop_df[mmm].values[0]*1e6*(1-pc_pop_2025))
        else:
            pop_u.append(pop_df[mmm].values[0]*1e6*pc_pop_2030)
            pop_r.append(pop_df[mmm].values[0]*1e6*(1- pc_pop_2030))
        
        pop.append(pop_df[mmm].values[0]*1e6)
    ssp_df.append(pd.DataFrame({
                'year':demand_yrs,
                'pop':pop,
                'pop_w/access':pop_u, # percentage population without access to electricity 
                'pop_w/o access':pop_r})) # percentage population with access to electricity 

    ssp_df = pd.concat(ssp_df)
    
    # Tiers in GWa from Woldbank Multi-Tier framework 
    # See Beyond Connections Energy Access Redefined by E S M A P
    tier1 = 1.0274E-10
    tier2 = 1.66667E-09
    tier3 = 8.33333E-09
    tier4 = 2.8539E-08
    tier5 = 6.84932E-08
    
    # Multiplying tier3 elec consumption per capita with pop without elec access data 
    ssp_df['Elec_consumption_basic'] = ssp_df['pop_w/o access'].mul(tier2)
    # Multiplying tier3 elec consumption per capita with pop with elec access data 
    ssp_df['Elec_consumption_full']= ssp_df['pop_w/access'].mul(tier4)
    ssp_df['Elec_consumption_full'][0:5] = ssp_df['pop_w/access'][0:5].mul(tier4)
    ssp_df['Elec_consumption_full'][6:15] = ssp_df['pop_w/access'][6:15].mul(tier5)
    # Adding both to get improved  total elec demand
    ssp_df['Total Elec Consumption'] = ssp_df['Elec_consumption_basic'] + ssp_df['Elec_consumption_full']
    
    #loss = msgSDG.par('input',{'technology':'sp_el_RC'})    
	#loss = loss.iloc[5:19].reset_index(drop = True) 
    
    
    ssp_df['elec_demand'] = ssp_df['Total Elec Consumption'] * 2
    ssp_df['elec_demand'][0] = dmds['value'][60]
    
    
    #ssp_df['old demands'] = dmds['']
    # changing elec demands for access 
    msgSDG.check_out()
    cmdty = 'rc_spec'
    elec_dmd = msgSDG.par('demand',{'commodity': cmdty})
    msgSDG.remove_par('demand', elec_dmd)
    elec_dmd['value'] = ssp_df['elec_demand'].values
    msgSDG.add_par('demand', elec_dmd)
    
    # Increasing demands for clean cooking fuels 

    
    pc_pop = {
                2015:[0.71],    
                2020:[0.50],
                2025:[0.30],
                2030:[0.00],
                2035:[0.00],
                2040:[0.00],
                2045:[0.00],
                2050:[0.00],
            }
    pc_pop = pd.DataFrame(data = pc_pop)
    msg_yrs = [int(x) for x in msgSDG.set('year')]
    
    # Population with acess to clean cooking fuels 
    pop_df = ssp_data( msgSDG, path, iso , regionName)
    pop_df = pop_df.loc[(pop_df.Variable == "Population")]
    pop_df = pd.DataFrame(data = pop_df)
   
    ssp_df = []
    pop = []
    pop_wc = []
    pop_c = []
 
    for jjj in demand_yrs:
        if jjj < 2110:
              mmm = jjj
        else:
              mmm = 2100
            
           
            
        if mmm < 2050:
            pop_wc.append((pop_df[mmm].values[0]*1e6)*(pc_pop[mmm].values[0]))
            pop_c.append((pop_df[mmm].values[0]*1e6)*(1-pc_pop[mmm].values[0]))
        
        else:
            pop_wc.append((pop_df[mmm].values[0]*1e6)*0)
            pop_c.append((pop_df[mmm].values[0]*1e6))
        
        
        pop.append(pop_df[mmm].values[0]*1e6)
    ssp_df.append(pd.DataFrame({
                'year':demand_yrs,
                'pop':pop,
                'pop_w/access':pop_c, # percentage population without access to clean cooking fuels
                'pop_w/o access':pop_wc})) # percentage population with access to clean cooking fuels

    ssp_df = pd.concat(ssp_df)
    
    # Tiers in GWa vpnverted grom GJ/per capita 
    # See cameron et al. Nature 
    tier1 = 9.58904E-08 # lower demand per capita for traditional fuel 
    tier2 = 1.27854E-07 # higher for non-traditional 
   
    
    # Multiplyingc cooking per capita with pop without elec access data 
    ssp_df['t_cooking'] = ssp_df['pop_w/o access'].mul(tier1)*0.25
    # Multiplying cooking consumption per capita with pop with elec access data 
    ssp_df['nt_cooking'] = ssp_df['pop_w/access'].mul(tier2)*0.25
    # Adding both to get improved  total elec demand
    
    
    			
    # changing elec demands for access 
    
    cmdty = 't_cooking'
    cook_dmd = msgSDG.par('demand',{'commodity': cmdty})
    msgSDG.remove_par('demand', cook_dmd)
    ssp_df = ssp_df.iloc[0:14]
    cook_dmd['value'] = ssp_df['t_cooking'].values
    msgSDG.add_par('demand', cook_dmd)
    
     
    cmdty = 'nt_cooking'
    cook_dmd = msgSDG.par('demand',{'commodity': cmdty})
    msgSDG.remove_par('demand', cook_dmd)
    
    cook_dmd['value'] = ssp_df['nt_cooking'].values
    msgSDG.add_par('demand', cook_dmd)
    

    msgSDG.commit('demands adjusted wrt mitigation scenario')
    
   
    
    
    
    
   