def add_federal_carbon_tax(mp, msg, nodes):
    """
    Implements a federal carbon tax across all provinces in the given nodes list.

    Parameters:
    mp (ixmp.Platform): An instance of the ixmp.Platform class, providing
    a connection to the database used for scenario handling.
    msg (ixmp.Scenario): An instance of the ixmp.Scenario class, representing a particular energy system configuration and associated dynamics.
    nodes (list): A list of provinces where the federal carbon tax should be applied.

    The function first defines the carbon prices in CAD from 2023 to 2030 and a conversion rate to USD. It then converts these prices to USD and calculates the average prices for the intervals 2023-2025 and 2026-2030.

    Next, it extends the prices for the years 2035 to 2060 at 5-year intervals, using the last available price for these future years.

    A DataFrame is created to hold the years and corresponding prices. The function then selects all Canadian provinces from the nodes list (assuming the first two entries are not provinces) and creates a new DataFrame that repeats the emission prices for each province.

    A nested function, make_df(var_name, **kwargs), is defined within the function to format the data for MESSAGEix.

    Finally, the function adds the new unit to the platform (if not already added), checks out the scenario, adds the parameter 'tax_emission' to the scenario, and commits the changes with a message 'Added carbon tax emission prices.'

    In summary, this function is a key part of implementing a federal carbon tax across all provinces in the energy system model.
    """
    # Carbon prices in CAD from 2023 to 2030
    prices_cad = np.array([65, 80, 95, 110, 125, 140, 155, 170])

    # Conversion rate from CAD to USD
    conversion_rate = 0.74

    # Convert prices to USD
    prices_usd = prices_cad * conversion_rate

    # Calculate average prices for specified intervals
    average_2025 = np.mean(prices_usd[:3])  # Average for 2023, 2024, 2025
    average_2030 = np.mean(prices_usd[3:])  # Average for 2026 to 2030

    # Extend for years 2035 to 2060 at 5-year intervals
    extended_years = list(range(2035, 2061, 5))
    extended_prices = [prices_usd[-1]] * len(
        extended_years
    )  # Using the last available price

    # Combine the existing and extended data frames
    emission_prices = pd.DataFrame(
        {
            "year": [2025, 2030] + extended_years,
            "price": [average_2025, average_2030] + extended_prices,
        }
    )

    # All Canadian provinces
    nodes_tax = nodes[2:]

    # Create a DataFrame that repeats the emission prices for each node
    expanded_emission_prices = (
        pd.concat([emission_prices] * len(nodes_tax), keys=nodes_tax)
        .reset_index(level=1, drop=True)
        .reset_index()
    )
    expanded_emission_prices.rename(columns={"index": "node"}, inplace=True)

    # Format data for MESSAGEix
    def make_df(var_name, **kwargs):
        return pd.DataFrame({k: v for k, v in kwargs.items()})

    tax_emission = make_df(
        "tax_emission",
        node=expanded_emission_prices["node"],
        type_year=expanded_emission_prices["year"],
        type_tec="all",
        unit="USD/tCO2",
        type_emission="TCE",
        value=expanded_emission_prices["price"],
    )

    # Add the new unit to the platform (if not already added)
    mp.add_unit("USD/tCO2")

    msg.check_out()
    msg.add_par("tax_emission", tax_emission)
    msg.commit("Added carbon tax emission prices.")
