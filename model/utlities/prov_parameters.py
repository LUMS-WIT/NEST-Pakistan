import pandas as pd


def generator(msg):
    """This function creates a dictionary of provincial parameter dataframes by copying national ones

    msg: message_ix.Scenario() instance
    """
    # Province names for creating dataframes
    provinces = [
        "Alberta",
        "BritishColumbia",
        "Manitoba",
        "NewBrunswick",
        "NewfoundlandandLabrador",
        "NorthwestTerritories",
        "NovaScotia",
        "Nunavut",
        "Ontario",
        "PrinceEdwardIsland",
        "Quebec",
        "Saskatchewan",
        "Yukon",
    ]

    # All (non-empty) parameters of the Canadian model
    total_pars = [par for par in msg.par_list() if not msg.par(par).empty]

    # Parameters already found with data
    found_pars = ["demand", "historical_activity", "historical_new_capacity"]

    # Economic parameters to skip for now
    econ_pars = [
        # "MERtoPPP",
        # "abs_cost_activity_soft_lo",
        # "abs_cost_activity_soft_up",
        # "cost_MESSAGE",
        # "depr",
        # "drate",
        # "esub",
        # "fix_cost",
        # "gdp_calibrate",
        # "grow",
        # "interestrate",
        # "inv_cost",
        # "kgdp",
        # "kpvs",
        # "level_cost_activity_soft_lo",
        # "level_cost_activity_soft_up",
        # "level_cost_new_capacity_soft_up",
        # "price_MESSAGE",
        # "relation_cost",
        # "resource_cost",
        # "var_cost",
    ]

    # Filter out un-needed parameters
    filtered = [x for x in total_pars if x not in found_pars if x not in econ_pars]
    filtered.sort()

    # Create dictionary to store parameter : <columns containing 'node'> pairs
    pars_to_change = {}

    # Iterate through parameters
    for par in filtered:
        # Create lists for appending 'node' and 'year' containing columns
        node_stuff = []
        year_stuff = []

        # Iterate through columns of parameter dataframe
        for col in msg.par(par).columns:
            # Check for node column (or some variation including string 'node')
            if "node" in col:
                node_stuff.append(col)

            # Check for year column, make sure it contains integers
            if "year" in col and msg.par(par).dtypes[col] == "int64":
                year_stuff.append(col)

        if len(node_stuff) != 0:
            # Add parameter and column values to dictionary
            pars_to_change[par] = [node_stuff, year_stuff]

    # Create dictionary with key = <parameter name> and value = provincial dataframe
    dfs = dict.fromkeys(pars_to_change.keys())

    for par in dfs:
        # Copy canadian dataframe
        can_df = msg.par(par).copy()

        dfs[par] = can_df

        # Only need data for years after (and including) 2010
        for year_data in pars_to_change[par][1]:
            can_df = can_df[can_df[year_data] >= 2010]

        for prov in provinces:
            # Create copy of Canadian dataframe
            df = msg.par(par).copy()

            # Only need data for years after (and including) 2010
            for year_data in pars_to_change[par][1]:
                df = df[df[year_data] >= 2010]

            # Change node values to province
            for node_data in pars_to_change[par][0]:
                df[node_data] = prov

            # Append provincial data to parameter dataframe
            dfs[par] = pd.concat([dfs[par], df], ignore_index=True)

    for par in dfs:
        # Identify all columns that contain the string 'node'
        node_columns = [col for col in dfs[par].columns if "node" in col]

        # For each identified node column, filter out rows with 'Canada'
        for node_col in node_columns:
            dfs[par] = dfs[par][dfs[par][node_col] != "Canada"]

    return dfs


def remove_canada_data(sc):
    """
    This function removes data related to 'Canada' from all parameters in a
    message_ix.Scenario instance that contain 'node' in their column names.
    """

    # Get all parameters
    all_pars = sc.par_list()

    for par in all_pars:
        # Load the parameter data
        df = sc.par(par)

        # Identify columns that contain the string 'node'
        node_columns = [col for col in df.columns if "node" in col]

        # Check if these columns contain 'Canada' and create a filter
        filter_condition = pd.Series(False, index=df.index)
        for col in node_columns:
            filter_condition = filter_condition | (df[col] == "Canada")

        # Filter out rows where 'Canada' is present in any 'node' column
        canada_data = df[filter_condition]

        # Remove data related to 'Canada' from the parameter
        if not canada_data.empty:
            sc.remove_par(par, canada_data)
            print(f'> Data related to Canada removed from parameter "{par}".')

    print("All relevant Canada data has been removed from parameters.")


def remove_technology_data(sc, technologies_to_remove):
    """
    This function removes data related to specified technologies from all parameters in a
    message_ix.Scenario instance.

    Parameters:
    - sc: message_ix.Scenario instance
    - technologies_to_remove: List of technologies to remove from parameters
    """
    # Get all parameters
    all_pars = sc.par_list()

    for par in all_pars:
        # Load the parameter data
        df = sc.par(par)

        # Iterate through columns to find columns containing technologies to remove
        for col in df.columns:
            for tech in technologies_to_remove:
                if tech in col:
                    # Filter out rows where the technology is present in the column
                    tech_data = df[df[col] == tech]

                    # Remove data related to the specified technology from the parameter
                    if not tech_data.empty:
                        sc.remove_par(par, tech_data)
                        print(
                            f'> Data related to technology "{tech}" removed from parameter "{par}".'
                        )

    print(
        "All relevant data for specified technologies has been removed from parameters."
    )
