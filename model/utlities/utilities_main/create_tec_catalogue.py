# -*- coding: utf-8 -*-
"""
This script creates a table of techno-economic parameters for a set of
technologies, obtained from a MESSAGEix scenario
"""
import pandas as pd
from itertools import product

# A mapping for renaming some parameters or splitting their data in several columns
rename_par = {
    "input": ["Input commodity", "Input"],
    "output": ["Output commodity", "Output", "Energy efficiency"],
    "capacity_factor": "Capacity factor",
    "technical_lifetime": "Technical lifetime",
    "inv_cost": "Capital cost ($/kW)",
    "fix_cost": "Fix OM cost ($/kW/yr)",
    "var_cost": "Variable OM cost ($/MWh)",
    "emission_factor": ["Emission", "Emission factor"],
}


def input_output(sc, dff, com_remove=[]):
    """
    Configures efficiency based on "input" and "output" parameters for each commodity.

    Parameters
    ----------
    sc : message_ix.Scenario
        Scenario from which data is being read.
    dff : DataFrame
        2-D table of parameters fetched from the scenario.
    com_remove : list of strings, optional
        List of commodities to be removed from the table. The default is [].

    Returns
    -------
    dff: DataFrame
        Updated 2-D table of all parameters with input and output-related
        information (eff, commodities).

    """
    # Creating a table with the same indexes and adding requires columns
    df = pd.DataFrame(
        index=dff.index,
        columns=[
            "Input commodity",
            "Input",
            "Output commodity",
            "Output",
            "Energy efficiency",
        ],
    )
    # Loop over each technology-mode pair for "input" and "output"
    for (tec, mode), parname in product(df.index, ["input", "output"]):
        df_par = sc.par(
            parname,
            {
                "technology": tec,
                "node_loc": node,
                "year_act": yr_act,
                "year_vtg": yr_vtg,
                "mode": mode,
            },
        )
        df_par = (
            df_par.loc[~df_par["commodity"].isin(com_remove)]
            .copy()
            .set_index(["technology"])
        )

        if df_par.empty:
            continue

        # Finding "value" based on "commodity"
        df_par = df_par[df_par["value"] != 0].copy()
        if len(df_par.index) > 1:
            coms = df_par.loc[tec, "commodity"].tolist()
            df.loc[(tec, mode), parname.title() + " commodity"] = (", ").join(coms)
            df.loc[(tec, mode), parname.title()] = (", ").join(
                [str(round(x, 3)) for x in df_par.loc[tec, "value"].tolist()]
            )
        elif tec in df_par.index:
            df.loc[(tec, mode), parname.title() + " commodity"] = df_par.loc[
                tec, "commodity"
            ]
            df.loc[(tec, mode), parname.title()] = df_par.loc[tec, "value"].round(3)

        # Estimating overall efficiency
        for (tec, mode) in df.index:
            if pd.isna(df.loc[(tec, mode), "Output"]):
                continue
            if type(df.loc[(tec, mode), "Output"]) == str:
                out = sum([float(x) for x in df.loc[(tec, mode), "Output"].split(", ")])
            else:
                out = float(df.loc[(tec, mode), "Output"])

            if type(df.loc[(tec, mode), "Input"]) == str:
                inp = sum([float(x) for x in df.loc[(tec, mode), "Input"].split(", ")])
            else:
                inp = float(df.loc[(tec, mode), "Input"])

            df.loc[(tec, mode), "Energy efficiency"] = out / inp

    return pd.concat([df, dff], axis=1)


