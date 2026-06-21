import math

import numpy as np
import pandas as pd


def get_cum_inst_cap(scen, node, tec, calibration_year=None):
    # Retrieve `historical_new_capacity` parameter.
    years = (
        scen.par(
            "historical_new_capacity", filters={"node_loc": [node], "technology": [tec]}
        )[["year_vtg", "value"]]
        .set_index("year_vtg")
        .to_dict()["value"]
    )
    # Retrieve calibrated new capacity for model years
    if calibration_year is not None and calibration_year >= scen.firstmodelyear:
        years2 = scen.par(
            "bound_new_capacity_lo", filters={"node_loc": [node], "technology": [tec]}
        )[["year_vtg", "value"]]
        filter_years = [
            y
            for y in years2.year_vtg.unique()
            if y not in years.keys() and y <= calibration_year
        ]
        years2 = (
            years2.loc[years2.year_vtg.isin(filter_years)]
            .set_index("year_vtg")
            .to_dict()["value"]
        )
        years.update(years2)

    # Filter out all non-zero data
    years = {y: years[y] for y in years if years[y] > 0.0}

    dfs = [
        pd.DataFrame(
            {
                "year_vtg": y,
                "year_act": scen.years_active(node, tec, y),
                "value": years[y]
                * float(scen.par("duration_period", filters={"year": y}).iloc[0].value),
            }
        ).pivot_table(index="year_vtg", columns="year_act", values="value")
        for y in years
    ]
    if dfs:
        df = pd.concat(dfs)
    else:
        df = pd.DataFrame()
    return df


def calc_real_cf(scen, df, node, tec, calibration_year=None):
    # Create df with sum over vintage years
    result = (
        df.sum()
        .reset_index()
        .set_index("year_act")
        .rename(columns={0: "cumulative capacity"})
    )

    # Get current capacity factors
    cf = scen.par("capacity_factor", filters={"node_loc": node, "technology": tec})
    cf = cf[cf["year_act"] == cf["year_vtg"]][["year_act", "value"]].set_index(
        "year_act"
    )
    result["cf"] = cf.value

    # Get historical activity
    tmp = scen.par(
        "historical_activity", filters={"node_loc": node, "technology": tec}
    )[["year_act", "value"]].set_index("year_act")["value"]

    if calibration_year is not None and calibration_year >= scen.firstmodelyear:
        tmp2 = scen.par(
            "bound_activity_lo", filters={"node_loc": node, "technology": tec}
        )[["year_act", "value"]]
        filter_years = [
            y
            for y in tmp2.year_act
            if y not in tmp.index.tolist() and y <= calibration_year
        ]
        tmp2 = tmp2.loc[tmp2.year_act.isin(filter_years)]
        tmp2 = tmp2.set_index("year_act")["value"]
        tmp = pd.concat([tmp, tmp2])

    result["historical activity"] = tmp

    # calculate real CF
    val = result["historical activity"] / result["cumulative capacity"]
    result["Real CF"] = val.apply(
        lambda x: math.ceil(x * 1000.0) / 1000.0 if not np.isnan(x) else x
    )

    return result


def closest(List, K):
    """Finds the member of a list closest to a value (k)"""
    return List[min(range(len(List)), key=lambda i: abs(List[i] - K))]


def f_index(df1, df2):
    """Checks the index of two dataframes"""

    return df1.loc[df1.index.isin(df2.index)]


def f_slice(df, idx, level, locator, value):
    """Slices a MultiIndex dataframe and setting a value to a specific level

    Parameters
    ----------
    df: dataframe
    idx: list
    level: string
    locator: list,
    value: integer/string
    """
    df = df.reset_index().loc[df.reset_index()[level].isin(locator)].copy()
    df[level] = value
    return df.set_index(idx)


def idx_memb(List, x, distance):
    """Retrurns the member of the list with distance from x"""

    if List.index(x) + distance < len(List):
        return List[List.index(x) + distance]
    else:
        return False


def intpol(y1, y2, x1, x2, x, dataframe=False):
    """Interpolate between (*x1*, *y1*) and (*x2*, *y2*) at *x*.

    Parameters
    ----------
    y1, y2 : float or pd.Series
    x1, x2, x : int
    dataframe : boolean (default=True)
        Option to consider checks appropriate for dataframes/series or not.
    """
    if dataframe is False and x2 == x1 and y2 != y1:
        print(">>> Warning <<<: No difference between x1 and x2," "returned empty!!!")
        return []
    elif dataframe is False and x2 == x1 and y2 == y1:
        return y1
    else:
        if x2 == x1 and dataframe is True:
            return y1
        else:
            y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
            return y


def CAGR(first, last, periods):
    """Calculate Annual Growth Rate

    Parameters
    ----------
    first : number
        value of the first period
    second : number
        value of the second period
    periods : number
        period length between first and second value

    Returns
    -------
    val : number
        calculated annual growth rate
    """

    val = (last / first) ** (1 / periods)
    val = val.rename(last.name)
    return val


def unit_uniform(df):
    """Unifroming the "unit" in different years to prevent
    mistakes in indexing and grouping
    """

    column = [x for x in df.columns if x in ["commodity", "emission"]]
    if column:
        com_list = set(df[column[0]])
        for com in com_list:
            df.loc[df[column[0]] == com, "unit"] = df.loc[
                df[column[0]] == com, "unit"
            ].mode()[0]
    else:
        df["unit"] = df["unit"].mode()[0]
    return df
