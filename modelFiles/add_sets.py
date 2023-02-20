# -*- coding: utf-8 -*-
''' This function creates the sets and adds them to the MESSAGE model.
    Data requirements:
        1. Excel file "ModelSetup.xlsx", the follwoing sheets: "technology",
        "emissions", "lists", and "reliability".
        2. Excel file "Parameters_<suffix>.xlsx", sheets: "resource" and
        "renewable".
'''
import pandas as pd


def add_set_print(msgSC, setname, members):
    msgSC.add_set(setname, members)
    print('- ' + setname)


def add_sets(msgSC, msgWSC, nodeName, regionName, path, suffix, period,
             copy_all=False):

    # %% 1) Initialization and importing data from relevant Excel files
    print('> Adding sets to the new model...')
    # Year
    firstyear = period['firstyear']
    horizon = period['horizon']
    years = period['years']

    if not copy_all:
        # 1.1) Using Excel files for adding sets
        # 1.1.1) Excel input data
        xl_set = pd.ExcelFile(str(path + '/ModelSetup' + suffix + '.xlsx'))
        xl_par = pd.ExcelFile(str(path + '/Parameters' + suffix + '.xlsx'))

        # Emission
        sheet_em = xl_set.parse('emissions')
        sheet_list = xl_set.parse('lists')
        emission = list(sheet_em.loc[sheet_em['em_copy'] == 'y',
                                     "emission"].dropna())
        type_em = list(sheet_em.loc[sheet_em['type_copy'] == 'y',
                                    "type_emission"].dropna())

        # Technology
        sheet_tech = xl_set.parse('technology')
        df_tech1 = sheet_tech[sheet_tech['INCLUDE'] == 'y'
                              ].dropna(subset=['TECHNOLOGY'])
        technology = list(set([i for i in list(set(df_tech1['TECHNOLOGY']
                                                   )) if str(i) != 'nan']))

        # Set - mode
        mode = list(sheet_list["mode"].dropna())

        # Type Technology
        
        type_tec = {'powerplant': list(set(df_tech1['TECHNOLOGY'][
                         df_tech1['POWERPLANT'] == 'y'])),
                    'powerplant_low-carbon': list(set(df_tech1['TECHNOLOGY'][
                         df_tech1['POWERPLANT_LOWCARBON'] == 'y' ])),
                    'powerplant_fossil': list(set(df_tech1['TECHNOLOGY'][
                         df_tech1['POWERPLANT_FOSSIL'] == 'y']))}
                    
     
        # Set - cat_tec 
        cat_tec = []
        for typ, tecs in type_tec.items():
            for tec in tecs:
                cat_tec.append([typ, tec])

        type_tec = list(type_tec.keys())
        # Resources
        sheet_fossil = xl_par.parse('resource')
        df_res = sheet_fossil[['Commodity', 'Volume', 'Grade', 'Level',
                               'ResourceRemaining']]
        df_res = df_res.dropna(subset=['Commodity'])
        grade_res = [i for i in list(set(df_res['Grade'])) if str(i) != 'nan']
        lvl_res = list(set(df_res['Level']))

        # Renewable resources
        df_renew = xl_par.parse('renewable').dropna()
        grade_renew = list(set(df_renew['grade']))
        lvl_renew = list(set(df_renew['level']))

        # Set - grade (resources and renewables)
        grade = list(set(grade_res + grade_renew))

        # Set - rating
        relbin = xl_set.parse('reliability')
        rating = list(set(relbin['rating']))
        rating = list(set(rating + list(sheet_list["rating"].dropna())))

        # Set - relation
        sheet_rel = xl_set.parse('relation')
        rel = sheet_rel[sheet_rel['tier'] == "y"].dropna(subset=['relation'])
        relation = rel['relation'].tolist()

        # 1.1.2) Copying required sets from parent region in the MESSAGE global
        # Set - level
        lvl = msgWSC.set('level')
        lvl_exclude = list(sheet_list["lvl_excluded"].dropna())
        exclude = []
        for lev in lvl_exclude:  # Excluding levels containing some strings
            exclude = exclude + lvl.loc[lvl.str.contains(lev)].tolist()

        lvls = list(set(lvl.tolist()) - set(exclude))
        df_tech = sheet_tech[sheet_tech['FROM_REGION'] == 'y'
                             ].dropna(subset=['TECHNOLOGY'])
        tecs_fromreg = [t for t in list(set(df_tech.TECHNOLOGY)) if
                        t in list(set(msgWSC.set('technology')))]

        dict_reg = {'node_loc': regionName, 'year_act': years,
                    'year_vtg': years, 'technology': tecs_fromreg,
                    'level': lvls}

        par_in = msgWSC.par('input', dict_reg)
        par_out = msgWSC.par('output', dict_reg)

        level = list(set(par_in['level'].append(par_out['level'])))
        level = level + list(set(df_tech1['INPUT_LEVEL'].dropna()))
        level = level + list(set(df_tech1['OUTPUT_LEVEL'].dropna()))

        # Set - mode
        mode = mode + list(set(par_in['mode'].append(par_out['mode'])))

        # Set - commodity
        commodity = list(set(par_in.commodity.append(par_out.commodity)))
        commodity = commodity + list(set(df_tech1['INPUT'].dropna()))
        commodity = commodity + list(set(df_tech1['OUTPUT'].dropna()))

    else:
        # 1.2) Reading data only from the global model

        # Emission
        emission = list(msgWSC.set('emission'))
        type_em = list(msgWSC.set('type_emission'))

        # Technology
        d1 = msgWSC.par('input', {'node_loc': regionName}
                        )['technology'].unique().tolist()
        d_rem = [x for x in set(msgWSC.set('technology')) if x not in d1]
        d2 = msgWSC.par('output', {'node_loc': regionName, 'technology': d_rem}
                        )['technology'].unique().tolist()
        d_rem = list(set(d_rem) - set(d2))

        dict_tec = {'input': 'node_origin', 'output': 'node_dest',
                    'historical_activity': 'node_loc',
                    'bound_activity_up': 'node_loc',
                    'bound_activity_lo': 'node_loc',
                    'relation_activity': 'node_loc',
                    'relation_total_capacity': 'node_rel',
                    'relation_new_capacity': 'node_rel'}
        d3 = []
        for parname, node_idx in dict_tec.items():
            d3 = d3 + msgWSC.par(parname, {node_idx: regionName,
                                           'technology': d_rem}
                                 )['technology'].unique().tolist()

        technology = sorted(list(set(d1 + d2 + d3)))

        # Set - mode
