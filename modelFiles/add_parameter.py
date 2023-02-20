# -*- coding: utf-8 -*-
'''
    1. This function copies parameters from a specified region in the Global
    MESSAGE Model to a newly created model.
    2. The list of intended parameters to be copied can be specified by the
    user, i.e., parameters marked as "yes" under the column "from_region"
    in the sheet "par_list" in the Excel file "ModelSetup_<suffix>.xlsx".
'''
import pandas as pd


def copy_global_par(msgSC, msgWSC, nodeName, regionName, path, suffix=None,
                    copy_all=False, glb_node=None):

    # %% 1) Initialization and preparations
    xl_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))

    # Parameters that should be copied
    sheet_par = xl_set.parse('par_list')
    df_par = sheet_par.loc[sheet_par['from_region'] == 'yes']
    com_removal = list(set(sheet_par['parameter'].loc[
        sheet_par['commodityRemoval'] != 'n']))

    if not copy_all:
        sheet_tech = xl_set.parse('technology')
        technology_df = sheet_tech[sheet_tech['INCLUDE'] == 'y'
                                   ].dropna(subset=['TECHNOLOGY'])
        tec_reg = list(set(technology_df['TECHNOLOGY'].loc[
                                         technology_df['FROM_REGION'] == 'y']))
        technology = [t for t in tec_reg if t in list(
                set(msgWSC.set('technology')))]
    else:
        par_rem = [x for x in msgWSC.par_list() if x not in list(
                df_par['parameter'])]
        df = pd.DataFrame(columns=df_par.columns, index=par_rem)
        df['multiplier'] = 1
        df['parameter'] = df.index
        df_par = df_par.append(df, ignore_index=True)
        technology = list(msgSC.set('technology'))

    year = [int(x) for x in list(msgSC.set('year'))]
    commodity = list(msgSC.set('commodity'))

    # %% 2) Copying specified parameters
    print('> Copying parameters from "{}" in the global MESSAGE to the new'
          ' model...'.format(regionName))
    msgSC.check_out()

    for i in df_par.index:
        parname = df_par.loc[i, 'parameter']
        par_idxs = msgWSC.idx_names(parname)
        dict_par = {}

        if 'technology' in par_idxs:
            dict_par['technology'] = technology
        if 'relation' in par_idxs:
            dict_par['relation'] = list(msgSC.set('relation'))
        if 'emission' in par_idxs:
            dict_par['emission'] = list(msgSC.set('emission'))
        if 'node' in par_idxs:
            dict_par['node'] = regionName
        elif 'node_loc' in par_idxs:
            dict_par['node_loc'] = regionName
        elif 'node_rel' in par_idxs:
            dict_par['node_rel'] = regionName
        if 'year_vtg' in par_idxs:
            dict_par['year_vtg'] = year
        if 'year_act' in par_idxs:
            dict_par['year_act'] = year
        if 'year' in par_idxs:
            dict_par['year'] = year

        df_new = msgWSC.par(parname, dict_par)
        if not df_new.empty:
            print('- ' + parname)
            multiplier = float(df_par.loc[i, 'multiplier'])
            df_new['value'] = df_new['value'] * multiplier

            # Renaming node names
            # NOTICE: here all the node names are changed to the new model name
            node_col = [x for x in df_new.columns if x in ['node', 'node_loc']]
            node_idx = [x for x in df_new.columns if
                        'node' in x and x not in ['node', 'node_loc']]

            if node_col:
                df_new[node_col[0]] = nodeName
            if node_idx:
                if glb_node:
                    df_new.loc[df_new[node_idx[0]] != regionName,
                               node_idx[0]] = glb_node
                df_new.loc[df_new[node_idx[0]] == regionName,
                           node_idx[0]] = nodeName

            if parname in com_removal:
                com_list = sheet_par.loc[sheet_par['parameter'] == parname,
                                         'commodityRemoval'].item().split(',')
                for com in com_list:
                    df_new = df_new[df_new.commodity != com]

            if 'commodity' in df_new.columns:
                df_new = df_new[df_new['commodity'].isin(commodity)]

            # Adding parameters to the new MESSAGE model
            if parname not in msgSC.par_list():
                msgSC.init_par(parname, idx_names=msgWSC.idx_names(parname),
                               idx_sets=msgWSC.idx_sets(parname))
            msgSC.add_par(parname, df_new)

    # %% 3) Commiting the additions
    msgSC.commit('Parameters copied from Global MESSAGE to the new model!')
