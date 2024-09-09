# -*- coding: utf-8 -*-
"""
This Script is use to adjust renewable potential in the model, in case if there is any missing
renenwable potential in your model you can adjust/add using this script

- When we receive our primary file there is missing hydro renewable potential 
- We set hydro renewable pootential = 60 and renewable capacity factor = 0.512

"""
# Import required Libraries 
from message_ix import make_df

def adjust_renewable_potential_and_capacity(scenerio):

    # Filter years from 2020-2050
    years = [x for x in scenerio.set('year') if x >2020]

    add_hydro_renewable_potential = make_df("renewable_potential", node = "Pakistan",
        commodity = "hydro",grade = "c1", level = "renewable", year = years, value = 60, unit = "GWa/a")

    scenerio.add_par("renewable_potential", add_hydro_renewable_potential)

    add_hydro_renewable_potential = make_df("renewable_capacity_factor", node = "Pakistan", commodity = "hydro",
            grade = "c1", level = "renewable", year = years, value = 0.512, unit = "GWa/a")

    scenerio.add_par("renewable_capacity_factor", add_hydro_renewable_potential)
