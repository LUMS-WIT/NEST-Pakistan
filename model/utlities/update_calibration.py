# -*- coding: utf-8 -*-

# from utilities_main.message_utils import (
#     add_vintage,
#     calibrate_hist_act_to_others,
#     calibrate_hist_act_to_commodity_lvl,
#     replace_with_most_common,
#     update_share,
# )


def model_calibrate(msg, nodeNames, replace_negative=False):
    """
    Calibrating the model after parameterization.

    Parameters
    ----------
    msg : message_ix.Scenario
    nodeNames: list
        List of nodes for updating calibration.
    """
    # Adding historical activity for some technologies, based on activity or input
    # commodity of other technologies
    tech_mapping = {
        "heat_t_d": ["heat_i", "heat_rc"],
        "elec_t_d": ["sp_el_I", "sp_el_RC"],
        "loil_t_d": ["loil_trp", "loil_i", "loil_rc"],
        "foil_t_d": ["foil_trp", "foil_i", "foil_rc"],
        "biomass_t_d": ["biomass_nc", "biomass_rc", "biomass_i"],
        "land_use_biomass": ["biomass_nc", "biomass_rc", "biomass_i"],
        "coal_t_d": ["coal_rc", "coal_i"],
        "eth_t_d": ["sp_eth_I", "eth_i", "eth_rc"],
    }
    # Calling the relevant utility function
    calibrate_hist_act_to_others(msg, tech_mapping, nodeNames, input_commodity=True)

    # Adding historical activity based on input "commodity" at a certain "level"
    calibrate_hist_act_to_commodity_lvl(
        msg, {"gas_t_d": [["gas"], ["final"]]}, nodeNames
    )

    # ===========================================================================
    # Replacing negative or near zero values in some parameters, which are probably
    # the result of some sort of extrapolation when extending lifetime
    if replace_negative:
        replace_with_most_common(
            msg, tec_list=["loil_ppl", "foil_ppl"], par_list=["capacity_factor"]
        )
        replace_with_most_common(msg, tec_list=["gas_cc"], par_list=["input"])

    # ==========================================================================
    # Adding vintage capacity for some technologies that have historical activity
    tec_list = [
        "elec_t_d",
        "gas_t_d",
        "heat_t_d",
        "loil_t_d",
        # "gas_exp", 'elec_exp',
        "biomass_t_d",
        # "loil_ppl", # There are negative values in capcity factor in some regions
        "hydro_lc",
    ]
    add_vintage(msg, tec_list, nodeNames)

    # ==========================================================================
    # Updating minimum shares of some commodities at the end use sectors
    # including, electric_transport and non-commercial biomass
    relations = {
        "UE_res_comm_th_biomass": ["useful_res_comm_th", "biomass_rc", "_rc"],
        "UE_transport_electric_Minimum": ["useful_transport", "elec_trp", "_trp"],
        "UE_industry_sp_liquid": ["useful_industry_sp", "sp_eth_I", "_I"],
    }
    for relation, items in relations.items():
        tec_list = [x for x in set(msg.set("technology")) if x.endswith(items[2])]
        update_share(msg, relation, items[0], items[1], tec_list, nodes=nodeNames)

    # ==========================================================================
    # Notice: check which of the following is needed?
    # 1. Update of useful demand technologies growth rates
    # See: https://github.com/iiasa/message_data/blob/dev/message_data/tools/utilities/calibrate_UE_gr_to_demand.py

    # 2. Update of useful demand share constraints based on historical data
    # See: https://github.com/iiasa/message_data/blob/dev/message_data/tools/utilities/calibrate_UE_share_constraints.pY


    # -*- coding: utf-8 -*-
""" A set of utility functions for:
    - add_bound_from_hist:
        adding bounds on activity based on historical values and growth rates
    - add_bound:
        adding bounds for certain technologies, modes, nodes.
    - add_bound_from_results:
        adding bounds based on ACT (activity) or CAP (capacity) of a technology
    - extend_bound:
        adding bounds on activity as a ratio of activity of technologies in one level/commodity
    - update_share:
        updating the existing shares in relation_activity based on new historical data.
    - read_var:
        fetching data of a parameter or variable and sorting that for a given information.
    - subtract_data:
        subtracting data of one node from another node for a parameter
    - biomass_globiom:
        linking biomass in primary level to Globiom of another node (nesting process)
    - correct_sum_history:
        correcting historical activity of technologies that are the sum of other technologies.
    - subtract_RE_new_from_old:
        subtracting new renewable potentials in one node from old implementation in
        another node.
    - remove_tec_from_node:
        removing a technology from parameters of a certain node
    - par_copy:
        copying parameters from one technology to another
    - demand_supply_match:
        Checking if supply > demand, and setting them equal.
        
    To be completed...
    
"""
import pandas as pd
from itertools import product


def add_bound_from_hist(sc, nodeName, tecs, bound_up_yr=0, bound_lo_yr=0, yearly=False):
    '''
    """
    This function add bounds in model years based on annual growth rates
    specified by the user applying to historical values of that technology.

    Parameters
    ----------
    sc : message_ix.Scenario
    nodeName : string
        Model region to be used for adding bounds.
    tecs : list
        List of technologies to which the bound should be added.
    bound_up_yr : float, optional
        Growth rate of bound_act_up per year based on 2015, default is 0.
    bound_lo_yr : float, optional
        Negative growth rate of bound_act_lo per year. The default is 0.
    yearly : bool, optional
        If True, the bound is to be generated based on the yearly value (not time
        slice). The default is False.

    Returns
    -------
    NOTICE: Adds the results directly to the scenario.

    '''
    # Finding relevant years
    yrs = [int(x) for x in sc.set("year").tolist() if int(x) >= sc.firstmodelyear]
    yr_hist = max([x for x in sc.set("year") if x < sc.firstmodelyear])

    # Loading historical data
    df_hist = sc.par(
        "historical_activity",
        {"node_loc": nodeName, "technology": tecs, "year_act": yr_hist},
    )
    if yearly:
        df_hist["time"] = "year"
        df_hist = (
            df_hist.groupby(sc.idx_names("historical_activity") + ["unit"])
            .sum(numeric_only=True)
            .reset_index()
        )

    sc.check_out()
    # Filling empty historical data for some technologies
    if not df_hist.empty:
        tec_ref = list(set(df_hist["technology"]))[0]
        df_ref = df_hist.loc[df_hist["technology"] == tec_ref].copy()
        tec_m = [x for x in tecs if x not in list(set(df_hist["technology"]))]

        # Finding missing technologies from hist and adding zero hist
        df_ref["value"] = 0
        for t in tec_m:
            df_ref["technology"] = t
            df_hist = pd.concat([df_hist, df_ref], ignore_index=True)

            print(
                'No historical activity for "{}" in "{}", zero values'
                " added.".format(t, nodeName)
            )
    else:
        print(
            ">>>Warning<<<: No historical activity for"
            ' technologies "{}" in "{}", no bounds added.'.format(tecs, nodeName)
        )
        sc.commit("")
        return

    if bound_up_yr:
        df_bdu = pd.DataFrame(columns=sc.par("bound_activity_up").columns)
        for yr in yrs:
            d = df_hist.copy()
            d["year_act"] = yr
            d["value"] *= 1 + (yr - yr_hist) * bound_up_yr
            df_bdu = pd.concat([df_bdu, d], ignore_index=True)
        df_bdu.loc[df_bdu["value"] < 0, "value"] = 0
        sc.add_par("bound_activity_up", df_bdu)
        print(
            f'- Upper bound with growth of "{bound_up_yr}" per year added for "{tecs}" in "{nodeName}".'
        )

    if bound_lo_yr:
        df_bdl = pd.DataFrame(columns=sc.par("bound_activity_lo").columns)
        for yr in yrs:
            d = df_hist.copy()
            d["year_act"] = yr
            d["value"] *= 1 + (yr - yr_hist) * bound_lo_yr
            df_bdl = pd.concat([df_bdl, d], ignore_index=True)
        df_bdl.loc[df_bdl["value"] < 0, "value"] = 0
        sc.add_par("bound_activity_lo", df_bdl)
        print(
            '- Lower bound with grwoth of "{}" per year addedr'
            ' in "{}".'.format(bound_lo_yr, nodeName)
        )

    sc.commit("bounds added.")


def add_bound(
    sc,
    parname,
    tec,
    nodes="all",
    years="all",
    value=0,
    mode="M1",
    times=["year"],
    add_to_scenario=True,
):
    """
    Adding bounds for a technology

    Parameters
    ----------
    sc : message_ix.Scenario
    parname : str
        Parameter name to be used for adding bounds.
    tec : str
        Technology for adding bounds.
    nodes : list or "all", optional
        List of nodes to be used for applying bounds. The default is "all".
    years : list or "all", optional
        List of years to be used for applying bounds. The default is "all".
    value : float, optional
        Value of the bound. The default is 0.
    mode : str, optional
        Mode of operation of the technology under the bound. The default is "M1".
    times : list, optional
        List of sub-annual time slices for bound. The default is ["year"].
    add_to_scenario : bool, optional
        Adding changes to the scenario. The default is True.

    Returns
    -------
    dfb : dataframe
        Bounds as a table.

    """
    if nodes == "all":
        nodes = [
            x for x in set(sc.set("node")) if x not in ["world", "R14_GLB", "R11_GLB"]
        ]
    elif type(nodes) != list:
        nodes = [nodes]
    if years == "all":
        years = sorted([x for x in set(sc.set("year")) if x >= sc.firstmodelyear])
    elif type(years) != list:
        years = [years]

    # Preparing the bounds
    dfb = pd.DataFrame()
    for node in nodes:
        df = pd.DataFrame(columns=sc.par(parname).columns)
        yr_col = [x for x in df.columns if "year" in x][0]
        df[yr_col] = years
        df["value"] = value
        df["technology"] = tec
        df["node_loc"] = node
        if "mode" in df.columns:
            df["mode"] = mode
            df["unit"] = "GWa"
            for t in times:
                df["time"] = t
                dfb = pd.concat([dfb, df], ignore_index=True)
        else:
            df["unit"] = "GW"
            dfb = pd.concat([dfb, df], ignore_index=True)

    if add_to_scenario:
        sc.check_out()
        sc.add_par(parname, dfb)
        sc.commit("bound updated")
    return dfb


