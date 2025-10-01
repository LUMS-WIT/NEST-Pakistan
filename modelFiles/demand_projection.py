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

    # country and region name mapping - using iso_reg.xlsx file
    reg_df = pd.read_excel( str(path) +
                           str('/') + str('iso_reg.xlsx'), 'Sheet1')
    reg_df['node'] = str('R14_') + reg_df['node'].astype(str)
    isoreg = reg_df[reg_df['node']==reg]
    isoreg = isoreg['iso'].tolist()

    # country metadata regarding data sources e.g., iea, platts, ssp, adb etc
    country_map = pd.read_excel( str(path) + str('/') + str(nodeName) +
                                str('_map.xlsx'), 'country_map')
    country = country_map.loc[(country_map['include']=='Y')&
                              (country_map['msg_14'] == reg.split('_')[1])]
#    iea = country.loc[country.iso==iso].iea[0]

    #################################################################################################3
    # # SSP GDP data
    # ssp_gdp_df = pd.read_excel(
    #         str(path) + str('/') + str('OECD_SSP_GDP_PPP.xlsx'), 'OECD_SSP_GDP_PPP',
    #         header = 0 )


    # ssp_gdp_df = ssp_gdp_df.loc[ ( ssp_gdp_df.Scenario == ssp+ '_v9_130325' )&
    #                             ( ssp_gdp_df.Region == iso ) ].reset_index(
    #                                 drop=True)

    # # SSP population data
    # ssp_pop_df = pd.read_excel(
    #         str(path) + str('/') + str('OECD_SSP_POP.xlsx'),
    #         'OECD_SSP_POP',
    #         header = 0 )

    # ssp_pop_df = ssp_pop_df.loc[ ( ssp_pop_df.Scenario == ssp + '_v9_130325' )&(
    #     ssp_pop_df.Region == iso  ) ].reset_index(drop=True)
    ################################################################################################### 

    # SSP GDP data
    gdp_df = pd.read_csv(str(path) + str('/') + str("GDP_PPP_SSP2.csv"))
    long_gdp_df = pd.melt(
        gdp_df,
        id_vars=["Model", "Scenario", "Region", "Variable", "Unit"],
        var_name="Year",
        value_name="GDP"
    ) # convert to long format for merging purpose

    ssp_gdp_df = long_gdp_df.loc[long_gdp_df.Scenario == ssp].reset_index(drop=True)
    hist_gdp_df = long_gdp_df.loc[long_gdp_df.Scenario == "Historical Reference"].reset_index(drop=True)
    hist_gdp_df["Scenario"] = "SSP2"
    ssp_gdp_df = pd.merge( hist_gdp_df, ssp_gdp_df,  how = 'outer' ).dropna()

    ssp_gdp_df = ssp_gdp_df.pivot_table(
        index=["Model", "Scenario", "Region", "Variable", "Unit"],
        columns="Year",
        values="GDP"
    ).reset_index() # convert back to wide

    # SSP population data
    pop_df = pd.read_csv(str(path) + str('/') + str("populationSSP2.csv"))

    long_pop_df = pd.melt(
        pop_df,
        id_vars=["Model", "Scenario", "Region", "Variable", "Unit"],
        var_name="Year",
        value_name="GDP"
    ) # convert to long format for merging purpose

    ssp_pop_df = long_pop_df.loc[long_pop_df.Scenario == ssp].reset_index(drop=True)
    hist_pop_df = long_pop_df.loc[long_pop_df.Scenario == "Historical Reference"].reset_index(drop=True)
    hist_pop_df["Scenario"] = "SSP2"
    ssp_pop_df = pd.merge( hist_pop_df, ssp_pop_df,  how = 'outer' ).dropna()

    ssp_pop_df = ssp_pop_df.pivot_table(
        index=["Model", "Scenario", "Region", "Variable", "Unit"],
        columns="Year",
        values="GDP"
    ).reset_index() # convert back to wide


    # # SSP data scaling to account for changes since release
    # ################################################################################################
    # wbi_2015_df = pd.read_excel( str(path) + str('/') + str('wbi_pop_gdp_2015.xlsx'), 'wbi_pop_gdp_2015')
    # wbi_2015_df = wbi_2015_df.loc[(wbi_2015_df.iso == iso)].reset_index(drop=True)
    # for aaa in ssp_pop_df.index:
    #     if not (wbi_2015_df.loc[wbi_2015_df['iso']==ssp_pop_df.Region[aaa]]).empty:
    #         x0 = [ 1e-6*wbi_2015_df.loc[wbi_2015_df['iso']==ssp_pop_df.Region[aaa]].pop_2015.to_numpy()[0] ] # convert population of pakistan in 2015 to a numpy float
    #         x = ssp_pop_df.iloc[aaa,range(12,len(ssp_pop_df.columns))] # extract ssp pop values from 2015 and onward
    #         dx = x.diff()/ssp_pop_df.iloc[aaa,range(12,len(ssp_pop_df.columns))] # 5year-on-5year growth values 
    #         dx = dx.replace([np.inf,-np.inf,np.nan],0)
    #         xf = [] # will contain scaled ssp projections wrt world bank value in 2015
    #         xfi = x0[0]
    #         for ggg in dx.index:
    #             rs = xfi*(1+dx[ggg])
    #             xf.append(round(rs*1e6)/1e6)
    #             xfi = rs
    #         ssp_pop_df.iloc[aaa,range(12,len(ssp_pop_df.columns))] = xf

    # #################################################################################################
    # for aaa in ssp_gdp_df.index:
    #     if not (wbi_2015_df.loc[wbi_2015_df['iso']==ssp_gdp_df.Region[aaa]]).empty:
    #         x0 = [ 1e-9*wbi_2015_df.loc[wbi_2015_df['iso']==ssp_gdp_df.Region[aaa]].gdp_ppp_usd_2015.to_numpy()[0] ]
    #         x = ssp_gdp_df.iloc[aaa,range(12,len(ssp_gdp_df.columns))]
    #         dx = x.diff()/ssp_gdp_df.iloc[aaa,range(12,len(ssp_gdp_df.columns))]
    #         dx = dx.replace([np.inf,-np.inf,np.nan],0)
    #         xf = []
    #         xfi = x0[0]
    #         for ggg in dx.index:
    #             rs = xfi*(1+dx[ggg])
    #             xf.append(round(rs*1e9)/1e9)
    #             xfi = rs
    #         ssp_gdp_df.iloc[aaa,range(12,len(ssp_gdp_df.columns))] = xf

    # Get the time parameters
    first_year = msgSC.set('cat_year').loc[msgSC.set(
            'cat_year')['type_year'] == 'firstmodelyear', 'year'].item() # first model year
    msg_yrs = [int(x) for x in msgSC.set('year')] # all message years (1950 and onward)
    # hist_year = 2020 ############################################################################
    hist_year = 2020
    demand_yrs = [x for x in msg_yrs if x >= hist_year] # ? 2015 and onward
    
    # regional demands (R11_SAS) from the global model file
    # gmodel_df = pd.read_csv(path +  str('/') + str('/messageix_pak_R11_SAS.csv'))
    # gmodel_df2 = gmodel_df[(gmodel_df['year'] >= 2015) & (gmodel_df['year'] < 2065)] # filtered for the year range

    gmodel_df = pd.read_excel(path +  str('/') + str('/global_model.xlsx'), sheet_name="demand")
    gmodel_df2 = gmodel_df[(gmodel_df['year'] >= 2020) & (gmodel_df['year'] <= 2070) & (gmodel_df['node'] == "R11_SAS")] # filtered for the year range

    df_region = gmodel_df2 # filtered regional demands (R11_SAS) from the global model file
    df_dem = df_region # filtered regional demands (R11_SAS) from the global model file
    cmdtys = df_dem['commodity'].unique().tolist() # useful level commodities: i_therm etc. 
    cmdtys.remove("transport")
    # ##############################################################################################
    # # Get the historical demands for country in the region from excel sheet
    # xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx') # similar to the model file. contains selective parameters including historical_activity, in_cost, input, output etc.
    # hist_act_df = xls_par.parse('historical_activity').dropna(axis =1) 
    # ##############################################################################################
    hist_act_df = msgSC.par("historical_activity")

    
    # GDP and population
    ssp_df = []
    for ccc in country.iea.values.tolist(): # ccc = PAK, country is the metadata df with 1 row

        c_ssp_gdp_df = ssp_gdp_df.loc[ ssp_gdp_df.Region == ccc ] # same as ssp_gdp_df since we already filtered it
        c_ssp_pop_df = ssp_pop_df.loc[ ssp_pop_df.Region == ccc ]
        gdp = []
        pop = []
        gdpc = [] # gdp per capita

        for jjj in demand_yrs: # demand_yrs = 2015 till 2110 for now

            if jjj < 2110:
                mmm = str(jjj)
            else:
                mmm = "2100"

            gdp.append(c_ssp_gdp_df[mmm].values[0]) # just a list of values column from ssp_gdp_df
            pop.append(c_ssp_pop_df[mmm].values[0]) # list of values column from ssp_pop_df
            gdpc.append(1e3*c_ssp_gdp_df[mmm].values[0]/c_ssp_pop_df[mmm].values[0]) # gdp / populatiom

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
            dff = df_region[df_region['commodity']==cmdty].sort_values('year').reset_index(drop=True)  # sorting by year for each commodity

            # use dff as basis for country df so update node location
            dff['node'] = iso # R11_SAS replaced by PAK
            # dff['node'] = dff['node'].str.replace('R11_SAS','R12_PAK')

            # Add percent change
            dff['pc'] = dff['value'].pct_change(periods = 1) # percentage changes for the demand of each useful level commodity at the regional level R12_SAS

            dff = dff.replace([np.inf,-np.inf,np.nan],0)

            # useful/demand level technologies that come under the cmdty
            tec_list = list(set((msgSC.par(
                            'output', {'level': dff.level.values[0],
                                    'commodity': cmdty}))['technology'])) 

            # filter historical activity datafrme to include technologies for current commodity -- getting from excel
            # check historical activity of the technologies we just shortlisted
            if(len(tec_list)>1):
                ha = hist_act_df.loc[hist_act_df.technology.isin(tec_list)]
            else:
                ha = hist_act_df.loc[hist_act_df['technology'] == tec_list[0]]

            # output df filtered for the cmdty and its useful level technologies
            oe = msgSC.par('output', {
                'technology': ha.technology.unique(), # same as tec_list
                'commodity': cmdty
            })

            # Ensure the necessary columns exist before proceeding
            if 'technology' in oe.columns and 'year_act' in oe.columns and 'value' in oe.columns:
                
                # Group by 'year_act' and 'technology', calculate the mean for the 'value' (e.g., 1.0, 0.11, 0.03 etc) column
                # Make sure we only aggregate numeric columns (i.e., 'value')
                oe_mean = oe.groupby(['year_act', 'technology'], as_index=False).agg({'value': 'mean'})
                
                # Select the relevant columns
                oe = oe_mean[['technology', 'year_act', 'value']]

            else:
                print(f"Error: 'technology', 'year_act', or 'value' column is missing in output for commodity: {cmdty}")


            # update historical activity to account for efficiency losses at the output
            ha = pd.merge( ha, oe, on = ['year_act','technology'], how = 'left' ).dropna() # ha and oe values in the same df
            ha['value'] = ha['value_x'] * ha['value_y'] # multiply to account for efficiency losses

 
                    
            for ind in dff.index: # iterate through each year's demand for the useful level cmdty
                # print(f"Processing index: {ind}, Year: {dff.year.iloc[ind]}, Demand years: {demand_yrs}")

                # if the first year, use the historical demands calibrated to iea db
                if dff.year.iloc[ind] == demand_yrs[0]:
                    print(f"Initializing dm for the first year: {dff.year.iloc[ind]}")

                    # sum iea demands
                    # sum historical activity of all technologies (in tec_list) for the current iteration year 
                    dm = ha.loc[ha['year_act'] == dff.year.iloc[ind]].groupby('node_loc', as_index=False).agg({'value': 'sum'})

                    # Isolate GDP and GDPC information of first year
                    gdp = [ssp_df['gdp'].to_numpy()[0]]
                    gdpc = [ssp_df['gdpc'].to_numpy()[0]]

                    # Construct DataFrame for demand in first model year
                    dm = pd.DataFrame({
                        'node': dm['node_loc'].to_numpy(),
                        'value': dm['value'].to_numpy(),
                        'ei': dm['value'].to_numpy() / gdp, # ei = activity / gdp
                        'gdp': gdp,
                        'gdpc': gdpc
                    })

                    dt = dm['value'] # total ha/demand of the cmdty - just the dm value
                    dm0 = dm  # Initialize dm0 at the first iteration - whole df

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
                    # total demand of the current iteration cmdty for the current iteration year using regional growth rate according to the global model result
                    dt = dm['value'] * (1 + dff['pc'].iloc[ind]) 

                    # Update state equation variables
                    dm0 = dm # previous year's demands
                    gdpf = [ssp_df.loc[ssp_df['year'] == dff.year.iloc[ind], 'gdp'].to_numpy()[0]] # extract gdp value for the current iteration year from ssp_df
                    gdpcf = [ssp_df.loc[ssp_df['year'] == dff.year.iloc[ind], 'gdpc'].to_numpy()[0]] # extract gdpc value for the current iteration year from ssp_df

                    # Unload some variables and call the LP downscaling algorithm
                    names = dm0['node'].to_numpy() # Pakistan
                    vl = dm0['value'].to_numpy() # previous year's demand for the current iteration cmdty
                    gdpco = dm0['gdpc'].to_numpy()  # previous year's gdpc for the current iteration cmdty

                    # Avoid zero intensities in future time steps for non-biomass technologies
                    if 'biomass' not in cmdty:
                        ei = vl / gdpco # ei = activity / gdpc (for non-biomass)
                        vl = ei * gdpco

                    # Call the downscaling function
                    dmf = downscale_demands(
                        dt,   # target
                        vl,   # initial country demands
                        gdpco,  # initial country gdpc
                        gdpcf,  # final country gdpc
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