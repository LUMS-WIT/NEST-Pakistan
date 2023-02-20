# -*- coding: utf-8 -*-
"""

This function add main parameters of new technologies (technical_lifetime, input, output, inv_cost, and var_cost)

"""

import pandas as pd
import numpy as np
import pycountry
from geotext import GeoText
from itertools import product

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())],
                       columns=dictionary.keys())

def setdefaults(par,nodeName):
    if 'mode' in par.columns:
        par['mode'] = 'M1'
    if 'node' in par.columns:
        par['node'] = nodeName
    if 'node_loc' in par.columns:
        par['node_loc'] = nodeName
    if 'node_parent' in par.columns:
        par['node_parent'] = nodeName
    if 'node_origin' in par.columns:
        par['node_origin'] = nodeName
    if 'node_dest' in par.columns:
        par['node_dest'] = nodeName
    if 'node_rel' in par.columns:
        par['node_rel'] = nodeName
    if 'time' in par.columns:
        par['time'] = 'year'
    if 'time_dest' in par.columns:
        par['time_dest'] = 'year'
    if 'time_origin' in par.columns:
        par['time_origin'] = 'year'
    return(par)

def add_renewables(msgSC, msgWSC, path, nodeName, regionName, iso,suffix):


    # 1) Initialization and importing data
    year = list(msgSC.set('year').astype(int))
    xls_par = pd.ExcelFile(str(path + '/Parameters' + suffix + '.xlsx'))
    df_renew = xls_par.parse('renewable')
    df_renew = df_renew.loc[df_renew['active'] == 'yes']

    # 2) Adding required sets if not yet
    msgSC.check_out()
    msgSC.add_set('grade', list(df_renew['grade']))
    msgSC.add_set('level', list(df_renew['level']))
    msgSC.add_set('level_renewable', list(set(df_renew['level'])))

    # 3) Adding data
    for parname in ['renewable_potential', 'renewable_capacity_factor']:
        df = df_renew.copy()

        par = pd.DataFrame(columns=msgSC.par(parname).columns,
                           index=product(year, df.index))
        par['commodity'] = [df.loc[i[1], 'commodity'] for i in par.index]
        par['grade'] = [df.loc[i[1], 'grade'] for i in par.index]
        par['level'] = [df.loc[i[1], 'level'] for i in par.index]
        par['node'] = nodeName
        par['unit'] = [df.loc[i[1], 'unit'] for i in par.index]
        par['value'] = [df.loc[i[1], parname] for i in par.index]
        par['year'] = [i[0] for i in par.index]

        par.reset_index(inplace=True, drop=True)
        msgSC.add_par(parname, par)

    # List of technologies added renewabale with biomass and hydro
    # wind_ppl, wind_ppf. solar_v_ppl, solar_th_ppl, geo_hp. hydro_new, biomass_extr

    # region country mapping
    reg_df = pd.read_excel( str(path ) + str('/') + str('iso_reg.xlsx'), 'Sheet1')
    reg_df['node'] = str('R14_') + reg_df['node'].astype(str)
