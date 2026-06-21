import warnings
from itertools import product

import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)

from .utilities.get_historical_years import main as get_historical_years
from .utilities.get_optimization_years import main as get_optimization_years

#  Define Parameters to be updated
par_list = [
    "capacity_factor",
    "growth_activity_lo",
    "growth_new_capacity_up",
    "initial_activity_lo",
    "initial_new_capacity_up",
    "inv_cost",
    "fix_cost",
    "technical_lifetime",
    "relation_total_capacity",
    "soft_new_capacity_up",
    "abs_cost_new_capacity_soft_up",
    "bound_new_capacity_up",
    "bound_new_capacity_lo",
    "bound_activity_lo",
    "bound_activity_up",
    "input",
    "output",
    "historical_new_capacity",
    "historical_activity",
    "bound_total_capacity_lo",
    # "level_cost_new_capacity_soft_up",
    # "relation_activity",
    # "var_cost",
    # "initial_activity_up",
    # "growth_activity_up",
]

# Define mapping from Utility Solar PV to Rooftop Solar PV
mapping_names = {
    "solar_pv_ppl": "solar_pv_rt_ppl",
    "solar_res1": "solar_res_RT1",
    "solar_res2": "solar_res_RT2",
    "solar_res3": "solar_res_RT3",
    "solar_res4": "solar_res_RT4",
    "solar_res5": "solar_res_RT5",
    "solar_res6": "solar_res_RT6",
    "solar_res7": "solar_res_RT7",
    "solar_res8": "solar_res_RT8",
    "solar_res_hist_2000": "solar_res_rt_hist_2000",
    "solar_res_hist_2005": "solar_res_rt_hist_2005",
    "solar_res_hist_2010": "solar_res_rt_hist_2010",
    "solar_res_hist_2015": "solar_res_rt_hist_2015",
    "solar_res_hist_2020": "solar_res_rt_hist_2020",
    "solar_res_hist_2025": "solar_res_rt_hist_2025",
}

# Define rooftop historical technology and MPEN
rt_hist_tecs = [
    "solar_pv_rt_ppl",
    "solar_res_rt_hist_2000",
    "solar_res_rt_hist_2005",
    "solar_res_rt_hist_2010",
    "solar_res_rt_hist_2015",
    "solar_res_rt_hist_2020",
    "solar_res_rt_hist_2025",
]

# Define rooftop solar bins
rt_bins = [
    "solar_res_RT1",
    "solar_res_RT2",
    "solar_res_RT3",
    "solar_res_RT4",
    "solar_res_RT5",
    "solar_res_RT6",
    "solar_res_RT7",
    "solar_res_RT8",
]

# Define utility historical technology and MPEN
ut_hist_tecs = [
    "solar_pv_ppl",
    "solar_res_hist_2000",
    "solar_res_hist_2005",
    "solar_res_hist_2010",
    "solar_res_hist_2015",
    "solar_res_hist_2020",
    "solar_res_hist_2025",
]

# Define utility solar bins
ut_bins = [
    "solar_res1",
    "solar_res2",
    "solar_res3",
    "solar_res4",
    "solar_res5",
    "solar_res6",
    "solar_res7",
    "solar_res8",
]


