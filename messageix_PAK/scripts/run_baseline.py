"""
MESSAGEix-Pakistan — Baseline scenario runner.

Usage
-----
    python scripts/run_baseline.py

Run from the repository root. Loads data from data/data_MESSAGE_PK.xlsx,
builds the baseline scenario, solves the model, and generates output plots
and reports under output/.
"""
import argparse
from pathlib import Path

import ixmp
import message_ix

from message_pak.postprocess import (
    unit_correction,
    plotter,
    plot,
    get_report_df,
    primary_energy_by_fuel_plot,
    demand_by_sector_plot,
    emission_plots,
    operation_investment_cost_plot,
)

# ---------------------------------------------------------------------------
# Paths (all relative to repo root — works on any OS)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / 'data' / 'data_MESSAGE_PK.xlsx'
OUTPUT_DIR = ROOT / 'output'


def parse_args():
    parser = argparse.ArgumentParser(description='Run MESSAGEix-Pakistan baseline scenario.')
    parser.add_argument('--model', default='Pakistan Model',
                        help='Model name in the ixmp platform (default: %(default)s)')
    parser.add_argument('--scenario', default='baseline_xlsx',
                        help='Scenario name (default: %(default)s)')
    parser.add_argument('--no-solve', action='store_true',
                        help='Build and commit the scenario without solving.')
    parser.add_argument('--no-plots', action='store_true',
                        help='Skip postprocessing and plot generation.')
    return parser.parse_args()


def main():
    args = parse_args()

    # Ensure output directories exist
    (OUTPUT_DIR / 'plots').mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Load platform and create scenario
    # ------------------------------------------------------------------
    print('Connecting to ixmp platform...')
    mp = ixmp.Platform()

    print(f'Creating scenario: {args.model} / {args.scenario}')
    scenario = message_ix.Scenario(mp, model=args.model,
                                   scenario=args.scenario, version='new')

    # ------------------------------------------------------------------
    # 2. Load data from Excel
    # ------------------------------------------------------------------
    print(f'Loading data from: {DATA_FILE}')
    scenario.read_excel(str(DATA_FILE), add_units=True,
                        commit_steps=False, init_items=True)

    # ------------------------------------------------------------------
    # 3. Correct units
    # ------------------------------------------------------------------
    print('Correcting units...')
    unit_correction(mp, scenario)

    # ------------------------------------------------------------------
    # 4. Commit scenario
    # ------------------------------------------------------------------
    scenario.check_out()
    scenario.commit(comment='Baseline scenario built from Excel data')
    scenario.set_as_default()
    print(f'Scenario committed as version {scenario.version}.')

    if args.no_solve:
        print('--no-solve flag set. Skipping solve.')
        mp.close_db()
        return

    # ------------------------------------------------------------------
    # 5. Solve
    # ------------------------------------------------------------------
    case_name = f'{scenario.model}__{scenario.scenario}__v{scenario.version}'
    print(f'Solving scenario (case: {case_name})...')
    scenario.solve()
    print(f'Objective value: {scenario.var("OBJ")["lvl"]}')

    if args.no_plots:
        print('--no-plots flag set. Skipping postprocessing.')
        mp.close_db()
        return

    # ------------------------------------------------------------------
    # 6. Postprocess — plotter (stacked bar charts)
    # ------------------------------------------------------------------
    print('Running postprocessing (plotter)...')
    alldf = plotter(scenario, case_name, OUTPUT_DIR)
    plot(alldf, case_name, OUTPUT_DIR)

    # ------------------------------------------------------------------
    # 7. Postprocess — reporter (pyam / IAMC format)
    # ------------------------------------------------------------------
    print('Running reporter...')
    csv_out = OUTPUT_DIR / 'MESSAGE_Pakistan_report.csv'
    pyam_df = get_report_df(scenario, output_csv=csv_out)
    print(f'Report saved to: {csv_out}')

    primary_energy_by_fuel_plot(pyam_df)
    demand_by_sector_plot(pyam_df)
    emission_plots(pyam_df)
    operation_investment_cost_plot(pyam_df)

    # ------------------------------------------------------------------
    # 8. Close database
    # ------------------------------------------------------------------
    mp.close_db()
    print('Done.')


if __name__ == '__main__':
    main()