def add_bound_from_results(
    sc,
    parname="bound_activity_lo",
    tec="coal_ppl",
    nodes="all",
    years="all",
    multiplier=1,
    missing_value=0,
    times=["year"],
):
    """
    Adding bounds based on ACT (activity) or CAP (capacity) of a technology

    Parameters
    ----------
    sc : message_ix.Scenario
    parname : string, optional
        Bound name. The default is "bound_activity_lo".
    tec : string, optional
        Technology name. The default is "coal_ppl".
    nodes : List or "all", optional
        List of nodes to which the bound must be applied. The default is "all".
    years : List or "all", optional
        List of years to which the bound must be applied. The default is "all".
    multiplier : float, optional
        Multiplying the values for the bound. The default is 1.
    missing_value : float, optional
        Filling missing values with this value. The default is 0.
    times : list, optional
        List of sub-annual time slices for adding bounds. The default is ["year"].

    Returns
    -------
    bound : DataFrame
        DataFrame of the generated bounds.

    """

    # Nodes
    if nodes == "all":
        nodes = list(set(sc.set("node")))

    # Finding suitable years before or after the reference year
    if years == "all":
        years = sorted([x for x in set(sc.set("year")) if x >= sc.firstmodelyear])

    # Preparing the bounds
    bound = pd.DataFrame()
    for node in nodes:
        columns = sc.par(parname).columns

        # year index
        yr_col = [x for x in columns if "year" in x][0]

        # Reading the results based on the submitted "bound" parameter
        if "activity" in parname:
            varname = "ACT"
        elif "total" in parname:
            varname = "CAP"
        else:
            varname = "CAP_NEW"

        idx = [x for x in sc.idx_names(varname) if x != "year_vtg"]
        result = sc.var(varname, {"node_loc": node, "technology": tec, yr_col: years})
        if "activity" in parname:
            result = result.loc[result["time"].isin(times)].copy()
        result = (
            result.groupby(idx)
            .sum(numeric_only=True)
            .reset_index()
            .rename({"lvl": "value", "mrg": "unit"}, axis=1)
        )

        result = result[columns]
        # In case no results available
        if result.empty:
            modes = list(
                set(
                    sc.par(
                        "output", {"technology": tec, "node_loc": node, "time": times}
                    )["mode"]
                )
            )
            for mode in modes:
                result = pd.concat(
                    [
                        result,
                        add_bound(
                            sc,
                            parname,
                            tec,
                            node,
                            years,
                            missing_value,
                            mode,
                            times,
                            False,
                        ),
                    ],
                    ignore_index=True,
                )

        if result.empty:
            continue
        # Adding missing values (ToDO: find missing values if two modes)
        missing_years = [x for x in years if x not in set(result[yr_col])]
        for yr in missing_years:
            d = result.iloc[[0]].copy()
            d[yr_col] = yr

            # Bound for missing values)
            d["value"] = missing_value
            result = pd.concat([result, d], ignore_index=True)

        # Multiplying values if needed
        result["value"] *= multiplier

        # Adding unit
        if "mode" in columns:
            result["unit"] = "GWa"
        else:
            result["unit"] = "GW"

        # Slicing and appending the results
        bound = pd.concat([bound, result], ignore_index=True)
    return bound


def extend_bound(
    sc,
    parname,
    tec,
    year_ref=2020,
    yr_forward=True,
    nodes="all",
    years="all",
    multiplier=1,
    times=["year"],
):
    """
    Adding bounds on activity of a technology as a ratio to the total activity of
    a group of technologies in that level/commodity.

    Parameters
    ----------
    sc : message_ix.Scenario
    parname : string, optional
        Bound name. The default is "bound_activity_lo".
    tec : string, optional
        Technology name. The default is "coal_ppl".
    year_ref : int, optional
        Reference year for using the results. The default is 2020.
    yr_forward : bool, optional
        Forewarding the bounds from reference year. The default is True.
    nodes : List or "all", optional
        List of nodes to which the bound must be applied. The default is "all".
    years : List or "all", optional
        List of years to which the bound must be applied. The default is "all".
    multiplier : float, optional
        Multiplying the values for the bound. The default is 1.
    times : list, optional
        List of sub-annual time slices for adding bounds. The default is ["year"].

    Returns
    -------
    dfb : DataFrame
        DataFrame of the generated bounds.

    """
    # Multiplier can be list or a number
    if nodes == "all":
        nodes = [
            x for x in set(sc.set("node")) if x not in ["World", "R14_GLB", "R11_GLB"]
        ]

    # Finding suitable years before or after the reference year
    if years == "all" and yr_forward:
        years = sorted([x for x in set(sc.set("year")) if x > year_ref])

    if years == "all" and not yr_forward:
        years = sorted([x for x in set(sc.set("year")) if x < year_ref])
    # Preparing the bounds
    dfb = pd.DataFrame()
    for node in nodes:
        df = pd.DataFrame(columns=sc.par(parname).columns)
        yr_col = [x for x in df.columns if "year" in x][0]
        df[yr_col] = years

        # Finding relevant level and commodity
        lvl = list(
            set(sc.par("output", {"technology": tec, "node_loc": node})["level"])
        )[0]
        com = list(
            set(sc.par("output", {"technology": tec, "node_loc": node})["commodity"])
        )[0]
        mode = list(
            set(sc.par("output", {"technology": tec, "node_loc": node})["mode"])
        )[0]
        tec_list = list(
            set(
                sc.par("output", {"node_loc": node, "commodity": com, "level": lvl})[
                    "technology"
                ]
            )
        )

        # Reading the results
        if "activity" in parname:
            varname = "ACT"
        elif "total" in parname:
            varname = "CAP"
        else:
            varname = "CAP_NEW"
        res = sc.var(varname, {"node_loc": node, "technology": tec, yr_col: year_ref})[
            "lvl"
        ].sum()
        tot = sc.var(
            varname, {"node_loc": node, "technology": tec_list, yr_col: year_ref}
        )["lvl"].sum()
        others = (
            sc.var(varname, {"node_loc": node, "technology": tec_list, yr_col: years})
            .groupby([yr_col])
            .sum(numeric_only=True)["lvl"]
            .sort_index()
            .to_list()
        )

        # Basis share
        share = res / tot

        # Adding data for each year (one number or a list)
        df["value"] = [share * multiplier * x for x in others]
        df["technology"] = tec
        df["node_loc"] = node
        if "mode" in df.columns:
            df["unit"] = "GWa"
            df["mode"] = mode
            for t in times:
                df["time"] = t
                dfb = pd.concat([dfb, df], ignore_index=True)
        else:
            df["unit"] = "GW"
            dfb = pd.concat([dfb, df], ignore_index=True)
    return dfb


def update_share(
    sc,
    relation,
    tec_relation,
    tec_share,
    tec_list,
    nodes="all",
    year_hist=2015,
    parname="relation_activity",
):
    """
    Updating the existing shares in relation_activity based on new historical data.
    For example, updating share of "electric_transport"
    Parameters
    ----------
    sc : MESSAGEix scenario object
        scenario of the nesting process.
    relation : string
        relation that needs to be updated.
    tec_relation : string
        technology in the relation that the share applies to its activity.
    tec_share : string
        technology that its share is being calculated.
    tec_list : list
        list of technologies for the total sum of activity.
    nodes : list, optional
        node that the share needs to be updated. The default is 'all'.
    year_hist : int, optional
        historical year as the basis of share calculation. The default is 2015.
    parname : string, optional
        parameter fo relation activity. The default is 'relation_activity'.
    Returns
    -------
    None. The updated share will be added to the scenairo.
    """
    # tec_list = [x for x in set(sc.set('technology')) if x.endswith("_trp")]
    # tec_relation = 'useful_transport'
    # relation = 'UE_transport_electric_Minimum'
    sc.check_out()

    if nodes == "all":
        nodes = [x for x in set(sc.set("node")) if x not in ["World"]]

    for node in nodes:
        df = sc.par(
            "historical_activity",
            {"node_loc": node, "year_act": year_hist, "technology": tec_list},
        )

        df_share = df.loc[df["technology"] == tec_share]
        if not df_share.empty:
            share = round(float(df_share["value"]) / df["value"].sum(), 3)
            df2 = sc.par(
                parname,
                {"node_loc": node, "technology": tec_relation, "relation": relation},
            )
            if not df2.empty:
                old_share = df2["value"].mean()
                df2["value"] = -share
                sc.add_par(parname, df2)
                print(
                    ' Share of "{}" in relation "{}" in node "{}" was '
                    " updated from {} to {}".format(
                        tec_share, relation, node, str(-old_share), str(share)
                    )
                )
            else:
                print(
                    ' There is no share for "{}" in relation "{}" in node'
                    ' "{}" to be updated.'.format(tec_share, relation, node)
                )

    sc.commit("share updated.")


def read_var(
    sc,
    variable,
    tec_list,
    time=["year"],
    node="all",
    year_col="year_act",
    rename_tec={},
    year_min=2020,
    year_max=2050,
    year_result=None,
    groupby_by_year="year",
):
    """
    Fetching data of a parameter or variable and sorting that for a given information.

    Parameters
    ----------
    sc : message_ix.Scenario
    variable : str
        message_ix parameter or variable.
    tec_list : list
        List of technologies for generating the data.
    time : list, optional
        List of sub-annual time slices. The default is ["year"].
    node : list or "all", optional
        List of nodes. The default is "all".
    year_col : str, optional
        The index name for "year" to groupby the results. The default is "year_act".
    rename_tec : dict, optional
        Renaming technologies for reporting. The default is {}.
    year_min : int, optional
        Minimum model year for the results. The default is 2020.
    year_max : int, optional
        Maximum model years for the results. The default is 2050.
    year_result : int or None, optional
        If int, the results only for this year will be reported. The default is None.
    groupby_by_year : bool, optional
        If "True, grouping the results by year if not by "time". The default is True.

    Returns
    -------
    df : DataFrame
        DataFranme of the results.

    """
    # Nodes
    if node == "all":
        node = [x for x in sc.set("node") if x != "World"]

    # Finding if variable is MESSAGEix parameter or not
    if variable in sc.par_list():
        value = "value"
    else:
        value = "lvl"
    # Fetching variable data
    if time:
        if variable in sc.par_list():
            df = sc.par(
                variable, {"node_loc": node, "technology": tec_list, "time": time}
            )
        else:
            df = sc.var(
                variable, {"node_loc": node, "technology": tec_list, "time": time}
            )
    else:
        if variable in sc.par_list():
            df = sc.par(variable, {"node_loc": node, "technology": tec_list})
        else:
            df = sc.var(variable, {"node_loc": node, "technology": tec_list})

    # Results for one year
    if year_result:
        df = df.loc[df[year_col] == year_result].copy()

    # Grouping
    if groupby_by_year:
        df = df.groupby([year_col, "technology"]
                        ).sum(numeric_only=True)[[value]].reset_index()
    else:
        df = df.groupby(["time", "technology"]
                        ).sum(numeric_only=True)[[value]].reset_index()

    # Pivot table
    df = df.pivot_table(index=year_col, columns="technology", values=value)
    df = df.fillna(0)

    # Renaming
    if rename_tec:
        d = pd.DataFrame(index=df.index)
        for key, val in rename_tec.items():
            d[key] = df.loc[:, df.columns.isin(val)].sum(axis=1)
        df = d.copy()

    # Choosing non-zero columns
    df = df.loc[:, (df != 0).any(axis=0)].copy()

    # Min maximum year
    if not year_result:
        df = df[(df.index <= year_max) & (df.index >= year_min)].copy()
    return df