#        d1 = msgWSC.par('input', {'technology': technology}
#                        )['mode'].unique().tolist()
#        d2 = msgWSC.par('output', {'technology': technology}
#                        )['mode'].unique().tolist()
#        mode = sorted(list(set(d1 + d2)))
        mode = list(msgWSC.set('mode'))

        # Type Technology
        type_tec = list(msgWSC.set('type_tec'))

        # Set - cat_tec
        d = msgWSC.set('cat_tec')
        cat_tec = d.loc[d['technology'].isin(technology)]

        # Resources
        lvl_res = msgWSC.set('level_resource')['level'].tolist()

        # Renewables
        lvl_renew = msgWSC.set('level_renewable')['level'].tolist()

        # Set - level
        level = list(msgWSC.set('level'))

        # Set - commodity
        d1 = msgWSC.par('input', {'technology': technology}
                        )['commodity'].unique().tolist()
        d2 = msgWSC.par('output', {'technology': technology}
                        )['commodity'].unique().tolist()
        d3 = msgWSC.par('land_output', {'node': regionName}
                        )['commodity'].unique().tolist()
        commodity = sorted(list(set(d1 + d2 + d3)))

        # Check what commodities left
        # commodity1 = list(msgWSC.set('commodity'))
        # [x for x in commodity1 if x not in commodity]

        # Set - grade
        grade = list(msgWSC.set('grade'))

        # Set - rating
        rating = list(msgWSC.set('rating'))

        # Set - relation
        dict_rel = [['relation_activity', 'node_rel'],
                    ['relation_activity', 'node_loc'],
                    ['relation_total_capacity', 'node_rel'],
                    ['relation_new_capacity', 'node_rel']
                    ]
        rel = []
        for x in dict_rel:
            rel = rel + msgWSC.par(x[0], {x[1]: regionName,
                                   'technology': technology}
                                   )['relation'].unique().tolist()

        relation = sorted(list(set(rel)))

    # %% 2) Adding required sets to the MESSAGE model

    if msgSC.version != 0:
        msgSC.check_out()

    # Set - year
    msgSC.add_horizon({'year': horizon, 'firstmodelyear': firstyear,
                       'lastmodelyear': max(horizon)})
    print('- year, firstmodelyear')

    msgSC.add_cat('year', 'lastmodelyear', max(horizon))
    print('- year, lastmodelyear')

    # Set - node
    msgSC.add_spatial_sets({'country': nodeName})
    print('- node, lvl_spatial')

    # Set - technology
    add_set_print(msgSC, 'technology', technology)

    # Set - mode
    add_set_print(msgSC, 'mode', mode)

    # Set - type_tec
    add_set_print(msgSC, 'type_tec', type_tec)

    # Set - cat_tec
    add_set_print(msgSC, 'cat_tec', cat_tec)

    # Set - emission
    add_set_print(msgSC, 'emission', emission)

    # Set - type_emission
    add_set_print(msgSC, 'type_emission', type_em)

    # Set - cat_emission
    cat_em = msgWSC.set('cat_emission')
    cat_em = cat_em.loc[(cat_em['emission'].isin(emission)) &
                        (cat_em['type_emission'].isin(type_em))]
    add_set_print(msgSC, 'cat_emission', cat_em)

    # Set - level
    add_set_print(msgSC, 'level', level)

    # Set - commodity
    add_set_print(msgSC, 'commodity', commodity)

    # Set - grade
    add_set_print(msgSC, 'grade', grade)

    # Set - level_resource
    add_set_print(msgSC, 'level_resource', lvl_res)

    # Set - level_renewable
    if lvl_renew:
        add_set_print(msgSC, 'level_renewable', lvl_renew)

    # Set - rating
    if rating:
        add_set_print(msgSC, 'rating', rating)

    # Set - relation
    add_set_print(msgSC, 'relation', relation)

    # %% 3) Copying remaining sets

    if copy_all:
        set_init = [x for x in msgWSC.set_list(
                ).tolist() if x not in msgSC.set_list().tolist()]
        for s in set_init:
            if not msgWSC.set(s).empty:
                msgSC.init_set(s, idx_sets=msgWSC.idx_sets(s),
                               idx_names=msgWSC.idx_names(s))

        set_left = [x for x in msgWSC.set_list().tolist() if
                    x not in ['map_spatial_hirerarchy', 'map_node'] and not
                    msgWSC.set(x).empty and msgSC.set(x).empty]

        for setname in set_left:
            df = msgWSC.set(setname)
            if not isinstance(df, pd.DataFrame):
                d_new = df.tolist()
            elif 'node' not in msgWSC.idx_names(setname):
                d_new = df.copy()
            else:
                node_li = [x for x in msgWSC.idx_names(setname) if 'node' in x]
                d_new = pd.DataFrame(columns=df.columns)
                for node_idx in node_li:
                    d_new = d_new.append(df.loc[df[node_idx] == regionName],
                                         ignore_index=True)
                    d_new = d_new.replace({regionName: nodeName})
            add_set_print(msgSC, setname, d_new)

    # %% 4) Committing all the additions
    msgSC.commit('All sets were added to the model!')
