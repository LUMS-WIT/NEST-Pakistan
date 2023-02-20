# -*- coding: utf-8 -*-
"""
This utility reindex a dataframe and adds it as a parameter to the MESSAGE model
"""

def reindexandadd(par, parname, msgDS):
    par = par.dropna(axis=0, how='any', thresh=None, subset=['value'])
    par.index = range(0, len(par))
    msgDS.add_par(parname, par)
    return(par)
