# -*- coding: utf-8 -*-
"""
This function generates "demand" based on one of the following methods:
    1. Importing demand data for each period and commodity directly from Excel
    2. Importing demand data from a parent region in the global model
    3. Importing demand data for a base year and growth rates for the horizon
    both from Excel
    4. Importing historical activity data form a MESSAGE model as the basis for
    calculating demand, then applying growth rates specified in Excel for each
    period and commodity.
    NOTICE: In the case (3), parameter "historical_activity" should be updated
    before running this script!
    To update "historical activity", you may consult with the functiona here:
    "...message_data\calibration\iea_activity...".

"""


import pandas as pd
import numpy as np
from itertools import product
from modelFiles.downscale_demands import downscale_demands
#from modelFiles.historical_activity import historical_activity
# from modelFiles.parameter_modifier import import_parameter, copy_parameter
from scipy.optimize import linprog
import warnings

warnings.filterwarnings("ignore")

def demands(msgSC, path, ssp):

    nodeName = 'Pakistan'     # Name of the stand-alone model region.
    regionName = 'R14_SAS'      # Name of the reference region in MESSAGE global
    ieaName = "'Pakistan'"         # In the form of: "'Russian Federation'"
    plattsName = 'Pakistan'        # In the form of: 'Russia'
    suffix = '_PAK'             # The extension of Excel files, like: '_RU'
    iso = 'PAK'
    reg = regionName

    # Region to country mapping
    reg_df = pd.read_excel( str(path) +
                           str('/') + str('iso_reg.xlsx'), 'Sheet1')
    reg_df['node'] = str('R14_') + reg_df['node'].astype(str)
    isoreg = reg_df[reg_df['node']==reg]
    isoreg = isoreg['iso'].tolist()

    # country and region name mapping
    country_map = pd.read_excel( str(path) + str('/') + str(nodeName) +
                                str('_map.xlsx'), 'country_map')
    country = country_map.loc[(country_map['include']=='Y')&
                              (country_map['msg_14'] == reg.split('_')[1])]
