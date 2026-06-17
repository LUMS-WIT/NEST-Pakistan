# -*- coding: utf-8 -*-


def update_reserve_margin(scenario, nodeNames, contin):
    """
    Update the reserve-margin constraint (res_marg) for elec_t_d.

    Computes a sector-weighted load factor for each region/year and writes
    the corresponding relation_activity coefficient for the res_marg relation.

    Parameters
    ----------
    scenario : message_ix.Scenario
    nodeNames : list
        List of node names to update.
    contin : float
        Contingency/reserve margin fraction (e.g. 0.15 for 15%).
    """
    demands = scenario.par("demand")
    input_df = scenario.par("input", {"technology": "elec_t_d"})

    with scenario.transact("Update reserve-margin constraint"):
        for reg in nodeNames:
            if "Canada" in reg:
                continue

            for year in demands["year"].unique():
                d = demands[(demands["node"] == reg) & (demands["year"] == year)]

                rc_row = d[d["commodity"] == "rc_spec"]
                i_row = d[d["commodity"] == "i_spec"]

                if rc_row.empty or i_row.empty:
                    continue

                rc_spec = float(rc_row["value"].iloc[0])
                i_spec = float(i_row["value"].iloc[0])

                inp_row = input_df[
                    (input_df["node_loc"] == reg)
                    & (input_df["year_act"] == year)
                    & (input_df["year_vtg"] == year)
                    & (input_df["commodity"] == "electr")
                    & (input_df["level"] == "secondary")
                    & (input_df["mode"] == "M1")
                ]

                if inp_row.empty:
                    continue

                inp = float(inp_row["value"].iloc[0])

                val = (
                    ((i_spec * 1.0 + rc_spec * 2.0) / (i_spec + rc_spec))
                    * (1.0 + contin)
                    * inp
                    * -1.0
                )

                scenario.add_par(
                    "relation_activity",
                    {
                        "relation": ["res_marg"],
                        "node_rel": [reg],
                        "year_rel": [year],
                        "node_loc": [reg],
                        "technology": ["elec_t_d"],
                        "year_act": [year],
                        "mode": ["M1"],
                        "value": [val],
                        "unit": ["GWa"],
                    },
                )
