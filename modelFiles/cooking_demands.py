# -*- coding: utf-8 -*-
"""
This function introduce cooking fuel demands to meet basic access levels


"""
import pandas as pd
import numpy as np
from itertools import product
from modelFiles.downscale_demands import downscale_demands
from modelFiles.demands import demands
from modelFiles.ssp_data import ssp_data
from modelFiles.parameter_modifier import import_parameter, copy_parameter
from scipy.optimize import linprog



def cooking_demand(msgSC, msgWSC, path,ssp):


    dmds = msgSC.par('demand')
    nodeName = 'Pakistan'
    iso ='PAK'
    regionName = 'R14_SAS'



    # share of population without access to clean cooking fuels
    cook_acc_df = pd.read_excel(
        str(path) + str('/') + str('API_EG.CFT.ACCS.ZS_DS2_en_excel_v2_889166.xls'),
        'Data',
        header = 2)
    cook_acc_df.columns = cook_acc_df.iloc[0]
    cook_acc_df = cook_acc_df.loc[(cook_acc_df['Country Name'] == "Pakistan")]
    pc_cook_acc = cook_acc_df[2016]/100

    # Percentage of population without access to clean cooking fuels in 2020 in Pakistan
    # From PAkistan NAP , the figures are contradictory , so using those values as baseline instead Assumes 10% increase in access since 2015
    pc_pop_2020 = 0.69

    # targets to increase cooking access as per baseline
    # increase in population increased wrt historical trends and
    # future projections from local data
    pc_pop = {
                2015:[0.71],
                2020:[0.69],
                2025:[0.66],
                2030:[0.58],
                2035:[0.45],
                2040:[0.28],
                2045:[0.15],
                2050:[0.00],
            }
    pc_pop = pd.DataFrame(data = pc_pop)
    msg_yrs = [int(x) for x in msgSC.set('year')]
    hist_year = 2015
    final_year = 2100
    demand_yrs = [x for x in msg_yrs if x >= hist_year and x <= final_year]
    demand_yrs = [x for x in msg_yrs if x >= hist_year ]

    # Population with acess to clean cooking fuels
    pop_df = ssp_data( msgSC, path, iso , regionName,ssp)
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


    # Multiplying tier3 elec consumption per capita with pop without elec access data
    ssp_df['t_cooking'] = ssp_df['pop_w/o access'].mul(tier1)*0.25
    # Multiplying tier3 elec consumption per capita with pop with elec access data
    ssp_df['nt_cooking'] = ssp_df['pop_w/access'].mul(tier2)*0.25
    # Adding both to get improved  total elec demand



    # changing elec demands for access
    msgSC.check_out()
    dmds['commodity'] = 't_cooking'
    dmds = dmds.iloc[0:14 ,:]
    dmds['value']= ssp_df['t_cooking']
    dmds_a = dmds.copy()
    dmds_a['value']= ssp_df['nt_cooking']
    dmds_a['commodity'] = 'nt_cooking'

    dmds = pd.concat([dmds,dmds_a], ignore_index = True)
    msgSC.add_par('demand', dmds)


    msgSC.commit('cooking demands introduced')
    print('cooking demands introduced')
    # # Access to cooking fuels