def retreive_parameter(sc, dff, par_list, currency=1):
    """
    Retreiving scenario data and formatting into a single table

    Parameters
    ----------
    sc : message_ix.Scenario
        Scenario from which data is being read.
    dff : DataFrame
        2-D table of parameters fetched from the scenario.
    par_list : List of strings
        List of parameters to be added as columns of the 2-D table.
    currency : float/int, optional
        A multiplier, e.g., for converting the currency, if needed. The default is 1.

    Returns
    -------
    dff : DataFrame
        Updated 2-D table of all parameters.

    """
    # Loop over each technology-mode pair for each parameter
    for (tec, mode), parname in product(dff.index, par_list):
        node_col = [
            x
            for x in sc.idx_names(parname)
            if x in ["node", "node_loc", "node_rel", "node_share"]
        ]
        # Filter data
        filters = {"technology": tec, node_col[0]: node}
        
        # Finding year-related indexes
        yr_col = [x for x in sc.idx_names(parname) if "year" in x]
        
        # Configuration based on the number of year-related indexes
        if len(yr_col) == 1 or "year_rel" in yr_col:
            yr_data = yr_vtg if yr_col[0] == "year_vtg" else yr_act
            filters.update({yr_col[0]: yr_data})
        else:
            filters.update({"year_act": yr_act, "year_vtg": yr_vtg})

        if "mode" in sc.idx_names(parname):
            filters.update({"mode": mode})

        # Loading data of the parameter
        df_par = sc.par(parname, filters).set_index("technology")

        if not df_par.empty:
            multiplier = (
                currency if parname in ["inv_cost", "fix_cost", "var_cost"] else 1
            )
            dff.loc[(tec, mode), parname] = (
                float(df_par.loc[tec, "value"].mean()) * multiplier
            )
    return dff


