# Import required Libraries 
import pandas as pd
import ixmp
import message_ix
from message_ix import make_df
import os

# for modefiles execuation
import matplotlib.pyplot as plt
import pyam
import pandas as pd 
from ixmp import Platform
from ixmp.reporting import configure
from message_ix.reporting import Reporter
from pathlib import Path
import plotly.graph_objects as go

# Add Utilis Functions to add different parameters or set in the model
# Set Input in model 
def set_input(scenerio, year_vtg, year_act, technology, commodity, level, value):

    input_df = make_df('input',
                       node_loc = "Pakistan",
                       technology = technology,
                       year_vtg = year_vtg,
                       year_act = year_act,
                       mode = "M1",
                       node_origin = "Pakistan",
                       commodity = commodity,
                       level =  level,
                       time = "year",
                       time_origin = "year",
                       value = value,
                       unit = "GWa"
    )

    scenerio.add_par("Input", input_df )

# Set Output in model 
def set_output(scenerio, year_vtg, year_act, technology, commodity, level, value):

    output_df = make_df('input',
                       node_loc = "Pakistan",
                       technology = technology,
                       year_vtg = year_vtg,
                       year_act = year_act,
                       mode = "M1",
                       node_dest = "Pakistan",
                       commodity = commodity,
                       level =  level,
                       time = "year",
                       time_dest = "year",
                       value = value,
                       unit = "GWa"
    )

    scenerio.add_par("output", output_df)


# Adjust Renewables Potential
def set_renewables_potential(scenerio, commodity, grade, value):

    # Get all years
    years =  scenerio.set("year")

    renewable_potential_df = make_df("renewable_potential",
                                     node = 'Pakistan',
                                     commodity = commodity,
                                     grade = grade,
                                     level = "renewable",
                                     year = years[14:],
                                     value = value,
                                     unit = "GWa/a"
    )
    
    scenerio.add_par("renewable_potential", renewable_potential_df)









