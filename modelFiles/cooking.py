#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This function adds necessary technologies, data for cooking fuels 

"""
import numpy as np
import pycountry
from geotext import GeoText
from itertools import product
import pandas as pd

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())],
                       columns=dictionary.keys())


def add_cooking(msgSC, msgWSC, path, nodeName, regionName, iso,suffix):


    # 1) Initialization and importing data
    year = list(msgSC.set('year').astype(int))
   
    # 2) Adding required sets if not yet
    msgSC.check_out()
    
    msgSC.add_set('commodity','nt_cooking')
    msgSC.add_set('commodity','t_cooking')
    type_tec = 'cooking'
    msgSC.add_set('type_tec', type_tec)
    
    
    # Oil-based cooking 
    tec = 'oil_stove'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':type_tec,'technology':tec},index=[0]))

    # Vintaging
    lft = 5 # Technical lifetime of 5 yrs 
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
         
    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    
    for vvv in vtgs:
        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':vtgs ,
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('lightoil')],
            'level':[str('final')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1.65],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('nt_cooking')],
            'level':[str('useful')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)
        
         # bound activity up
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_act':yrs,
            'mode':[str('M1')],
            'time':[str('year')],
            'value':[2],
            'unit':[str('GWa')]}
        df = expand_grid(dic)
        msgSC.add_par('bound_activity_up', df)   
        
    # Gas-based cooking 
    tec = 'gas_stove'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':type_tec,'technology':tec},index=[0]))

    # Vintaging
    lft = 10 # Technical lifetime of 5 yrs 
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
         
    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    
    for vvv in vtgs:
        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':vtgs ,
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('gas')],
            'level':[str('final')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1.4],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('nt_cooking')],
            'level':[str('useful')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)
        
     # Electric-based cooking 
    tec = 'electr_stove'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':type_tec,'technology':tec},index=[0]))

    # Vintaging
    lft = 10 # Technical lifetime of 5 yrs 
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
         
    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    
    for vvv in vtgs:
        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':vtgs ,
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('electr')],
            'level':[str('final')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1.2],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('nt_cooking')],
            'level':[str('useful')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)   
        
        # bound activity up
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_act':yrs,
            'mode':[str('M1')],
            'time':[str('year')],
            'value':[1],
            'unit':[str('GWa')]}
        df = expand_grid(dic)
        msgSC.add_par('bound_activity_up', df)   
        
    # Non-traditional biomass cooking 
    tec = 'ntbiom_stove'
    msgSC.add_set('technology',tec)
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':type_tec,'technology':tec},index=[0]))

    # Vintaging
    lft = 3 # Technical lifetime of 5 yrs 
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
         
    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    
    for vvv in vtgs:
        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':vtgs ,
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('biomass')],
            'level':[str('final')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1.7],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('nt_cooking')],
            'level':[str('useful')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df)  
        
         # bound activity up
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_act':yrs,
            'mode':[str('M1')],
            'time':[str('year')],
            'value':[1],
            'unit':[str('GWa')]}
        df = expand_grid(dic)
        msgSC.add_par('bound_activity_up', df)   
        
        
    # traditional biomass cooking 
    tec = 'biom_stove'
    msgSC.add_set('technology',tec)
    #msgSC.add_set('commodity','biomass_t')
    msgSC.add_set('cat_tec',pd.DataFrame({'type_tec':type_tec,'technology':tec},index=[0]))

    # Vintaging
    lft = 3 # Technical lifetime of 5 yrs 
    hc = msgSC.par('historical_new_capacity',{'technology':[tec]})
    if not hc.empty:
        year1 = hc.year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
    vtgs = msgSC.set('year').values
    if not hc.empty:
        year1 = msgSC.par('historical_new_capacity',{'technology':[tec]}).year_vtg.values[0]
    else:
        year1 = msgSC.set('cat_year',{'type_year':['firstmodelyear']}).year.values[0]
         
    # update technical lifetime and construction time
    dic = {
        'node_loc':[nodeName],
        'technology':[tec],
        'year_vtg':vtgs,
        'value':[lft],
        'unit':['-']}
    df = expand_grid(dic)
    msgSC.add_par('technical_lifetime', df)
    
    for vvv in vtgs:
        # years for this vintage based on technical lifetime
        yrs = []
        for vv in vtgs:
            if (float(vv)>=float(vvv)) & (float(vv)<=(float(vv)+float(lft))):
                yrs.append(vv)

        # input
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':vtgs ,
            'year_act':yrs,
            'mode':[str('M1')],
            'node_origin':[nodeName],
            'commodity':[str('biomass')],
            'level':[str('final')],
            'time':[str('year')],
            'time_origin':[str('year')],
            'value':[1.85],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('input', df)

        # output
        dic = {
            'node_loc':[nodeName],
            'technology':[tec],
            'year_vtg':[vvv],
            'year_act':yrs,
            'mode':[str('M1')],
            'node_dest':[nodeName],
            'commodity':[str('t_cooking')],
            'level':[str('useful')],
            'time':[str('year')],
            'time_dest':[str('year')],
            'value':[1],
            'unit':[str('-')]}
        df = expand_grid(dic)
        msgSC.add_par('output', df) 
        
    
        
    msgSC.commit('cooking technologies added')
    print('cooking technologies added')
        