def subtract_data(
    sc, node, node_ref, parname, sc_ref=None, filters={}, negative_value=False
):
    """
    Description:
        This functions subtracts the data of parameter "parname" in "node_ref"
        in scenario "sc_ref", from the data of "node" in "sc".
        "sc" and "sc_ref" can be the same scenario (if sc_ref = None).


    Parameters
    ----------
    sc : MESSAGEix scenario object
        scenario of the nesting process.
    sc_ref : MESSAGEix scenario object
        reference scenario to read the data of the nested node
        (if None, sc_ref = sc).
    node : string
        model region to subtract data from (e.g., R11_WEU).
    node_ref : string
        model region, data of which to be subtracted from node (e.g., R11_NOR).
    parname : string
        MESSAGEix parameter.
    filters : dictionary (default: {})
        filters to slice a parameter for subtracting
    negative_value: bool
        if False, negative values after subtraction will be removed, otherwise
        will be returned as they are.

    Returns
    -------
    DataFrame
        Results of subtraction ready to be added to the respective parameter.

    """

    if not sc_ref:
        sc_ref = sc

    # Finding relevant indexes
    idx = [x for x in sc.idx_names(parname)]
    node_idx = [x for x in idx if "node" in x][0]

    sc.check_out()

    # Load the data of the whole
    filters.update({node_idx: node})
    df_old = sc.par(parname, filters)

    # If no data in the parent region, return empty dataframe
    if df_old.empty:
        sc.commit("")
        return df_old

    df_old = df_old.set_index(idx)

    # Load the data that must be subtracted
    filters.update({node_idx: node_ref})
    df_ref = sc_ref.par(parname, filters)
    df_ref[node_idx] = node
    df_ref = df_ref.set_index(idx)

    # Finding common indexes to be subtracted
    df_ref = df_ref.loc[df_ref.index.isin(df_old.index)].copy()

    # Subtracting
    df_new = df_old.loc[df_old.index.isin(df_ref.index)].copy()
    df_new["value"] -= df_ref["value"]

    # Removing negative values
    if not negative_value:
        df_new = df_new.loc[df_new["value"] >= 0].copy()

    sc.add_par(parname, df_new.reset_index())
    print(
        ' Data of "{}" was subtracted from "{}" in Parameter "{}"'.format(
            node_ref, node, parname
        )
    )

    sc.commit("data subtracted")
    return df_new.reset_index()


def biomass_globiom(sc, node_parent, node):
    """
    Linking biomass in primary level to Globiom
    Parameters
    ----------
    sc : MESSAGEix scenario object
        scenario of the nesting process.
    node_parent : string
        parent node.
    node : string
        nested node.

    Returns
    -------
    None.

    """

    sc.check_out()
    # Finding technology/ies generating biomass primary in the nested node
    tecs = list(
        set(
            sc.par(
                "output", {"node_loc": node, "commodity": "biomass", "level": "primary"}
            )["technology"]
        )
    )

    # Finding technology/ies generating biomass primary in the parent node
    tecs_parent = list(
        set(
            sc.par(
                "output",
                {"node_loc": node_parent, "commodity": "biomass", "level": "primary"},
            )["technology"]
        )
    )

    # Finding output of technology/ies generating biomass in the parent node
    inp = sc.par("input", {"node_loc": node_parent, "technology": tecs_parent})

    # Removing input and cost of biomass technologies in nested node (if any)
    for parname in ["input", "inv_cost", "var_cost", "fix_cost"]:
        df = sc.par(parname, {"node_loc": node, "technology": tecs})
        if not df.empty:
            sc.remove_par(parname, df)

    # Linking the input of biomass in the nested node to the parent
    df = inp.copy()
    for t in tecs:
        df["technology"] = t
        df["node_loc"] = node
        sc.add_par("input", df)

    print(
        '- Input of biomass technologies in "{}" was linked to the "{}"'
        ' in "{}".'.format(node, tecs_parent, node_parent)
    )
    sc.commit("globiom linked")


def correct_sum_history(sc, tec_dict={}, extraction_mpen=True):
    """
    Correcting the activity of technologies, which are the sum of other technologies
    in the historical data (needed after subtracting data of one node from another)
    Parameters
    ----------
    sc : Object
        MESSAGEix Scenario.
    tec_dict : dictionary, optional
        dictionary of technologies (dict keys) that should be the sum of other
        technologies (dict values). The default is {}.
    extraction_mpen : bool, optional
        correcting market penetration activity. The default is True.
    """
    if extraction_mpen:
        # Extraction technologies
        extr = {
            "gas_extr_mpen": [
                "gas_extr_1",
                "gas_extr_2",
                "gas_extr_3",
                "gas_extr_4",
                "gas_extr_5",
                "gas_extr_6",
            ],
            "oil_extr_mpen": [
                "oil_extr_1",
                "oil_extr_1_ch4",
                "oil_extr_2",
                "oil_extr_2_ch4",
                "oil_extr_3",
                "oil_extr_3_ch4",
                "oil_extr_4",
                "oil_extr_4_ch4",
                "oil_extr_5",
                "oil_extr_6",
                "oil_extr_7",
            ],
            "coal_extr_mpen": [
                "coal_extr",
                "coal_extr_ch4",
                "lignite_extr",
            ],
        }
        # Updating technology mapping
        tec_dict.update(extr)

    parname = "historical_activity"

    sc.check_out()
    for t_mp, tec_list in tec_dict.items():
        df = sc.par(parname, {"technology": tec_list})
        df["technology"] = t_mp
        df = df.groupby(sc.idx_names(parname)).sum(numeric_only=True)
        df = df.reset_index()
        df["unit"] = "GWa"
        if not df.empty:
            sc.add_par(parname, df)
    sc.commit("mpen technologies updated")


def subtract_RE_new_from_old(sc, node_new, node_old, rel_dict={}):
    """
    Subtracting new renewable potentials in one node from old implementation in
    another node.
    Notice: this function is not checking if numbers match between old and new
    implementations.

    Parameters
    ----------
    sc : message_ix.Scenario
    node_new : str
        Node to subtract the data of it (e.g., a country).
    node_old : str
        Node to subtract the data from (e.g., a MESSAGE region in the global model).
    rel_dict : dict, optional
        Pairing commodities and relations for renewable potential. The default is {}.

    """
    par_new = "renewable_potential"
    par_old = "relation_upper"

    if not rel_dict:
        rel_dict = {
            "hydro": "hydro",
            "solar_pot": "solar_pv",
            "wind_pot": "wind_offshore",
            "wind_pof": "wind_onshore",
        }

    # Retrieving old potential
    for rel_old, com_new in rel_dict.items():
        df_new = sc.par(par_new, {"node": node_new, "commodity": com_new})
        grade_list = sorted(list(set(df_new["grade"])))

        # Finding relation list of this commodity
        rel_list = sorted([x for x in set(sc.set("relation")) if rel_old in x])

        for yr in set(df_new["year"]):
            for grade in grade_list:
                df_g = df_new.loc[(df_new["grade"] == grade) & (df_new["year"] == yr)][
                    "value"
                ]
                val_new = float(df_g)

                # Finding corresponding relation in old implementation
                k = 0
                while val_new > 0:
                    if grade_list.index(grade) + k > len(rel_list) - 1:
                        print(
                            "- Warning: Not enough renewable potential "
                            'for "{}" in "{}" to subtract data '
                            'of "{}"'.format(node_old, rel_old, node_new)
                        )
                        break
                    rel = rel_list[grade_list.index(grade) + k]
                    df = sc.par(
                        par_old, {"node_rel": node_old, "relation": rel, "year_rel": yr}
                    )

                    # Subtracting
                    if df.empty:
                        val_old = 0
                    else:
                        val_old = float(df["value"])
                    if val_new > val_old:
                        df["value"] = 0
                        val_new = val_new - val_old
                        k = k + 1
                    else:
                        df["value"] = val_old - val_new
                        val_new = 0
                    sc.add_par(par_old, df)


def remove_tec_from_node(sc, technologies, nodes):
    """
    removing a technology from a region
    Parameters
    ----------
    sc : Object
        MESSAGEix Scenario.
    technologies : string or list of strings
        technology/ies to be removed.
    nodes :  string or list of strings
        node/s to be removed.

    """
    par_list = [x for x in sc.par_list() if "technology" in sc.idx_sets(x)]
    par_list = [x for x in par_list if "node" in sc.idx_sets(x)]
    sc.check_out()
    for parname in par_list:
        node_idx = [x for x in sc.idx_names(parname) if "node" in x]
        for node_column in node_idx:
            df = sc.par(parname, {node_column: nodes, "technology": technologies})
            sc.remove_par(parname, df)
    sc.commit("technology was removed")
    print('- Technology "{}" removed from "{}".'.format(technologies, nodes))


