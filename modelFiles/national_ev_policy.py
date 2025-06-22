import pandas as pd
from message_ix import make_df
from itertools import product

def ev_shares(msgSC):

    scl = msgSC.par("share_commodity_lo")
    to_remove = scl.loc[scl['shares'] == 'UE_transport_electric_Minimum']
    msgSC.remove_par('share_commodity_lo', to_remove)
    
    trp_dmd = msgSC.par("demand", {"commodity":"transport"})
    trp_dmd = trp_dmd.copy()
    trp_dmd = trp_dmd.sort_values(by="year")
    trp_dmd["increase"] = trp_dmd['value'].pct_change() 
    trp_dmd = trp_dmd[trp_dmd["year"].isin([2025, 2030, 2040, 2045, 2050, 2055, 2060, 2070])]
    trp_dmd["perc_total_trp"] = trp_dmd["increase"] * ([0.1, 0.4] + [0.9]*6)

    scl = pd.DataFrame({
        "shares":"UE_transport_electric_Minimum",
        "node_share":"R12_PAK",
        "year_act":[2025, 2030, 2040, 2045, 2050, 2055, 2060, 2070],
        "value": trp_dmd["perc_total_trp"],
        "time":"year",
        "unit":"-",
    })

    msgSC.add_par('share_commodity_lo', scl)

def make_share_df(year_act, value):
    return make_df(
        "share_commodity_lo",
        shares="UE_transport_electric_Minimum",
        node_share="R12_PAK",
        year_act=year_act,
        time="year",
        value=value,
        unit="-"
    )

def expand_grid(dictionary):
    return pd.DataFrame([row for row in product(*dictionary.values())], 
                        columns=dictionary.keys())
