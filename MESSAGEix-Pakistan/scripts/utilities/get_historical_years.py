def main(scenario, year_min=1990, year_max=None):
    """Retrieves historical time periods for a given scenario.

    Parameters
    ----------
    scenario : :class:`message_ix.Scenario`
        scenario for which the historical time period should be retrieved
    year_min : int
        starting year of historical time period.

    Returns
    -------
    years : list
        all historical time periods
    year_min : int (default=1990)
        year as of which to return historical years
    year_max : int (default=None)
        year upto, including, for which to return historical years
    """

    model_years = [int(x) for x in scenario.set("year")]

    if year_max:
        years = [y for y in model_years if y <= year_max and y >= year_min]
    else:
        years = [
            y for y in model_years if y < scenario.firstmodelyear and y >= year_min
        ]
    return years