def par_copy(
    sc_ref,
    sc=None,
    tec_ref="coal_ppl",
    tec=None,
    node_ref="all",
    node="all",
    par_list="all",
    par_exclude=[],
    remove_old=True,
):
    """
    Copying parameters from one technology to another

    Parameters
    ----------
    sc_ref : message_ix.Scenario()
        MESSAGEix Scenario for copying data from.
    sc : message_ix.Scenario()
        MESSAGEix Scenario for copying the data to.
    tec_ref : string
        reference technology for copying parameters from.
    tec : string or None, optional
        technology for copying parameters to. if None: the same as tec_ref.
    node_ref : string
        reference node for copying parameters from.
    node : string
        node for copying parameters to.
    par_list : list, optional
        list of parameters to be copied. The default is 'all'.
    par_exclude : list, optional
        list of parameters to be excluded from being copied. The default is [].
    remove_old : bool, optional
        removing old data before copying new data. The default is True.

    """
    if not sc:
        sc = sc_ref

    sc.check_out()
    if par_list == "all":
        par_list = sc.par_list()

    if not tec:
        tec = tec_ref
    elif tec not in set(sc.set("technology")):
        sc.add_set("technology", tec)

    par_list = [x for x in par_list if x not in par_exclude]

    print(
        "- The following parameters will be copied from "
        "{}/{} to {}/{}:".format(node_ref, tec_ref, node, tec)
    )
    for parname in par_list:
        node_col = [
            x
            for x in sc.idx_names(parname)
            if x in ["node", "node_loc", "node_rel", "node_share"]
        ]

        if node_col and "technology" in sc.idx_names(parname):
            if node_ref == "all":
                df = sc_ref.par(parname, {"technology": tec_ref})
                old = sc.par(parname, {"technology": tec})
            else:
                df = sc_ref.par(parname, {node_col[0]: node_ref, "technology": tec_ref})
                old = sc.par(parname, {node_col[0]: node, "technology": tec})

            # Remving old data (optional)
            if remove_old:
                sc.remove_par(parname, old)
            if not df.empty:
                df["technology"] = tec
                if node_ref != "all":
                    df = df.replace(node_ref, node)
                sc.add_par(parname, df)
                print(parname)
    sc.commit("parameters copied")


def demand_supply_match(
    sc,
    node_commodity=[("R14_NAM", "useful", "i_feed", 2020)],
    correct=True,
    find_imbalance=True,
):
    """
    Checking if supply > demand, which will result in zero commodity prices

    Parameters
    ----------
    sc : message_ix.Scenario
    node_commodity : list of tuples, optional
        Info for setting balance equality. The default is [("R14_NAM", "useful", "i_feed", 2020)].
    correct : bool, optional
        Setting supply == demand for commodities specified or found imbalanced. The default is True.
    find_imbalance : bool, optional
        if True, find commodity-level pairs at which supply > demand. The default is True.

    """
    if find_imbalance:
        if sc.has_solution():
            print("Scenario has no solution, please check!!!")
            return
        results = []
        for node, lvl, com, yr in node_commodity:
            # Demand
            dem = sc.par(
                "demand", {"commodity": com, "node": node, "level": lvl, "year": yr}
            )
            dem = float(dem["value"])

            # Activity
            out = sc.par("output", {"commodity": com, "node_loc": node, "year_act": yr})
            tec_list = list(set(out["technology"]))
            act = sc.var(
                "ACT", {"technology": tec_list, "node_loc": node, "year_act": yr}
            )["lvl"].sum()

            # Checking
            if act > dem:
                print("Oversupply of {} in {} {}".format(com, node, yr))
                results.append((node, com, yr))
            if correct:
                # Correction by cloning
                sc = sc.clone(keep_solution=False)

    else:
        results = node_commodity

    # Set supply = balance
    if correct:
        sc.check_out()
        for node, lvl, com, yr in results:
            sc.add_set("balance_equality", [com, lvl])
            print("Balance equality added for {}-{}".format(com, lvl))
        sc.commit("")


def add_emission_bound(
    scen,
    budget=float,
    adjust_cumulative=False,
    type_emission="TCE",
    type_tec="all",
    type_year="cumulative",
    region="World",
    unit="tC",
):
    """Adds a budget constraint to a given region.
    Parameters
    ----------
    scen : :class:`message_ix.Scenario`
        Scenario to which budget should be applied
    budget : numeric
        Budget in average tC
    adjust_cumulative : bool, optional
        Option whether to adjust cumulative years to which the budget is applied to
        the optimization time horizon.
    type_emission : str (default: 'TCE')
        type_emission for which the constraint should be applied. This element must
        already be defined in `scen`.
    type_tec : str (default: 'all')
        technology type for which the bound applies
    region : str (default: 'World')
        region to which the bound applies
    unit : str (default: 'tC')
        unit in which the bound is provided
    """

    scen.check_out()

    if adjust_cumulative:
        current_cumulative_years = scen.set("cat_year", {"type_year": ["cumulative"]})

        remove_cumulative_years = current_cumulative_years[
            current_cumulative_years["year"] < scen.firstmodelyear
        ]

        if not remove_cumulative_years.empty:
            scen.remove_set("cat_year", remove_cumulative_years)

    scen.add_par(
        "bound_emission", [region, type_emission, type_tec, type_year], budget, unit
    )

    scen.commit(f"bound_emission {budget} added")


def prep_for_macro(sc_clone_from, sc, year, regions="all"):
    """
    Adjusting demand and historical GDP based on output of another scenario
    Parameters
    ----------
    sc_clone_from : message_ix.Scenario
        Reference scenario for reading data from.
    sc : message_ix.Scenario
        Target scenario.
    year : int
        Year for the reference data.
    regions : list or "all", optional
        List of regions to be updated. The default is "all".

    """

    if regions == "all":
        demands = sc_clone_from.var("DEMAND")
        gdp = sc_clone_from.var("GDP")
    else:
        demands = sc_clone_from.var("DEMAND", {"node": regions})
        gdp = sc_clone_from.var("GDP", {"node": regions})

    assert not gdp.empty, "There is no MACRO results in submitted scenario!!!"

    # Preparing demand
    demands = demands.rename(columns={"lvl": "value"})
    demands["unit"] = "GWa"

    # Preparing GDP
    gdp = gdp.rename(columns={"lvl": "value"})
    gdp["unit"] = "T$"
    gdp = gdp[gdp["year"] == year].copy()

    # Adding data to the model
    sc.check_out()
    sc.add_par("demand", demands)
    sc.add_par("historical_gdp", gdp)
    sc.commit("")
    print(
        '- Parameters "demand" and "historical_gdp" updated with data'
        " from: {}/{}/{}".format(
            sc_clone_from.model, sc_clone_from.scenario, str(sc_clone_from.version)
        )
    )


def regional_mapping(
    sc,
    new_parent,
    subregions,
    new_level="subregion",
    old_parent="World",
    old_level="region",
):
    """
    Changes the spatial hierarchy of some nodes to a new parent node.

    Parameters
    ----------
    sc : message_ix.Scenario
    new_parent : string
        New node name as a new parent.
    subregions : list of strings
        Nodes that should be mapped to the new parent.
    new_level : string, optional
        New spatial level for the nodes. The default is 'subregion'.
    old_parent : string, optional
        Name of the existing parent node. The default is 'World'.
    old_level : string, optional
        Spatial level of the nodes before change. The default is 'region'.

    Returns
    -------
    Modifies the scenario directly.

    """

    sc.check_out()
    # Adding the new node
    sc.add_set("node", new_parent)
    df = sc.set("map_spatial_hierarchy")
    df = df.loc[
        (df["node"].isin(subregions)) & (df["node_parent"] == old_parent)
    ].reset_index(drop=True)

    # Removing the current mapping
    sc.remove_set("map_spatial_hierarchy", df)

    # Making a new mapping
    df["node_parent"] = new_parent
    df["lvl_spatial"] = new_level
    sc.add_set("map_spatial_hierarchy", df)

    # New region mapping
    sc.add_set("map_spatial_hierarchy", [old_level, new_parent, old_parent])
    sc.commit("")


def relative_emission(
    sc,
    sc_rf,
    sc_mitig,
    regions=["World"],
    emiss_ref="TCE_CO2",
    emiss_base="TCE_c",
    type_tec="all",
    slice_yr=2035,
    based_on_bound=False,
    regions_map={"World": "UNECE"},
    type_yr_cumul=False,
    unit="MtC",
):
    """
    Calculates emission bounds for a (target) scenario based on the relative emission
    in two scenarios (e.g., a "reference" relative to a "mitigation" scenario)

    Parameters
    ----------
    sc : message_ix.Scenario
        Target scenario.
    sc_rf : message_ix.Scenario
        Reference scenario.
    sc_mitig : message_ix.Scenario
        Mitigation scenario.
    regions : list, optional
        List of nodes for adding emission bounds. The default is ["World"].
    emiss_ref : string, optional
        Emission type to be used as reference. The default is "TCE_CO2".
    emiss_base : string, optional
        Emission type to be added to the target scenario. The default is "TCE_c".
    type_tec : string, optional
        Type of technologies for including in emissions bound. The default is "all".
    slice_yr : int, optional
        Year of slicing for cumulative bounds. The default is 2035.
    based_on_bound : TYPE, optional
        Calculating the relative reduction based on inpput "bound_emission" (True)
        or based on EMISS (False). The default is False.
    regions_map : dict, optional
        Mapping of global nodes from the reference to target scenario.
        The default is {"World": "UNECE"}.
    type_yr_cumul : bool, optional
        A flag for calculating cumulative emissions. The default is False.
    unit : string, optional
        Unit to be used for emissions. The default is "MtC".
    """
    # Renaming dictionary
    rename = {
        "lvl": "value",
        "mrg": "unit",
        "year": "type_year",
        "emission": "type_emission",
    }
    yrs = [x for x in set(sc_rf.set("year")) if x >= slice_yr]

    yrs_em = "cumulative" if type_yr_cumul else yrs

    # Emissions of the reference mitigation scenario
    # Either based on the bounds
    if based_on_bound:
        mit = sc_mitig.par(
            "bound_emission",
            {
                "node": regions,
                "type_year": yrs_em,
                "type_emission": emiss_ref,
                "type_tec": type_tec,
            },
        )
        mit = mit.set_index(["node", "type_year"])
    # Or based on the output emissions
    else:
        mit = sc_mitig.var(
            "EMISS",
            {
                "node": regions,
                "year": yrs_em,
                "emission": emiss_ref,
                "type_tec": type_tec,
            },
        ).rename(rename, axis=1)
        mit = mit.set_index(["node", "type_year"])

    # Emissions of the reference scenario
    ref = sc_rf.var(
        "EMISS",
        {"node": regions, "year": yrs_em, "emission": emiss_ref, "type_tec": type_tec},
    ).rename(rename, axis=1)
    ref = ref.set_index(["node", "type_year"])

    # Calculating emissions of mitigation relative to reference
    share = mit.copy()
    share["value"] /= ref["value"]
    share.index = [(regions_map[x[0]], x[1]) for x in share.index]

    # Emissions of new baseline
    regions_new = [regions_map[x] for x in regions]
    base = sc.var(
        "EMISS",
        {
            "node": regions_new,
            "year": yrs_em,
            "emission": emiss_base,
            "type_tec": type_tec,
        },
    ).rename(rename, axis=1)
    base = base.set_index(["node", "type_year"])

    # Applying shares from the reference scenarios to new baseline
    base["value"] *= share["value"]
    base["unit"] = unit
    return base.reset_index()


