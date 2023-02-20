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
from modelFiles.parameter_modifier import import_parameter, copy_parameter
from scipy.optimize import linprog

def demands(msgSC, msgWSC, path, ssp):



    nodeName = 'Pakistan'     # Name of the stand-alone model region.
    regionName = 'R14_SAS'      # Name of the reference region in MESSAGE global
    ieaName = "'Pakistan'"         # In the form of: "'Russian Federation'"
    plattsName = 'Pakistan'        # In the form of: 'Russia'
    suffix = '_PAK'             # The extension of Excel files, like: '_RU'
    iso = 'PAK'
    reg = regionName


    # region to country mapping
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

    df_region = msgWSC.par('demand',{'node': reg,'year':demand_yrs})
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

        # Isolate regional demands
        dff = df_region[df_region['commodity']==cmdty].sort_values('year').reset_index(drop=True)

        # use dff as basis for country df so update node location
        dff['node'] = iso
        dff['node'] = dff['node'].str.replace('PAK','Pakistan')

        # Add percent change
      # dff['pc'] = dff['value'].diff()
        dff['pc'] = dff['value'].pct_change(periods = 1)
      #  for iii in dff.index:
      #       if iii == 0:
      #            dff.pc[iii] = 0
      #    else:
      #           dff.pc[iii] = ( dff.pc[iii] / dff.value[(iii-1)] ) -1

        dff = dff.replace([np.inf,-np.inf,np.nan],0)

        # list of technologies outputing on the demand level
        tec_list = list(set((msgSC.par(
                        'output', {'level': dff.level.values[0],
                                   'commodity': cmdty}))['technology']))

        # filter historical activity datafrme to include technologies for current commodity
        if(len(tec_list)>1):
            ha = hist_act_df.loc[hist_act_df.technology.isin(tec_list)]
        else:
            ha = hist_act_df.loc[hist_act_df['technology'] == tec_list[0]]

        # output efficiency for tecs (typically = 1)
        oe = msgSC.par( 'output', {
                            'technology': ha.technology.unique(),
                            'commodity': cmdty}).groupby(['year_act','technology']).mean().reset_index()
        oe = oe[['technology','year_act','value']]

        # update historical activity to account for efficiency losses at the output
        ha = pd.merge( ha, oe, on = ['year_act','technology'], how = 'left' ).dropna()
        ha['value'] = ha['value_x'] * ha['value_y']

        # Go through each demand year and scale the historical demands to follow regional growth pattern
        # must be sorted by year because the state equations are updated sequentially
        for ind in dff.index:

            # if the first year, use the historical demands calibrated to iea db
            if dff.year.iloc[ind] == demand_yrs[0]:

                # isolate the regonal demand target
                # dt = dff.value.iloc[ind]

                # sum iea demands
                dm = ha.loc[ha['year_act']==dff.year.iloc[ind]].groupby('node_loc').sum().reset_index()
                dm = dm[['node_loc','value']]

                # isolate gdp information
                gdp = []
                gdpc = []


                gdp.append(ssp_df.gdp.to_numpy()[0])
                gdpc.append(ssp_df.gdpc.to_numpy()[0])

                dm = pd.DataFrame({'node':dm.node_loc.to_numpy(),
                                    'value':dm.value.to_numpy(),
                                    'ei':dm.value.to_numpy()/gdp,
                                    'gdp':gdp,
                                    'gdpc':gdpc})

                dt = dm.value
                dm0 = dm


            # downscale the demands to match growth rate from regional pathway
            else:

                # update total regional demands using growth rate from global model
                dt = dm.value * (1 + dff.pc.iloc[ind])

                # update state equation variables
                dm0 = dm
                gdpf = []
                gdpcf = []

                inds = (ssp_df['year']==dff.year.iloc[ind])
                gdpf.append(ssp_df.loc[inds,'gdp'].to_numpy()[0])
                gdpcf.append(ssp_df.loc[inds,'gdpc'].to_numpy()[0])

                # unload some variables and call LP downscaling algorithm
                names = dm0.node.to_numpy()
                vl = dm0.value.to_numpy()
                gdpco = dm0.gdpc.to_numpy()

                # don't allow 0 intensities in future time steps if not biomass technologies
                if not 'biomass' in cmdty:
                    ei = vl / gdpco
                   # ei[np.where(ei==0)] = min(ei[ei.nonzero()])
                    vl = ei * gdpco

                dmf = downscale_demands(
                    dt, # target
                    vl, # initial country demands
                    gdpco, # initial country income
                    gdpcf, # final country income
                    gdpf, # final country total GDP
                    names) # node names

                # update demand state variables
                dm = pd.DataFrame({'node':dmf.node.to_numpy(),
                                    'value':dmf.value.to_numpy(),
                                    'ei':dmf.value.to_numpy()/gdpf,
                                    'gdp':gdpf,
                                    'gdpc':gdpcf})

            # Check
            print('--- cmdty ---')
            print(cmdty)

            print('--- dm ---')
            print(dm)

            print('--- country: total ---')
            print(dff.value.iloc[ind])

            print('---country: pc set----')
            print(dff.pc.iloc[ind])

            print('---country: pc act----')
            print(dm.value.sum()/dm0.value.sum()-1)

            print('--- target ---')
            print(dt)

            print('---  total ---')
            print(dm.value.sum())

            # set the country level demand for this commodity and time step
            dff.value.iloc[ind] = dm.value.to_numpy()[0]

            if ind > 0 :
                print('--- diff ---')
                print(((dff.value.iloc[ind]/dff.value.iloc[ind-1])-1))
                print(dff.pc.iloc[ind])

        # add demand for particular commodity to the model
        dmds.append(dff[list(msgSC.par('demand').columns)])

    dmds = pd.concat(dmds).reset_index()
    dmds['node'] = dmds['node'].str.replace('PAK','Pakistan')

    # check out scenario
    msgSC.check_out()

    # add demand for particular commodity to the model
    msgSC.add_par('demand', dmds)

    # # commit changes to demands
    msgSC.commit('demand data added!')
