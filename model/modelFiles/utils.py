import pandas as pd
import numpy as np

def insert_history(msgSC, year, tecs):
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

    merged["growth"] = (merged["value_2015"] - merged["value_2010"]) / merged["value_2010"]

    merged["value_year"] = np.where(
        merged["technology"].isin(["oil_imp", "loil_imp"]),
        merged["value_2015"] * (1 + 0.3 * merged["growth"]),
        merged["value_2015"] * (1 + merged["growth"])
    )
    msgSC.add_par("historical_activity", {"node_loc": "R12_PAK", "mode": "M1", "time": "year", "year_act": year, "technology": merged["technology"], "value": merged["value_year"], "unit": "GWa"})

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