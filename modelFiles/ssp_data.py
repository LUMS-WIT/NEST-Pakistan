# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from openpyxl import load_workbook

def ssp_data( msgSC, path, iso , regionName, ssp):


    # population
    # SSP GDP data
    ssp_gdp_df = pd.read_excel(
            str(path) + str('/') + str('OECD_SSP_GDP_PPP.xlsx'),
            'OECD_SSP_GDP_PPP',
            header = 0)
    ssp_gdp_df = ssp_gdp_df.loc[ ( ssp_gdp_df.Scenario == ssp + '_v9_130325' )&( ssp_gdp_df.Region == iso ) ].reset_index(drop=True)

    # SSP population data

    ssp_pop_df = pd.read_excel(
            str(path) + str('/') + str('OECD_SSP_POP.xlsx'),
            'OECD_SSP_POP',
            header = 0)
    ssp_pop_df = ssp_pop_df.loc[ ( ssp_pop_df.Scenario == ssp + '_v9_130325' )&( ssp_pop_df.Region == iso  ) ].reset_index(drop=True)

    skip = ['FSM', 'KIR', 'MHL', 'NRU', 'PLW', 'TUV']

    # SSP data scaling to account for changes since release
    if not iso in skip:

        wbi_2015_df = pd.read_excel( str(path) + str('/') + str('wbi_pop_gdp_2015.xlsx'), 'wbi_pop_gdp_2015')
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

    df_out = ssp_pop_df.append(ssp_gdp_df).reset_index(drop=True)

    fl = str(path) + str('/') + str('ssp_check.xlsx')
    dat = pd.read_excel( str(path) + str('/') + str('ssp_check.xlsx'), ssp)
    if not dat.empty:
        dat = dat.loc[dat.Region!=iso]
    dat = dat.append(df_out)
    dat.to_excel(str(path) + str('/') + str('ssp_check.xlsx'), ssp, index=False)

    return df_out