def transport_update(
    sc, data={}, base_cost=69, remove_capex=["h2_fc_trp"], remove_tec=["coal_trp"]
):
    """
    Updating cost and efficiency of transport technologies.

    Parameters
    ----------
    sc : message_ix.Scenario
    data : dict, optional
        The info of the region, technology, and parameters that must be udpated,
        e.g., {"R11_NAM": {"elec_trp": {"cost": 1.2, "input": 0.28}}}.
        The default is {}.
    base_cost : int or float, optional
        The base cost for "relation_cost". The default is 69 $/kWa.
    remove_capex : list, optional
        List of technologies for which the CAPEX is removed. The default is ["h2_fc_trp"].
    remove_tec : list, optional
        List of technologies to be removed. The default is ["coal_trp"].

    """
    # Default data
    if not data:
        data = {
            "all": {
                "elec_trp": {"cost": 1.2, "input": 0.28},
                "eth_fc_trp": {"cost": 4.5, "input": 0.45},
                "eth_ic_trp": {"cost": 1, "input": 1},
                "foil_trp": {"cost": 1.3, "input": 1.05},
                "gas_trp": {"cost": 1.2, "input": 1.07},
                "loil_trp": {"cost": 1, "input": 1},
                "meth_fc_trp": {"cost": 4, "input": 0.45},
                "meth_ic_trp": {"cost": 1, "input": 1},
                "h2_fc_trp": {"cost": 4.5, "input": 0.4},
            },
            "R14_NAM": {
                "elec_trp": {"cost": 1.2, "input": 0.28},
                "eth_fc_trp": {"cost": 4.5, "input": 0.45},
                "eth_ic_trp": {"cost": 1, "input": 1},
                "foil_trp": {"cost": 1.3, "input": 1.05},
                "gas_trp": {"cost": 1.2, "input": 1.07},
                "loil_trp": {"cost": 1 * 1.25, "input": 1},
                "meth_fc_trp": {"cost": 4, "input": 0.45},
                "meth_ic_trp": {"cost": 1, "input": 1},
                "h2_fc_trp": {"cost": 4.5, "input": 0.4},
            },
        }

    sc.check_out()

    # Removing coal transport
    for t in remove_tec:
        if t in set(sc.set("technology")):
            sc.remove_set("technology", t)
            print("- {} removed.".format(t))

    # Removing inv_cost and technical_lifetime of fuel cells
    for parname in ["inv_cost", "technical_lifetime"]:
        df = sc.par(parname, {"technology": remove_capex})
        sc.remove_par(parname, df)

    # Removing vintaging
    for parname in [
        "input",
        "output",
        "var_cost",
        "fix_cost",
        "emission_factor",
        "capacity_factor",
    ]:
        df = sc.par(parname, {"technology": remove_capex})
        sc.remove_par(parname, df)
        df = df.loc[df["year_act"] == df["year_vtg"]].copy()
        sc.add_par(parname, df)

    print("- Capex removed and vintaging corrected for {}".format(remove_capex))
    # Updating O&M cost in relations
    nodes = [x for x in sc.set("node") if x not in data.keys()]
    for node, item in data.items():
        if node == "all":
            node = nodes

        # Changing the base cost
        df_cost = sc.par("relation_cost", {"relation": "weight_trp", "node_rel": node})
        df_cost["value"] = base_cost
        sc.add_par("relation_cost", df_cost)

        # Loading existing data
        for tec, info in item.items():
            # Cost
            df_cost = sc.par(
                "relation_activity",
                {"relation": "weight_trp", "node_loc": node, "technology": tec},
            )
            if df_cost.empty:
                df_cost = sc.par(
                    "relation_activity",
                    {
                        "relation": "weight_trp",
                        "node_loc": node,
                        "technology": "loil_trp",
                    },
                )
                df_cost["technology"] = tec

            df_cost["value"] = info["cost"]
            sc.add_par("relation_activity", df_cost)

            # Input fuel
            df_inp = sc.par("input", {"node_loc": node, "technology": tec})
            df_inp["value"] = info["input"]
            sc.add_par("input", df_inp)

    print("- O&M updated for transport technologies.")
    sc.commit("")


def compare_scen_tech(sc1, sc2, node1="R14_WEU", node2=None, tec1="h2_smr", tec2=None):
    """
    Comparing two scenarios on parameters of one or two technologies.

    Parameters
    ----------
    sc1 : message_ix.Scenario
        First scenario to be compared.
    sc2 : message_ix.Scenario
        Second scenario to be compared.
    node1 : string, optional
        Node in the first scenario. The default is "R14_WEU".
    node2 : string or None, optional
        Node in the second scenario (if None, the same node as node1 is used).
        The default is None.
    tec1 : string, optional
        Technology to be compared from scenario 1. The default is "h2_smr".
    tec2 : string or None, optional
        Technology to be compared from scenario 2. (if None, the same technology
        as tec1 is used). The default is "h2_coal".

    """
    # Generating None value entries
    node2 = node1 if not node2 else node2
    tec2 = tec1 if not tec2 else tec2

    par_list = [x for x in sc1.par_list() if "technology" in sc1.idx_sets(x)]
    par_list2 = [x for x in sc2.par_list() if "technology" in sc2.idx_sets(x)]

    # Creating two dictionaries to compare
    par_dict1 = {}
    for parname in par_list:
        node_call = [
            x for x in sc1.idx_names(parname) if x in ["node", "node_loc", "node_rel"]
        ]
        if node_call:
            par1 = sc1.par(parname, {"technology": tec1, node_call[0]: node1})
            if not par1["value"].dropna().empty:
                par_dict1[parname] = par1
        else:
            par1 = sc1.par(parname, {"technology": tec1})
            if not par1["value"].dropna().empty:
                par_dict1[parname] = par1

    par_dict2 = {}
    if tec2:
        for parname in par_list2:
            node_call = [
                x
                for x in sc2.idx_names(parname)
                if x in ["node", "node_loc", "node_rel"]
            ]
            if node_call:
                par2 = sc2.par(parname, {"technology": tec2, node_call[0]: node2})
                if not par2["value"].dropna().empty:
                    par_dict2[parname] = par2
            else:
                par2 = sc2.par(parname, {"technology": tec2})
                if not par2["value"].dropna().empty:
                    par_dict2[parname] = par2
    return par_dict1, par_dict2


def update_cost(
    sc,
    sc_ref=None,
    regions="all",
    par_list="all",
    tec_list="all",
    conversion=1.325,
    region_mapping={},
):
    """
    Updates the value of cost-related parameters in a MESSAGEix model.
    Notice: does not change "unit" entries.

    Parameters
    ----------
    sc : message_ix.Scenario
        Scenario to be edited.
    sc_ref : message_ix.Scenario, optional
        A reference scenario for copying parameters from. The default is None.
    regions : list or "all", optional
        List of model regions to be used for cost conversion. The default is "all".
    par_list : list or "all", optional
        List of parameters to be updated. The default is "all".
    tec_list : list or "all", optional
        List of technologies for which cost to be updated. The default is "all".
    conversion : float or int, optional
        Conversion factor for cost. The default is 1.325 (USD2005 to 2020).
    region_mapping : dict, optional
        Mapping of regions when copying from another scenario. The default is {}.

    Returns
    -------
    None.

    """
    if par_list == "all":
        par_list = [
            "abs_cost_activity_soft_lo",
            "abs_cost_activity_soft_up",
            "abs_cost_new_capacity_soft_lo",
            "abs_cost_new_capacity_soft_up",
            "cost_MESSAGE",
            "fix_cost",
            "inv_cost",
            "land_cost",
            "relation_cost",
            "resource_cost",
            "price_MESSAGE",
            "tax_emission",
            "var_cost",
        ]

    if regions == "all":
        regions = sc.set("node").tolist()

    if not sc_ref:
        sc_ref = sc

    if tec_list == "all":
        tec_list = list(set(sc.set("technology")))

    # Updating the costs
    sc.check_out()
    for parname in [x for x in par_list if x in sc.par_list()]:
        node_col = [x for x in sc.idx_names(parname) if "node" in x][0]

        # If copying from another model/scenario
        if region_mapping:
            for node_ref, node_list in region_mapping.items():
                df_ref = sc_ref.par(parname, {node_col: node_ref})

                df = pd.DataFrame(columns=df_ref.columns)
                for node in node_list:
                    df_ref[node_col] = node
                    df = pd.concat([df, df_ref], ignore_index=True)

        else:
            df = sc_ref.par(parname, {node_col: regions})

        # Check if technology exists in the list
        if "technology" in df.columns:
            df = df.loc[df["technology"].isin(tec_list)].copy()

        # Cost conversion
        df["value"] *= conversion
        sc.add_par(parname, df)
        print("Cost updated for parameter {}".format(parname))
    sc.commit("")


