# -*- coding: utf-8 -*-
"""
This function adds the required user-defined relations in the context of the MESSAGE modelling framework

"""
import pandas as pd

def add_relation(msgSC, msgWSC, nodeName, regionName, path, suffix):

#%% 1) Initialization and importing data from Excel

    print('> Importing relation parameters from global MESSAGE to the model...')
    xls_set = pd.ExcelFile(str(path + '/ModelSetup'+suffix+'.xlsx'))
    sheet_rel=xls_set.parse('relation')
    sheet_par=xls_set.parse('par_list')
    sheet_tech=xls_set.parse('technology')

    relation_df = sheet_rel[sheet_rel['tier'] == "y"].dropna(subset=['relation'])
    technology_df = sheet_tech[sheet_tech['FROM_REGION'] == 'y'].dropna(subset=['TECHNOLOGY'])

    firstyear=msgSC.set('cat_year',{'type_year' : 'firstmodelyear'}).year.item()
    year = [int(i) for i in list(msgSC.set('year')) if int(i) >= firstyear]

    par_list = list(set(sheet_par['parameter'].loc[sheet_par['add_relation']=='yes']))   # Those parameters related to relations

#%% 2) Importing relation parameters

    msgSC.check_out()

    # Reading the set of relations
    relation = [i for i in list(set(relation_df.relation)) if str(i) != 'nan']
    msgSC.add_set('relation', relation)

    for par in par_list:
        col = msgSC.par(par).columns
        dict_rel = {}
        if 'relation' in col:
            dict_rel['relation'] = list(set(relation))
        if 'node_rel' in col:
            dict_rel['node_rel'] = regionName
        elif 'node_loc' in col:
            dict_rel['node_loc'] = regionName
        if 'year_act' in col:
            dict_rel['year_act'] = year
        if 'year_rel' in col:
            dict_rel['year_rel'] = year

        par_rel = msgWSC.par(par, dict_rel)
        if par in ['relation_activity']:
            par_rel = par_rel[par_rel['technology'].isin(list(technology_df.TECHNOLOGY))]

        # Renaming node to the new model name
        if 'node_rel' in par_rel.columns:
            par_rel['node_rel'] = nodeName
        if 'node_parent' in par_rel.columns:
            par_rel['node_parent'] = nodeName
        if 'node_loc' in par_rel.columns:
            par_rel['node_loc'] = nodeName
        if 'node_origin' in par_rel.columns:
            par_rel['node_origin'] = nodeName
        if 'node_dest' in par_rel.columns:
            par_rel['node_dest'] = nodeName

        # Adding parameter to the MESSAGE model
        msgSC.add_par(par, par_rel)
        print('- Parameter "' + par + '" was imported!')

#%% 3) Commiting the additions

    msgSC.commit('copied relations parameters from msgWorld')
    print('> All parameters related to "relations" were imported!')