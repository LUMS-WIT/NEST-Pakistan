import message_ix
import pandas as pd
import pyam

def generate_report(
    model_obj,
    output_path="model/scenarios/baseline/MESSAGE_test.csv",
    min_year=2015,
    max_year=2060,
    from_excel=False,
    unit_correct=True,
):
    """
    Generate a report from the MESSAGEix scenario and save it to a CSV file.
    Args:
                    output_path (str): The path where the output CSV file will be saved.
                    min_year (int): The minimum year for the report.
                    max_year (int): The maximum year for the report.
                    from_excel (bool): Whether to read the report from an Excel file.
                    unit_correct (bool): Whether to correct units in the report.
    """
    rep = message_ix.Reporter.from_scenario(
        model_obj.ctx.source_scenario['scenario'],
        units={"apply": {"var_cost": "", "inv_cost": "", "fix_cost": ""}},
    )
    report = rep.get("message::default")
    if from_excel:
        report_df = pd.read_csv("MESSAGE_NO_example_default_report.csv")
    else:
        report_df = report.timeseries()
        report_df.reset_index(inplace=True)
        report_df.columns = report_df.columns.astype(str)
        report_df.columns = report_df.columns.str.title()
    years = model_obj.ctx.source_scenario['scenario'].set("year").tolist()
    years = [str(x) for x in years if int(x) >= min_year and int(x) <= max_year]
    report_df.fillna(0, inplace=True)
    report_df.columns = report_df.columns.astype(str)
    try:
        report_df = report_df.drop(
            report_df.columns.to_series()["2020" : str(min_year)], axis=1
        )
    except:
        print("")
    in_flows = report_df[report_df["Variable"].str.startswith("in|")]
    out_flows = report_df[report_df["Variable"].str.startswith("out|")]
    all_flows = pd.concat([out_flows, in_flows])
    report_df["Model"] = "MESSAGEix-Canada"
    report_df["Scenario"] = "Reference"
    report_df["Variable"] = report_df["Variable"].str.replace(
        "emis", "Emissions", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "in|final|", "Final Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "out|final|", "Final Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "in|primary|", "Primary Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "out|primary|", "Primary Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "in|secondary|", "Secondary Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "out|secondary|", "Secondary Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "in|renewable|", "Primary Energy|renewable|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "out|renewable|", "Primary Energy|renewable|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "total om cost|", "Total Costs|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "out|useful|", "Useful Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "in|useful|", "Useful Energy|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "CAP_NEW|new capacity|", "Capacity Addition|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "CAP|capacity|", "Capacity|", regex=False
    )
    report_df["Variable"] = report_df["Variable"].str.replace(
        "inv cost|", "Capital Cost|", regex=False
    )
    report_df["Region"] = report_df["Region"].apply(lambda x: x.split("|")[0])
    report_df.rename(columns={'Model': 'model', 'Scenario': 'scenario', 'Variable': 'variable'}, inplace=True)
    report_df = report_df.drop_duplicates(subset=["model", "scenario", "Region", "variable"], keep='first')
    pyam_df = pyam.IamDataFrame(report_df)
    variable = pyam_df.variable
    pyam_df.aggregate_region(variable, append=True)
    pyam_df.rename({"region": {"World": "Canada"}}, inplace=True)
    pyam_df.to_csv(output_path)
    print(f"Report saved to {output_path}")