# %% Removing cooling technologies from a list
def remove_cooling(sc, tec_list=[], cool_terms=[], com_cool=[], lvl_cool=[]):
    print("- Removing cooling technologies...")

    # Both commodity and technology must be removed
    if not cool_terms:
        cool_terms = ["__air", "__cl_fresh", "__ot_fresh", "__ot_saline"]

    # Cooling technologies
    if not tec_list:
        tec_list = sorted(list(set(sc.set("technology"))))
    tec_cool = [
        x
        for x in set(sc.set("technology"))
        if x in [y + z for (y, z) in product(tec_list, cool_terms)]
    ]
    # tec_cool = sc2.set('cat_tec', {'type_tec': 'power_plant_cooling'})
    tec_cool = [x for x in tec_cool if x in set(sc.set("technology"))]

    # Cooling commodities
    if not com_cool:
        com_cool = [
            x
            for x in sc.set("commodity").tolist()
            if any([y in x for y in ["cooling"]])
        ]

    # Cooling levels
    if not lvl_cool:
        lvl_cool = ["cooling"]

    sc.check_out()
    for x in tec_cool:
        sc.remove_set("technology", x)
    for x in com_cool:
        sc.remove_set("commodity", x)
    for x in lvl_cool:
        if x in sc.set("level"):
            sc.remove_set("level", x)
    tec_list = [x for x in tec_list if x not in tec_cool]
    tec_rem = list(set([x.split("__")[0] for x in tec_cool]))
    print(
        "- Cooling technologies for {}, and cooling commodities {}, and"
        " levels {} were removed.".format(tec_rem, com_cool, lvl_cool)
    )
    sc.commit("cooling removed")
    return sorted(tec_list)


# %% Change initial activity parameters for some nodes based on different ratios
def change_parameter_values(
    sc,
    sc_ref=None,
    node_ref="R14_RUS",
    shares={"R14_RUS": 0.81, "R14_CAS": 0.08, "R14_SCS": 0.03, "R14_UBM": 0.08},
    par_dict={
        "initial_activity_lo": ["loil_trp"],
        "initial_activity_up": "all",
    },
):
    # Assigning the reference scenario
    if not sc_ref:
        sc_ref = sc

    sc.check_out()
    for parname, tec_list in par_dict.items():
        node_col = [x for x in sc.idx_names(parname) if "node" in x][0]
        if tec_list != "all":
            df = sc_ref.par(parname, {node_col: node_ref, "technology": tec_list})
        else:
            df = sc_ref.par(parname, {node_col: node_ref})

        # Chaning values based on shares from the parent
        for node, ratio in shares.items():
            df_new = df.copy()
            df_new[node_col] = node
            df_new["value"] *= ratio
            sc.add_par(parname, df_new)

    sc.commit("")


def rename_node(sc, rename):
    """
    This scripts renames the specified nodes by new node names
    The procedure is as follows:
        - Adding the new node names to the model
        - Creating required sets with new node names
        - Replacing the old node names with new ones in the parameters
        - Removing old node names from the model
    Parameters
    ----------
    sc : message_ix.Scenario
        Scenario to be edited.
    rename: dict
        A dictionary of the old names to new names.

    """
    # 1) Adding new nodes to relevant sets
    sc.check_out()
    sc.add_set("node", list(rename.values()))

    # Node related sets
    set_list = [x for x in sc.set_list() if "node" in sc.idx_sets(x)]
    for setname in set_list:
        old = sc.set(setname)
        new = old.replace(rename)
        sc.add_set(setname, new)
    sc.commit(" ")

    # 2) Replacing node names in parameters
    par_list = sc.par_list()

    # Break down large parameters to the nodes
    large_par = ["land_output"]
    par_list = [x for x in par_list if x not in large_par]

    # A secondary list to continue with if the for-loop collapses at some point
    par_list_check = par_list.copy()

    # Main parameters
    for parname in par_list:
        node_list = [col for col in list(sc.par(parname).columns) if "node" in col]
        if node_list:
            par_old = sc.par(parname)
            if par_old.empty:
                continue
            sc.check_out()
            par_new = par_old.copy()
            for node_type in node_list:
                par_new[node_type] = par_new[node_type].replace(rename)

            sc.remove_par(parname, par_old)
            sc.add_par(parname, par_new)
            sc.commit("")
            print('Nodes renamed in parameter "' + parname + '".')

        par_list_check.remove(parname)

    # Large parameters like "land_output"
    for parname in large_par:
        node_list = [col for col in list(sc.par(parname).columns) if "node" in col]
        for node in rename.keys():
            sc.check_out()
            for node_type in node_list:
                par_old = sc.par(parname, {node_type: node})
                if par_old.empty:
                    continue
                par_new = par_old.copy()
                par_new[node_type] = par_new[node_type].replace(node, rename[node])
                sc.add_par(parname, par_new)
            sc.commit("")
        print('Nodes renamed in parameter "' + parname + '".')

    # 3) Removing old nodes
    sc.check_out()
    for node in rename.keys():
        if node in set(sc.set("node")):
            sc.remove_set("node", node)
            print("Node " + node + " removed!")
    sc.commit("Nodes renamed!")


def add_share_activity(
    sc,
    relation,
    tec_share,
    tec_total,
    shares,
    regions,
    remove_old=True,
    bounds=[("relation_lower_time", 0)],
    parname="relation_activity_time",
):
    """
    Adding share constraints through user-defined relations

    Parameters
    ----------
    sc : message_ix.Scenario
    relation : string
        Name of relation.
    tec_share : list
        List of technologies forming the share.
    tec_total : list
        List of technologies forming the total.
    shares : dict
        Pair of year and share values, e.g., {2030: 0.2, 2050: 0.5}
    regions : list
        List of model regions that this share applies to.
    remove_old : bool, optional
        If this relation name exists, will be removed. The default is True.
    bounds : list, optional
        List of relation bound parameters and their values.
        The default is [("relation_lower_time", 0)].
    parname : string, optional
        Parameter of relations. The default is "relation_activity_time".

    """
    if relation in set(sc.set("relation")) and remove_old:
        sc.remove_set("relation", relation)
    sc.add_set("relation", relation)
    # If tec share in tec total
    tec_tot = [x for x in tec_total if x not in tec_share]
    tec_tot_share = [x for x in tec_total if x in tec_share]
    print(" - Adding share on activity ...")
    for yr, val in shares.items():
        # Total technologies Coefficient of total is (-)
        for tec, node in product(tec_tot, regions):
            # Check if technology has output in this node and year
            df = sc.par("output", {"node_loc": node, "technology": tec, "year_act": yr})
            if df.empty:
                continue
            else:
                mode = df["mode"][0]
            sc.add_par(
                parname, [relation, node, yr, node, tec, yr, mode, "year"], -val, "-"
            )
        # Share technologies
        for tec, node in product(tec_share, regions):
            # Check if technology has output in this node and year
            df = sc.par("output", {"node_loc": node, "technology": tec, "year_act": yr})
            if df.empty:
                continue
            else:
                mode = df["mode"][0]

            # If technology in "share" is in "total" too or not
            coefficient = 1 - val if tec in tec_tot_share else 1
            sc.add_par(
                parname,
                [relation, node, yr, node, tec, yr, mode, "year"],
                coefficient,
                "-",
            )
        # Bound of relation
        for node, (bound, num) in product(regions, bounds):
            sc.add_par(bound, [relation, node, yr, "year"], num, "-")


def update_mapping_sets(sc, par_list=["relation_upper_time"]):
    """
    Updating and adding mapping sets for new parameters. For example, if a new
    parameter "foo" is added to a scenario, this function adds the mapping/masking
    set of "<is_>foo" to the scenario.

    Parameters
    ----------
    sc : message_ix.Scenario
    par_list : list, optional
        List of new parameters. The default is ["relation_upper_time"].

    """
    sc.check_out()
    for parname in par_list:
        setname = "is_" + parname

        # initiating the sets
        idx_s = sc.idx_sets(parname)
        idx_n = sc.idx_names(parname)
        try:
            sc.set(setname)
        except:
            sc.init_set(setname, idx_sets=idx_s, idx_names=idx_n)
            print("- Set {} was initiated.".format(setname))

        # emptying old data in sets
        df = sc.set(setname)
        sc.remove_set(setname, df)

        # adding data to the mapping sets
        df = sc.par(parname)
        if not df.empty:
            for i in df.index:
                d = df.loc[i, :].copy().drop(["value", "unit"])
                sc.add_set(setname, d)

            print('- Mapping sets updated for "{}"'.format(setname))
    sc.commit("")


def init_storage(sc):
    """
    Initializing storage sets and parameters if needed

    Parameters
    ----------
    sc : message_ix.Scenario
    """
    sc.check_out()
    # 1) Adding sets
    idx = ["node", "technology", "mode", "level", "commodity", "year", "time"]
    dict_set = {
        "tec_storage": None,
        "storage_tec": None,
        "level_storage": None,
        "map_tec_storage": [
            "node",
            "technology",
            "mode",
            "tec_storage",
            "mode",
            "level",
            "commodity",
            "lvl_temporal",
        ],
        "is_relation_lower_time": ["relation", "node", "year", "time"],
        "is_relation_upper_time": ["relation", "node", "year", "time"],
    }
    for item, idxs in dict_set.items():
        try:
            sc.init_set(item, idx_sets=idxs)
        except:
            if item == "storage_tec":
                members = set(sc.set(item))
                for s in members:
                    sc.add_set("tec_storage", s)

            elif item == "map_tec_storage":
                df = sc.set(item)
                sc.remove_set(item)
                sc.init_set(
                    item,
                    idx_sets=idxs,
                    idx_names=[
                        "node",
                        "technology",
                        "mode",
                        "tec_storage",
                        "mode_storage",
                        "level",
                        "commodity",
                        "lvl_temporal",
                    ],
                )
                if not df.empty:
                    df = df.rename({"storage_tec": "tec_storage"}, axis=1)
                    sc.add_set(item, df)
            else:
                pass
    sc.remove_set("storage_tec")

    # 2) Adding parameters
    dict_par = {
        "time_order": ["lvl_temporal", "time"],
        "storage_self_discharge": idx,
        "storage_initial": idx,
    }

    for item, idxs in dict_par.items():
        try:
            sc.init_par(item, idx_sets=idxs)
        except:
            if "storage" in item:
                sc.remove_par(item)
                sc.init_par(item, idx_sets=idxs)
            else:
                pass

    sc.commit("")


