from message_ix import make_df

def adjust_transport(msgSC):
    fc_tecs = ['eth_fc_trp','h2_fc_trp','meth_fc_trp'] # fuel cell: not enough scope in pak
    ic_tecs = ['eth_ic_trp', 'meth_ic_trp'] # ic ethanol/methanol: discussions on going but no concrete policy
    for tec in fc_tecs:
        fc_bau = make_df("bound_activity_up", node_loc = "R12_PAK", technology = tec, 
                                year_act = [2025, 2030, 2035, 2040], value = 0, mode="M1", time="year", unit = "GWa")
        msgSC.add_par("bound_activity_up", fc_bau)

    for tec in ic_tecs:
        ic_bau = make_df("bound_activity_up", node_loc = "R12_PAK", technology = tec, mode="M1", time="year",
                                year_act = 2025, value = 0, unit = "GWa")
        msgSC.add_par("bound_activity_up", ic_bau)
