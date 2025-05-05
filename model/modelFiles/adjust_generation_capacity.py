from message_ix import make_df

def adjust_gas(msgSC):
    gas_tecs = ["gas_ppl", "gas_cc", "gas_ct"]
    for tec in gas_tecs:
        gas_bncu = make_df("bound_new_capacity_up", node_loc = "R12_PAK", technology = tec, 
                                year_vtg = 2025, value = 0, unit = "GW")
        msgSC.add_par("bound_new_capacity_up", gas_bncu)

def adjust_generation_capacity(msgSC):
    adjust_gas(msgSC)