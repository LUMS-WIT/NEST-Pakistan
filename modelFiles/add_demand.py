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
from itertools import product


def add_demand(msgSC, msgWSC, nodeName, regionName, path, suffix, year_ref):

    first_year = msgSC.set('cat_year').loc[msgSC.set(
            'cat_year')['type_year'] == 'firstmodelyear', 'year'].item()
    msg_yrs = [int(x) for x in msgSC.set('year')]
    hist_year = msg_yrs[msg_yrs.index(first_year) - 1]
    demand_yrs = [x for x in msg_yrs if x >= hist_year]

    xls = pd.ExcelFile(str(path +'\Parameters' + suffix + '.xlsx'))
    demand_sheet = xls.parse('demand_data')
    demand_sheet = demand_sheet.set_index(['commodity'])
    lvl_name = demand_sheet['level'][0]

    parname = 'demand'
    df_region = msgWSC.par(parname, {'node': regionName}
                           ).set_index(['commodity', 'year'])
    df_dem = pd.DataFrame(columns=list(msgSC.par(parname).columns),
                          index=product(demand_sheet.index, demand_yrs))

    for i in df_dem.index:
        df_dem.loc[i, 'commodity'] = i[0]
        df_dem.loc[i, 'level'] = lvl_name
        df_dem.loc[i, 'year'] = int(i[1])
        df_dem['node'] = nodeName
        df_dem['time'] = 'year'
        df_dem['unit'] = 'GWa'
        # ------------------------------------------------------------
        if demand_sheet.loc[i[0], 'data type'] == 'rate':
            # This part generates demand time series based on a base year
            if demand_sheet.loc[i[0], 'data from'] == 'model':
                # reading data for demand from the model
                tec_list = list(set((msgSC.par(
                        'output', {'level': lvl_name, 'node_loc': nodeName,
                                   'commodity': i[0]}))['technology']))

                hist_act = sum(msgSC.par('historical_activity',
                                         {'technology': tec_list,
                                          'year_act': year_ref,
                                          'node_loc': nodeName})['value'])

                df_dem.loc[i, 'value'] = hist_act * (
                        1 + float(demand_sheet.loc[i[0], i[1]])) * (
                                float(demand_sheet.loc[i[0], 'multiplier']))
            else:
                # Reading base demand and growth rates from the Excel file
                dem_base = float(demand_sheet.loc[i[0], 'base year'])
                df_dem.loc[i, 'value'] = dem_base * (
                        1 + float(demand_sheet.loc[i[0], i[1]]))

        elif demand_sheet.loc[i[0], 'data type'] == 'value':
            if demand_sheet.loc[i[0], 'data from'] == 'model':
                # Reading demand data from a parent region
                df_dem.loc[i, 'value'] = df_region.loc[i, 'value'] * (
                                float(demand_sheet.loc[i[0], 'multiplier']))
            else:
                # Reading demand data directly from in Excel
                df_dem.loc[i, 'value'] = float(demand_sheet.loc[i[0], i[1]])

    df_dem = df_dem.reset_index(drop=True)

    if demand_sheet.loc[i[0], 'data type'] == 'rate':
        if demand_sheet.loc[i[0], 'data from'] == 'model':
            print('>Parameter "demand" in "{}" calibrated to IEA data in {}'
                  ' and growth rates from Excel.'.format(nodeName, year_ref))
        else:
            print('>Parameter "demand" in "{}" calibrated to {} and growth '
                  'rates  both from the Excel file.'.format(year_ref))
    elif demand_sheet.loc[i[0], 'data type'] == 'value':
        if demand_sheet.loc[i[0], 'data from'] == 'model':
            print('>Parameter "demand" in "{}" was calibrated to values'
              ' relative to demand in "{}".'.format(nodeName, regionName))
        else:
            print('>Parameter "demand" in "' + nodeName + '" was calibrated to'
              ' values from the Excel file.')

    msgSC.check_out()
    msgSC.add_par('demand', df_dem)
    msgSC.commit('demand data added!')
    return


