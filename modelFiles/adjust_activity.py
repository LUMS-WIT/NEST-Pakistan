from message_ix import make_df
import pandas as pd

def adjust_hydro(msgSC):
    hydro_tecs = ["hydro_lc", "hydro_hc"]
    gal = msgSC.par("growth_activity_lo", {"technology":["hydro_lc", "hydro_hc"]})
    msgSC.remove_par("growth_activity_lo", gal)
    for tec in hydro_tecs:
        hydro_gal = make_df("growth_activity_lo", node_loc = "R12_PAK", technology = tec, 
                                year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                time="year", value = 0.025, unit = "%")
        msgSC.add_par("growth_activity_lo", hydro_gal)

def adjust_coal(msgSC):
    # coal_tecs = ["coal_adv", "coal_adv_ccs", "coal_hpl", "coal_ppl", "coal_ppl_u"]
    # gau = msgSC.par("growth_activity_up", {"technology":["coal_adv", "coal_adv_ccs", "coal_imp"]})
    # msgSC.remove_par("growth_activity_up", gau)
    # for tec in coal_tecs:
    #     coal_gau = make_df("growth_activity_up", node_loc = "R12_PAK", technology = tec, 
    #                             year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
    #                             time="year", value = 0.03, unit = "%")
    #     msgSC.add_par("growth_activity_up", coal_gau)

    # coal_imp_gau = make_df("growth_activity_up", node_loc = "R12_PAK", technology = "coal_imp", 
    #                             year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
    #                             time="year", value = 0.04, unit = "%")
    # msgSC.add_par("growth_activity_up", coal_imp_gau)

    # syn_liq_up = make_df("bound_activity_up", node_loc = "R12_PAK", technology = "syn_liq", 
    #                             year_act= [2025, 2030, 2035, 2040, 2045, 2050],
    #                             time="year", mode="M1", value = 0, unit = "GWa")
    # msgSC.add_par("bound_activity_up", syn_liq_up)

    # igcc_bau = make_df("bound_activity_up", node_loc = "R12_PAK", technology = "igcc", 
    #                         year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
    #                         mode="M1", time="year", value = 0, unit = "GWa")
    # msgSC.add_par("bound_activity_up", igcc_bau)

    # gau = msgSC.par("growth_activity_up", {"technology":"coal_imp", "year_act":[2025, 2030]})
    # msgSC.remove_par("growth_activity_up", gau)

    bound_act_up_path = "D:/COMMITTED/Models/NEST-Pakistan/modelData/historicalData/bound_activity_up.xlsx"
    imp_bau = pd.read_excel(bound_act_up_path, sheet_name="coal_imp")
    msgSC.add_par("bound_activity_up", imp_bau)
    
    

def adjust_oil(msgSC):
    oil_tecs = ["oil_imp"]
    gau = msgSC.par("growth_activity_up", {"technology":"oil_imp"})
    msgSC.remove_par("growth_activity_up", gau)
    for tec in oil_tecs:
        oil_gau = make_df("growth_activity_up", node_loc = "R12_PAK", technology = tec, 
                                year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                time="year", value = 0.03, unit = "%")
        msgSC.add_par("growth_activity_up", oil_gau)

def adjust_biomass(msgSC):
    biomass_tecs = ["land_use_biomass"]
    for tec in biomass_tecs:
        biomass_gau = make_df("growth_activity_up", node_loc = "R12_PAK", technology = tec, 
                                year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                time="year", value = 0.2, unit = "%")
        msgSC.add_par("growth_activity_up", biomass_gau)

def adjust_solar(msgSC):
    solar_tecs = ["solar_pv_ppl"]
    gal = msgSC.par("growth_activity_lo", {"technology":"solar_pv_ppl"})
    msgSC.remove_par("growth_activity_lo", gal)
    for tec in solar_tecs:
        solar_gal = make_df("growth_activity_lo", node_loc = "R12_PAK", technology = tec, 
                                year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                                time="year", value = 0.025, unit = "%")
        msgSC.add_par("growth_activity_lo", solar_gal)

def adjust_transport(msgSC):
    gau = gau = msgSC.par("growth_activity_up", {"technology":"elec_trp"})
    msgSC.remove_par("growth_activity_up", gau)
    oil_gau = make_df("growth_activity_up", node_loc = "R12_PAK", technology = "elec_trp", 
                            year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                            time="year", value = 0.1, unit = "%")
    msgSC.add_par("growth_activity_up", oil_gau)

    

def adjust_activity(msgSC):
    # adjust_hydro(msgSC)
    adjust_coal(msgSC)
    # adjust_solar(msgSC)
    # adjust_transport(msgSC)
