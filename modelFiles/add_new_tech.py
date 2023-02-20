# -*- coding: utf-8 -*-
"""
This function add main parameters of new technologies (technical_lifetime, input, output, inv_cost, and var_cost)

"""
import pandas as pd
from itertools import product
from modelFiles.utilities.util1 import setdefaults
from modelFiles.utilities.util2 import reindexandadd

def add_new_tech(msgSC, node_loc, path, suffix):

#%% 1) Initialization and importing data from Excel
    print('> Adding new technologies and their relevant parameters from the Excel file...)')

    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    xls_set = pd.ExcelFile(str(path + '/ModelSetup'+suffix+'.xlsx'))
    sheet_para=xls_set.parse('par_list')
    par_compact=list(set(sheet_para['parameter'].loc[sheet_para['xlx_compact'] == 'yes']))
    sheet_tech=xls_set.parse('technology')
    technology_df = sheet_tech[sheet_tech['INCLUDE'] == 'y'].dropna(subset=['TECHNOLOGY'])

    horizon = [int(i) for i in list(msgSC.set('year'))]

    msgSC.check_out()
    msgSC.add_set('technology', list(set(technology_df['TECHNOLOGY'])))           #

#%% 2) Adding parameters mostly related to new technologies with a compact representation in the Excel input data
    # Parameter "technical_lifetime" should be imported first, as it will be used later for "input" and "output" years.
    parname = 'technical_lifetime'

    if parname in par_compact:
        sheet_par = xls_par.parse(parname)
        sheet_par = sheet_par.loc[sheet_par.technology.isin(list(set(msgSC.set('technology'))))]

        for i in sheet_par[sheet_par['add_tec'] == 'yes'].index:
            tec = sheet_par['technology'][i]
            vtg_yrs = [int(j) for j in sheet_par['vtg_years'][i].split(',')]
            vtg_yrs = [x for x in vtg_yrs if x in horizon]
            par = pd.DataFrame(columns=msgSC.par(parname).columns, index=vtg_yrs)
            par['year_vtg'] = [par.index[y] for y in range(0, len(par))]
            par['technology'] = tec
            par['unit'] = 'y'
            par['value'] = sheet_par['value'][i]

            for node_loc in sheet_par['node_loc'][i].split(','):
                par['node_loc'] = node_loc
                par = reindexandadd(par, parname, msgSC)

        par_compact.remove(parname)
        print('> Parameter "{}" was added for technologies in {}!'.format(parname,
              list(sheet_par[sheet_par['add_tec'] == 'yes']['technology'])))

    msgSC.commit('parameter "technical_lifetime" added for new technologies!')

#%% Parameter "input"

    msgSC.check_out()
    parname='input'

    if parname in set(par_compact) & set(xls_par.sheet_names):
        sheet_par = xls_par.parse(parname)
        sheet_par = sheet_par.loc[sheet_par.technology.isin(list(set(msgSC.set('technology'))))]

        for i in sheet_par[sheet_par['add_tec'] == 'yes'].index:
            tec = sheet_par['technology'][i]
            vtg_yrs = msgSC.par('technical_lifetime',{'technology':tec,
                                'node_loc':sheet_par['node_loc'][i].split(',')[0]}).year_vtg.tolist()
            act_p = msgSC.par('technical_lifetime',{'technology':tec,
                                'node_loc':sheet_par['node_loc'][i].split(',')[0]}).value
            yrs = [x for x in list(product(vtg_yrs, vtg_yrs)) if (x[0] >= x[1]) & (x[0] - x[1] <= act_p[vtg_yrs.index(x[1])])]
            com=sheet_par['commodity'][i].split(',')

            par = pd.DataFrame(columns=msgSC.par(parname).columns, index=product(yrs,com))
            par = setdefaults(par,node_loc)
            par['commodity'] = [par.index[y][1] for y in range(0, len(par))]
            par['year_act'] = [par.index[y][0][0] for y in range(0, len(par))]
            par['year_vtg'] = [par.index[y][0][1] for y in range(0, len(par))]
            par['level']=sheet_par['level'][i]
            par['technology'] = tec
            par['unit'] = 'GWa'
            par['value'] = sheet_par['value'][i]

            for node_loc in sheet_par['node_loc'][i].split(','):
                par['node_loc'] = node_loc
                par['node_origin'] = sheet_par['node_origin'][i].split(',')[sheet_par['node_loc'][i].split(',').index(node_loc)]
                par = reindexandadd(par, parname, msgSC)

        par_compact.remove(parname)
        print('> Parameter "{}" was added for technologies in {}!'.format(parname, list(
                sheet_par[sheet_par['add_tec'] == 'yes']['technology'])))

