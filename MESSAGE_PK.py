import os
from pathlib import Path
import click
from model.Model import model_MSG
from model.report.Plotter import plotter_MSG
from model.utlities.utils import report_to_pyam

# Options for the CLI
@click.command()
@click.option('--scenario', default='baseline', help='Build the scenario folder name.')
@click.option('--solve/--no-solve', default=False, is_flag=True, help='Solve the model or not.')
@click.option('--debug/--no-debug', default=False, is_flag=True, help='Enable debug mode or not.')
@click.option('--report/--no-report', default=False, is_flag=True, help='Generate report or not.')
@click.option('--plot/--no-plot', default=False, is_flag=True, help='Generate plots')
@click.option('--config', default=None, help='yaml config path')

def messagerun(scenario, solve, debug, report, plot, config):
    """
    This function executes the MESSAGEix-Canada model workflow based on command-line inputs.
    """
    # Print the chosen options
    print(f"Running scenario: {scenario}")
    print(f"Solve: {solve}, Debug: {debug}, Report: {report}, Plotting: {plot}, Config: {config}")

    # Create model instance
    msg1 = model_MSG(scenario_name=scenario, config=config, report=report, solve=solve)

    # Set up model with the selected scenario
    platform, msg_scenario, msg_folder = msg1.setup_scenario()
    
    # TODO: Add policies to the scenario

    

    # Remove the model solution (if any) and check out the scenario
    try:
        msg_scenario.remove_solution()
    except ValueError as e:
        print(e)
    msg_scenario.check_out()

    # Implement solve logic
    if solve:
        print("Solving the model...")
    
    # Plotter
    if plot:
        msg_plt = plotter_MSG(msg_scenario)
        nodes = msg_scenario.set("node")[2:]
        #TODO Do we need plots_df here ?
        msg_plt.plotter(
            case="test", nodeloc= nodes, path="./", yr_min=2020, yr_max=2060
        )

    # Debug mode logic
    if debug:
        print("Debug mode enabled")

    # Report generation logic - report to PYAM, not the MESSAGE Reporter
    if report:
        print("Generating report...")


if __name__ == "__main__":
    messagerun()
