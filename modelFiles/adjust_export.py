from message_ix import make_df
import pandas as pd

def adjust_oil(msgSC):
    foil_exp_bau = make_df("bound_activity_up", node_loc = "R12_PAK", technology = "foil_exp", 
                            year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                            time="year", mode="M1", value = 0, unit = "GWa")
    msgSC.add_par("bound_activity_up", foil_exp_bau)    
    

def adjust_eth(msgSC):
    eth_exp_bau = make_df("bound_activity_up", node_loc = "R12_PAK", technology = "eth_exp", 
                            year_act= [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
                            time="year", mode="M1", value = 0, unit = "GWa")
    msgSC.add_par("bound_activity_up", eth_exp_bau)   

def adjust_exp(msgSC):
    adjust_eth(msgSC)
    adjust_oil(msgSC)
