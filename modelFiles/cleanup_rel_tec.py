import pandas as pd


def cleanup_rel_tec(msgSC, nodes='all', glb=None):
    """ This function will remove any unused relations and technologies.
    Relations will be removed if:
        1. They have no upper and lower bound and no costs - therefore
           non-binding and have been used for accounting purposes
        2. They have no entries from any technologies
        2./3. NOTE: Only applied if this is the case in all regions.
        3. Specifically defined to be excluded.
            - some are manualyy removed because technologies using these
              are deleted in the next step.
            - all relations for historic calibration are removed
    Technologies will be removed if:
        1. They have a bound 0on activity of 0 for the entire
           optimization period
        2. Specifically defined to be excluded.
    """
    if nodes == 'all':
        reg = [x for x in msgSC.set('node') if
               x not in ['World', glb]]
    else:
        reg = nodes

    # REMOVE Relations ----------------------------------------------------

    # Retrieve all relations
    relations = msgSC.set('relation').tolist()

    # Retrieve all relation parameters
    rel_par = []
    for par in ['relation_upper', 'relation_lower', 'relation_cost']:
        df = msgSC.par(par)[['node_rel', 'relation']]\
            .set_index('node_rel')
        rel_par.append(df)

    rel_par = pd.concat(rel_par)\
                .reset_index()\
                .drop_duplicates()

    # Retrieve all entries in relations
    rel_act = []
    for par in ['relation_new_capacity', 'relation_total_capacity',
                'relation_activity']:
        df = msgSC.par(par)[['node_rel', 'relation']]\
            .set_index('node_rel')
        rel_act.append(df)

    rel_act = pd.concat(rel_act)\
                .reset_index()\
                .drop_duplicates()

    # Filter for all elements which are NOT contained in both list,
    # therefore remove everything that does not have both entry into
    # relations and some bound or cost
    exclusion = pd.concat([rel_act, rel_par])\
                  .drop_duplicates(keep=False)\
                  .sort_values(by='node_rel')
    exclusion = exclusion['relation'].unique().tolist()

    # Add any relation which is not contained in either of the two lists
    exclusion += [r for r in relations if r not in rel_act[
            'relation'].unique().tolist() and r not in rel_par[
            'relation'].unique().tolist()]

    # Manually add where no tech entry
    # Removed because tecs are removed (excl_rem_tec)
    excl_rem_tec = ['PE_domestic_total', 'PE_import_total',
                    'PE_import_share', 'PE_export_total',
                    'demb_limit', 'demF_limit', 'demI_limit',
                    'demp_limit', 'demR_limit', 'demt_limit']
    # Removed because historic calibration (excl_rem_hist_calib)
    excl_rem_hist_calib = ['elec_coal', 'elec_gas', 'elec_hydro',
                           'elec_nuclear', 'ele_nuc', 'foil_prod',
                           'oil_based_elec_gen', 'gas_export']
    # Remove any relations used for accounting of SO2 related emissions
    # for the purpose of constraing SO2 scrubbers
    excl_SOtwo_mitig = ['SO2_red_ref', 'SO2_red_synf', 'SO2_ind',
                        'SO2_elec', 'SO2_import', 'SO2_r_c']
    exclusion += excl_rem_tec + excl_rem_hist_calib + excl_SOtwo_mitig
    exclusion = [e for e in exclusion if e != 'CO2_cc']

    msgSC.check_out()
    for rel in exclusion:
        if rel in msgSC.set('relation').unique().tolist():
            msgSC.remove_set('relation', rel)
    msgSC.commit('Step1_cleanup: Remove unused relations')

    for rel in exclusion:
        print('Relation: {} - deleted'.format(rel))

    # REMOVE TECHNOLOGIES -------------------------------------------------

    # Retrieve firstyear and all_years to make list of all years
    # in optimization period
    optyears = [x for x in msgSC.set('year') if
                x > msgSC.firstmodelyear]

    bdaup = msgSC.par('bound_activity_up')

    # Adds all backstops to list of technologies to be deleted
    all_tecs = msgSC.set('technology').unique().tolist()
    del_tec = [t for t in all_tecs if 'back' in t or 'BS' in t]
    # Adds other additional selected technologies to be deleted.
    del_tec += [t for t in all_tecs if 'total' in t]

    if not bdaup.empty:
        bdaup = pd.pivot_table(bdaup, columns='year_act', index=[
                               'mode', 'node_loc', 'technology',
                               'time', 'unit'], values='value')
        bdaup = bdaup[optyears].dropna()\
                               .loc[(bdaup == 0).all(axis=1)]

        # Split out GLB Regions
        bdaup_glb = bdaup.loc(axis=0)[:, glb].reset_index()

        # Split out 11 Regions
        # Replace all 0 by 1 and sum by technology
        # Filter out all that have a sum of 11 and so are in each region.
        bdaup_reg = bdaup.loc(axis=0)[:, reg]\
            .replace(0, 1)\
            .reset_index()\
            .groupby('technology')\
            .sum()
        del_tec += bdaup_reg.loc[(bdaup_reg == 11).all(axis=1)]\
            .reset_index()['technology']\
            .unique()\
            .tolist()
        bdaup_glb = bdaup_glb['technology'].unique().tolist()
        del_tec += [t for t in bdaup_glb if t not in del_tec]

    # Adds SO2 mitigation technologies

    del_tec += ['SO2_scrub_ind', 'SO2_scrub_ppl', 'SO2_scrub_ref',
                'SO2_scrub_synf',
                'coal_t_d-in-06p', 'coal_t_d-in-SO2',
                'coal_t_d-rc-06p', 'coal_t_d-rc-SO2',
                'Feeds_con', 'Ispec_con', 'Itherm_con',
                'RCspec_con', 'RCtherm_con', 'Trans_con',
                ]

    msgSC.check_out()
    for tec in del_tec:
        if tec in msgSC.set('technology').unique().tolist():
            msgSC.remove_set('technology', tec)
    msgSC.commit('Step1_cleanup: Remove unused technologies')

    for tec in del_tec:
        print('Technology: {} - deleted'.format(tec))


# %%
if __name__ == '__main__':
    import ixmp as ix
    import message_ix

    mp = ix.Platform()
    model = 'MESSAGEix_KR'
    scen = 'test'
    version = 1
    msgSC = message_ix.Scenario(mp, model, scen, version=6)
    msgSC = msgSC.clone()
    cleanup_rel_tec(msgSC, glb='R11_GLB', verbose=False, nodes='all')