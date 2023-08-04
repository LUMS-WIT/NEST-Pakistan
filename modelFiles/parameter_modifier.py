 # -*- coding: utf-8 -*-
"""
This scripts include functions for changing, copying, replacing, and removing parameters in a MESSAGE model

"""
import pandas as pd
from math import isnan

#%%
def import_parameter(msgSC, path, suffix):

    """
    This function reads parameters directly from the Excel file "Parameters_<suffix>.xlsx". Those parameters
    that are specified as "compact" in the sheet "parameter" of the file "ModelSetup.xlsx" are NOT read here.
    Hence, this function only read parameters specified as a dataframe in the respective Excel sheet.

    """
    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    xls_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))

    sheet_par = xls_set.parse('par_list')
    par_compact = list(set(sheet_par['parameter'].loc[sheet_par['xlx_compact'] == 'yes']))

    dict_par = {}
    par_list = [p for p in set(xls_par.sheet_names) & set(msgSC.par_list()) if p not in  par_compact]

    for par in par_list:
        dict_par[par] = xls_par.parse(par)

    msgSC.check_out()
    print('> Importing parameters from the Excel file...')
    for par in dict_par.keys():
        if 'technology' in dict_par[par].columns:
            dict_par[par] = dict_par[par][dict_par[par]['technology'].isin(list(msgSC.set('technology')))]

        msgSC.add_par(par, dict_par[par])
        if not dict_par[par].empty:
            print('- {}'.format(par))
    msgSC.commit('Excel parameters added!')

#%%
def copy_parameter(msgSC, path, suffix):

    """
    This function reads the content of an existing parameter, let's say for a technology, and copies
    the whole or a part of that parameter to a another technology.
    The list of copying parameters and attributes are read from the Excel file "Parameters_<suffix>.xlsx", the sheet "parCopy".
    Notice: only those parameters will be copied that are marked "yes" in the column "active" in the respective Excel sheet!
    This is to save time in running the function by deactivating the already copied parameters in multiple runs.

    """
    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    df_copy = xls_par.parse('parCopy')

    msgSC.check_out()

    for i in df_copy[df_copy['active'] == 'yes'].index:
        dictfrom = {}
        par_copy = df_copy['parameter'][i]
        columns = df_copy['columns'][i].split(',')
        tec_from = df_copy['from'][i].split(',')
        tec_to = df_copy['to'][i].split(',')   # BZ: The parameter can be copied to more than one technology at once

        for col in columns:
            dictfrom[col] = tec_from[columns.index(col)]

        dict_p = msgSC.par(par_copy,dictfrom)
        for col in columns:
            dict_p[col] = tec_to[columns.index(col)]

        if str(df_copy['attribute'][i]) != 'nan':
            dict_p[df_copy['attribute'][i]] = dict_p[df_copy['attribute'][i]]*df_copy['multiply'][i]+df_copy['plus'][i]

        msgSC.add_par(par_copy,dict_p)
        print('> Parameter "{}" was copied from {} to {}!'.format(par_copy, tec_from, tec_to))

    msgSC.commit('Excel parameters copied!')

#%%
def replace_parameter(msgSC, path, suffix):

    """
    This function reads the content of an existing parameter and replaces the whole or a part of that parameter.
    The list of parameters and attributes to be replaced are read from the Excel file "Parameters_<suffix>.xlsx", the sheet "parReplace".
    Notice: only those parameters will be replaced that are marked "yes" in the column "active" in the respective Excel sheet!
    This is to save time in running the function by deactivating the already replaced parameters in new runs.
    """

    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    df_rep = xls_par.parse('parReplace')

    msgSC.check_out()

    for i in df_rep[df_rep['active'] == 'yes'].index:
        par_rep = df_rep['parameter'][i]
        dictrep = {}
        columns = df_rep['columns'][i].split(',')
        tec_from = df_rep['columns_value'][i].split(',')

        for col in columns:
            dictrep[col] = tec_from[columns.index(col)]

        df_rep_rem = msgSC.par(par_rep,dictrep)
        df_rep_add = df_rep_rem.copy()
        df_rep_add[df_rep['attribute'][i]] = df_rep['value'][i]

        msgSC.remove_par(par_rep,df_rep_rem)
        msgSC.add_par(par_rep,df_rep_add)
        print('> In parameter "{}" for "{}": the value of "{}" was replaced by "{}"!'.format(par_rep,
              tec_from, df_rep['attribute'][i], df_rep['value'][i]))
    msgSC.commit('replaced parameters of tecs')

#%%
def remove_parameter(msgSC, path, suffix):

    """
    This function removes the whole or a part of  an existing parameter.
    The list of parameters and attributes to be removed are read from the Excel file "Parameters_<suffix>.xlsx", the sheet "parRemove".
    Notice: only those parameters will be removed that are marked "yes" in the column "active" in the respective Excel sheet!
    This is to save time in running the function by deactivating the already removed parameters.
    """

    xls_par = pd.ExcelFile(path + '/Parameters'+suffix+'.xlsx')
    df_rem = xls_par.parse('parRemove')

    msgSC.check_out()

    for i in df_rem[df_rem['active'] == 'yes'].index:
        par_rem = df_rem['parameter'][i]
        dictrem = {}
        columns = df_rem['columns'][i].split(',')
        tec_from = df_rem['columns_value'][i].split(',')

        for col in columns:
                dictrem[col] = tec_from[columns.index(col)]

        if not (isinstance(df_rem['rem_attribute'][i], float) and isnan(df_rem['rem_attribute'][i])):
            dictrem[df_rem['rem_attribute'][i]] = df_rem['rem_value'][i].split(',')

        msgSC.remove_par(par_rem,msgSC.par(par_rem, dictrem))
        print('> Parameter "{}" was removed for {}!'.format(par_rem, dictrem))

    msgSC.commit('removed parameters of unwanted attributes')