def create_table_from_model(
    sc,
    node,
    tec_list,
    yr_act=2030,
    par_list="all",
    yr_vtg=None,
    emission_cleanup=False,
    com_remove=[],
    rename={},
    rel_list=[],
    currency=1,
    variables=False,
    active=False,
    extra_par=[],
):
    """
    Configures the specification of a group or all of technologies from a scenario,
    and creates a 2-D technology table (catalogue).

    Parameters
    ----------
    sc : message_ix.Scenario
        Scenario from which data is being read.
    node : string
        Model region for which the data is being configured.
    tec_list : List of strings
        List of technologies for which the catalogue is being created.
    yr_act : int, optional
        Desired model period for which the catalogue is being built.
        The default is 2030.
    par_list : List of strings or "all", optional
        List of parameters to be included in the catalogue. The default is "all".
    yr_vtg : int, optional
        Construction year for the desired activity year. If not specified,
        the same year as "yr_act" will be used. The default is None.
    emission_cleanup : bool, optional
        Using emissions from a cleaned scenario, i.e., "emission_factor". If False,
        will use emission factors from "relation_activity". The default is False.
    com_remove : List, optional
        List of commodities to be removed from the final table. The default is [].
    rename : dict, optional
        A mapping for renaming parameter names. The default is {}.
    rel_list : List, optional
        List of relations to be included. The default is [].
    currency : float/int, optional
        A currency converter that is multiplied to the values of a parameter.
        The default is 1.
    variables : bool, optional
        A flag to include output results in the table or not. The default is False.
    active : bool, optional
        Showing "ACT" of technologies that are active (non-zero). The default is False.
    extra_par : List, optional
        List of parameters to be ignored when creating the catalogue. The default is [].

    Returns
    -------
    df : DataFrame
        A 2-D technology table (catalogue), with technology-mode pairs
    as rows and parameter information as columns.

    """
    # Check if the passed node name is correct
    if node not in set(sc.set("node")):
        print("WARNING: There is no node {} in the scenario!!".format(node))
        return
    
    # Specifying parameters to be configured
    if par_list == "all":
        par_list = [
            x
            for x in sc.par_list()
            if "technology" in sc.idx_sets(x)
            and x not in ["input", "output", "relation_activity", "emission_factor"]
        ]
    par_list = [x for x in par_list if not any([y in x for y in extra_par])]

    # Year of vintage (construction)
    if not yr_vtg:
        yr_vtg = yr_act
    
    # Finding operating "mode"s of the technologies if more than one,
    # and using M1 if no mode given
    dict_mode = {
        x: list(
            set(
                sc.par(
                    "input",
                    {
                        "technology": x,
                        "node_loc": node,
                        "year_act": yr_act,
                        "year_vtg": yr_vtg,
                    },
                )["mode"]
            )
        )
        for x in tec_list
    }
    [dict_mode.update({x: ["M1"]}) for x in dict_mode.keys() if dict_mode[x] == []]
    d = []
    for x in dict_mode.keys():
        d = d + list(product([x], dict_mode[x]))

    # Creating a table with the default columns based on list of parameters
    df = pd.DataFrame(
        index=pd.MultiIndex.from_tuples(d),
        columns=par_list,
    )
    df.index.names = ["Technology", "Mode"]

    # Configuring the information for "input" and "output" ==> efficiency
    df = input_output(sc, df, com_remove)

    # Configuring other parameters
    df = retreive_parameter(sc, df, par_list, currency=1)

    # Configuring emission factors
    parname = "emission_factor"
    if emission_cleanup:
        # Method 1) based on parameter "emission_factor"
        emiss_list = [
            x for x in sc.set("emission") if not any(y in x for y in ["fresh", "trans"])
        ]
        for (tec, mode) in df.index:
            df_par = sc.par(
                parname,
                {
                    "technology": tec,
                    "node_loc": node,
                    "year_act": yr_act,
                    "year_vtg": yr_vtg,
                    "emission": emiss_list,
                    "mode": mode,
                },
            ).set_index("technology")
            if not df_par.empty:
                # df_par = df_par[df_par['value'] != 0]
                if len(df_par.index) > 1:
                    df.loc[(tec, mode), "Emission"] = (", ").join(
                        df_par.loc[tec, "emission"].tolist()
                    )
                    df.loc[(tec, mode), "Emission factor"] = (", ").join(
                        [str(round(x, 3)) for x in df_par.loc[tec, "value"].tolist()]
                    )
                else:
                    df.loc[(tec, mode), "Emission"] = df_par.loc[tec, "emission"]
                    df.loc[(tec, mode), "Emission factor"] = df_par.loc[
                        tec, "value"
                    ].round(3)
    else:
        # Method 2) based on parameter "relation_activity"
        parname = "relation_activity"
        emiss_list = [x for x in sc.set("relation") if x.endswith("_Emission")]
        emiss_list.remove("CO2_Emission")
        emiss_list.append("CO2_cc")
        for (tec, mode) in df.index:
            df_par = sc.par(
                parname,
                {
                    "technology": tec,
                    "node_loc": node,
                    "year_act": yr_act,
                    "year_rel": yr_act,
                    "relation": emiss_list,
                    "mode": mode,
                },
            ).set_index("technology")
            if not df_par.empty:
                df_par = df_par.replace({"CO2_cc": "CO2"})
                if len(df_par.index) > 1:
                    df.loc[(tec, mode), "Emission"] = (", ").join(
                        [
                            x.split("_Emission")[0]
                            for x in df_par.loc[tec, "relation"].tolist()
                        ]
                    )
                    df.loc[(tec, mode), "Emission factor"] = (", ").join(
                        [str(round(x, 3)) for x in df_par.loc[tec, "value"].tolist()]
                    )
                else:
                    df.loc[(tec, mode), "Emission"] = df_par.loc[tec, "relation"].split(
                        "_Emission"
                    )[0]
                    df.loc[(tec, mode), "Emission factor"] = df_par.loc[
                        tec, "value"
                    ].round(3)
    
    # Reporting the value of relations in "relation_activity", each in one column
    # Notice: this may make the catalogue table too wide (many columns) if the number of 
    # technologies are large. This can be useful only if it is needed to check relations.
    if rel_list:
        parname = "relation_activity"
        for (tec, mode) in df.index:
            df_par = sc.par(
                parname,
                {
                    "technology": tec,
                    "node_loc": node,
                    "year_act": yr_act,
                    "year_rel": yr_vtg,
                    "mode": mode,
                },
            )
            if rel_list == "all":
                rels = sorted(list(set(df_par["relation"])))
            else:
                rels = rel_list
            for rel in rels:
                df_rel = (
                    df_par.loc[df_par["relation"] == rel].copy().set_index("technology")
                )
                df.loc[(tec, mode), "relation: " + rel] = float(
                    df_rel.loc[tec, "value"]
                )
    
    # Reporting output variables in the catalogue table
    if variables:
        varname = "ACT"
        for (tec, mode) in df.index:
            df_var = sc.var(
                varname,
                {"technology": tec, "node_loc": node, "year_act": yr_act, "mode": mode},
            ).set_index("technology")
            if not df_var.empty:
                df.loc[(tec, mode), varname] = df_var.loc[tec, "lvl"].sum()

        varname = "CAP"  # Here it is only 'CAP' in this vintage year
        for (tec, mode) in df.index:
            df_var = sc.var(
                varname, {"technology": tec, "node_loc": node, "year_act": yr_act}
            ).set_index("technology")
            if not df_var.empty:
                df.loc[(tec, mode), varname] = df_var.loc[tec, "lvl"].sum()
        # Only showing the activity of technologies that are greater than zero
        if active:
            df = df.loc[df["ACT"] > 0]

    # Droping extra columns
    # Nan values for some parameters
    df = df.dropna(axis=1, how="all").sort_index()
    return df


