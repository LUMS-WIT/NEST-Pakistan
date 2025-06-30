import pandas as pd
from message_ix import make_df

def generation_shares(msgSC):
    _add_initial_sets(msgSC) # this includes "shares" and "type_tec"

    # add to and remove from technologies powerplant_low-carbon and powerplant_fossil in cat_tec
    elec_gen = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})
    elec_gen_remove = elec_gen[elec_gen["technology"].str.contains("scr|hpl|htfc|sm._ppl|curtailment|cv|solar_pv_ppl|stor_ppl|geo_ppl|wind_ppl|wind_ppf|hydro|nuc", regex=True)]
    msgSC.remove_set("cat_tec", elec_gen_remove)
    elec_gen_lc_add = make_df("cat_tec", type_tec="powerplant_low-carbon", technology=["solar_res_hist_2000", "solar_res_hist_2005", "solar_res_hist_2010", "solar_res_hist_2015", "solar_res_hist_2025",
                                                            "wind_res_hist_2000", "wind_res_hist_2005", "wind_res_hist_2010", "wind_res_hist_2015", "wind_res_hist_2020", 
                                                            "wind_res_hist_2025", "wind_ref_hist_2000", "wind_ref_hist_2005", "wind_ref_hist_2010", "wind_ref_hist_2015", 
                                                            "wind_ref_hist_2020", "wind_ref_hist_2025", "csp_sm1_res_hist_2015", "csp_sm1_res_hist_2020", "csp_sm1_res_hist_2010",])
    msgSC.add_set("cat_tec", elec_gen_lc_add)
    # elec_gen_fossil_add = make_df("cat_tec", type_tec="powerplant_fossil", technology="igcc")
    # msgSC.add_set("cat_tec", elec_gen_fossil_add)

    # define new type_tec called hydro
    hydro_total = make_df("cat_tec", type_tec="powerplant_hydro", technology= ["hydro_lc", "hydro_hc"])
    msgSC.add_set("cat_tec", hydro_total)

    # define new type_tec called nuclear
    nuclear_total = make_df("cat_tec", type_tec="powerplant_nuclear", technology=["nuc_lc", "nuc_hc"])
    msgSC.add_set("cat_tec", nuclear_total)    

    # define new type_tec called powerplant_total
    ppl_total = msgSC.set("cat_tec", {"type_tec":["powerplant_low-carbon", "powerplant_fossil", "powerplant_hydro", "powerplant_nuclear"]})["technology"]
    to_add_ppl_total = make_df("cat_tec", type_tec="powerplant_total", technology=ppl_total)
    msgSC.add_set("cat_tec", to_add_ppl_total)

    # mapping and then adding shares for low carbon technologies
    _add_share_mappings(msgSC, "powerplant_low-carbon", "powerplant_total")
    lc_2025 = share_commodity_lo_df("powerplant_low-carbon", '2025', 0.0420) # pakistan economic survey 23-24
    lc_post_2025 = [0.13 + 0.13] + ([0.16 + 0.15]*7) # igcep 24-34
    lc_shares = pd.DataFrame(
        {
            "shares":"powerplant_low-carbon",
            "node_share":"R12_PAK",
            "year_act":[2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
            "value": lc_post_2025,
            "time":"year",
            "unit":"-",
        }
    )
    lc_shares = pd.concat([lc_2025, lc_shares], ignore_index=True)
    msgSC.add_par('share_commodity_lo', lc_shares)

    # mapping and then adding shares for fossil technologies
    _add_share_mappings(msgSC, "powerplant_fossil", "powerplant_total")
    fossil_25 = share_commodity_up_df('powerplant_fossil', '2025', 0.4588) # pakistan economic survey 23-24
    fossil_30 = share_commodity_up_df('powerplant_fossil', '2030', 0.3400) # igcep 24-34
    fossil_35 = share_commodity_up_df('powerplant_fossil', '2035', 0.2700) # igcep 24-34
    fossil_shares = pd.DataFrame(
        {
            "shares":"powerplant_fossil",
            "node_share":"R12_PAK",
            "year_act":[2040, 2045, 2050, 2055, 2060, 2070],
            "value": [0.27]*6,
            "time":"year",
            "unit":"-",
        }
    )

    fossil_shares = pd.concat([fossil_25, fossil_30, fossil_35, fossil_shares], ignore_index=True)
    # msgSC.add_par('share_commodity_up', fossil_shares)

    # mapping and then adding shares for hydropower technologies
    _add_share_mappings(msgSC, "powerplant_hydro", "powerplant_total")
    hydro_2025 = share_commodity_lo_df("powerplant_hydro", '2025', 0.25) # pakistan economic survey 23-24
    hydro_post_2025 = [0.3600] + ([0.4000]*7) # igcep 24-34
    hydro_shares = pd.DataFrame(
        {
            "shares":"powerplant_hydro",
            "node_share":"R12_PAK",
            "year_act":[2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
            "value": hydro_post_2025,
            "time":"year",
            "unit":"-",
        }
    )
    hydro_shares = pd.concat([hydro_2025, hydro_shares], ignore_index=True)
    msgSC.add_par("share_commodity_lo", hydro_shares)

    # mapping and then adding shares for nuclear technologies
    _add_share_mappings(msgSC, "powerplant_nuclear", "powerplant_total")
    nuclear_2025 = share_commodity_lo_df("powerplant_nuclear", '2025', 0.18) # pakistan economic survey 23-24
    nuclear_post_2025 = [0.13] + ([0.15]*7) # igcep 24-34
    nuclear_shares = pd.DataFrame(
        {
            "shares":"powerplant_nuclear",
            "node_share":"R12_PAK",
            "year_act":[2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
            "value": nuclear_post_2025,
            "time":"year",
            "unit":"-",
        }
    )
    nuclear_shares = pd.concat([nuclear_2025, nuclear_shares], ignore_index=True)
    # msgSC.add_par("share_commodity_lo", nuclear_shares)

def share_commodity_lo_df(shares, year_act, value):
    return make_df(
        "share_commodity_lo",
        shares=shares,
        node_share="R12_PAK",
        year_act=year_act,
        time="year",
        value=value,
        unit="-"
    )

def share_commodity_up_df(shares, year_act, value):
    return make_df(
        "share_commodity_up",
        shares=shares,
        node_share="R12_PAK",
        year_act=year_act,
        time="year",
        value=value,
        unit="-"
    )

def _add_initial_sets(msgSC):
    msgSC.add_set('type_tec', 'powerplant_hydro')
    msgSC.add_set('type_tec', 'powerplant_nuclear')
    msgSC.add_set('type_tec', 'powerplant_total')

    msgSC.add_set('shares', 'powerplant_low-carbon')
    msgSC.add_set('shares', 'powerplant_fossil')
    msgSC.add_set('shares', 'powerplant_hydro')
    msgSC.add_set('shares', 'powerplant_nuclear')
    msgSC.add_set('shares', 'powerplant_total')

def _add_share_mappings(msgSC, shares: str, total: str):
    msct = make_df(
        "map_shares_commodity_total", 
        shares=shares, 
        type_tec=total, 
        node_share="R12_PAK", 
        node="R12_PAK", 
        mode="M1",
        level="secondary",
        commodity="electr"
    )

    msgSC.add_set('map_shares_commodity_total', msct)

    mscs = make_df(
        "map_shares_commodity_share", 
        shares=shares, 
        type_tec=shares, 
        node_share="R12_PAK", 
        node="R12_PAK", 
        mode="M1",
        level="secondary",
        commodity="electr"
    )

    msgSC.add_set('map_shares_commodity_share', mscs)