def calibrate_hist_act_to_others(msg, tech_mapping, node_list=[], input_commodity=True):
    """
    Updating historical activity of one (reference) technology based on the (i) input
    commodity feeding to, or (ii) activity of several other technologies.

    Parameters
    ----------
    msg : message_ix.Scenario
    tech_mapping : dict
        Mapping of (reference) technologies to be updated as keys and a list of other
        technologies as values (e.g., {"heat_t_d": ["heat_i" , "heat_rc"]}).
    node_list : list, optional
        List of model nodes to which these changes must be applied. The default is [].
    input_commodity : bool
        if True, historical activity of the reference technology will be calibrated
        to the input of others, if False, to the activity of others.
    """
    # List of nodes for applying the calibration in this module
    if not node_list:
        node_list = [x for x in msg.set("node") if x not in ["World"]]
    parname = "historical_activity"
    msg.check_out()
    # Do the mapping over the loop of nodes
    for node in node_list:
        for tec_ref, tec_list in tech_mapping.items():
            # Existing historical activity of a list of technologies
            df = msg.par(parname, {"node_loc": node, "technology": tec_list})

            # Check if the data is not empty
            if df.empty:
                print(
                    '>>>Warning<<<: No historical data for "{}" in "{}"'.format(
                        tec_list, node
                    )
                )
                continue
            unit = df["unit"].mode()[0]
            df = df.set_index(["technology", "year_act"])

            if input_commodity:
                # Finding input value of technolgies (averaged per year_act)
                inp = msg.par("input", {"node_loc": node, "technology": tec_list})
                inp = inp.groupby(["technology", "year_act"])[["value"]].mean()
                inp = inp.loc[inp.index.isin(df.index)]

                # Calculating input commodity needs of the reference technology
                df["value"] *= inp["value"]

            # Updating the historical activity of reference technology
            df = df.reset_index().dropna(subset=["value"])
            df["technology"] = tec_ref
            df = df.groupby(msg.idx_names(parname)
                            ).sum(numeric_only=True).reset_index()
            # Retaining the unit
            df["unit"] = unit

            # Adding data to the scenario
            msg.add_par(parname, df)

    msg.commit("historical data calibration updated.")


def calibrate_hist_act_to_commodity_lvl(msg, tech_comm_lvl, node_list=[]):
    """
    Updating historical activity of one (reference) technology based on the input
    "commodity" feeding to a certain "level".

    Parameters
    ----------
    msg : message_ix.Scenario
    tech_comm_lvl : dict
        Pair of (i) technolgies with missing historical_activity as "key" and (ii) a list
        of commodity-levels as "value" that their input can be used for the historical
        activity of the corresponding key. The default is {}. Example:
        {'gas_t_d': [['gas'], ['final']]}
    node_list : list, optional
        List of model nodes to which these changes must be applied. The default is [].

    """
    # List of nodes for applying the calibration in this module
    if not node_list:
        node_list = [x for x in msg.set("node") if x not in ["World"]]
    parname = "historical_activity"

    # Creating a mapping of technologies (key: the one with missing activity,
    # value: list of those that their input commodity will be used)
    tech_mapping = {}

    # Finding technologies with a certain input commodity at a level
    for tec, [comm, lvl] in tech_comm_lvl.items():
        tec_list = list(
            set(msg.par("input", {"commodity": comm, "level": lvl})["technology"])
        )
        tech_mapping.update({tec: tec_list})

    # Using a utility function for updating historical activity
    calibrate_hist_act_to_others(msg, tech_mapping, node_list, input_commodity=True)


def convert_loss_to_activity(msg, tec_list, node_list=[]):
    """
    Updating historical activity of a technology by calculating it as a loss
    ( the existing value is considered a loss, and will be converted to a new
     value as activity)

    Parameters
    ----------
    msg : message_ix.Scenario
    tec_list : list
        List of technologies that their historical activity must be converted as a loss
        between their input and output.
    node_list : list, optional
        List of model nodes to which these changes must be applied. The default is [].
    """
    # List of nodes for applying the calibration in this module
    if not node_list:
        node_list = [x for x in msg.set("node") if x not in ["World"]]
    parname = "historical_activity"
    msg.check_out()

    # Finding historical years
    yr_hist = [x for x in set(msg.set("year")) if x < msg.firstmodelyear]
    for tec, node in product(tec_list, node_list):
        df = msg.par(parname, {"technology": tec, "node_loc": node}).set_index(
            "year_act"
        )
        # Calculating input value for each year, averaged over different vintage years
        inp = (
            msg.par("input", {"technology": tec, "node_loc": node, "year_act": yr_hist})
            .groupby(["year_act"])
            .mean()["value"]
        )
        # Calculating output value for each year, averaged over different vintage years
        out = (
            msg.par(
                "output", {"technology": tec, "node_loc": node, "year_act": yr_hist}
            )
            .groupby(["year_act"])
            .mean()["value"]
        )
        # Calculating activity based on "input", "output", and loss
        # activity = loss / (1 - output/input))
        for yr in df.index:
            df.loc[yr, "value"] = df["value"][yr] / (1 - (out[yr] / inp[yr]))
        # Add data to the scenario and commit
        msg.add_par(parname, df.reset_index())
    msg.commit("Historical data recalibrated based on the loss to activity.")


def add_vintage(msg, tec_list, node_list=[], rewrite=True):
    """
    Calibrates historical_new_capacity based on historical_activity.

    Parameters
    ----------
    msg : message_ix.Scenario
    tec_list : list of strings
        List of technologies for which historical_new_capacity is calibrated based on
        their historical_activity.
    node_list : list, optional
        List of model nodes to which these changes must be applied. The default is [].
    rewrite : bool
        If True, historical new capacity will be overwritten based on activity.
        If False, historical new capacity will be calibrated based on activity,
        only for those technologies with missing historical new capacity data.
        The default is True.

    """
    # List of nodes for applying the calibration in this module
    if not node_list:
        node_list = [x for x in msg.set("node") if x not in ["World"]]
    msg.check_out()
    # Converting historical_activity to historical_new_capacity using capacity factor
    for node in node_list:
        cap_old = msg.par(
            "historical_new_capacity", {"technology": tec_list, "node_loc": node}
        )

        # Finding technologies that have investment and must have vintage corrected.
        # If technology has no inv_cost, it's not important to represent their vintage
        inv = msg.par("inv_cost", {"technology": tec_list, "node_loc": node})
        tec_inv = inv.loc[inv["value"] > 1]["technology"].unique()

        # Those technologies that don't have historical capacity data
        tec_miss = [x for x in tec_inv if x not in set(cap_old["technology"])]

        # If rewrite=True, all technologies get updated (and not only the missing ones)
        if rewrite:
            tec_miss = tec_list

        # Finding historical years
        yr_hist = [x for x in set(msg.set("year")) if x < msg.firstmodelyear]
        for tec in tec_miss:
            # calculating capacity factor as an average of vintage years
            cf = (
                msg.par(
                    "capacity_factor",
                    {"technology": tec, "node_loc": node, "year_act": yr_hist},
                )
                .groupby(["year_act"])[["value"]]
                .mean()
            )
            if cf.empty:
                print(
                    "- There is no capacity factor data for {}, update ignored.".format(
                        tec
                    )
                )
                # NOTICE: we can consider a capacity factor of 1 for the missing values
                # At the moment, the missing CF results in ignoring that technology
                continue
            act = msg.par("historical_activity", {"technology": tec, "node_loc": node})
            if act.empty:
                print(
                    "- There is no historical activity data for {}, update ignored.".format(
                        tec
                    )
                )
                continue
            act = act.groupby(["technology", "node_loc", "year_act"]
                              )[["value"]].sum(numeric_only=True)
            # Shifting values of historical activity by one model period (seems not needed anymore)
            act_ally = act.copy().shift(+1, fill_value=0)

            # Finding maximum historical activity reported between two model periods
            for i in range(1, len(act_ally.index)):
                act_ally.iloc[i]["value"] = max(act.iloc[0:i, :]["value"])

            # Finding how much additional historical_activity is reported between two periods
            new_act = (act - act_ally).reset_index()
            new_act.loc[new_act["value"] < 0, "value"] = 0

            # Converting historical_activity to historical_new_capacity
            new_cap = (
                new_act.copy()
                .rename({"year_act": "year_vtg"}, axis=1)
                .set_index("year_vtg")
            )
            new_cap["unit"] = "GW"

            # Duration of historical model periods
            duration = (
                msg.par("duration_period", {"year": new_cap.index})
                .rename({"year": "year_vtg"}, axis=1)
                .set_index("year_vtg")
            )

            # Correcting values by capacity factor and dividing by duration period
            new_cap["value"] = (new_cap["value"] / cf["value"].mean()) / duration[
                "value"
            ]
            msg.add_par("historical_new_capacity", new_cap.reset_index())

    msg.commit("")


def historical_to_ref(
    sc, years="historical", sc_ref=None, regions="all", remove_ref=False
):
    """
    Copies data from historical parameters (e.g., "historical_activity") to MESSAGEix
    reference parameters (e.g., "ref_activity").
    Notice: reference parameters are widely used in legacy reporting for reporting
    data for historical years.

    Parameters
    ----------
    sc : message_ix.Scenario
    years : list of int or "historical"
        Years for which copy historical data to reference parameters.
        The default is "historical".
    sc_ref : message_ix.Scenario, optional
        The historical data can be copied from another (reference) scenario.
        The default is None.
    regions : list or "all", optional
        List of model regions to update the reference parameters.
        The default is "all".
    remove_ref : bool, optional
        If True, removes all the existing data in reference parameters before
        adding the data from historical parameters. The default is False.

    """
    # Finding relevant regions
    if regions == "all":
        regions = list(sc.set("node"))

    # Finding relevant years
    if years == "historical":
        years = [x for x in set(sc.set("year")) if x <= sc.firstmodelyear]

    # Mapping of historical to reference parameters
    par_map = {
        "historical_activity": "ref_activity",
        "historical_new_capacity": "ref_new_capacity",
        "historical_extraction": "ref_extraction",
        # "historical_emission": "ref_emission",
    }

    # If no reference scenario is given, use the same scenario for copying data
    if not sc_ref:
        sc_ref = sc

    sc.check_out()
    # Removing existing data of reference parameters before updating
    if remove_ref:
        for parname in par_map.values():
            node_col = [x for x in sc.par(parname).columns if "node" in x][0]
            year_col = [x for x in sc.par(parname).columns if "year" in x][0]
            df_ref = sc.par(parname, {node_col: regions, year_col: years})
            sc.remove_par(parname, df_ref)

    # Updating reference data based on historical
    for par_hist, par_ref in par_map.items():
        node_col = [x for x in sc.par(par_hist).columns if "node" in x][0]
        year_col = [x for x in sc.par(par_hist).columns if "year" in x][0]
        df_par = sc_ref.par(par_hist, {node_col: regions, year_col: years})
        if not df_par.empty:
            sc.add_par(par_ref, df_par)

        print(
            '> The content of parameter "{}" was copied to "{}".'.format(
                par_hist, par_ref
            )
        )

    sc.commit("Reference parameters updated.")


