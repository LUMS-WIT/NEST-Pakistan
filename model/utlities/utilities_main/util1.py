# -*- coding: utf-8 -*-
"""
This utility sets the default values to a MESSAGE parameter
"""


def setdefaults(par,nodeName):
    if 'mode' in par.columns:
        par['mode'] = 'M1'

    if 'node' in par.columns:
        par['node'] = nodeName
    if 'node_loc' in par.columns:
        par['node_loc'] = nodeName
    if 'node_parent' in par.columns:
        par['node_parent'] = nodeName
    if 'node_origin' in par.columns:
        par['node_origin'] = nodeName
    if 'node_dest' in par.columns:
        par['node_dest'] = nodeName
    if 'node_rel' in par.columns:
        par['node_rel'] = nodeName
           
    if 'time' in par.columns:
        par['time'] = 'year'
    if 'time_dest' in par.columns:
        par['time_dest'] = 'year'
    if 'time_origin' in par.columns:
        par['time_origin'] = 'year'

    return(par)



