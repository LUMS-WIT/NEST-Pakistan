import pandas as pd
import numpy as np
from message_ix import make_df

def insert_history(msgSC, year, tecs):

    # adding bound_activity_lo as historical_activity
    bound_activity_lo_year = msgSC.par('bound_activity_lo', {'year_act': year})
    bound_new_capacity_lo_year = msgSC.par('bound_new_capacity_lo', {'year_vtg': year})

    bound_activity_lo_year = bound_activity_lo_year[np.isfinite(bound_activity_lo_year['value'])]
    bound_new_capacity_lo_year = bound_new_capacity_lo_year[np.isfinite(bound_new_capacity_lo_year['value'])]
    
    hist_act = bound_activity_lo_year.copy()
    hist_act['unit'] = 'GWa'
    msgSC.add_par('historical_activity', hist_act)

    hist_cap = bound_new_capacity_lo_year.copy()
    hist_cap['unit'] = 'GW'
    msgSC.add_par('historical_new_capacity', hist_cap)

    act_2010 = msgSC.par("historical_activity", {"year_act": 2010, "technology": tecs})
    act_2015 = msgSC.par("historical_activity", {"year_act": 2015, "technology": tecs})

    merged = pd.merge(
        act_2010[["technology", "value"]],
        act_2015[["technology", "value"]],
        on="technology",
        suffixes=('_2010', '_2015')
    )

    # catering to tecs which do not have bound_activity_lo values
    merged["growth"] = (merged["value_2015"] - merged["value_2010"]) / merged["value_2010"]

    merged["value_year"] = np.where(
        merged["technology"].isin(["oil_imp", "loil_imp"]),
            merged["value_2015"] * (1 + 0.3 * merged["growth"]),
        # np.where(
        #     merged["technology"] == "coal_imp",
        #         merged["value_2015"] * 2,
            merged["value_2015"] * (1.3 + merged["growth"])
        # )
    )
    msgSC.add_par("historical_activity", {"node_loc": "R12_PAK", "mode": "M1", "time": "year", "year_act": year, "technology": merged["technology"], "value": merged["value_year"], "unit": "GWa"})

def insert_solar_distribution(msgSC):
    hist_cap = msgSC.par("bound_new_capacity_lo", {"technology":["solar_res_hist_2010", "solar_res_hist_2015", "solar_res_hist_2020", "solar_res_hist_2025"]})
    total_dist_cap = (hist_cap["value"].sum() * 5)/3
    hist_cap_2025 = total_dist_cap/5 + hist_cap[hist_cap["year_vtg"] == 2025]["value"]
    to_remove = hist_cap[hist_cap["year_vtg"] == 2025]
    msgSC.remove_par("bound_new_capacity_lo", to_remove)
    bncl_res = make_df("bound_new_capacity_lo", node_loc="R12_PAK", technology="solar_res_hist_2025", year_vtg=2025, value=hist_cap_2025, unit="GW")
    msgSC.add_par("bound_new_capacity_lo", bncl_res)

    bncl_pv = msgSC.par("bound_new_capacity_up", {"technology":"solar_pv_ppl", "year_vtg":2025})
    msgSC.remove_par("bound_new_capacity_up", bncl_pv)
    bncl_pv = make_df("bound_new_capacity_lo", node_loc="R12_PAK", technology="solar_pv_ppl", year_vtg=2025, value=hist_cap_2025, unit="GW")
    msgSC.add_par("bound_new_capacity_lo", bncl_pv)

    bncu = msgSC.par("bound_new_capacity_up", {"technology":["solar_pv_ppl", "solar_res_hist_2025"], "year_vtg":2025})
    msgSC.remove_par("bound_new_capacity_up", bncu)
    bncu_res = make_df("bound_new_capacity_up", node_loc="R12_PAK", technology="solar_res_hist_2025", year_vtg=2025, value=hist_cap_2025*1.005, unit="GW")
    msgSC.add_par("bound_new_capacity_up", bncu_res)

    bncu_pv = make_df("bound_new_capacity_up", node_loc="R12_PAK", technology="solar_pv_ppl", year_vtg=2025, value=hist_cap_2025*1.005, unit="GW")
    msgSC.add_par("bound_new_capacity_up", bncu_pv)


def modify_last_year(msgSC, new_last_yr):
    years = msgSC.set("year")
    remove_years = [x for x in years if x > new_last_yr]
    msgSC.check_out()
    msgSC.remove_set("year", remove_years)
    years = msgSC.set("year")

    lastmodelyr = pd.DataFrame(
        {
            "type_year": ["lastmodelyear"],
            "year": [new_last_yr]
        }
    )
    msgSC.add_set("cat_year", lastmodelyr)