# -*- coding: utf-8 -*-
"""
This function reads and modifies the cost of fossil fuel resources either
from a MESSAGE model or as raw data in the Excel files
"""

import pandas as pd
from itertools import product
from modelFiles.utilities.util1 import setdefaults
from modelFiles.utilities.util2 import reindexandadd


def add_resource_cost(msgSC, nodeName, path, suffix):

    # 1) Initialization and importing data from Excel

    firstyear = msgSC.firstmodelyear

    xls = pd.ExcelFile(str(path + '/Parameters' + suffix + '.xlsx'))
    res_df = xls.parse('resourceCost')
    res_df = res_df[res_df['commodity'].isin(msgSC.set('commodity'))]
    res_df.index = zip(res_df['commodity'], res_df['grade'])

    msgSC.check_out()

    # 2) Changing the extraction cost through "inv_cost" parameter
    parname = 'inv_cost'
    resource = msgSC.par('input', {'level': 'resource'})
    tecs_extr = [tec for tec in list(set(resource['technology'])) if
                 'ch4' not in tec]
    com_extr = msgSC.par('input', {'technology': tecs_extr}
                         )[['commodity', 'technology']].drop_duplicates()
    com_extr['grade'] = 'a'
    com_extr.index = zip(com_extr['commodity'], com_extr['grade'])
    par_inv = msgSC.par(parname, {'technology': tecs_extr}
                        )[['technology', 'value', 'year_vtg']]
    par_inv = par_inv.pivot('technology', 'year_vtg').fillna(0)
    par_inv.columns = par_inv.columns.droplevel(0)
    par_inv_div = par_inv.div(par_inv[firstyear], axis=0)

    par = pd.DataFrame(columns=list(msgSC.par(parname).columns),
                       index=product(com_extr['technology'], par_inv.columns))
    par = setdefaults(par, nodeName)

    for i in par.index:
        par.loc[par.index == i, 'year_vtg'] = int(i[1])
        par.loc[par.index == i, 'technology'] = i[0]

        # This part of the code generates resource extraction cost time series
        # based on the MESSAGE Global region and a multiplier from Excel
        tec = com_extr.index[com_extr['technology'] == i[0]][0]
        multiplier = res_df.loc[res_df.index == tec, 'cost_multiplier']
        if list(res_df.loc[res_df.index == tec, 'MESSAGE_cost'])[0] == 'Yes':
            par.loc[par.index == i, 'value'] = float(par_inv[i[1]][i[0]]
                                                     ) * int(multiplier)

        # This part generates resource extraction cost time series by
        # a multiplier from Excel and also time-dependant rates from "inv_cost"
        else:
            extr_c = float(res_df.loc[res_df.index == tec, 'extraction_cost'])
            par.at[i, 'value'] = extr_c * float(par_inv_div[i[1]][i[0]]
                                                ) * int(multiplier)

    par['unit'] = 'USD/kWa'
    reindexandadd(par, parname, msgSC)
    print('> Resource cost curve data added!')

    # 3) Treatment of the cost of coal and lignite in grades not entirely
    # represnted in the parameter "inv_cost"
    parname = 'resource_cost'
    par_cost = msgSC.par(parname)
    par_cost.index = zip(par_cost['commodity'], par_cost['grade'])

    #grades = [('coal', 'c'), ('coal', 'd'), ('lignite', 'c'), ('lignite', 'd')]
    grades = [('coal', 'c'), ('coal', 'd')]
    
    for i in grades:

        # Cost from parent region and a multiplier from the Excel file
        if res_df['MESSAGE_cost'][i] == 'Yes':
            par_cost.loc[par_cost.index == i, 'value'] *= res_df[
                'cost_multiplier'][i]
            reindexandadd(par_cost.loc[par_cost.index == i], parname, msgSC)

        # Cost from base year and multiplier from the Excel,
        # This will be scaled based on the growth rate in "inv_cost" of the
        # extraction technology. Cost of "coal_extr" for grade "a" is deducted.
        else:
            extr_c = res_df['extraction_cost'][i]*res_df['cost_multiplier'][i]
            cost_inv = (par_inv_div.loc[par_inv_div.index == i[0]+'_extr'
                                        ].transpose() * extr_c)[i[0]+'_extr']
            df = par.loc[par['technology'] == i[0] + '_extr'].copy()
            df = df.rename(index=str, columns={"year_vtg": "year",
                                               "node_loc": "node",
                                               "technology": "commodity"})
            cost_inv.index = df.index

            df['commodity'] = i[0]
            df['grade'] = i[1]
            df['value'] = cost_inv - df['value']

            reindexandadd(df, parname, msgSC)

    # Commiting the changes
    msgSC.commit('Added resource_cost!')
