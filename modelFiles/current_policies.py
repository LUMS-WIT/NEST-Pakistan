import pandas as pd
from message_ix import make_df

def nuclear_shares(msgSC):
    msgSC.add_set('type_tec', 'nuclear')
    msgSC.add_set('type_tec', 'non_nuclear')
    msgSC.add_set('type_tec', 'nuc_total')

    msgSC.add_set('shares', 'nuclear')
    msgSC.add_set('shares', 'non_nuclear')
    msgSC.add_set('shares', 'nuc_total')

    # add to and remove from technologies powerplant_low-carbon and powerplant_fossil in cat_tec
    elec_gen = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})
    elec_gen_remove = elec_gen[elec_gen["technology"].str.contains("scr|hpl|htfc|sm\d_ppl|curtailment|cv|solar_pv_ppl|stor_ppl|geo_ppl|wind_ppl|wind_ppf", regex=True)] # nuc
    msgSC.remove_set("cat_tec", elec_gen_remove)
    elec_gen_fixed = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})

    add_nuc_tecs = make_df("cat_tec", type_tec="nuclear", technology=["nuc_hc", "nuc_lc"])
    msgSC.add_set("cat_tec", add_nuc_tecs)

    non_nuc_tecs = elec_gen_fixed[(elec_gen_fixed["technology"] != "nuc_hc") & (elec_gen_fixed["technology"] !="nuc_lc")]
    non_nuc_tecs["type_tec"] = "non_nuclear"

    more_non_nuc_tecs = make_df("cat_tec", type_tec="non_nuclear", technology=["solar_res_hist_2015", "solar_res_hist_2020",
                                                            "wind_res_hist_2000", "wind_res_hist_2005", "wind_res_hist_2010", "wind_res_hist_2015", "wind_res_hist_2020", 
                                                            "wind_res_hist_2025", "wind_ref_hist_2000", "wind_ref_hist_2005", "wind_ref_hist_2010", "wind_ref_hist_2015", 
                                                            "wind_ref_hist_2020", "wind_ref_hist_2025", "csp_sm1_res_hist_2015", "csp_sm1_res_hist_2020", "csp_sm1_res_hist_2010",])
    all_non_nuc_tecs = pd.concat([non_nuc_tecs, more_non_nuc_tecs])
    msgSC.add_set("cat_tec", all_non_nuc_tecs)

    # define new type_tec called powerplant_total
    ppl_total = msgSC.set("cat_tec", {"type_tec":["nuclear", "non_nuclear"]})["technology"]
    to_add_ppl_total = make_df("cat_tec", type_tec="nuc_total", technology=ppl_total)
    msgSC.add_set("cat_tec", to_add_ppl_total)

    # mapping and then adding shares for low carbon technologies
    _add_share_mappings(msgSC, "nuclear", "nuc_total")
    nuc_shares = pd.DataFrame(
        {
            "shares":"nuclear",
            "node_share":"R12_PAK",
            "year_act":[2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
            "value": [0.15, 0.09, 0.11] + [0.07]*6,
            "time":"year",
            "unit":"-",
        }
    )
    msgSC.add_par('share_commodity_lo', nuc_shares)

def clean_shares(msgSC):
    msgSC.add_set('type_tec', 'clean')
    msgSC.add_set('type_tec', 'unclean')
    msgSC.add_set('type_tec', 'clean_total')

    msgSC.add_set('shares', 'clean')
    msgSC.add_set('shares', 'unclean')
    msgSC.add_set('shares', 'clean_total')

    # add to and remove from technologies powerplant_low-carbon and powerplant_fossil in cat_tec
    elec_gen = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})
    elec_gen_remove = elec_gen[elec_gen["technology"].str.contains("scr|hpl|htfc|sm\d_ppl|curtailment|cv|solar_pv_ppl|stor_ppl|geo_ppl|wind_ppl|wind_ppf", regex=True)]
    msgSC.remove_set("cat_tec", elec_gen_remove)
    elec_gen_fixed = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})

    ccs_tecs = elec_gen[elec_gen["technology"].str.contains("_ccs")]["technology"].to_list()

    lc_tecs_list = elec_gen_fixed[elec_gen_fixed["type_tec"]=="powerplant_low-carbon"]["technology"].to_list()
    lc_tecs_list = [x for x in lc_tecs_list if x not in ["bio_ppl", "bio_istig"]]
    clean_tecs_list = lc_tecs_list + ccs_tecs + ["solar_res_hist_2015", "solar_res_hist_2020",
                                "wind_res_hist_2000", "wind_res_hist_2005", "wind_res_hist_2010", "wind_res_hist_2015", "wind_res_hist_2020", 
                                "wind_res_hist_2025", "wind_ref_hist_2000", "wind_ref_hist_2005", "wind_ref_hist_2010", "wind_ref_hist_2015", 
                                "wind_ref_hist_2020", "wind_ref_hist_2025", "csp_sm1_res_hist_2015", "csp_sm1_res_hist_2020", "csp_sm1_res_hist_2010",]
    add_clean_tecs = make_df("cat_tec", type_tec="clean", technology=clean_tecs_list)                                 
    msgSC.add_set("cat_tec", add_clean_tecs)

    unclean_tecs = elec_gen_fixed[~elec_gen_fixed["technology"].isin(clean_tecs_list)]
    unclean_tecs["type_tec"] = "unclean"    
    msgSC.add_set("cat_tec", unclean_tecs)

    # define new type_tec called powerplant_total
    ppl_total = msgSC.set("cat_tec", {"type_tec":["clean", "unclean"]})["technology"]
    to_add_ppl_total = make_df("cat_tec", type_tec="clean_total", technology=ppl_total)
    msgSC.add_set("cat_tec", to_add_ppl_total)

    # mapping and then adding shares for low carbon technologies
    _add_share_mappings(msgSC, "clean", "clean_total")
    clean_shares = pd.DataFrame(
        {
            "shares":"clean",
            "node_share":"R12_PAK",
            "year_act":[2030, 2035, 2040, 2045, 2050, 2055, 2060],
            "value":[0.65]*7,
            "time":"year",
            "unit":"-",
        }
    )
    msgSC.add_par('share_commodity_lo', clean_shares)

