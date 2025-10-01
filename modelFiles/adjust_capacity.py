from message_ix import make_df

def adjust_gas(msgSC):
    gas_tecs = ["gas_ppl", "gas_cc", "gas_ct"]
    for tec in gas_tecs:
        val = 0.26 if tec == "gas_cc" else 0
        gas_bncu = make_df("bound_new_capacity_up", node_loc = "R12_PAK", technology = tec, 
                                year_vtg = 2025, value = val, unit = "GW")
        msgSC.add_par("bound_new_capacity_up", gas_bncu)

def adjust_refineries(msgSC):
    ref_tecs = ["ref_hil", "ref_lol"]
    for tec in ref_tecs:
        ref_bncu = make_df("bound_new_capacity_up", node_loc = "R12_PAK", technology = tec, 
                                year_vtg = 2025, value = 0, unit = "GW")
        msgSC.add_par("bound_new_capacity_up", ref_bncu)

def adjust_oil(msgSC):
    oil_tecs = ["loil_ppl", "foil_ppl"]
    for tec in oil_tecs:
        oil_bncu = make_df("bound_new_capacity_up", node_loc = "R12_PAK", technology = tec, 
                                year_vtg = 2025, value = 0, unit = "GW")
        msgSC.add_par("bound_new_capacity_up", oil_bncu)

def adjust_nuclear(msgSC):
    nuc_tecs = ["nuc_lc", "nuc_hc"]
    for tec in nuc_tecs:
        nuc_bncu = make_df("bound_new_capacity_up", node_loc = "R12_PAK", technology = tec, 
                                year_vtg = 2025, value = 0, unit = "GW")
        msgSC.add_par("bound_new_capacity_up", nuc_bncu)

def adjust_hydro(msgSC):
    hydro_tecs = ["hydro_lc", "hydro_hc"]

    for tec in hydro_tecs:
        hydro_gal = make_df("growth_new_capacity_lo", node_loc = "R12_PAK", technology = tec, 
                                year_vtg= [2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                value = 0.025, unit = "%")
        msgSC.add_par("growth_new_capacity_lo", hydro_gal)
    
    gncu = msgSC.par("growth_new_capacity_up", {"technology":["hydro_lc", "hydro_hc"]})
    msgSC.remove_par("growth_new_capacity_up", gncu)

def adjust_coal(msgSC):
    # coal_tecs = ["coal_adv", "coal_adv_ccs", "coal_ppl", "coal_ppl_u"]
    # gau = msgSC.par("growth_new_capacity_up", {"technology":["coal_adv", "coal_adv_ccs"]})
    # msgSC.remove_par("growth_new_capacity_up", gau)
    # for tec in coal_tecs:
    #     coal_gau = make_df("growth_new_capacity_up", node_loc = "R12_PAK", technology = tec, 
    #                             year_vtg= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
    #                             value = 0.02, unit = "%")
    #     msgSC.add_par("growth_new_capacity_up", coal_gau)

    # igcc_bncu = make_df("bound_new_capacity_up", node_loc = "R12_PAK", technology = "igcc", 
    #                         year_vtg = 2025, value = 0, unit = "GW")
    # msgSC.add_par("bound_new_capacity_up", igcc_bncu)

    btcl = msgSC.par("bound_total_capacity_lo", {"technology":"coal_adv"})
    msgSC.remove_par("bound_total_capacity_lo", btcl)

    btcu = msgSC.par("bound_total_capacity_up", {"technology":"coal_adv"})
    msgSC.remove_par("bound_total_capacity_up", btcu)

def adjust_solar(msgSC):
    solar_tecs = ["solar_pv_ppl"]
    for tec in solar_tecs:
        solar_gncl = make_df("growth_new_capacity_lo", node_loc = "R12_PAK", technology = tec, 
                                year_vtg= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                value = 0.025, unit = "%")
        msgSC.add_par("growth_new_capacity_lo", solar_gncl)

    gncu = msgSC.par("growth_new_capacity_up", {"technology":"solar_pv_ppl"})
    msgSC.remove_par("growth_new_capacity_up", gncu)

def adjust_wind(msgSC):
    wind_tecs = ["wind_ppl"]
    for tec in wind_tecs:
        wind_gncl = make_df("growth_new_capacity_lo", node_loc = "R12_PAK", technology = tec, 
                                year_vtg= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                value = 0.001, unit = "%")
        msgSC.add_par("growth_new_capacity_lo", wind_gncl)

    # gncu = msgSC.par("growth_new_capacity_up", {"technology":"wind_ppl"})
    # msgSC.remove_par("growth_new_capacity_up", gncu)

def adjust_capacity(msgSC):
    # adjust_gas(msgSC)
    # adjust_oil(msgSC)
    # adjust_hydro(msgSC)
    adjust_coal(msgSC)
    # adjust_solar(msgSC)
    # adjust_wind(msgSC)