# Data calibration for UT and RT
def update_calibration(
    scen, nodes, path_data_RT, ssp, verbose, s_n, m_t, h_y, f_y, h_t, h_b
):
    with scen.transact("update rt calibration"):
        data = pd.read_excel(
            path_data_RT,
            sheet_name=s_n,
        )

        # Map country-specific node suffixes to R11 region codes used in calibration data
        node_r11_map = {"PAK": "SAS"}

        # Build year → hist-tec mapping so per-year lookups use the right technology
        year_to_hist_tec = {
            int(tec.split("_")[-1]): tec
            for tec in h_t
            if tec.split("_")[-1].isdigit()
        }

        for parmod in [
            "historical_new_capacity",
            "historical_activity",
            "bound_activity_up",
            "bound_activity_lo",
            "bound_new_capacity_up",
            "bound_new_capacity_lo",
            "bound_total_capacity_lo",
            "capacity_factor",
        ]:
            if verbose:
                print("------------------" + parmod + "------------------")

            if parmod == "historical_new_capacity":

                for node, year in product(nodes, h_y):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["bound_new_capacity_lo"]
                    )
                    df_mod = scen.par(
                        parmod, {"node_loc": node, "technology": h_t, "year_vtg": year}
                    )
                    for index, row in df_mod.iterrows():
                        if row["technology"] == m_t:
                            df_mod.loc[index, "value"] = val
                        elif df_mod.loc[index, "value"] == 0:
                            df_mod.loc[index, "value"] = 0
                        else:
                            df_mod.loc[index, "value"] = val
                    scen.add_par(parmod, df_mod)

            if parmod == "historical_activity":

                for node, year in product(nodes, h_y):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["bound_activity_lo"]
                    )

                    tech = data.loc[
                        (data["time"] == year)
                        & (data["node_loc"] == r11_node)
                    ]["technology"].values

                    df_mod = scen.par(
                        parmod, {"node_loc": node, "technology": tech, "year_act": h_y}
                    )
                    for index, row in df_mod.iterrows():

                        if row["technology"] == m_t:
                            df_mod.loc[index, "value"] = val
                        # elif df_mod.loc[index, "value"] == 0:
                        #     df_mod.loc[index, "value"] = 0
                        else:
                            df_mod.loc[index, "value"] = val
                    scen.add_par(parmod, df_mod)

            if parmod == "bound_activity_lo":

                for node, year in product(nodes, h_y + [2020, 2025]):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["bound_activity_lo"]
                    )

                    tech = data.loc[
                        (data["time"] == year)
                        & (data["node_loc"] == r11_node)
                    ]["technology"].values

                    df_mod = scen.par(
                        parmod,
                        {"node_loc": node, "technology": tech, "year_act": h_y + f_y},
                    )
                    for index, row in df_mod.iterrows():

                        if row["technology"] == m_t:
                            df_mod.loc[index, "value"] = val
                        # elif df_mod.loc[index, "value"] == 0:
                        #     df_mod.loc[index, "value"] == 0
                        else:
                            df_mod.loc[index, "value"] = val

                    scen.add_par(parmod, df_mod)

            if parmod == "bound_activity_up":

                for node, year in product(nodes, h_y + [2020, 2025]):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["bound_activity_up"]
                    )

                    tech = data.loc[
                        (data["time"] == year)
                        & (data["node_loc"] == r11_node)
                    ]["technology"].values

                    df_mod = scen.par(
                        parmod,
                        {"node_loc": node, "technology": tech, "year_act": h_y + f_y},
                    )
                    for index, row in df_mod.iterrows():

                        if row["technology"] == m_t:
                            df_mod.loc[index, "value"] = val
                        # elif df_mod.loc[index, "value"] == 0:
                        #     df_mod.loc[index, "value"] == 0
                        else:
                            df_mod.loc[index, "value"] = val

                    scen.add_par(parmod, df_mod)

            if parmod == "bound_new_capacity_lo":

                for node, year in product(nodes, h_y + [2020, 2025]):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["bound_new_capacity_lo"]
                    )

                    df_mod = scen.par(
                        parmod,
                        {
                            "node_loc": node,
                            "technology": h_t,
                            "year_vtg": year,
                        },
                    )
                    for index, row in df_mod.iterrows():

                        if row["technology"] == m_t:
                            df_mod.loc[index, "value"] = val
                        else:
                            df_mod.loc[index, "value"] = val

                    scen.add_par(parmod, df_mod)

            if parmod == "bound_new_capacity_up":

                for node, year in product(nodes, h_y + [2020, 2025]):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["bound_new_capacity_up"]
                    )

                    df_mod = scen.par(
                        parmod,
                        {
                            "node_loc": node,
                            "technology": h_t,
                            "year_vtg": year,
                        },
                    )
                    for index, row in df_mod.iterrows():

                        if row["technology"] == m_t:
                            df_mod.loc[index, "value"] = val
                        else:
                            df_mod.loc[index, "value"] = val

                    scen.add_par(parmod, df_mod)

            if parmod == "bound_total_capacity_lo":

                for node, year in product(nodes, h_y + [2020, 2025, 2030]):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    for technology in h_t:
                        val = data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == technology)
                        ]["bound_total_capacity_lo"]
                        if val.empty:
                            continue
                        else:
                            val = float(val)

                        df_mod = pd.DataFrame(
                            {
                                "node_loc": node,
                                "technology": technology,
                                "year_act": [y for y in f_y if y >= year],
                                "value": val,
                                "unit": "GW",
                            }
                        )

                        scen.add_par(parmod, df_mod)

            if parmod == "bound_activity_up":
                full_years = h_y + f_y
                for node, year, tec in product(nodes, full_years, h_b):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    try:  # capturing CHN RES1=0 for SSP2, solar_ut
                        val = float(
                            data.loc[
                                (data["time"] == "all")
                                & (data["node_loc"] == r11_node)
                                & (data["SSP"] == ssp)
                                & (data["technology"] == tec)
                            ]["bound_activity_up"]
                        )
                    except:
                        val = 0

                    df_mod = scen.par(
                        parmod, {"node_loc": node, "technology": tec, "year_act": year}
                    )
                    df_mod["value"] = val
                    scen.add_par(parmod, df_mod)

            if parmod == "capacity_factor":

                for node, year in product(nodes, h_y + [2020, 2025]):
                    r11_node = node_r11_map.get(node.split("_")[1], node.split("_")[1])
                    lookup_tec = year_to_hist_tec.get(year, m_t)
                    val = float(
                        data.loc[
                            (data["time"] == year)
                            & (data["node_loc"] == r11_node)
                            & (data["SSP"] == "all")
                            & (data["technology"] == lookup_tec)
                        ]["capacity_factor"]
                    )

                    tech = data.loc[
                        (data["time"] == year)
                        & (data["node_loc"] == r11_node)
                    ]["technology"].values

                    if val == 0:

                        for parrem in par_list + ["relation_activity"]:
                            if verbose:
                                print(
                                    "Encountered Zero CF, removing ... "
                                    + str(parrem)
                                    + " Node ..."
                                    + node
                                    + " tec ..."
                                    + tech
                                )

                            node_idx = [
                                x for x in scen.idx_names(parrem) if "node" in x
                            ]

                            temp_df = scen.par(
                                parrem,
                                {
                                    node_idx[0]: node,
                                    "technology": tech,
                                },
                            )
                            scen.remove_par(parrem, temp_df)

                    else:

                        df_mod = scen.par(
                            parmod, {"node_loc": node, "technology": tech}
                        )

                        df_mod["value"] = val

                        scen.add_par(parmod, df_mod)