def ARE_shares(msgSC):
    msgSC.add_set('type_tec', 'renewable')
    msgSC.add_set('type_tec', 'non-renewable')
    msgSC.add_set('type_tec', 'renewable_total')

    msgSC.add_set('shares', 'renewable')
    msgSC.add_set('shares', 'non-renewable')
    msgSC.add_set('shares', 'renewable_total')

    # add to and remove from technologies powerplant_low-carbon and powerplant_fossil in cat_tec
    elec_gen = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})
    elec_gen_remove = elec_gen[elec_gen["technology"].str.contains("scr|hpl|htfc|sm\d_ppl|curtailment|cv|solar_pv_ppl|stor_ppl|geo_ppl|wind_ppl|wind_ppf", regex=True)]
    msgSC.remove_set("cat_tec", elec_gen_remove)
    elec_gen_fixed = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})

    lc_tecs_list = elec_gen_fixed[elec_gen_fixed["type_tec"]=="powerplant_low-carbon"]["technology"].to_list()
    re_tecs = [x for x in lc_tecs_list if x not in ["nuc_hc", "nuc_lc", "hydro_hc", "hydro_lc"]]
    re_tecs_list = re_tecs + ["solar_res_hist_2015", "solar_res_hist_2020",
                                "wind_res_hist_2000", "wind_res_hist_2005", "wind_res_hist_2010", "wind_res_hist_2015", "wind_res_hist_2020", 
                                "wind_res_hist_2025", "wind_ref_hist_2000", "wind_ref_hist_2005", "wind_ref_hist_2010", "wind_ref_hist_2015", 
                                "wind_ref_hist_2020", "wind_ref_hist_2025", "csp_sm1_res_hist_2015", "csp_sm1_res_hist_2020", "csp_sm1_res_hist_2010",]
    add_re_tecs = make_df("cat_tec", type_tec="renewable", technology=re_tecs_list)                                 
    msgSC.add_set("cat_tec", add_re_tecs)

    non_re_tecs = elec_gen_fixed[~elec_gen_fixed["technology"].isin(re_tecs_list)]
    non_re_tecs["type_tec"] = "non-renewable"    
    msgSC.add_set("cat_tec", non_re_tecs)

    # define new type_tec called powerplant_total
    ppl_total = msgSC.set("cat_tec", {"type_tec":["renewable", "non-renewable"]})["technology"]
    to_add_ppl_total = make_df("cat_tec", type_tec="renewable_total", technology=ppl_total)
    msgSC.add_set("cat_tec", to_add_ppl_total)

    # mapping and then adding shares for low carbon technologies
    _add_share_mappings(msgSC, "renewable", "renewable_total")
    re_shares = pd.DataFrame(
        {
            "shares":"renewable",
            "node_share":"R12_PAK",
            "year_act":[2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060],
            "value":[0.05] + [0.30]*7,
            "time":"year",
            "unit":"-",
        }
    )
    msgSC.add_par('share_commodity_lo', re_shares)

