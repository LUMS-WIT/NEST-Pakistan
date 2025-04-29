import pandas as pd
from pathlib import Path
from typing import Union
from model.utlities.demands import adjust_demands

def update_historical_activity(model_obj, path: Union[str, Path]):
    """
    Update the historical activity parameter in the scenario with data from a specified path.

    Args:
                    path (str or Path): Path to the historical activity data.
    """
    # Checkout scenario for editing
    model_obj.ctx.source_scenario['scenario'].check_out()

    # Retrieve the current historical activity data from the scenario
    ha = model_obj.ctx.source_scenario['scenario'].par("historical_activity")

    # Read new historical activity data from the specified path
    ha_new = pd.read_csv(Path(f"{path}/historical_activity.csv"))

    # Balance import and export values in the new historical activity data
    ha_new = balance_import_export(model_obj, ha_new)

    # Remove the previous historical activity data from the scenario
    model_obj.ctx.source_scenario['scenario'].remove_par("historical_activity", ha)

    # Add the new, balanced historical activity data to the scenario
    model_obj.ctx.source_scenario['scenario'].add_par("historical_activity", ha_new)

    # Commit the changes to the scenario with a descriptive message
    model_obj.ctx.source_scenario['scenario'].commit("Updated historical activity based on new data")

    # Adjust demands in the scenario based on the updated historical activity
    adjust_demands(model_obj)