#%% Parameter "output"

    parname='output'

    if parname in set(par_compact) & set(xls_par.sheet_names):
        sheet_par = xls_par.parse(parname)
        sheet_par = sheet_par.loc[sheet_par.technology.isin(list(set(msgSC.set('technology'))))]

        for i in sheet_par[sheet_par['add_tec'] == 'yes'].index:
            tec = sheet_par['technology'][i]
            vtg_yrs = msgSC.par('technical_lifetime',{'technology':tec,
                                'node_loc':sheet_par['node_loc'][i].split(',')[0]}).year_vtg.tolist()
            act_p = msgSC.par('technical_lifetime',{'technology':tec,
                                'node_loc':sheet_par['node_loc'][i].split(',')[0]}).value
            yrs = [x for x in list(product(vtg_yrs, vtg_yrs)) if (x[0] >= x[1]) & (x[0] - x[1] <= act_p[vtg_yrs.index(x[1])])]
            com=sheet_par['commodity'][i].split(',')

            par = pd.DataFrame(columns=msgSC.par(parname).columns, index=product(yrs,com))
            par = setdefaults(par,node_loc)
            par['commodity'] = [par.index[i][1] for i in range(0, len(par))]
            par['year_act'] = [par.index[i][0][0] for i in range(0, len(par))]
            par['year_vtg'] = [par.index[i][0][1] for i in range(0, len(par))]
            par['level'] = sheet_par['level'][i]
            par['technology'] = tec
            par['unit'] = 'GWa'
            par['value'] = sheet_par['value'][i]

            for node_loc in sheet_par['node_loc'][i].split(','):
                par['node_loc'] = node_loc
                par['node_dest'] = sheet_par['node_dest'][i].split(',')[sheet_par['node_loc'][i].split(',').index(node_loc)]
                par = reindexandadd(par, parname, msgSC)

        par_compact.remove(parname)
        print('> Parameter "{}" was added for technologies in {}!'.format(parname, list(
                sheet_par[sheet_par['add_tec'] == 'yes']['technology'])))

#%% Parameter "inv_cost"

    parname='inv_cost'

    if parname in set(par_compact) & set(xls_par.sheet_names):
        sheet_par = xls_par.parse(parname)
        sheet_par = sheet_par.loc[sheet_par.technology.isin(list(set(msgSC.set('technology'))))]

        for i in sheet_par[sheet_par['add_tec'] == 'yes'].index:
            tec = sheet_par['technology'][i]
            vtg_yrs = msgSC.par('technical_lifetime',{'technology':tec,
                                'node_loc':sheet_par['node_loc'][i].split(',')[0]}).year_vtg.tolist()

            par = pd.DataFrame(columns=msgSC.par(parname).columns, index=vtg_yrs)
            par = setdefaults(par,node_loc)
            par['year_vtg'] = [par.index[y] for y in range(0, len(par))]
            par['technology'] = tec
            par['unit'] = 'GWa'
            par['value'] = sheet_par['value'][i]

            for node_loc in sheet_par['node_loc'][i].split(','):
                par['node_loc'] = node_loc
                par = reindexandadd(par, parname, msgSC)

        par_compact.remove(parname)
        print('> Parameter "{}" was added for technologies in {}!'.format(parname, list(
                sheet_par[sheet_par['add_tec'] == 'yes']['technology'])))

#%% Parameter "var-cost"

    parname='var_cost'

    if parname in set(par_compact) & set(xls_par.sheet_names):
        parname='var_cost'
        sheet_par = xls_par.parse(parname)
        sheet_par = sheet_par.loc[sheet_par.technology.isin(list(set(msgSC.set('technology'))))]

        for i in sheet_par[sheet_par['add_tec'] == 'yes'].index:
            tec = sheet_par['technology'][i]
            vtg_yrs = msgSC.par('technical_lifetime',{'technology':tec,
                                                      'node_loc':sheet_par['node_loc'][i].split(',')[0]}).year_vtg.tolist()
            act_p = msgSC.par('technical_lifetime',{'technology':tec,
                                                      'node_loc':sheet_par['node_loc'][i].split(',')[0]}).value
            yrs = [x for x in list(product(vtg_yrs, vtg_yrs)) if (x[0] >= x[1]) & (x[0] - x[1] <= act_p[vtg_yrs.index(x[1])])]

            par = pd.DataFrame(columns=msgSC.par(parname).columns, index=yrs)
            par = setdefaults(par,node_loc)
            par['year_act'] = [par.index[y][0] for y in range(0, len(par))]
            par['year_vtg'] = [par.index[y][1] for y in range(0, len(par))]
            par['technology'] = tec
            par['unit'] = 'GWa'
            par['value'] = sheet_par['value'][i]

            for node_loc in sheet_par['node_loc'][i].split(','):
                par['node_loc'] = node_loc
                par = reindexandadd(par, parname, msgSC)

        par_compact.remove(parname)
        print('> Parameter "{}" was added for technologies in {}!'.format(parname, list(sheet_par[sheet_par['add_tec'] == 'yes']['technology'])))

#%% 3) Commiting the new additions

    msgSC.commit('New technologies and parameters added!')

