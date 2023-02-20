# -*- coding: utf-8 -*-
"""
    This function reads maximum potential of renewable energy sources and their
    capacity factor from the Excel file
"""

import pandas as pd
from itertools import product


def renewables(msgSC, nodeName, path, suffix):

    # 1) Initialization and importing data
    year = list(msgSC.set('year').astype(int))
    xls_par = pd.ExcelFile(str(path + '\\Parameters' + suffix + '.xlsx'))
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

    # Committing the additions
    msgSC.commit('added renewable capacity factors & renewable potentials')
    print('> Renewable potential and capacity factors added!')