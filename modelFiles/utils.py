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
    """
    ratios taken from https://www.iea.org/data-and-statistics/data-tools/renewable-energy-progress-tracker
    we look at cumulative capacity in 2025 since catering to yearly or 5 year ratios is a bit more challenging
    """
    
    hist_cap = msgSC.par("bound_new_capacity_lo", {"technology":["solar_res_hist_2010", "solar_res_hist_2015", "solar_res_hist_2020", "solar_res_hist_2025"]})
    total_dist_cap = hist_cap["value"].sum() * 0.37
    hist_cap_2025 = total_dist_cap + hist_cap[hist_cap["year_vtg"] == 2025]["value"]
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


def calibrate_solar(msgSC):
    """
    we recaluculate new capacity bounds for 2025 due to changing/increasing trends
    we include solar distribution in 2020 and 2025 bins due to its significant share
    """
    # path to solar generation and capacity data collected from IEA
    solar_pv_path = "D:/COMMITTED/Models/NEST-Pakistan/modelData/historicalData/IEA_renewable_tracker_solar_dist_util.xlsx"

    solar_cumulative = pd.read_excel(solar_pv_path, sheet_name="cumulative_capacity")

    start_year = 2017 # using this year gives projection closest to IEA forecast
    end_year = solar_cumulative['year_vtg'].max()

    start_value = solar_cumulative[solar_cumulative['year_vtg'] == start_year]["value"].values[0]
    end_value = solar_cumulative[solar_cumulative['year_vtg'] == end_year]["value"].values[0]
    n = end_year - start_year

    cagr = (end_value / start_value) ** (1 / n) - 1

    base_value = solar_cumulative[solar_cumulative['year_vtg'] == end_year]["value"].values[0]

    projections = {end_year:base_value}
    net_additions = [base_value] # temporarily keeping cumulative capacity in 2017 to calculate net additions

    # project cumulative capacity and calculate net additions for 2023-2025
    for year in [2023, 2024, 2025]:
        n = year - end_year
        projections[year] = base_value * (1 + cagr) ** n
        net_additions.append(projections[year] - projections[year-1])

    # print(projections)
    net_additions.pop(0) # remove the temporary value

    # reading in available data for 2016-2022 as a dataframe
    solar_new_cap = pd.read_excel(solar_pv_path, sheet_name="new_capacity")
    solar_new_cap = solar_new_cap.fillna(0)
    solar_new_cap["value"] = solar_new_cap["value_dist"] + solar_new_cap["value_util"]
    solar_new_cap = solar_new_cap.drop(columns=["value_util", "value_dist"])

    # preparaing projections for 2023-2025 as a dataframe
    new_caps_23_24_25 = pd.DataFrame(
        {
            "node_loc":"R12_PAK",
            "technology":"solar_res_hist_2025",
            "year_vtg": [2023, 2024, 2025],
            "value": net_additions,
            "unit": "GWa"

        }
    )

    # combining into one df
    df_all_yrs = [solar_new_cap, new_caps_23_24_25]
    solar_new_cap = pd.concat(df_all_yrs)

    # aggregating for 5 years as per messageix standard
    hist_2020 = solar_new_cap[solar_new_cap["technology"] == "solar_res_hist_2020"]
    avg_2020 = hist_2020[["value"]].sum() / 5

    hist_2025 = solar_new_cap[solar_new_cap["technology"] == "solar_res_hist_2025"]
    avg_2025 = hist_2025[["value"]].sum() / 5

    # removing previous lower bound values
    bound_new_cap_lo = msgSC.par("bound_new_capacity_lo", {"technology":["solar_res_hist_2020", "solar_res_hist_2025", "solar_pv_ppl"]})
    bncl_remove = bound_new_cap_lo[bound_new_cap_lo["year_vtg"].isin([2020, 2025])]
    msgSC.remove_par("bound_new_capacity_lo", bncl_remove)

    # adding projected values as lower bounds
    bncl = pd.DataFrame(
        {
            "node_loc": ["R12_PAK"] * 4,
            "technology": ["solar_res_hist_2020", "solar_res_hist_2025", "solar_pv_ppl", "solar_pv_ppl"],
            "year_vtg": [2020, 2025, 2020, 2025],
            "value": [avg_2020, avg_2025, avg_2020, avg_2025],
            "unit": ["GW"] * 4
        }
    )
    msgSC.add_par("bound_new_capacity_lo", bncl)

    # removing previous values
    bound_new_cap_up = msgSC.par("bound_new_capacity_up", {"technology":["solar_res_hist_2020", "solar_res_hist_2025", "solar_pv_ppl"]})
    bncu_remove = bound_new_cap_up[bound_new_cap_up["year_vtg"].isin([2020, 2025])]
    msgSC.remove_par("bound_new_capacity_up", bncu_remove)

    # adding 1.0005 times the lower bound as upper bound
    bncu = pd.DataFrame(
        {
            "node_loc": ["R12_PAK"] * 4,
            "technology": ["solar_res_hist_2020", "solar_res_hist_2025", "solar_pv_ppl", "solar_pv_ppl"],
            "year_vtg": [2020, 2025, 2020, 2025],
            "value": [avg_2020*1.0005, avg_2025*1.0005, avg_2020*1.0005, avg_2025*1.0005],
            "unit": ["GW"] * 4
        }
    )
    msgSC.add_par("bound_new_capacity_up", bncu)

    # calculation of generation data according to the projection capacity values and cf values in the model data
    # act = cf * cap
    cf_2020 = msgSC.par("capacity_factor", {"technology":"solar_res_hist_2020", "year_vtg":"2020", "year_act":"2020"})["value"].values[0]
    act_2020 = cf_2020 * hist_2020[["value"]].sum().values[0]

    cf_2025 = msgSC.par("capacity_factor", {"technology":"solar_res_hist_2025", "year_vtg":"2025", "year_act":"2025"})["value"].values[0]
    act_2025 = cf_2025 * hist_2025[["value"]].sum().values[0]

    # adding upper and lower bounds for activity
    bal_20_25 = pd.DataFrame(
        {
            "node_loc": "R12_PAK",
            "technology": ["solar_res_hist_2020", "solar_res_hist_2025"],
            "year_act": [2020, 2025],
            "mode":"M1",
            "time":"year",
            "value": [act_2020, act_2025],
            "unit": "GWa",
        }
    )
    msgSC.add_par("bound_activity_lo", bal_20_25)

    bau_20_25 = pd.DataFrame(
        {
            "node_loc": "R12_PAK",
            "technology": ["solar_res_hist_2020", "solar_res_hist_2025"],
            "year_act": [2020, 2025],
            "mode":"M1",
            "time":"year",
            "value": [act_2020*1.0005, act_2025*1.0005],
            "unit": "GWa",
        }
    )
    msgSC.add_par("bound_activity_up", bau_20_25)


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