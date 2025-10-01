import pandas as pd
import numpy as np
from message_ix import make_df

def insert_history(msgSC, year, tecs):

    # calibrating some of the bound_activity_lo values
    bal_2020_remove = msgSC.par('bound_activity_lo', {'year_act': year, "technology":"bio_ppl"})
    msgSC.remove_par("bound_activity_lo", bal_2020_remove)
    bal_2020_BE = 0.06443607306
    bal_2020_BE_df = make_df("bound_activity_lo", node_loc="R12_PAK", technology="bio_ppl", year_act=year, mode="M1", time="year", value=bal_2020_BE, unit="GWa")
    msgSC.add_par("bound_activity_lo", bal_2020_BE_df)

    # adding bound_activity_lo and bound_new_capacity_lo as historical_activity and historical_new_capacity, respectively, for specified year
    bound_activity_lo_2020 = msgSC.par('bound_activity_lo', {'year_act': year})
    bound_new_capacity_lo_2020 = msgSC.par('bound_new_capacity_lo', {'year_vtg': year})

    bound_activity_lo_2020 = bound_activity_lo_2020[np.isfinite(bound_activity_lo_2020['value'])]
    bound_new_capacity_lo_2020 = bound_new_capacity_lo_2020[np.isfinite(bound_new_capacity_lo_2020['value'])]
    
    bound_activity_lo_2020['unit'] = 'GWa'
    msgSC.add_par('historical_activity', bound_activity_lo_2020)

    bound_new_capacity_lo_2020['unit'] = 'GW'
    msgSC.add_par('historical_new_capacity', bound_new_capacity_lo_2020)

    bound_activity_lo_2020['unit'] = 'GWa'
    msgSC.add_par('historical_activity', bound_activity_lo_2020)

    bound_new_capacity_lo_2020['unit'] = 'GW'
    msgSC.add_par('historical_new_capacity', bound_new_capacity_lo_2020)

    # catering to tecs which do not have bound_activity_lo values
    act_05_10_15 = msgSC.par("historical_activity", {"year_act": [2000, 2005, 2010, 2015], "technology": tecs})
    hist_act_2020 = []

    for tec in act_05_10_15['technology'].unique():
        ha_imp_df = act_05_10_15[act_05_10_15['technology'] == tec].sort_values('year_act')
        v2000, v2005, v2010, v2015 = ha_imp_df['value'].values
        # calculate growth rates
        growth_1 = (v2005 - v2000) / v2000
        growth_2 = (v2010 - v2005) / v2005
        growth_3 = (v2015 - v2010) / v2010

        if tec == "loil_imp":
            avg_growth = (growth_1 + growth_2 + growth_3) / 3
        else:
            avg_growth = (growth_2 + growth_3) / 2

        v2020 = v2015 * (1 + avg_growth)

        # new row df
        imp_2020 = {
            'node_loc': 'R12_PAK',
            'technology': tec,
            'year_act': 2020,
            'mode': 'M1',
            'time': 'year',
            'value': v2020,
            'unit': 'GWa'
        }
        hist_act_2020.append(imp_2020)

    ha_2020_df = pd.DataFrame(hist_act_2020)

    msgSC.add_par("historical_activity", ha_2020_df)

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

    # adding 1.005 times the lower bound as upper bound
    bncu = pd.DataFrame(
        {
            "node_loc": ["R12_PAK"] * 4,
            "technology": ["solar_res_hist_2020", "solar_res_hist_2025", "solar_pv_ppl", "solar_pv_ppl"],
            "year_vtg": [2020, 2025, 2020, 2025],
            "value": [avg_2020*1.005, avg_2025*1.05, avg_2020*1.005, avg_2025*1.05],
            "unit": ["GW"] * 4
        }
    )
    msgSC.add_par("bound_new_capacity_up", bncu)

    # removal of previous generation data
    bound_act_up_remove = msgSC.par("bound_activity_up", {"technology":["solar_res_hist_2020", "solar_res_hist_2025"]})
    msgSC.remove_par("bound_activity_up", bound_act_up_remove)

    bound_act_lo_remove = msgSC.par("bound_activity_lo", {"technology":["solar_res_hist_2020", "solar_res_hist_2025"]})
    msgSC.remove_par("bound_activity_lo", bound_act_lo_remove)

    # calculation of generation data according to the projection capacity values and cf values in the model data
    # act = cf * cap
    cf_2020 = msgSC.par("capacity_factor", {"technology":"solar_res_hist_2020", "year_vtg":"2020", "year_act":"2020"})["value"].values[0]
    act_2020 = cf_2020 * hist_2020[["value"]].sum().values[0]

    cf_2025 = msgSC.par("capacity_factor", {"technology":"solar_res_hist_2025", "year_vtg":"2025", "year_act":"2025"})["value"].values[0]
    act_2025 = cf_2025 * hist_2025[["value"]].sum().values[0]

    # adding upper and lower bounds for activity
    year_all = list(range(2020, 2065, 5)) + [2070] + list(range(2025, 2065, 5)) + [2070]
    bal_20_25 = pd.DataFrame(
        {
            "node_loc": "R12_PAK",
            "technology": ["solar_res_hist_2020"]*10 + ["solar_res_hist_2025"]*9,
            "year_act": year_all,
            "mode":"M1",
            "time":"year",
            "value": [act_2020]*10 + [act_2025]*9,
            "unit": "GWa",
        }
    )
    msgSC.add_par("bound_activity_lo", bal_20_25)

    bau_20_25 = pd.DataFrame(
        {
            "node_loc": "R12_PAK",
            "technology": ["solar_res_hist_2020"]*10 + ["solar_res_hist_2025"]*9,
            "year_act": year_all,
            "mode":"M1",
            "time":"year",
            "value": [act_2020*1.005]*10 + [act_2025*1.05]*9,
            "unit": "GWa",
        }
    )
    msgSC.add_par("bound_activity_up", bau_20_25)


def calibrate_coal(msgSC):
    """
    historical activity for coal_adv has non zero values in 1990 and 1995 despite zero historical new capacity
    we will remove the historical activity values
    """
    hist_act_remove = msgSC.par("historical_activity", {"technology":"coal_adv", "year_act":["1990", "1995"]}) # df to be removed
    msgSC.remove_par("historical_activity", hist_act_remove)

    hist_act = make_df("historical_activity", node_loc="R12_PAK", technology="coal_adv", year_act=["1990", "1995"], mode="M1", time="year", value=[0, 0], unit="GWa" )
    msgSC.add_par("historical_activity", hist_act)


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