#    iea = country.loc[country.iso==iso].iea[0]

    # SSP GDP data
    ssp_gdp_df = pd.read_excel(
            str(path) + str('/') + str('OECD_SSP_GDP_PPP.xlsx'),
            'OECD_SSP_GDP_PPP',
            header = 0 )


    ssp_gdp_df = ssp_gdp_df.loc[ ( ssp_gdp_df.Scenario == ssp+ '_v9_130325' )&
                                ( ssp_gdp_df.Region == iso ) ].reset_index(
                                    drop=True)

    # SSP population data
    ssp_pop_df = pd.read_excel(
            str(path) + str('/') + str('OECD_SSP_POP.xlsx'),
            'OECD_SSP_POP',
            header = 0 )

    ssp_pop_df = ssp_pop_df.loc[ ( ssp_pop_df.Scenario == ssp + '_v9_130325' )&(
        ssp_pop_df.Region == iso  ) ].reset_index(drop=True)

    # SSP data scaling to account for changes since release
    wbi_2015_df = pd.read_excel( str(path) + str('/') + str('wbi_pop_gdp_2015.xlsx'), 'wbi_pop_gdp_2015')
    wbi_2015_df = wbi_2015_df.loc[(wbi_2015_df.iso == iso)].reset_index(drop=True)
    for aaa in ssp_pop_df.index:
        if not (wbi_2015_df.loc[wbi_2015_df['iso']==ssp_pop_df.Region[aaa]]).empty:
            x0 = [ 1e-6*wbi_2015_df.loc[wbi_2015_df['iso']==ssp_pop_df.Region[aaa]].pop_2015.to_numpy()[0] ]
            x = ssp_pop_df.iloc[aaa,range(12,len(ssp_pop_df.columns))]
            dx = x.diff()/ssp_pop_df.iloc[aaa,range(12,len(ssp_pop_df.columns))]
            dx = dx.replace([np.inf,-np.inf,np.nan],0)
            xf = []
            xfi = x0[0]
            for ggg in dx.index:
                rs = xfi*(1+dx[ggg])
                xf.append(round(rs*1e6)/1e6)
                xfi = rs
            ssp_pop_df.iloc[aaa,range(12,len(ssp_pop_df.columns))] = xf


    for aaa in ssp_gdp_df.index:
        if not (wbi_2015_df.loc[wbi_2015_df['iso']==ssp_gdp_df.Region[aaa]]).empty:
            x0 = [ 1e-9*wbi_2015_df.loc[wbi_2015_df['iso']==ssp_gdp_df.Region[aaa]].gdp_ppp_usd_2015.to_numpy()[0] ]
            x = ssp_gdp_df.iloc[aaa,range(12,len(ssp_gdp_df.columns))]
            dx = x.diff()/ssp_gdp_df.iloc[aaa,range(12,len(ssp_gdp_df.columns))]
            dx = dx.replace([np.inf,-np.inf,np.nan],0)
            xf = []
            xfi = x0[0]
            for ggg in dx.index:
                rs = xfi*(1+dx[ggg])
                xf.append(round(rs*1e9)/1e9)
                xfi = rs
            ssp_gdp_df.iloc[aaa,range(12,len(ssp_gdp_df.columns))] = xf

    # Get the time parameters
    first_year = msgSC.set('cat_year').loc[msgSC.set(
            'cat_year')['type_year'] == 'firstmodelyear', 'year'].item()
    
    msg_yrs = [int(x) for x in msgSC.set('year')]
    hist_year = 2015
    demand_yrs = [x for x in msg_yrs if x >= hist_year]

    gmodel_df = pd.read_csv(path +  str('/') + str('/messageix_pak_R11_SAS.csv'))
    gmodel_df2 = gmodel_df[(gmodel_df['year'] >= 2015) & (gmodel_df['year'] < 2065)]

    df_region = gmodel_df2
    df_dem = df_region
    cmdtys = df_dem['commodity'].unique().tolist()

    # Get the historical demands for country in the region from excel sheet
    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    hist_act_df = xls_par.parse('historical_activity').dropna(axis =1)


    # GDP and population
    ssp_df = []
    for ccc in country.iso.values.tolist():

        c_ssp_gdp_df = ssp_gdp_df.loc[ ssp_gdp_df.Region == ccc ]
        c_ssp_pop_df = ssp_pop_df.loc[ ssp_pop_df.Region == ccc ]
        gdp = []
        pop = []
        gdpc = []

        for jjj in demand_yrs:

            if jjj < 2110:
                mmm = jjj
            else:
                mmm = 2100

            gdp.append(c_ssp_gdp_df[mmm].values[0])
            pop.append(c_ssp_pop_df[mmm].values[0])
            gdpc.append(1e3*c_ssp_gdp_df[mmm].values[0]/c_ssp_pop_df[mmm].values[0])

        ssp_df.append(pd.DataFrame({
            'year':demand_yrs,
            'gdp':gdp,
            'pop':pop,
            'gdpc':gdpc,
            'iso':ccc}))

    ssp_df = pd.concat(ssp_df)

    # initial df for demand data
    dmds = []

    # Go through each demand commodity and update demands then add to df above
    for cmdty in cmdtys: 

            # Isolate regional demands - give dataframe of loop commodity from our scenerio
            dff = df_region[df_region['commodity']==cmdty].sort_values('year').reset_index(drop=True)  

            # use dff as basis for country df so update node location
            dff['node'] = iso
            dff['node'] = dff['node'].str.replace('R11_SAS','R12_PAK')

            # Add percent change
            dff['pc'] = dff['value'].pct_change(periods = 1)

            dff = dff.replace([np.inf,-np.inf,np.nan],0)

            # list of technologies outputing on the demand level
            tec_list = list(set((msgSC.par(
                            'output', {'level': dff.level.values[0],
                                    'commodity': cmdty}))['technology']))

            # filter historical activity datafrme to include technologies for current commodity -- getting from excel
            if(len(tec_list)>1):
                ha = hist_act_df.loc[hist_act_df.technology.isin(tec_list)]
            else:
                ha = hist_act_df.loc[hist_act_df['technology'] == tec_list[0]]

            oe = msgSC.par('output', {
                'technology': ha.technology.unique(),
                'commodity': cmdty
            })

            # Ensure the necessary columns exist before proceeding
            if 'technology' in oe.columns and 'year_act' in oe.columns and 'value' in oe.columns:
                
                # Group by 'year_act' and 'technology', calculate the mean for the 'value' column
                # Make sure we only aggregate numeric columns (i.e., 'value')
                oe_mean = oe.groupby(['year_act', 'technology'], as_index=False).agg({'value': 'mean'})
                
                # Select the relevant columns
                oe = oe_mean[['technology', 'year_act', 'value']]

            else:
                print(f"Error: 'technology', 'year_act', or 'value' column is missing in output for commodity: {cmdty}")


            # update historical activity to account for efficiency losses at the output
            ha = pd.merge( ha, oe, on = ['year_act','technology'], how = 'left' ).dropna()
            ha['value'] = ha['value_x'] * ha['value_y']

 
                    
            for ind in dff.index:
                # print(f"Processing index: {ind}, Year: {dff.year.iloc[ind]}, Demand years: {demand_yrs}")

                # if the first year, use the historical demands calibrated to iea db
                if dff.year.iloc[ind] == demand_yrs[0]:
                    print(f"Initializing dm for the first year: {dff.year.iloc[ind]}")

                    # sum iea demands
                    dm = ha.loc[ha['year_act'] == dff.year.iloc[ind]].groupby('node_loc', as_index=False).agg({'value': 'sum'})

                    # Isolate GDP information
                    gdp = [ssp_df['gdp'].to_numpy()[0]]
                    gdpc = [ssp_df['gdpc'].to_numpy()[0]]

                    # Construct DataFrame for demand
                    dm = pd.DataFrame({
                        'node': dm['node_loc'].to_numpy(),
                        'value': dm['value'].to_numpy(),
                        'ei': dm['value'].to_numpy() / gdp,
                        'gdp': gdp,
                        'gdpc': gdpc
                    })

                    dt = dm['value']
                    dm0 = dm  # Initialize dm0 at the first iteration

                # Downscale the demands to match the growth rate from the regional pathway
                else:
                    # Ensure that `dm` has been initialized
                    if 'dm' not in locals():
                        print(f"Warning: dm not initialized for index {ind}. Initializing with default values.")
                        # Initialize `dm` with default values to avoid errors
                        dm = pd.DataFrame({
                            'node': ['default_node'],
                            'value': [1.0],  # You may choose a reasonable default value
                            'ei': [1.0],
                            'gdp': [1.0],
                            'gdpc': [1.0]
                        })
                        dm0 = dm

                    # Update total regional demands using growth rate from the global model
                    dt = dm['value'] * (1 + dff['pc'].iloc[ind])

                    # Update state equation variables
                    dm0 = dm
                    gdpf = [ssp_df.loc[ssp_df['year'] == dff.year.iloc[ind], 'gdp'].to_numpy()[0]]
                    gdpcf = [ssp_df.loc[ssp_df['year'] == dff.year.iloc[ind], 'gdpc'].to_numpy()[0]]

                    # Unload some variables and call the LP downscaling algorithm
                    names = dm0['node'].to_numpy()
                    vl = dm0['value'].to_numpy()
                    gdpco = dm0['gdpc'].to_numpy()

                    # Avoid zero intensities in future time steps for non-biomass technologies
                    if 'biomass' not in cmdty:
                        ei = vl / gdpco
                        vl = ei * gdpco

                    # Call the downscaling function
                    dmf = downscale_demands(
                        dt,   # target
                        vl,   # initial country demands
                        gdpco,  # initial country income
                        gdpcf,  # final country income
                        gdpf,  # final country total GDP
                        names  # node names
                    )

                    # Update demand state variables
                    dm = pd.DataFrame({
                        'node': dmf['node'].to_numpy(),
                        'value': dmf['value'].to_numpy(),
                        'ei': dmf['value'].to_numpy() / gdpf,
                        'gdp': gdpf,
                        'gdpc': gdpcf
                    })

                # Set the country level demand for this commodity and time step
                dff['value'].iloc[ind] = dm['value'].to_numpy()[0]

                # set the country level demand for this commodity and time step
                dff.value.iloc[ind] = dm.value.to_numpy()[0]

            # add demand for particular commodity to the model
            dmds.append(dff[list(msgSC.par('demand').columns)])

    dmds = pd.concat(dmds).reset_index()
    dmds['node'] = dmds['node'].str.replace('PAK','R12_PAK')

    #check out msgSC
    #msgSC.check_out()

    # add demand for particular commodity to the model
    msgSC.add_par('demand', dmds)
    print("-- Demands are updated --")

    # # commit changes to demands
    # msgSC.commit('demand data added!')