#%% Wind
    ### ONSHORE WIND

    tec = 'wind_ppl'
    msgSC.add_set('technology',tec)
    msgSC.add_set('type_tec', 'powerplant_low-carbon')
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tec},index=[0]))

    # Vintaging
    lft = 25
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgWSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs2 = []
    for vv in vtgs:
        if float(vv)>=float(year1):
            vtgs2.append(vv)
    vtgs = vtgs2

    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[1],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('construction_time', df)

    # Onshore wind investment costs from IRENA
    onshore_wind_costs_df = pd.read_excel(
            str(path ) + str('/') + str('irena_renewables_cost_2018.xlsx'),
            'onshore_wind',
            header = 0,
            skip_blank_lines = True)
    # region and country names
    onshore_wind_costs_df['R14'] = onshore_wind_costs_df['Country']
    for j in onshore_wind_costs_df.index:
        places = list( GeoText(onshore_wind_costs_df['Country'][j]).country_mentions.keys() )
        if places:
            places = places[0]
            places = pycountry.countries.get(alpha_2=places)
            places = places.alpha_3
        else:
            places = float('NaN')
        onshore_wind_costs_df['Country'][j] = places
        rg = reg_df.loc[reg_df['iso']==places]
        rg = rg.node.values
        onshore_wind_costs_df['R14'][j] = rg[0]

    # averaging for countries without data
    df = onshore_wind_costs_df.loc[onshore_wind_costs_df['Country'].isin([iso])]
    if not df.empty:
        onshore_wind_costs_df = onshore_wind_costs_df[onshore_wind_costs_df['Country']==iso]
        onshore_wind_costs_df = onshore_wind_costs_df[['Year','USD2018_per_kW']]
    else:
        df = onshore_wind_costs_df.loc[onshore_wind_costs_df['R14'].isin([regionName])]
        if not df.empty:
            onshore_wind_costs_df = df.groupby('Year').agg(
                USD2018_per_kW = pd.NamedAgg(column='USD2018_per_kW', aggfunc=np.mean)).reset_index()
        else:
            df = onshore_wind_costs_df.loc[onshore_wind_costs_df['R14'].isin(['R14_CPA','R14_SAS'])]
            onshore_wind_costs_df = df.groupby('Year').agg(
                USD2018_per_kW = pd.NamedAgg(column='USD2018_per_kW', aggfunc=np.mean)).reset_index()

    # most recent investement numbers
    onshore_wind_inv = onshore_wind_costs_df[onshore_wind_costs_df['Year']==2018]
    onshore_wind_inv = onshore_wind_inv.USD2018_per_kW.values[0] # assuming 1.06 USD 2018 = 1 USD 2015

    # investment change in the last 5 years
    num = np.diff(onshore_wind_costs_df.USD2018_per_kW.values)
    den = onshore_wind_costs_df.USD2018_per_kW.values[0:(len(onshore_wind_costs_df)-1)]
    onshore_wind_dinv = num/den
    onshore_wind_dinv = np.mean(onshore_wind_dinv[(len(onshore_wind_dinv)-5):len(onshore_wind_dinv)])

    # add commodity
    # msgSC.add_set('commodity', 'onshore_wind')

    # add inv cost for each vintage
    # limit reduction in costs to 50% vs 2015 values over the time horizon
    for vvv in vtgs:

        frf = ((1+onshore_wind_dinv)**max(0,(float(vvv)-2020)))
        val = max(0.5,frf)*onshore_wind_inv
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'value':[val],
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('inv_cost', df)

        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # fixed costs from IRENA in 2018USD per kW per Year rng is [31,55,75]]
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'value':[55*max(0.5,frf)], # average scaled symmetrically with the investements
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('fix_cost', df)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('wind')],
            'level':[str('renewable')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('electr')],
            'level':[str('secondary')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)


    ## OFFSHORE WIND

    tec = 'wind_ppf'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tec},index=[0]))

    # add commodity
    # msgSC.add_set('commodity', 'offshore_wind')

    # Vintaging
    lft = 25
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgWSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs2 = []
    for vv in vtgs:
        if float(vv)>=float(year1):
            vtgs2.append(vv)
    vtgs = vtgs2

    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[1],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('construction_time', df)

    # Offshore wind - only have global cost averages
    offshore_wind_costs_df = pd.read_excel(
            str(path ) + str('/') + str('irena_renewables_cost_2018.xlsx'),
            'offshore_wind',
            header = 0,
            skip_blank_lines = True)
    # region and country names
    offshore_wind_inv = offshore_wind_costs_df.average.values[offshore_wind_costs_df['Year']==2018][0]
    num = np.diff(offshore_wind_costs_df.average.values)
    den = offshore_wind_costs_df.average.values[0:(len(offshore_wind_costs_df)-1)]
    offshore_wind_dinv = num/den
    offshore_wind_dinv = np.mean(offshore_wind_dinv[(len(offshore_wind_dinv)-5):len(offshore_wind_dinv)])

    # add inv cost for each vintage
    # limit reduction in costs to 50% vs 2015 values over the time horizon
    for vvv in vtgs:

        frf = ((1+offshore_wind_dinv)**max(0,(float(vvv)-2020)))
        val = max(0.5,frf)*offshore_wind_inv
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'value':[val],
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('inv_cost', df)

        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # fixed costs from NREL COst of Wind ENergy 2017 in 2017USD per kW per Year rng is [43,115,216]]
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'value':[115*max(0.5,frf)], # average scaled symmetrically with the investements
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('fix_cost', df)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('wind')],
            'level':[str('renewable')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('electr')],
            'level':[str('secondary')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)

    # # wind resources
    # for wt in ['Onshore','Offshore']:
            
    #     # read wind potentials from NREL
    #     df_wind = pd.read_excel(
    #         str(path) + str('/') + str('nrelcfddawindsc20130603.xlsx'), 
    #         str(wt) + str(' Energy'), 
    #         header = 2,
    #         skip_blank_lines = True)
    #     cfs = pd.read_excel(
    #         str(path) + str('/') + str('nrelcfddawindsc20130603.xlsx'), 
    #         str('Class'), 
    #         skip_blank_lines = True)    
    #     # add the ISO country code
    #     for j in df_wind.index:
    #         if pd.isna(df_wind['IAM Country Name'][j]):
    #             df_wind['IAM Country Name'][j] = df_wind['IAM Country Name'][j-1]
    #         else:
    #             places = list( GeoText(df_wind['IAM Country Name'][j]).country_mentions.keys() )
    #             if places:
    #                 places = places[0]
    #                 places = pycountry.countries.get(alpha_2=places)
    #                 if places:
    #                     places = places.alpha_3
    #                 else:
    #                     places = float('NaN')
    #             else:
    #                 places = float('NaN') 
    #             if df_wind['IAM Country Name'][j] == 'Papua New Guinea':
    #                 places = 'PNG'
    #             df_wind['IAM Country Name'][j] = places        
        
    #     # Pull out data for on- and off- shore wind resources
    #     df_wind = df_wind[df_wind['IAM Country Name']==iso]
    #     rts = ['c1','c2','c3','c4','c5','c6','c7','c8','c9'] # 0 to 50 miles
    #     rts2 = ['c1.1','c2.1','c3.1','c4.1','c5.1','c6.1','c7.1','c8.1','c9.1'] # 50 to 100 miles
    #     cls = rts + rts2 # assuming the potential in each class 'c' is out to 100 miles
    #     if not df_wind.empty:
    #         if wt == 'Onshore':
    #             res = []
    #             for j in range(0,9):
    #                 i1 = str('c') + str(j+1)
    #                 i2 = str('c') + str(j+1) + str('.1')
    #                 res.append( df_wind[i1].sum()*1e3/8.76 + df_wind[i2].sum()*1e3/8.76) # convert from PWh to GWa
    #             df_wind_on = pd.DataFrame({
    #                 'renewable_potential': res,
    #                 'grade': rts,
    #                 'renewable_capacity_factor': cfs['mean'].tolist()})
    #             df_wind_on['node'] = iso
    #             df_wind_on['level'] = 'renewable'
    #             df_wind_on['commodity'] = 'onshore_wind'
    #             df_wind_on['unit'] = 'GWa'
    #             df_wind_on = df_wind_on[['node','level','commodity', 'grade', 'renewable_potential',	'renewable_capacity_factor', 'unit']]             
                
    #         else:
    #             res = []
    #             for j in range(0,9):
    #                 i1 = str('c') + str(j+1)
    #                 i2 = str('c') + str(j+1) + str('.1')
    #                 res.append(df_wind[i1].sum()*1e3/8.76 + df_wind[i2].sum()*1e3/8.76) # summing across the depth classes
    #             df_wind_off = pd.DataFrame({
    #                 'renewable_potential': res,
    #                 'grade': rts,
    #                 'renewable_capacity_factor': cfs['mean']})
    #             df_wind_off['node'] = iso
    #             df_wind_off['level'] = 'renewable'
    #             df_wind_off['commodity'] = 'offshore_wind'
    #             df_wind_off['unit'] = 'GWa'
    #             df_wind_off = df_wind_off[['node','level','commodity', 'grade', 'renewable_potential',	'renewable_capacity_factor', 'unit']] 
    #     else:
    #         dff = pd.DataFrame({
    #                 'renewable_potential': [0]*len(rts),
    #                 'grade': rts,
    #                 'renewable_capacity_factor': cfs['mean']})
    #         dff['node'] = iso
    #         dff['level'] = 'renewable'
    #         dff['commodity'] = 'offshore_wind'
    #         dff['unit'] = 'GWa'
    #         dff = dff[['node','level','commodity', 'grade', 'renewable_potential',	'renewable_capacity_factor', 'unit']]        
    #         if wt == 'Onshore':
    #             df_wind_on = dff
    #         else:
    #             df_wind_off = dff
                
    # # add wind resource parameterization to the model
    # dfw = df_wind_on.append(df_wind_off)
    # dfw['node'] = nodeName
    # msgSC.add_set('grade', dfw.grade.unique().tolist())
    # msgSC.add_set('level', dfw.level.unique().tolist())
    # msgSC.add_set('level_renewable', dfw.level.unique().tolist())
    # msgSC.add_set('commodity', dfw.commodity.unique().tolist())
    # year = list(msgSC.set('year').astype(int))
    # for yyy in year:
    #     df = dfw.copy()
    #     df['year'] = yyy
    #     rp = df[['node','commodity', 'grade', 'level','year','renewable_potential', 'unit']]
    #     rp.columns = ['node','commodity', 'grade', 'level', 'year', 'value', 'unit']
    #     rc = df[['node','commodity', 'grade', 'level','year','renewable_potential','unit']]
    #     rc.columns = ['node','commodity', 'grade', 'level', 'year', 'value','unit']
    #     rp.reset_index(inplace=True, drop=True)
    #     rc.reset_index(inplace=True, drop=True)
    #     msgSC.add_par('renewable_potential', rp)
    #     msgSC.add_par('renewable_capacity_factor', rc)
