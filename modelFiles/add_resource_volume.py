# -*- coding: utf-8 -*-
"""
This function adds fossil fuel resource_volume to a MESSAGE scenario.
"""
import pandas as pd
from modelFiles.utilities.util2 import reindexandadd


def add_resource_volume(msgSC, msgWSC, nodeName, regionName, path, suffix):

    # 1) Initialization and importing data from Excel

    xls = pd.ExcelFile(str(path + '/Parameters' + suffix + '.xlsx'))
    xls_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))
    res = xls.parse('resource')
    sheet_par = xls_set.parse('par_list')

    # 2) Reading data from MESSAGE global
    msgSC.check_out()
    parname = 'resource_volume'
    par_res = msgWSC.par(parname, {'node': regionName})

    # Removing some commodities that are extra (specified by the modeler)
    pars = sheet_par['parameter'].loc[sheet_par['commodityRemoval'] != 'n']
    if parname in list(set(pars)):
        com_list = sheet_par.loc[sheet_par['parameter'] == parname,
                                 'commodityRemoval'].item().split(',')
        for com in com_list:
            par_res = par_res[par_res['commodity'] != com]

    for c in [x for x in res['Commodity'].unique() if
              x not in msgSC.set('commodity').tolist()]:
        msgSC.add_set('commodity', c)

    par = par_res.copy()
    par.index = zip(par['commodity'], par['grade'])
    res = res.set_index(['Commodity', 'Grade'])
    par_new = pd.DataFrame(index=res.index, columns=par.columns)

    for i in par_new.index:
        # A percentage of resources in the parent region from Excel file
        if res.loc[i, 'UsingPercent'] == 'Yes' and i in par.index:
            par_new['value'][i] *= res.loc[i, 'Percentage']

        else:
            # Or using resource volumes directly from the Excel file
            par_new['value'][i] = res.loc[i, 'Volume']

        par_new.loc[i, 'commodity'] = i[0]
        par_new.loc[i, 'grade'] = i[1]

    par_new['unit'] = par['unit'].mode().any()
    par_new['node'] = nodeName
    par_new = reindexandadd(par_new, parname, msgSC)
    print('> Resource volume data added!')

    # 3) Adjustment of hist act of extraction tecs based on new resource vol
    par_new = par_new.set_index('commodity')
    parname = 'historical_activity'
    par_hist = msgSC.par(parname, {'technology': ['coal_extr','oil_extr_1', 'gas_extr_1'
                                                  ,'gas_extr_2']})
    par_hist_new = par_hist.copy()
    dict_fuel = {'crude_': 'oil_extr_', 'gas_': 'gas_extr_'}

    res = res.reset_index()

    for com in dict_fuel.keys():
        parline = par_hist.loc[par_hist['technology'] == dict_fuel[com]+str(1)]
        parline = parline.loc[parline['year_act'] == max(parline['year_act'])]
        if not parline.empty:
            hist_ref = float(parline['value'])

            for i in range(1, 8):
                commodity = com + str(i)
                tec = dict_fuel[com]+str(i)
                if hist_ref > 0:
                    if commodity not in par_new.index:
                        print('WARNING: historical activity for {}, but no '
                              'resource volume for {}. Please check'
                              '!!!'.format(tec, commodity))
                        break
                else:
                    break

                share = float(res.loc[res['Commodity'] == commodity,
                                      'Hist_max'])
                if share * par_new['value'][commodity] < hist_ref:
                    par_hist_new.loc[par_hist_new['technology'] == tec,
                                     'value'] = share * par_new['value'
                                                                ][commodity]
                    hist_ref = hist_ref - share*par_new['value'][commodity]
                elif i > 1:
                    parline_new = parline.copy()
                    parline_new['technology'] = tec
                    parline_new['value'] = hist_ref
                    par_hist_new = par_hist_new.append(parline_new,
                                                       ignore_index=True)
                    break
                else:
                    break
    if not par_hist_new.empty:
        msgSC.add_par(parname, par_hist_new)
        print('> Historical activity of extraction technologies updated'
              ' based on new resource volumes!')

    # Commiting changes to the database
    msgSC.commit('added resource_volume!')