def replace_with_most_common(
    sc, par_list=["capacity_factor"], tec_list=["loil_ppl"], node_list=[]
):
    """
    Replaces the entries of a parameter for each node/technology pair based on the
    most used value in that table.
    Background: this is useful because some parameters are corrupted due to extrapolations
    that have resulted in near zero or negative entries. For example, "capacity_factor"
    for "loil_ppl" in WEU.

    Parameters
    ----------
    msg : message_ix.Scenario
    par_list : list of strings
        List of parameters to be corrected. The default is ["capacity_factor"].
    tec_list : list of strings
        List of technologies for which parameters should be corrected. The default is ["loil_ppl"]
    node_list : list, optional
        List of model nodes to which these changes must be applied. The default is [].
    """
    # List of nodes for applying the calibration in this module
    if not node_list:
        node_list = [x for x in sc.set("node") if x not in ["World"]]

    # Subannual time indexes
    times = [x for x in set(sc.set("time"))]

    sc.check_out()
    for parname, node, tec, ti in product(par_list, node_list, tec_list, times):
        node_col = [
            x for x in sc.idx_names(parname) if x in ["node", "node_loc", "node_rel"]
        ][0]

        filters = {"technology": tec, node_col: node}

        if "time" in sc.idx_sets(parname):
            filters.update({"time": ti})

        # Load data
        df = sc.par(parname, filters)
        if df.empty:
            continue

        # Find the most common value
        df["value"] = df["value"].mode().item()

        # Adding to the scenario
        sc.add_par(parname, df)
        # Print warning
        print(f'- Parameter "{parname}" updated for "{tec}" in "{node}".')
    sc.commit("Parameters updated by replacing most common values.")


def update_trade_relative_price(
    sc, multiplier, relative_to_import=False, price_relation="fuel_price"
):
    """
    Updating the price of export commodities either based on a multiplier, or
    based on the price of import commodities.

    Parameters
    ----------
    sc : message_ix.Scenario
    multiplier : float (int)
        A multiplier to be applied to the price of export commodities.
    relative_to_import : bool, optional
        Calculating export prices as a multiplier of import prices. The default is False.
    price_relation: str, optional
        The name of the relation for representing trade prices.
        The default is "fuel_price".
    """
    # Loading existing data of trade commodity prices
    df = sc.par("relation_activity", {"relation": price_relation})

    # Finding import and export technologies
    tec_imp = [x for x in set(df["technology"]) if "_imp" in x]
    tec_extra = [
        x for x in set(sc.set("technology")) if "imp" in x and x not in tec_imp
    ]
    tec_exp = [x for x in set(sc.set("technology")) if "_exp" in x]
    sc.check_out()
    # Calculating export price relative toimport price
    if relative_to_import:
        for t_ex in tec_exp:
            # Find corresponding import technology
            t_im = t_ex.split("_")[0] + "_imp"

            # Use existing data to calculate export price
            if t_im in set(df["technology"]):
                d = df.loc[df["technology"] == t_im].copy()
                d.loc[:, "value"] *= -multiplier
                d["technology"] = t_ex

                # Correct the data for the lifetime of the export technology
                life = sc.par("technical_lifetime", {"technology": t_ex})[
                    "year_vtg"
                ].tolist()
                if life:
                    d = d.loc[d["year_act"].isin(life)]
                sc.add_par("relation_activity", d)
            else:
                print(
                    f'Warning: No import price available for "{t_im}", as such '
                    f'could not add export price for "{t_ex}"!'
                )
    # Calculating export price directly based on multiplier
    else:
        df = df.loc[df["technology"].isin(tec_exp)].copy()
        df["value"] *= multiplier
        sc.add_par("relation_activity", df)

    print("- Commodity price of export technologies (trade) updated.")
    sc.commit("Trade commodity price updated.")


def net_trade_iea(sc, sc_glb, exch, regions):
    """
    Correct the IEA data for net trade (useful when the data is fetched for a
    number of countries in one model region)

    Parameters
    ----------
    sc : message_ix.Scenario
    Scenario to be modified
    sc_glb: message_ix.Scenario
        Reference global scenario to read historical data of gas interconnectors
    exch : DataFrame
        Raw data of energy carrier import and export from IEA.
    regions: dict
        Data of model region names and their parent region in the global model

    Returns
    -------
    net : DataFrame
        Corrected trade data (net trade).

    """
    net = pd.DataFrame(columns=exch.columns)

    parname = "historical_activity"
    imp_tecs = [x for x in set(exch["technology"]) if "imp" in x]

    for tec_imp, node in product(imp_tecs, list(set(exch["node_loc"]))):
        # Respective export technology
        tec_exp = tec_imp.replace("imp", "exp")

        # Parent region in the reference scenario
        parent = [x for x in regions.keys() if node in regions[x]][0]

        # Reading data from IEA for import/export technologies
        df_imp = exch.loc[(exch["technology"] == tec_imp) & (exch["node_loc"] == node)]
        df_exp = exch.loc[(exch["technology"] == tec_exp) & (exch["node_loc"] == node)]

        # If import or export is empty, the net will be based on the other one
        if df_imp.empty and not df_exp.empty:
            if tec_exp != "gas_exp":
                net = pd.concat([net, df_exp], ignore_index=True, sort=True)
                continue
        if not df_imp.empty and df_exp.empty:
            net = pd.concat([net, df_imp], ignore_index=True, sort=True)
            continue

        df = df_imp.merge(
            df_exp, on=["year_act", "mode", "time", "node_loc", "unit"], how="left"
        )
        df["value"] = df["value_x"] - df["value_y"]
        df2_imp = (
            df.copy()
            .drop(["technology_y", "value_y", "value_x"], axis=1)
            .rename({"technology_x": "technology"}, axis=1)
        )
        df2_exp = (
            df.copy()
            .drop(["technology_x", "value_y", "value_x"], axis=1)
            .rename({"technology_y": "technology"}, axis=1)
        )

        # Omitting negative values
        df2_imp = df2_imp.loc[df2_imp["value"] > 0].copy()
        df2_exp = df2_exp.loc[df2_exp["value"] < 0].copy()
        df2_exp["value"] *= -1

        # Appending net import
        net = pd.concat([net, df2_imp], ignore_index=True)

        # Modifying gas export based on data of pipelines in the parent region
        if not df2_exp.empty and tec_exp == "gas_exp":
            yr_hist = list(set(df2_exp["year_act"]))
            tec_gas = list(
                set(
                    sc.par(
                        "output",
                        {"node_loc": node, "year_act": yr_hist, "level": "piped-gas"},
                    )["technology"]
                )
            )
            # Historical data of gas pipelines for the parent region
            df_gas = sc_glb.par(
                parname,
                {"node_loc": parent, "year_act": yr_hist, "technology": tec_gas},
            )

            gas = pd.DataFrame(columns=df2_exp.columns)
            # Dividing IEA data based on the share of each gas pipeline
            # technology in MESSAGE historical data of that year
            if not df_gas.empty:
                for tec in tec_gas:
                    exp = df2_exp.copy()
                    exp["technology"] = tec
                    # An arbitrary share
                    exp["share"] = -1

                    yrs_ref = list(set(df_gas["year_act"]))
                    for yr in yrs_ref:
                        val = df_gas.loc[
                            (df_gas["technology"] == tec) & (df_gas["year_act"] == yr),
                            "value",
                        ]
                        if val.empty:
                            exp.loc[exp["year_act"] == yr, "value"] = 0
                            # Assuming no data in MESSAGE means zero share
                            exp.loc[exp["year_act"] == yr, "share"] = 0

                        else:
                            if float(val) == 0:
                                shr = 0
                            else:

                                g = df_gas.loc[df_gas["year_act"] == yr, "value"]
                                shr = float(val) / g.sum(axis=0)
                            exp.loc[exp["year_act"] == yr, "value"] *= shr
                            exp.loc[exp["year_act"] == yr, "share"] = shr

                    # For the years in IEA but not in the reference model
                    for yr in set(yr_hist) - set(df_gas["year_act"]):

                        # Finding he adjacent year in the model
                        if [x for x in yrs_ref if x > yr]:
                            yr_near = min([x for x in yrs_ref if x > yr])
                        else:
                            yr_near = max([x for x in yrs_ref if x < yr])

                        shr = float(exp.loc[exp["year_act"] == yr_near, "share"])
                        exp.loc[exp["year_act"] == yr, "value"] *= shr

                    exp = exp.drop("share", axis=1)
                    gas = pd.concat([gas, exp], ignore_index=True, sort=True)


            else:  # No historical data available, divide equally
                for tec in tec_gas:
                    exp = df2_exp.copy()

                    exp["technology"] = tec
                    exp["value"] *= 1 / len(tec_gas)
                    gas = pd.concat([gas, exp], ignore_index=True, sort=True)
                print(
                    ">>> WARNING: Historical data of gas export in IEA"
                    ' for "' + node + '", but not in reference MESSAGE'
                    " model: the data equally divided between"
                    ": interconnectors" + str(tec_gas) + "!"
                )

            # Final results for gas export
            df2_exp = gas.copy()

        # 2.2) Appending gas export technology

        net = pd.concat([net, df2_exp], ignore_index=True, sort=True)

    # 2.3) LNG_imp for PAO
    pao = [x for x in set(net["node_loc"]) if "PAO" in x]
    if pao:
        df = net.loc[(net["technology"] == "gas_imp") & (net["node_loc"].isin(pao))]
        if not df.empty:
            net.loc[
                (net["technology"] == "gas_imp") & (net["node_loc"].isin(pao)),
                "technology",
            ] = "LNG_imp"

    return net