#%% Solar   
    # # solar resources
    # df_solar = pd.read_excel(
    #     str(path) + str('/') + str('solarresourceenergy.xlsx'), 
    #     str('Tilt_Lat'), 
    #     header = 0,
    #     skip_blank_lines = True)
    # cfs = pd.read_excel(
    #     str(path) + str('/') + str('solarresourceenergy.xlsx'), 
    #     str('Class'), 
    #     skip_blank_lines = True)    
    # =============================================================================
#     for j in df_solar.index:
#         places = list( GeoText(df_solar['Country'][j]).country_mentions.keys() )
#         if places:
#             places = places[0]
#             places = pycountry.countries.get(alpha_2=places)
#             if places:
#                 places = places.alpha_3
#             else:
#                 places = float('NaN')
#         else:
#             places = float('NaN') 
#     
#         if df_solar['Country'][j] == 'Papua New Guinea':
#             places = 'PNG'
#         
#         df_solar['Country'][j] = places
# =============================================================================
    
    # get data for country and format for upload
    # df_solar = df_solar[df_solar['Country']==nodeName]
    # if not df_solar.empty:
    #     df_solar = df_solar[['Country','Class','GWh/year']]
    #     df_solar.columns = ['node','grade','renewable_potential']
    #     df_solar['renewable_capacity_factor'] = df_solar['grade']
    #     for j in df_solar.index:
    #         cf = cfs[cfs['Class']==df_solar['grade'][j]]
    #         if not cf.empty:
    #             cf = cf['Capacity Factor']
    #         else:
    #             cf = 0
    #         df_solar['renewable_capacity_factor'][j] = cf / 100
    #         df_solar['grade'][j] = str('c')+str(df_solar['grade'][j])
    #     df_solar['renewable_potential'] = df_solar['renewable_potential'] / 8760  # convert GWh to GWa
    #     df_solar['commodity'] = 'solar'
    #     df_solar['level'] = 'renewable' 
    #     df_solar['unit'] = 'GWa'
        
    #     # add to model
    #     dfs = df_solar
    #     msgSC.add_set('grade', dfs.grade.unique().tolist())
    #     msgSC.add_set('level', dfs.level.unique().tolist())
    #     msgSC.add_set('level_renewable', dfs.level.unique().tolist())
    #     msgSC.add_set('commodity', dfs.commodity.unique().tolist())
    #     year = list(msgSC.set('year').astype(int))
    #     for yyy in year:
    #         df = dfs.copy()
    #         df['year'] = yyy
    #         rp = df[['node','commodity', 'grade', 'level','year','renewable_potential', 'unit']]
    #         rp.columns = ['node','commodity', 'grade', 'level', 'year', 'value', 'unit']
    #         rc = df[['node','commodity', 'grade', 'level','year','renewable_potential','unit']]
    #         rc.columns = ['node','commodity', 'grade', 'level', 'year', 'value','unit']
    #         rp.reset_index(inplace=True, drop=True)
    #         rc.reset_index(inplace=True, drop=True)
    #         msgSC.add_par('renewable_potential', rp)
    #         msgSC.add_par('renewable_capacity_factor', rc) 
    
    ## SOLAR PV

    tec = 'solar_pv_ppl'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tec},index=[0]))

    # Vintaging
    lft = 30
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgWSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs2 = []
    for vv in vtgs:
        if float(vv)>=float(year1):
            vtgs2.append(vv)
    vtgs = vtgs2

    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[1],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('construction_time', df)

    # Solar PV costs from IRENA for 2018
    solar_pv_costs_df = pd.read_excel(
            str(path ) + str('/') + str('irena_renewables_cost_2018.xlsx'),
            'solar_pv',
            header = 0,
            skip_blank_lines = True)

    # region and country names
    solar_pv_costs_df['R14'] = solar_pv_costs_df['Country']
    for j in solar_pv_costs_df.index:
        places = list( GeoText(solar_pv_costs_df['Country'][j]).country_mentions.keys() )
        if places:
            places = places[0]
            places = pycountry.countries.get(alpha_2=places)
            places = places.alpha_3
        else:
            places = float('NaN')
        solar_pv_costs_df['Country'][j] = places
        rg = reg_df.loc[reg_df['iso']==places]
        rg = rg.node.values
        solar_pv_costs_df['R14'][j] = rg[0]

    # averaging for countries without data
    df = solar_pv_costs_df.loc[solar_pv_costs_df['Country'].isin([iso])]
    if not df.empty:
        solar_pv_costs_df = solar_pv_costs_df[solar_pv_costs_df['Country']==iso]
        solar_pv_costs_df = solar_pv_costs_df[['Year','USD2018_per_kW']]
    else:
        df = solar_pv_costs_df.loc[solar_pv_costs_df['R14'].isin([regionName])]
        if not df.empty:
            solar_pv_costs_df = df.groupby('Year').agg(
                USD2018_per_kW = pd.NamedAgg(column='USD2018_per_kW', aggfunc=np.mean)).reset_index()
        else:
            df = solar_pv_costs_df.loc[solar_pv_costs_df['R14'].isin(['R14_CPA','R14_SAS'])]
            solar_pv_costs_df = df.groupby('Year').agg(
                USD2018_per_kW = pd.NamedAgg(column='USD2018_per_kW', aggfunc=np.mean)).reset_index()

    solar_pv_inv = solar_pv_costs_df[solar_pv_costs_df['Year']==2018]
    solar_pv_inv = solar_pv_inv.USD2018_per_kW.values[0] # assuming 1.06 USD 2018 = 1 USD 2015
    num = np.diff(solar_pv_costs_df.USD2018_per_kW.values)
    den = solar_pv_costs_df.USD2018_per_kW.values[0:(len(solar_pv_costs_df)-1)]
    solar_pv_dinv = num/den
    solar_pv_dinv = np.mean(solar_pv_dinv[(len(solar_pv_dinv)-5):len(solar_pv_dinv)])

    # add commodity
    # msgSC.add_set('commodity', 'solar')

    # add inv cost for each vintage
    # limit reduction in costs to 50% vs 2015 values over the time horizon
    for vvv in vtgs:

        frf = ((1+solar_pv_dinv)**max(0,(float(vvv)-2020)))
        val = max(0.5,frf)*solar_pv_inv
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'value':[val],
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('inv_cost', df)

        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # fixed costs from NREL ATB 2019 - range is [10,14,20]
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'value':[14*max(0.5,frf)], # average scaled symmetrically with the investements
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('fix_cost', df)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('solar_pv')],
            'level':[str('renewable')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('electr')],
            'level':[str('secondary')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)

    ## SOLAR CSP


    tec = 'solar_th_ppl'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tec},index=[0]))

    # Vintaging
    lft = 30
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgWSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs2 = []
    for vv in vtgs:
        if float(vv)>=float(year1):
            vtgs2.append(vv)
    vtgs = vtgs2

    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[1],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('construction_time', df)

    # solar_csp - only have global cost averages
    solar_csp_costs_df = pd.read_excel(
            str(path ) + str('/') + str('irena_renewables_cost_2018.xlsx'),
            'solar_csp',
            header = 0,
            skip_blank_lines = True)
    # investment and investment change
    solar_csp_inv = solar_csp_costs_df.average.values[solar_csp_costs_df['Year']==2018][0]
    num = np.diff(solar_csp_costs_df.average.values)
    den = solar_csp_costs_df.average.values[0:(len(solar_csp_costs_df)-1)]
    solar_csp_dinv = num/den
    solar_csp_dinv = np.mean(solar_csp_dinv[(len(solar_csp_dinv)-5):len(solar_csp_dinv)])

    # add inv cost for each vintage
    # limit reduction in costs to 50% vs 2015 values over the time horizon
    for vvv in vtgs:

        frf = ((1+solar_csp_dinv)**max(0,(float(vvv)-2020)))
        val = max(0.5,frf)*solar_csp_inv
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'value':[val],
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('inv_cost', df)

        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # fixed costs from NREL ATB 2019 - range is [40,51,66]
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'value':[51*max(0.5,frf)], # average scaled symmetrically with the investments
            'unit':['USD/GWa']}
        df = expand_grid(dic)
        msgSC.add_par('fix_cost', df)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('solar_th')],
            'level':[str('renewable')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('electr')],
            'level':[str('secondary')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)

    # ## GEOTHERMAL

    # tecs = ['geo_ppl','geo_hpl']
    # for tec in tecs:

    #     msgSC.add_set('technology',tec)
    #     msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tec},index=[0]))

    #     # Vintaging
    #     lft = 30
    #     hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    #     if not hc.empty:
    #         year1 = hc.year_vtg.values[0]
    #     else:
    #         year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    #     vtgs = msgWSC.set('year').values
    #     if not hc.empty:
    #         year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    #     else:
    #         year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    #     vtgs2 = []
    #     for vv in vtgs:
    #         if float(vv)>=float(year1):
    #             vtgs2.append(vv)
    #     vtgs = vtgs2

    #     # update technical lifetime and construction time
    #     dic = {
    #         'node_loc':[nodeName],
    #         'technology':[tec],
    #         'year_vtg':vtgs,
    #         'value':[lft],
    #         'unit':['-']}
    #     df = expand_grid(dic)
    #     msgSC.add_par('technical_lifetime', df)
    #     dic = {
    #         'node_loc':[nodeName],
    #         'technology':[tec],
    #         'year_vtg':vtgs,
    #         'value':[1],
    #         'unit':['-']}
    #     df = expand_grid(dic)
    #     msgSC.add_par('construction_time', df)

    #      # geothermal - only have global cost averages
    #     geothermal_costs_df = pd.read_excel(
    #             str(path ) + str('/') + str('irena_renewables_cost_2018.xlsx'),
    #             'geothermal',
    #             header = 0,
    #             skip_blank_lines = True)
    #     # region and country names
    #     geothermal_inv = geothermal_costs_df.average.values[geothermal_costs_df['Year']==2018][0]
    #     num = np.diff(geothermal_costs_df.average.values)
    #     den = geothermal_costs_df.average.values[0:(len(geothermal_costs_df)-1)]
    #     geothermal_dinv = num/den
    #     geothermal_dinv = np.mean(geothermal_dinv[(len(geothermal_dinv)-5):len(geothermal_dinv)])

    #     # add inv cost for each vintage
    #     # limit reduction in costs to 50% vs 2015 values over the time horizon
    #     for vvv in vtgs:

    #         frf = ((1+geothermal_dinv)**max(0,(float(vvv)-2020)))
    #         val = max(0.5,frf)*geothermal_inv
    #         dic = {
    #             'node_loc':[nodeName],
    #             'technology':[tec],
    #             'year_vtg':[vvv],
    #             'value':[val],
    #             'unit':['USD/GWa']}
    #         df = expand_grid(dic)
    #         msgSC.add_par('inv_cost', df)

    #         # years for this vintage based on technical lifetime
    #         yrs = []
    #         for vv in vtgs:
    #             if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
    #                 yrs.append(vv)

    #         # fixed costs from NREL ATB 2019 - range is [40,51,66]
    #         dic = {
    #             'node_loc':[nodeName],
    #             'technology':[tec],
    #             'year_vtg':[vvv],
    #             'year_act':yrs,
    #             'value':[51*max(0.5,frf)], # average scaled symmetrically with the investments
    #             'unit':['USD/GWa']}
    #         df = expand_grid(dic)
    #         msgSC.add_par('fix_cost', df)

    #         # output
    #         if tec == 'geo_hpl':
    #             oo = 'd_heat'
    #         else:
    #             oo = 'electr'
    #         dic = {
    #             'node_loc':[nodeName],
    #             'technology':[tec],
    #             'year_vtg':[vvv],
    #             'year_act':yrs,
    #             'mode':[str('M1')],
    #             'node_dest':[nodeName],
    #             'commodity':[str(oo)],
    #             'level':[str('secondary')],
    #             'time':[str('year')],
    #             'time_dest':[str('year')],
    #             'value':[1],
    #             'unit':[str('-')]}
    #         df = expand_grid(dic)
    #         msgSC.add_par('output', df)


    ### OLD HYDROPOWER

    # # initialize old hydropower technology following previous implementation
    # tecs=msgWSC.set('technology').loc[msgWSC.set('technology').str.contains('hydro_')].to_list()
    # msgSC.add_set('technology', tecs)
    # msgSC.add_set('cat_tec', msgWSC.set('cat_tec').loc[msgWSC.set('cat_tec').technology.isin(tecs)])

    # # other parameters for old hydropower taken from global model
    # for par in ['inv_cost','fix_cost','var_cost','output','capacity_factor','technical_lifetime','construction_time']:
        # a0 = msgWSC.par(par,{'node_loc':reg})
        # msgSC.add_par(par,a0.loc[ a0.technology.isin(tecs)].replace(to_replace=reg,value=iso))

    # ### NEW HYDROPOWER

    # # Specific national implementaiton based on IMAGE cost curves reported in Gernaat et al 2017
    # tec = 'hydro_new'

    # # Hydropower potential and costs from IMAGE model  (Gernaat et al 2017)
    # df_hydro_pot = pd.read_excel(
    #     str(path ) + str('/') + str('image_hydro_cost_country.xlsx'),
    #     str('MAX_POTENTIAL'))
    # df_hydro_lf = pd.read_excel(
    #     str(path ) + str('/') + str('image_hydro_cost_country.xlsx'),
    #     str('LOAD_FACTOR'))
    # df_hydro_cst = pd.read_excel(
    #     str(path ) + str('/') + str('image_hydro_cost_country.xlsx'),
    #     str('CAP_COST'))


    # # add the ISO country code
    # nms = []
    # for column in df_hydro_pot.columns.values:

    #     if column == 'Papua New Guinea':
    #         places = 'PNG'
    #     else:
    #         places = list( GeoText(column).country_mentions.keys() )

    #         if places:
    #             places = places[0]
    #             places = pycountry.countries.get(alpha_2=places)
    #             if places:
    #                 places = places.alpha_3
    #             else:
    #                 places = float('NaN')
    #         else:
    #             places = float('NaN')

    #     nms.append(places)

    # nms = np.array(nms)
    # nms2 = np.array(df_hydro_pot.columns.values)

    # # Get the data for particular iso
    # if iso in nms:

    #     ind = nms2[np.where(nms == iso)].tolist()
    #     hydro_pot = df_hydro_pot[ind].astype(float)
    #     hp = hydro_pot.iloc[0]
    #     df_hydro_lf = df_hydro_lf[['x',ind[0]]].astype(float)
    #     df_hydro_cst = df_hydro_cst[['x',ind[0]]].astype(float)

    #     # Vintaging
    #     lft = 50
    #     vtgs = msgWSC.set('year').values
    #     year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    #     vtgs2 = []
    #     for vv in vtgs:
    #         if float(vv)>=float(year1):
    #             vtgs2.append(vv)
    #     vtgs = vtgs2

    #     # hydropower investment costs from IRENA for 2018 - used as a cost change indicator in this case
    #     hydropower_costs_df = pd.read_excel(
    #             str(path ) + str('/') + str('irena_renewables_cost_2018.xlsx'),
    #             'hydro',
    #             header = 0,
    #             skip_blank_lines = True)
    #     # region and country names
    #     if regionName == 'R14_CPA':
    #         rrr = "\'China"
    #     if regionName in ['R14_SCS','R14_CAS']:
    #         rrr = "\'Eurasia"
    #     if regionName == "\'R14_SAS'":
    #         rrr = 'India'
    #     else:
    #         rrr = 'Other Asia'
    #     hydro_inv1 = hydropower_costs_df.y2014_to_2018.values[(hydropower_costs_df.Country == rrr)&(hydropower_costs_df.Percentile == 'Weighted average')][0]
    #     hydro_inv2 = hydropower_costs_df.y2010_to_2014.values[(hydropower_costs_df.Country == rrr)&(hydropower_costs_df.Percentile == 'Weighted average')][0]
    #     hydro_dinv = max(0, hydro_inv2/hydro_inv1 )

    #     # Make a new technology for each class
    #     classes = pd.DataFrame({'cls': [i for i in range(10)]}).astype(float)
    #     if not df_hydro_lf.empty:
    #         for ggg in classes.index:

    #             # tec name and add sets
    #             tecg = str(tec)+str('_c')+str(ggg)
    #             msgSC.add_set('technology',tecg)
    #             msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tecg},index=[0]))

    #             # go throgh vintages and add parameters
    #             for vvv in vtgs:

    #                 frf = ((1+hydro_dinv)**max(0,(float(vvv)-2020)))
    #                 frc = (classes.loc[ggg,'cls']+1)/10
    #                 res = hp*frc*0.002778/8760 # convert from GJ t GWa
    #                 cfs = df_hydro_lf[(df_hydro_lf['x']<=frc) & (df_hydro_lf['x']>(frc-0.1))]
    #                 cfs = cfs.iloc[:,1].mean()
    #                 cst = df_hydro_cst[(df_hydro_cst['x']<=frc) & (df_hydro_cst['x']>(frc-0.1))]
    #                 cst = cst.iloc[:,1].mean()

    #                 # inv cost
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'year_vtg':[vvv],
    #                     'value':[cst*max(0.5,frf)],
    #                     'unit':['USD/GWa']}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('inv_cost', df)

    #                 # bound_total_capacity_up - this limits the expansion of each grade
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'year_act':[vvv],
    #                     'value':[res],
    #                     'unit':['GWa']}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('bound_total_capacity_up', df)

    #                 # years for this vintage based on technical lifetime
    #                 yrs = []
    #                 for vv in vtgs:
    #                     if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
    #                         yrs.append(vv)

    #                 # capacity factor - limits the annual production based on resource assessment
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'year_vtg':[vvv],
    #                     'year_act':yrs,
    #                     'time':[str('year')],
    #                     'value':[cfs],
    #                     'unit':['-']}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('capacity_factor',df)

    #                 # fixed costs from NREL ATB 2019 - range is [41,32,20]
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'technology':[tecg],
    #                     'year_vtg':[vvv],
    #                     'year_act':yrs,
    #                     'value':[32*max(0.5,frf)], # average scaled symmetrically with the investments
    #                     'unit':['USD/GWa']}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('fix_cost', df)

    #                  # input
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'year_vtg':[vvv],
    #                     'year_act':yrs,
    #                     'mode':[str('M1')],
    #                     'node_origin':[nodeName],
    #                     'commodity':[str('hydro')],
    #                     'level':[str('renewable')],
    #                     'time':[str('year')],
    #                     'time_origin':[str('year')],
    #                     'value':[1],
    #                     'unit':[str('-')]}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('input', df)

    #                 # output
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'year_vtg':[vvv],
    #                     'year_act':yrs,
    #                     'mode':[str('M1')],
    #                     'node_dest':[nodeName],
    #                     'commodity':[str('electr')],
    #                     'level':[str('secondary')],
    #                     'time':[str('year')],
    #                     'time_dest':[str('year')],
    #                     'value':[1],
    #                     'unit':[str('-')]}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('output', df)

    #                # technical lifetime
    #                 dic = {
    #                     'node_loc':[nodeName],
    #                     'technology':[tecg],
    #                     'technology':[tecg],
    #                     'year_vtg':[vvv],
    #                     'year_act':yrs,
    #                     'value':[60], # average scaled symmetrically with the investments
    #                     'unit':['year']}
    #                 df = expand_grid(dic)
    #                 msgSC.add_par('technical_lifetime', df)

    ## BIOENERGY

    # bioenergy - extraction tec for moving flows from regional to country level
    # tec = 'bio_extr'

    # msgSC.add_set('technology',tec)
    # msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':'powerplant_low-carbon','technology':tec},index=[0]))

    # # add commodity
    # msgSC.add_set('commodity', 'biomass')

    # # Vintaging
    # lft = 50
    # vtgs = msgWSC.set('year').values
    # for vvv in vtgs:

    #     # var_cost from global model
    #     price_commodity = msgWSC.var(
    #         'PRICE_COMMODITY',
    #         {'commodity': 'biomass',
    #         'level': 'primary',
    #         'node': regionName,
    #         'year': vvv})
    #     if price_commodity.empty:
    #         pc = 0
    #     else:
    #         pc = price_commodity.lvl[0]
    #     # var_cost
    #     dic = {
    #         'node_loc':[nodeName],
    #         'technology':[tec],
    #         'year_vtg':[vvv],
    #         'year_act':[vvv],
    #         'mode':[str('M1')],
    #         'time':[str('year')],
    #         'value':[pc],
    #         'unit':[str('USD/GWa')]}
    #     df = expand_grid(dic)
    #     msgSC.add_par('var_cost', df)

    #     # output
    #     dic = {
    #         'node_loc':[nodeName],
    #         'technology':[tec],
    #         'year_vtg':[vvv],
    #         'year_act':[vvv],
    #         'mode':[str('M1')],
    #         'node_dest':[nodeName],
    #         'commodity':[str('biomass')],
    #         'level':[str('primary')],
    #         'time':[str('year')],
    #         'time_dest':[str('year')],
    #         'value':[1],
    #         'unit':[str('-')]}
    #     df = expand_grid(dic)
    #     msgSC.add_par('output', df)

    # Committing the additions
    msgSC.commit('added renewable capacity factors & renewable potentials')
    print('> Renewable potential and capacity factors added!')