def main(
    scen,
    path_data_RT,
    ssp="SSP2",
    verbose=False,
):
    """Add Rooftop Solar PV RES.

    The purpose of this script is to create seperate representation of Utility Scale Solar PV (UT) and Rooftop Solar PV (RT)

    Following steps are performed
    1.) Copy parameters from UT to RT based on par_list (above)
    2.) Link RT formulation to "PE_total_traditional" relation
    3.) Transfer RT formulation from secondary to "final_RT" level
    4.) Create new sp_el_RC_RT and sp_el_I_RT link to connect RC and Industry sectors with RT
    5,6.) Add calibration for historical and future parameters for RT and UT

    Parameters
    ----------
    scen : :class:`message_ix.Scenario`
        scenario to which changes should be applies
    ssp : string
        specify for which SSP the parameters should be added
    path_data_RT : path
        specify for which SSP the parameters should be added
    verbose : boolean (default=False)
        option whether to primnt onscreen messages.
    """

    # Define nodes
    nodes = sorted(
        [
            x
            for x in set(scen.set("node"))
            if not any([y in x for y in ["GLB", "World"]])
        ]
    )

    # STEP1: Copy UT parameters to RT
    with scen.transact("Copy parameters from source scenario"):

        scen.add_set("technology", rt_hist_tecs + rt_bins)
        scen.add_set("technology", ut_hist_tecs)
        scen.add_set("technology", ["sp_el_RC_RT", "sp_el_I_RT"])
        scen.add_set("level", "final_RT")
        scen.add_set("relation", "solar_ppl_res_RT")

        for parname in par_list:
            if verbose:
                print("Working on ... " + str(parname))
                print(scen.idx_names(parname))

            node_idx = [x for x in scen.idx_names(parname) if "node" in x]
            base_df = scen.par(
                parname,
                {
                    node_idx[0]: nodes,
                    "technology": ut_hist_tecs + ut_bins,
                },
            )
            base_df["technology"] = base_df["technology"].map(mapping_names)
            if parname == "relation_total_capacity":
                base_df["relation"] = "solar_ppl_res_RT"
            scen.add_par(parname, base_df)

    # STEP2: Hack to add relation activity to make sure solar_pv_rt_ppl is not thrown out
    with scen.transact("Adding relation_activity entry for MPEN tech"):
        base_df = scen.par(
            "relation_activity",
            {
                "relation": "PE_total_traditional",
                "technology": "solar_pv_ppl",
            },
        )
        base_df["technology"] = "solar_pv_rt_ppl"
        scen.add_par("relation_activity", base_df)

    # hack to limit relation values
    with scen.transact("Adding bounds on relation mpen"):
        base_df = scen.par(
            "relation_upper",
            {
                "relation": "solar_ppl_res",
            },
        )
        base_df["relation"] = "solar_ppl_res_RT"
        scen.add_par("relation_upper", base_df)

        base_df = scen.par(
            "relation_lower",
            {
                "relation": "solar_ppl_res",
            },
        )
        base_df["relation"] = "solar_ppl_res_RT"
        scen.add_par("relation_lower", base_df)

    node_idx = ["node_loc"]

    # STEP3: modify RT outputs and energy system levels
    with scen.transact("modify outputs"):

        base_df = scen.par(
            "output",
            {
                node_idx[0]: nodes,
                "technology": rt_hist_tecs + rt_bins,
            },
        )
        scen.remove_par("output", base_df)
        base_df["level"] = "final_RT"
        scen.add_par("output", base_df)

    # STEP4: Create new sp_el_RC_RT and sp_el_I_RT link to connect RC and Industry sectors
    with scen.transact("create new link for sp_el_rc and sp_el_I"):
        # sp_el_rc <<<-
        base_df = scen.par(
            "input",
            {
                node_idx[0]: nodes,
                "technology": "sp_el_RC",
            },
        )
        base_df["technology"] = "sp_el_RC_RT"
        base_df["level"] = "final_RT"
        scen.add_par("input", base_df)

        base_df = scen.par(
            "output",
            {
                node_idx[0]: nodes,
                "technology": "sp_el_RC",
            },
        )
        base_df["technology"] = "sp_el_RC_RT"
        base_df["commodity"] = "rc_spec"
        scen.add_par("output", base_df)

        # sp_el_I <<<-
        base_df = scen.par(
            "input",
            {
                node_idx[0]: nodes,
                "technology": "sp_el_I",
            },
        )
        base_df["technology"] = "sp_el_I_RT"
        base_df["level"] = "final_RT"
        scen.add_par("input", base_df)

        base_df = scen.par(
            "output",
            {
                node_idx[0]: nodes,
                "technology": "sp_el_I",
            },
        )
        base_df["technology"] = "sp_el_I_RT"
        base_df["commodity"] = "i_spec"
        scen.add_par("output", base_df)

    # STEP5: Update calibration for RT
    update_calibration(
        scen,
        nodes,
        path_data_RT,
        ssp,
        verbose,
        s_n="solar_pv_rt_ppl_RT",
        m_t="solar_pv_rt_ppl",
        h_y=get_historical_years(scen, year_min=2000),
        f_y=get_optimization_years(scen),
        h_t=rt_hist_tecs,
        h_b=rt_bins,
    )

    # STEP6: Update calibration for UT
    update_calibration(
        scen,
        nodes,
        path_data_RT,
        ssp,
        verbose,
        s_n="solar_pv_ppl_UT",
        m_t="solar_pv_ppl",
        h_y=get_historical_years(scen, year_min=2000),
        f_y=get_optimization_years(scen),
        h_t=ut_hist_tecs,
        h_b=ut_bins,
    )

    # STEP7: Update relation_activity for HFCs
    with scen.transact(
        "create new relation activity links for sp_el_rc_RT and sp_el_I_RT"
    ):
        # sp_el_RC_RT <<<-
        base_df = scen.par(
            "relation_activity",
            {
                node_idx[0]: nodes,
                "technology": "sp_el_RC",
            },
        )
        base_df["technology"] = "sp_el_RC_RT"
        scen.add_par("relation_activity", base_df)

        # sp_el_I_RT <<<-
        base_df = scen.par(
            "relation_activity",
            {
                node_idx[0]: nodes,
                "technology": "sp_el_I",
            },
        )
        base_df["technology"] = "sp_el_I_RT"
        scen.add_par("relation_activity", base_df)