def balance_import_export(model_obj, historical_activity: pd.DataFrame):
    """
    Balance energy production, import, and export for each province and year.

    Args:
                    historical_activity (pd.DataFrame): DataFrame containing historical activity data for each province and year.

    Returns:
                    pd.DataFrame: DataFrame with balanced import and export values.
    """
    # Define the provinces involved in the analysis
    PROVINCES = [
        "Alberta",
        "BritishColumbia",
        "Manitoba",
        "Ontario",
        "NewBrunswick",
        "NewfoundlandandLabrador",
        "NovaScotia",
        "PrinceEdwardIsland",
        "Quebec",
        "Saskatchewan",
        "Yukon",
    ]

    # Define the technologies associated with each energy type
    foil_techs = [
        "foil_fs",
        "foil_i",
        "foil_ppl",
        "foil_rc",
        "foil_t_d",
        "foil_trp",
    ]
    loil_techs = [
        "loil_fs",
        "loil_i",
        "loil_ppl",
        "loil_rc",
        "loil_t_d",
        "loil_trp",
    ]
    gas_techs = [
        "gas_cc",
        "gas_ct",
        "gas_fs",
        "gas_i",
        "gas_ppl",
        "gas_rc",
        "gas_t_d",
        "gas_trp",
    ]
    coal_techs = [
        "coal_fs",
        "coal_i",
        "coal_ppl",
        "coal_rc",
        "coal_t_d",
        "coal_trp",
    ]

    def sum_demand(df: pd.DataFrame, techs: list):
        """
        Sum the demand for a given set of technologies within the DataFrame.

        Args:
                        df (pd.DataFrame): DataFrame containing historical activity data.
                        techs (list): List of technology names to sum demand for.

        Returns:
                        pd.Series: Series with the summed demand for each province and year.
        """
        return (
            df[df["technology"].isin(techs)]
            .groupby(["year_act", "node_loc"])["value"]
            .sum()
        )

    def balance_energy(
        row: pd.Series, prod_col: str, imp_col: str, exp_col: str, demand_col: str
    ):
        """
        Balance the energy production, import, and export for a specific energy type.

        Args:
                        row (pd.Series): Row of data containing production, import, export, and demand values.
                        prod_col (str): Column name for production data.
                        imp_col (str): Column name for import data.
                        exp_col (str): Column name for export data.
                        demand_col (str): Column name for demand data.

        Returns:
                        pd.Series: Updated row with balanced production, import, and export values.
        """
        production = row[prod_col]
        imports = 0#row[imp_col]
        exports = 0#row[exp_col]
        demand = row[demand_col]

        # Calculate the net balance of energy
        net_balance = production + imports - exports

        # Adjust imports or exports to meet the demand
        if production < demand:
            imports += demand - net_balance
        elif production > demand:
            exports += net_balance - demand

        # Ensure imports are not negative
        if imports < 0:
            exports += abs(imports)
            imports = 0

        # Update the row with the balanced values
        row[imp_col] = imports
        row[exp_col] = exports
        return row

    # Get the unique years in the historical activity data
    years = historical_activity["year_act"].unique()

    # Iterate over each year to balance energy production, imports, and exports
    for year in years:
        # Filter data for the current year and relevant provinces
        df_year = historical_activity[
            (historical_activity["year_act"] == year)
            & (historical_activity["node_loc"].isin(PROVINCES))
        ]

        # Calculate the total demand for each energy type
        coal_demand = sum_demand(df_year, coal_techs)
        foil_demand = sum_demand(df_year, foil_techs)
        loil_demand = sum_demand(df_year, loil_techs)
        gas_demand = sum_demand(df_year, gas_techs)
        oil_demand = foil_demand.add(
            loil_demand, fill_value=0
        )  # Combine demands for foil and loil

        # Create a pivot table to summarize the production, import, and export data
        pivot_df = df_year.pivot_table(
            index="node_loc", columns="technology", values="value", aggfunc="sum"
        ).reset_index()

        # Define the required columns for production, import, and export data
        required_columns = [
            "coal_extr_mpen",
            "coal_imp",
            "coal_exp",
            "gas_extr_mpen",
            "gas_imp",
            "gas_exp",
            "oil_extr_mpen",
            "oil_imp",
            "oil_exp",
        ]

        # Ensure all required columns are present in the pivot table
        for tech in required_columns:
            if tech not in pivot_df.columns:
                pivot_df[tech] = 0

        # Extract the production, import, and export data for the current year and provinces
        production_import_export_data = pivot_df[
            ["node_loc"] + required_columns
        ].fillna(0)

        # Create a DataFrame to hold the demand data for the current year and provinces
        demand_data = pd.DataFrame(
            {
                "node_loc": coal_demand.index.get_level_values("node_loc"),
                "coal_demand": coal_demand.values,
                "gas_demand": gas_demand.values,
                "oil_demand": oil_demand.values,
            }
        ).fillna(0)

        # Merge the production/import/export data with the demand data
        merged_df = production_import_export_data.merge(
            demand_data, on="node_loc", how="left"
        ).fillna(0)

        # Create a copy of the merged data to apply balancing
        balanced_df = merged_df.copy()

        # Apply the balance_energy function to coal, gas, and oil data
        balanced_df = balanced_df.apply(
            balance_energy,
            axis=1,
            prod_col="coal_extr_mpen",
            imp_col="coal_imp",
            exp_col="coal_exp",
            demand_col="coal_demand",
        )

        balanced_df = balanced_df.apply(
            balance_energy,
            axis=1,
            prod_col="gas_extr_mpen",
            imp_col="gas_imp",
            exp_col="gas_exp",
            demand_col="gas_demand",
        )

        balanced_df = balanced_df.apply(
            balance_energy,
            axis=1,
            prod_col="oil_extr_mpen",
            imp_col="oil_imp",
            exp_col="oil_exp",
            demand_col="oil_demand",
        )

        # Update the historical_activity DataFrame with the balanced import and export data
        for index, row in balanced_df.iterrows():
            historical_activity.loc[
                (historical_activity["year_act"] == year)
                & (historical_activity["node_loc"] == row["node_loc"])
                & (historical_activity["technology"] == "coal_imp"),
                "value",
            ] = row["coal_imp"]
            historical_activity.loc[
                (historical_activity["year_act"] == year)
                & (historical_activity["node_loc"] == row["node_loc"])
                & (historical_activity["technology"] == "coal_exp"),
                "value",
            ] = row["coal_exp"]
            historical_activity.loc[
                (historical_activity["year_act"] == year)
                & (historical_activity["node_loc"] == row["node_loc"])
                & (historical_activity["technology"] == "gas_imp"),
                "value",
            ] = row["gas_imp"]
            historical_activity.loc[
                (historical_activity["year_act"] == year)
                & (historical_activity["node_loc"] == row["node_loc"])
                & (historical_activity["technology"] == "gas_exp"),
                "value",
            ] = row["gas_exp"]
            historical_activity.loc[
                (historical_activity["year_act"] == year)
                & (historical_activity["node_loc"] == row["node_loc"])
                & (historical_activity["technology"] == "oil_imp"),
                "value",
            ] = row["oil_imp"]
            historical_activity.loc[
                (historical_activity["year_act"] == year)
                & (historical_activity["node_loc"] == row["node_loc"])
                & (historical_activity["technology"] == "oil_exp"),
                "value",
            ] = row["oil_exp"]

    # Return the updated historical_activity DataFrame
    return historical_activity