def hydro_shares(msgSC):
    msgSC.add_set('type_tec', 'hydro')
    msgSC.add_set('type_tec', 'non-hydro')
    msgSC.add_set('type_tec', 'hydro_total')

    msgSC.add_set('shares', 'hydro')
    msgSC.add_set('shares', 'non-hydro')
    msgSC.add_set('shares', 'hydro_total')

    # add to and remove from technologies powerplant_low-carbon and powerplant_fossil in cat_tec
    elec_gen = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})
    elec_gen_remove = elec_gen[elec_gen["technology"].str.contains("scr|hpl|htfc|sm\d_ppl|curtailment|cv|solar_pv_ppl|stor_ppl|geo_ppl|wind_ppl|wind_ppf", regex=True)]
    msgSC.remove_set("cat_tec", elec_gen_remove)
    elec_gen_fixed = msgSC.set("cat_tec", {"type_tec": ["powerplant_low-carbon", "powerplant_fossil"]})
    
    add_hydro_tecs = make_df("cat_tec", type_tec="hydro", technology=["hydro_hc", "hydro_lc"])                                 
    msgSC.add_set("cat_tec", add_hydro_tecs)

    non_hydro_tecs = elec_gen_fixed[~elec_gen_fixed["technology"].isin(["hydro_hc", "hydro_lc"])]["technology"].to_list() + ["solar_res_hist_2015", "solar_res_hist_2020",
                                "wind_res_hist_2000", "wind_res_hist_2005", "wind_res_hist_2010", "wind_res_hist_2015", "wind_res_hist_2020", 
                                "wind_res_hist_2025", "wind_ref_hist_2000", "wind_ref_hist_2005", "wind_ref_hist_2010", "wind_ref_hist_2015", 
                                "wind_ref_hist_2020", "wind_ref_hist_2025", "csp_sm1_res_hist_2015", "csp_sm1_res_hist_2020", "csp_sm1_res_hist_2010",]

    non_hydro_tecs = make_df("cat_tec", type_tec="non-hydro", technology=non_hydro_tecs) 
    msgSC.add_set("cat_tec", non_hydro_tecs)

    # define new type_tec called powerplant_total
    ppl_total = msgSC.set("cat_tec", {"type_tec":["hydro", "non-hydro"]})["technology"]
    to_add_ppl_total = make_df("cat_tec", type_tec="hydro_total", technology=ppl_total)
    msgSC.add_set("cat_tec", to_add_ppl_total)

    # mapping and then adding shares for low carbon technologies
    _add_share_mappings(msgSC, "hydro", "hydro_total")
    hydro_shares = pd.DataFrame(
        {
            "shares":"hydro",
            "node_share":"R12_PAK",
            "year_act":"2030",
            "value":[0.30],
            "time":"year",
            "unit":"-",
        }
    )
    msgSC.add_par('share_commodity_lo', hydro_shares)


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