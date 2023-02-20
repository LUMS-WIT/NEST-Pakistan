# -*- coding: utf-8 -*-
'''
   This function imports the commodity trade costs (import and export) as
   variable cost of trade technologies.
   There is possibility to multiply export and import trade costs by a
   desirable factor ('fac_imp' and 'fac_exp').
'''
import pandas as pd
from itertools import product
from modelFiles.utilities.util1 import setdefaults


def add_trade(msgSC, msgWSC, nodeName, regionName, path, suffix, fac_imp=1,
              fac_exp=1, copy_all=False, price_from_model='R14_SAS'):

    print('> Adding commodity prices...')
    # %% 1) Initialization and reading Excel files

    xls_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))
    xls_par = pd.ExcelFile(str(path + '/Parameters' + suffix + '.xlsx'))
    df_trade = xls_set.parse('trade')
    df_trade = df_trade.loc[df_trade['included'] == 'yes']
    sheet_var = xls_par.parse('commodityPrice')
    sheet_var = sheet_var.loc[sheet_var['active'] == 'yes']
    sheet_var['year'] = sheet_var['year'].astype(int)
    
    if not copy_all:
        sheet_tech = xls_set.parse('technology')
        technology_df = sheet_tech[sheet_tech['INCLUDE'] == 'y'
                                   ].dropna(subset=['TECHNOLOGY'])
        tec_new = [x for x in set(df_trade['technology']) if
                   x not in technology_df['TECHNOLOGY'].unique()]
        var_cost = sheet_var[sheet_var['technology'].isin(
                list(set(technology_df['TECHNOLOGY'])) + tec_new)].copy()

    else:
        tec_new = [x for x in list(set(df_trade['technology'])) if
                   x not in list(msgSC.set('technology'))]
        var_cost = sheet_var[sheet_var['technology'].isin(
                list(set(msgSC.set('technology'))) + tec_new)].copy()

    msgSC.check_out()
    if tec_new:
        msgSC.add_set('technology', tec_new)

    # %% 2) Adding commodity prices for trade technologies
    msgSC.add_set('relation', 'fuel_price')
    parname = 'relation_activity'
    if not price_from_model:
        ind = []
        for tec in var_cost['technology'].unique():
            yr_tec = list(var_cost.loc[var_cost['technology'] == tec, 'year'])
            yrs_tec = list(product(yr_tec, [tec]))
            ind = list(ind + yrs_tec)

        par = pd.DataFrame(columns=msgSC.par(parname).columns, index=ind)

        par = setdefaults(par, nodeName)
        par['technology'] = [i[1] for i in par.index]
        par['relation'] = 'fuel_price'
        par['unit'] = 'USD/kWa'
        par['year_act'] = par['year_rel'] = [i[0] for i in par.index]


        for i in par.index:
            if float(var_cost.loc[(var_cost['technology'] == i[1]) & (
                    var_cost['year'] == i[0]), 'value'].mean()) < 0:
                fac = fac_exp
            else:
                fac = fac_imp
            cond1 = (var_cost['technology'] == par.at[i, 'technology'])
            cond2 = (var_cost['year'] == par.at[i, 'year_act'])
            par.at[i, 'value'] = float(var_cost.loc[cond1 & cond2,
                                                      'value'].mean()) * fac

        par.index = range(0, len(par.index))
    else:
        df_price = msgWSC.var('PRICE_COMMODITY', {'node': price_from_model})
        par = pd.DataFrame(columns=msgSC.par(parname).columns)
        for i in df_trade.index:
            cond1 = (df_price['commodity'] == df_trade.loc[i, 'commodity'])
            if 'SAS' in price_from_model:
                if '_imp' in df_trade.loc[i, 'technology']:
                    cond2 = (df_price['level'] == 'import')
                else:
                    cond2 = (df_price['level'] == 'export')

            else:
                cond2 = (df_price['level'] == df_trade.loc[i, 'level'])
            df = df_price.loc[cond1 & cond2]
            df = df.rename({'lvl': 'value', 'mrg': 'unit', 'node': 'node_loc',
                            'year': 'year_act', 'level': 'year_rel', 'time': 'relation',
                            'commodity': 'technology'}, axis=1)

            df['technology'] = df_trade.loc[i, 'technology']
            df['year_rel'] = df['year_act']
            df['node_loc'] = df['node_rel'] = nodeName
            df['relation'] = 'fuel_price'
            df['unit'] = 'USD/kWa'
            df['mode'] = 'M1'
            if '_exp' in df_trade.loc[i, 'technology']:
                df['value'] = -df['value']
            par = par.append(df, ignore_index=True, sort=True)

    msgSC.add_par(parname, par)
    msgSC.add_par('relation_cost', {'relation': 'fuel_price', 'node_rel': nodeName,
                                    'year_rel': par['year_rel'].unique().tolist(), 'value': 1,
                                    'unit': '-'})

    # %% 3) Setting up input/output for trade technologies

    # 3.1) Removing the input of import technologies
    tec_imp = [x for x in set(df_trade['technology']) if '_imp' in x]
    tec_model = msgSC.par('input', {'level': 'import'})['technology'].unique()
    tec_imp = tec_imp + [x for x in tec_model if x not in tec_imp]
    par_in = msgSC.par('input', {'technology': tec_imp})
    msgSC.remove_par('input', par_in)

    # 3.2) Output for import technologies
    par_out = msgSC.par('output', {'technology': tec_imp})
    tec_list = par_out['technology'].unique()
    tec_missing = [x for x in tec_imp if x not in tec_list]

    if tec_missing:
        yrs = [int(x) for x in msgSC.set('year').tolist() if
               int(x) >= msgSC.firstmodelyear]
        df_ref = pd.DataFrame(index=yrs, columns=msgSC.par('output').columns)
        for tec in tec_missing:
            df = df_ref.copy()
            df['technology'] = tec
            df['level'] = df_trade.loc[df_trade['technology'] == tec, 'level'].any()
            df['mode'] = 'M1'
            df['unit'] = '-'
            df['value'] = 1
            df['commodity'] = df_trade.loc[df_trade['technology'] == tec, 'commodity'].any()
            df['time'] = df['time_dest'] = 'year'
            df['node_loc'] = df['node_dest'] = nodeName
            df['year_vtg'] = df['year_act'] = [x for x in df.index]

            par_out = par_out.append(df, ignore_index=True)
    msgSC.add_par('output', par_out)

    # 3.2) Input for export technologies
    tec_exp = [x for x in set(df_trade['technology']) if '_exp' in x]
    tec_model = msgSC.par('output', {'level': 'export'})['technology'].unique()
    tec_exp = tec_exp + [x for x in tec_model if x not in tec_exp]
    par_in = msgSC.par('input', {'technology': tec_exp})
    tec_list = par_in['technology'].unique()
    tec_missing = [x for x in tec_exp if x not in tec_list]

    # Finding input for the missing technology
    # TODO: for other missing parameters as well
    if tec_missing:
        for tec in tec_missing:
            d = df_trade.loc[df_trade['technology'] == tec]
            node = d['source_node'].item()
            t = d['source_tec'].item()
            df_ref = msgWSC.par('input', {'node_loc': node, 'technology': t})

            df = df_ref.copy()
            df['technology'] = tec
            df['level'] = df_trade.loc[df_trade['technology'] == tec, 'level'].any()
            df['commodity'] = df_trade.loc[df_trade['technology'] == tec, 'commodity'].any()
            df['node_loc'] = df['node_origin'] = nodeName

            par_in = par_in.append(df, ignore_index=True)
    msgSC.add_par('input', par_in)

    # 3.3) Output for export technologies
    par_out = par_in.copy()
    par_out['time_dest'] = par_out['time_origin']
    par_out['node_dest'] = nodeName
    par_out['level'] = 'export'
    par_out = par_out.drop(['node_origin', 'time_origin'], axis=1)
    msgSC.add_par('output', par_out)

    # 3.4) Removing trade technologies at the global level
    tec_trd = msgSC.par('output', {'level': 'import',
                                   'node_loc': 'World'})['technology'].unique()
    if tec_trd:
        for t in tec_trd:
            msgSC.remove_set('technology', t)

    # %% 4) Committing the additions

    msgSC.commit('copied variable costs for import and export technologies!')
    print('> Trade commodity prices added!')