# %% Sample usage input data
if __name__ == "__main__":
    import ixmp
    import message_ix
    import os

    # Path to the folder of the stand-alone model on your machine
    path_files = os.path.dirname(os.path.abspath(__file__)).parents([1])
    path_data = str(path_files) + "\\modelData" 
    
    # Loading the modeling platform
    mp = ixmp.Platform(name="ene_ixmp", jvmargs=["-Xms800m", "-Xmx8g"])
    
    # Loading model/scenario
    sc = message_ix.Scenario(mp, "UNECE_SSP2_R15", "NPi2025_1000f_0ece_all_soec")

    # Step 1) Specifying the input data for the catalogue
    # List of years for which the cost data should be retreived
    year_act = [2020, 2030, 2050]
    year_vtg = [2020, 2030, 2050]
    
    # Reference year for all parameter data
    yr_ref = 2030
    
    # Model region
    node = "R14_UBM"
    global_node = "R14_GLB"
    
    # Using emission factors from cleaned up scenario (i.e., "emission_factor")
    # If False, these factors are read from "relation_activity"
    emission_cleanup = False
    
    # A currency converter for the cost data (a multiplier)
    # e.g., from 2005USD to 2020USD is 1.325
    currency_conv = 1
    
    # Reporting emissions separately
    emission_separate = True
    
    # Step 2) Finding relevant technologies
    # (these are several examples, but user can choose one their own technologies)
    # All technologies
    tec_list = "all"
    
    # Or, a list of technologies
    # tec_list = ['gas_cc', 'gas_ppl', 'gas_ct', 'gas_cc_ccs', 'wind_ppl',
    #  'wind_ppf', 'solar_pv_ppl', 'nuc_lc', 'nuc_hc', 'hydro_lc', 'hydro_hc',
    #  'bio_ppl', 'bio_istig', 'bio_istig_ccs']
    
    # Or, only hydrogen related technologies
    hydrogen_cycle = False
    
    # Or, only CCS related technologies
    ccs_cycle = False
    
    # Or, only nuclear related technologies
    nuclear = False
    
    # Or, only power system related technologies
    electricity = False
    
    # Or, only transport end use technologies
    transport = False
    
    # Or, only solar related technologies
    solar = False
    
    # Or, only wind related technologies
    wind = False
    
    # Excluding some technologies if not needed
    tec_exclude = []
    
    # Excluding some parameters if not needed, by passing partial or full name
    extra_par = ["ref_", "soft_", "relation_", "bound_"]

    # Loading MESSAGEix metadata file for reading the technology descriptions
    filename = "MESSAGE_definitions.xlsx"
    des = pd.ExcelFile(path_data + "\\" + filename)
    sh_tech = des.parse("technology")

    # Choosing relevant Tiers of technologies
    sh_tech = sh_tech.loc[sh_tech["Tier"].isin([1, 2, "aggregate"])].set_index(
        "technology"
    )

    # List of technologies
    if tec_list == "all":
        tec_list = list(set(sc.set("technology")))
        tec_list = [x for x in tec_list if x in sh_tech.index]
        tec_extra = [x for x in tec_list if x not in sh_tech.index]
    elif hydrogen_cycle:
        tec_list = [
            x for x in sc.set("technology") if any(y in x for y in ["h2", "lh"])
        ]
        tec_list2 = [
            x
            for x in sc.par("output", {"commodity": ["lh2", "hydrogen"]})[
                "technology"
            ].unique()
            if "Trans" not in x
        ]
        tec_list3 = [
            x
            for x in sc.par("input", {"commodity": ["lh2", "hydrogen"]})[
                "technology"
            ].unique()
            if "Trans" not in x
        ]
        tec_list = sorted(list(set(tec_list + tec_list2 + tec_list3)))
    elif ccs_cycle:
        tec_list = [
            x
            for x in sc.set("technology")
            if any(y in x for y in ["ccs", "scrub", "co2scr", "co2_tr"])
        ]
    elif nuclear:
        tec_list = [
            x
            for x in sc.set("technology")
            if any(y in x for y in ["nuc_hc", "u5", "Uran", "uran"])
        ]
    elif electricity:
        tec_list = sc.par("output", {"commodity": "electr"})["technology"].unique()
        tec_list = [x for x in tec_list if x not in tec_exclude]
    elif transport:
        tec_list = [x for x in sc.set("technology") if x.endswith("_trp")]
    elif solar:
        tec_list = [
            x for x in set(sc.set("technology")) if "solar" in x or "Solar" in x
        ]
    elif wind:
        tec_list = [x for x in set(sc.set("technology")) if "wind" in x]

    # Excluding cooling technologies
    tec_list = [
        x for x in tec_list if not any(y in x for y in ["saline", "fresh", "air"])
    ]
    
    # Renaming some commodities
    ren = {
        "i_therm": "heat",
        "i_spec": "electricity",
        "electr": "electricity",
        "rc_therm": "heat",
        "rc_spec": "electricity",
        "ht_heat": "high T heat",
    }
    
    # Removing some (cooling-related) commodities
    com_rem = [
        x for x in sc.set("commodity") if any(y in x for y in ["cool", "freshwater"])
    ]

    result = {}
    # Running the main function for each specified year
    for yr_vtg, yr_act in zip(year_vtg, year_act):
        df = create_table_from_model(
            sc,
            node,
            tec_list,
            yr_act,
            "all",
            yr_vtg,
            emission_cleanup=False,
            com_remove=com_rem,
            rename=ren,
            rel_list=[],
            currency=currency_conv,
            variables=False,
            active=False,
            extra_par=extra_par,
        )

        # For nuclear, the data from 2010 for nuc_lc and from the global node needed
        if nuclear:
            df2 = create_table_from_model(
                sc,
                node,
                ["nuc_lc"],
                2010,
                2010,
                com_remove=com_rem,
                rename=ren,
                currency=currency_conv,
            )
            df3 = create_table_from_model(
                sc,
                global_node,
                tec_list,
                year_act,
                year_vtg,
                com_remove=com_rem,
                rename=ren,
                currency=currency_conv,
            )

            df = pd.concat([df, df2, df3], axis=0)
        
        # Flag if the data is empty
        assert not df.empty
        
        # Removing Nan values (and global trade)
        df = df.dropna(axis=0, how="all")
        df = df.reset_index(["Mode"])

        # Adding technology description
        for x in df.index:
            if x in sh_tech.index:
                df.loc[x, "Description"] = sh_tech.loc[x, "Description"]
        df.insert(0, "Description", df.pop("Description"))

        df = df.reset_index()
        df = df.sort_values(["Technology", "Mode", "Input commodity"]).set_index(
            "Technology"
        )

        # Making CO2 and CH4 emissions separate
        if emission_separate:
            for tec in df.index:
                d = sc.par(
                    "relation_activity",
                    {
                        "relation": "CO2_cc",
                        "node_loc": node,
                        "year_act": year_act,
                        "technology": tec,
                    },
                )["value"]
                if not d.empty:
                    df.loc[tec, "CO2 emissions (MtCeq/GWa)"] = float(d[0])

                d = sc.par(
                    "relation_activity",
                    {
                        "relation": "CH4_Emission",
                        "node_loc": node,
                        "node_rel": node,
                        "year_act": year_act,
                        "year_rel": year_act,
                        "technology": tec,
                    },
                )["value"]
                if not d.empty:
                    df.loc[tec, "CH4 emissions (ktCeq/GWa)"] = float(d[0])

            # Dropping extra columns
            df = df.drop(["Emission", "Emission factor"], axis=1)

        # Compiling the results
        result[yr_act] = df

    # Generating one catalogue table for several years of cost data
    df = result[yr_ref].copy()
    cost_columns = [x for x in df.columns if "cost" in x]
    col_order = df.columns
    df.columns = pd.MultiIndex.from_tuples(product(df.columns, [yr_ref]))
    df.columns.name = ("Variable", "Year")

    for yr, cost in product([x for x in year_act if x != yr_ref], cost_columns):
        df0 = result[yr].copy()
        df[(cost, yr)] = df0[cost]

    # Sorting by year
    df = df.sort_index(level=1, axis=1)
    
    # Sorting by original parameter order
    new_cols = df.columns.reindex(col_order, level=0)
    df = df[new_cols[0]].copy()
    
    # Writing to Excel
    writer = pd.ExcelWriter(path_data + "//technology_catalogue.xlsx", engine="xlsxwriter")
    df.to_excel(writer)
    writer.save()
    writer.close()
