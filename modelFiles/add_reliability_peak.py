# -*- coding: utf-8 -*-
"""
This functions adds rating bins, reliability, and flexibility factors

"""
import pandas as pd
from itertools import product

def add_reliability_peak(msgSC, nodeName, path, suffix):

#%% 1) Initialization and importing data

    year = msgSC.set('year')
    xls_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))
    relbin = xls_set.parse('reliability')
    flex = xls_set.parse('flexfac')

    msgSC.check_out()

#%% 2) Adding penetration bin sizes (parameter "rating_bin")
    parname = 'rating_bin'
    df = pd.DataFrame(columns=['commodity', 'level', 'node', 'rating',
                               'technology', 'time', 'unit', 'value',
                               'year_act'], index=product(year, relbin.index))
    df.loc[:, 'commodity'] = [relbin.loc[i[1], 'commodity'] for i in df.index]
    df.loc[:, 'level'] = [relbin.loc[i[1], 'level'] for i in df.index]
    df.loc[:, 'node'] = nodeName
    df.loc[:, 'rating'] = [relbin.loc[i[1], 'rating'] for i in df.index]
    df.loc[:, 'technology'] = [relbin.loc[i[1], 'technology']
                               for i in df.index]
    df.loc[:, 'time'] = [relbin.loc[i[1], 'time'] for i in df.index]
    df.loc[:, 'unit'] = '-'
    df.loc[:, 'year_act'] = [i[0] for i in df.index]

    bin_size = df.copy()
    bin_size.loc[:, 'value'] = [relbin.loc[i[1], 'bin_size'] for i in df.index]
    bin_size.reset_index(inplace=True, drop=True)
    msgSC.add_par(parname, bin_size)
    print('> Parameter "{}" added!'.format(parname))

#%% 3) Adding parameter "reliability_factor"
    parname = 'reliability_factor'
    bin_reliability = df.copy()
    bin_reliability.loc[:, 'value'] = [relbin.loc[i[1],
                                       'bin_reliability'] for i in df.index]
    bin_reliability.reset_index(inplace=True, drop=True)
    msgSC.add_par(parname, bin_reliability)
    print('> Parameter "{}" added!'.format(parname))

#%% 4) Adding parameter "flexibility_factor"
    parname = 'flexibility_factor'
    for i in flex.index:
        if flex.loc[i, 'InOrOut'] == 'output':
            df = msgSC.par('output', {'technology': flex.loc[i, 'technology']})
        elif flex.loc[i, 'InOrOut'] == 'input':
            df = msgSC.par('input', {'technology': flex.loc[i, 'technology']})
        if not df.empty:
            df = df.drop_duplicates(['technology', 'mode', 'node_loc',
                                     'year_act', 'year_vtg'])
            df.loc[:, 'commodity'] = flex.loc[i, 'commodity']
            df.loc[:, 'level'] = flex.loc[i, 'level']
            df.loc[:, 'mode'] = flex.loc[i, 'mode']
            df.loc[:, 'node_loc'] = nodeName
            df.loc[:, 'time'] = flex.loc[i, 'time']
            df.loc[:, 'value'] = flex.loc[i, 'value']
            df.loc[:, 'rating'] = flex.loc[i, 'rating']
            df = df[msgSC.par(parname).columns]

            msgSC.add_par(parname, df)
    print('> Parameter "{}" added!'.format(parname))

#%% 3) Committing the additions

    msgSC.commit('reliability_factor, rating_bin, and flexibility_factor!')
