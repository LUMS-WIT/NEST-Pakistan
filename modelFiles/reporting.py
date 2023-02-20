# -*- coding: utf-8 -*-
"""
This function uses the reporting and plotting through pyam 
"""
import matplotlib.pyplot as plt
import pyam
import pandas as pd 
from ixmp import Platform
from ixmp.reporting import configure
from message_ix.reporting import Reporter



def collapse_callback(df):
    """Callback function to populate the IAMC 'variable' column."""
    df['variable'] = df['l'] + ' energy|' + df['c']+ '|' + df['t']
    return df.drop(['c', 'l', 't'], axis=1)

def reporter (caseName, msgSC, path, path_msg, suffix):

#%% 1) Initialization and importing required data

    nodeloc = msgSC.set('node').all()
    # Prepration for Excel writings
    writer_xls = pd.ExcelWriter(path + '\\plots\\' + caseName +'.xlsx', engine='xlsxwriter')

    
   
    # Unit conversion
    unitc = 8.76*3.6      # BZ: Conversion from GWa to PJ, Notic: modify these two lines together if needed
    unitname ='(PJ)'
    cost_unit = '(million USD/GWa)'
    modelName = 'MESSAGEix_PAK' 
    
    last_yr = 2070
    plotyrs = [2020,2025,2030,2035,2040,2045,2050,2055,2060]
    
    msgSC = message_ix.Scenario(mp, modelName, 'baseline',
                            version=3, annotation='')
    
    msgSCS = message_ix.Scenario(mp, model=modelName, scenario='SDG7',
                             version=6, annotation='')
    
    msgSCM = message_ix.Scenario(mp, model=modelName, scenario='mitigation',
                             version=5, annotation='')

    # Create a new Reporter object
    rep = rep = Reporter.from_scenario(msgSC)
    rep1 = rep1 = Reporter.from_scenario(msgSCS)
    rep2 = rep2 = Reporter.from_scenario(msgSCM)
    
    # Reporter uses the Python pint to handle units. '-', used in the Westeros
    # tutorial, is not a defined SI unit. We tell the Reporter to replace it with
    # '' (unitless) everywhere it appears.
    # need to recheck 
    configure(units={'replace': {'-': ''}})
    
    # Invesment cost 
    inv = rep.full_key('inv')
    inv_cost = rep.get(inv)
    
    inv1 = rep1.full_key('inv')
    inv_cost1 = rep1.get(inv1)
    
    inv2 = rep2.full_key('inv')
    inv_cost2 = rep2.get(inv2)
    
    
    
    def collapse_callback(df):
        """Callback function to populate the IAMC 'variable' column."""
        df['variable'] = 'Invesment Cost|' + df['t']
        return df.drop(['t'], axis =1)
    
    new_key = rep.convert_pyam(
        quantities=inv,
        year_time_dim='yv',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    df = rep.get(new_key) 
    
    new_key1 = rep1.convert_pyam(
        quantities=inv1,
        year_time_dim='yv',
        collapse=collapse_callback)
    
    new_key1 = new_key1[0]
    
    df = df.append(rep1.get(new_key1))
    
    new_key2 = rep2.convert_pyam(
        quantities=inv2,
        year_time_dim='yv',
        collapse=collapse_callback)
    
    new_key2 = new_key2[0]
    
    df = df.append(rep2.get(new_key2))
    
    
    
    df = df.append(df1)
    df = df.filter(year= plotyrs)
    df_inv = df.filter(variable='Invesment Cost|*').timeseries()
    df_inv = df.aggregate('Invesment Cost')
    
    
    df_inv = df_inv.filter(year = plotyrs)
    df_inv.interpolate(2015)
    df_inv.line_plot(color= 'scenario')
    
    fig, ax = plt.subplots(figsize=(10, 10))
    df.stack_plot(ax=ax, total=True)
    fig.subplots_adjust(right=0.55)
    plt.show()
    
    # Variable Cost + Fixed Cost 
    tom = rep.full_key('tom')
    tom = tom.drop('yv')
    tom_cost = rep.get(tom)
    
    tom1 = rep1.full_key('tom')
    tom1 = tom1.drop('yv')
    tom_cost1 = rep1.get(tom1)
    
    tom2 = rep2.full_key('tom')
    tom2 = tom2.drop('yv')
    tom_cost2 = rep2.get(tom2)
    
    def collapse_callback(df):
        """Callback function to populate the IAMC 'variable' column."""
        df['variable'] = 'Operational Cost|' + df['t']
        return df.drop(['t'], axis =1)
    
    new_key = rep.convert_pyam(
        quantities=tom,
        year_time_dim='ya',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    
    df = df.append(rep.get(new_key))
    
    new_key = rep1.convert_pyam(
        quantities=tom1,
        year_time_dim='ya',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    
    df = df.append(rep1.get(new_key))
    
    new_key = rep2.convert_pyam(
        quantities=tom2,
        year_time_dim='ya',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    
    df = df.append(rep2.get(new_key))
    
    df = df.filter(year= plotyrs)
    df_opra = df.filter(variable='Operational Cost|*').timeseries()
    df_opr = df.aggregate('Operational Cost')
    
    df_inv = df.aggregate('Invesment Cost') 
    
    df_cost = df_opr.append(df_inv)
    
    # Writing Output to Csv 
    
   
    df_cost.to_csv('cost.csv')

    fname = 'cost.csv'
    df_costu= pyam.IamDataFrame(fname, encoding='ISO-8859-1')
    df_costu= pyam.IamDataFrame(fname)
    
    
    data = df_costu.filter(level=0,
                 year='average')
    data = pd.read_csv('cost.csv')
    
    data.pivot("Scenario","Variable", "Average").plot(kind='bar')
    plt.ylabel("Cost (USD/GWa)")
    plt.show()
    
    
    
    import plotly.express as px
    df = px.data.tips()
    fig = px.bar(data, x="Scenario", y="Average", color='Variable',barmode = 'group',
                 height=400)
    fig.show()
    
    from plotly.offline import plot
    import plotly.graph_objs as go
    
    fig = go.Figure(data=[{'type': 'bar', 'y': [2, 1, 4]}])
    
    plot(fig)
    
    
    fig, ax = plt.subplots(figsize=(10, 10))
    data.pie_plot(ax=ax)
    fig.subplots_adjust(right=0.75, left=0.3)
    plt.show()
    
    fig, ax = plt.subplots(figsize=(10, 10))
    df_opra.stack_plot(ax=ax, total=True)
    fig.subplots_adjust(right=0.55)
    plt.show()
    
    # vom = rep.full_key('vom')
    # vom = vom.drop('yv')
    # vom_cost = rep.get(tom)
    
    # def collapse_callback(df):
    #     """Callback function to populate the IAMC 'variable' column."""
    #     df['variable'] = 'Variable Cost|' + df['t']
    #     return df.drop(['t'], axis =1)
    
    # new_key = rep.convert_pyam(
    #     quantities=inv,
    #     year_time_dim='yv',
    #     collapse=collapse_callback)
    
    # new_key = new_key[0]  # Unwrap the single item in the list
    

    # df_a = rep.get(new_key)
    # df_a = df_a.filter(year= plotyrs)
    # df_var = df_a.filter(variable='Variable Cost|*').timeseries()
    # df_vara= df_a.aggregate('Variable Cost')
    
    # fig, ax = plt.subplots(figsize=(10, 10))
    # df_vara.stack_plot(ax=ax, total=True)
    # fig.subplots_adjust(right=0.55)
    # plt.show()
    
    
    # Output 
    # Baseline
    out = rep.full_key('out')
    out = out.drop('h', 'hd', 'm', 'nd')
    rep.get(out)
    
    # SDG7 
    out1 = rep1.full_key('out')
    out1 = out1.drop('h', 'hd', 'm', 'nd', )
    rep1.get(out1)
    
    # Mitigation
    out2 = rep2.full_key('out')
    out2 = out2.drop('h', 'hd', 'm', 'nd')
    rep.get(out2)
    
    
    def collapse_callback(df):
        """Callback function to populate the IAMC 'variable' column."""
        df['variable'] = df['l'] + ' energy|' + df['c']+ '|' + df['t']
        return df.drop(['c', 'l', 't'], axis=1)

    new_key = rep.convert_pyam(
        quantities=out,
        year_time_dim='yv',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    df = df.append(rep.get(new_key))
    
    
    new_key = rep1.convert_pyam(
        quantities=out1.drop('h', 'hd', 'm', 'nd', 'yv'),
        year_time_dim='yv',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    df = df.append(rep1.get(new_key))
    
    new_key = rep2.convert_pyam(
        quantities=out2,
        year_time_dim='yv',
        collapse=collapse_callback)
    
    new_key = new_key[0]  
    
    df = df.append(rep2.get(new_key))
    
    
     # Demands
    # Baseline
    dmd = rep.full_key('demand')
    dmd = dmd.drop('h', 'l')
    ab = rep.get(dmd)
    
    # SDG7 
    dmd1 = rep1.full_key('demand')
    dmd1 = dmd1.drop('h', 'l')
    a = rep1.get(dmd1)
    
    # Mitigation
    dmd2 = rep2.full_key('demand')
    dmd2 = dmd2.drop('h', 'l')
    rep2.get(dmd2)
    
    
    
    def collapse_callback(df):
        
        """Callback function to populate the IAMC 'variable' column."""
        df['variable'] = 'Demand|' + df['c']
        return df.drop(['c'], axis=1)
    
    new_key = rep.convert_pyam(
        quantities= dmd,
        year_time_dim='y',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    df_dmd = rep.get(new_key)
    
    
    new_key = rep1.convert_pyam(
        quantities=dmd1,
        year_time_dim='y',
        collapse=collapse_callback)
    
    new_key = new_key[0]  # Unwrap the single item in the list
    
    df_dmd = df_dmd.append(rep1.get(new_key))
    
    new_key = rep2.convert_pyam(
        quantities=dmd2,
        year_time_dim='y',
        collapse=collapse_callback)
    
    new_key = new_key[0]  
    
    df_dmd = df_dmd.append(rep2.get(new_key))
    
    
    df_dmd = df_dmd.filter(year= plotyrs)
    
    df_dmd.to_csv('demands.csv')
    
    # df_dmd.interpolate(2015)
    
    scenarios = ('baseline', 'SDG7', 'mitigation')

    df_dmd_b = df_dmd.filter(scenario = 'baseline')
    df_dmd_sdg = df_dmd.filter(scenario = 'SDG7')
    
    df_tcook = df_dmd.filter(variable='Demand|nt_cooking')
    df_tcook.line_plot(color='scenario')
    
    df_tcoo = df_dmd.filter(variable='Demand|t_cooking')
    df_tcoo.line_plot(color='scenario')
    
    df_elec = df_dmd.filter(variable='Demand|rc_spec')
    df_elec.line_plot(color='scenario')
    
    
    df_dmd_b.filter(variable=['Demand|t_cooking',
                            'Demand|nt_cooking']).stack_plot(total=True)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    df_dmd_sdg.bar_plot(ax=ax, stacked=True)
    fig.subplots_adjust(right=0.55)
    plt.show()
    
    fig, ax = plt.subplots(figsize=(10, 10))
    df_elec.stack_plot(ax=ax, stack='scenario', cmap='tab20', total=True)
    plt.show()
    
    elec_dmd = df_dmd.filter(variable = 'Demand|rc_spec')
    
    elec_dmd.line_plot(color= 'scenario')
    
    fig, ax = plt.subplots(figsize=(10, 10))
    elec_dmd.stack_plot(ax=ax, total=True)
    fig.subplots_adjust(right=0.55)
    plt.show()    
    # Aggregation of primary energy  for sectors 
    df.filter(variable='primary energy|*').timeseries()
    df.aggregate('primary energy', append=True)
    df.aggregate('primary energy|coal', append=True)
    df.aggregate('primary energy|gas', append=True)
    df.aggregate('primary energy|crude oil', append=True)
    df.aggregate('primary energy|biomass', append=True)
    df.aggregate('primary energy|biomass', append=True)
    
    df.aggregate(variable='primary energy', components='coal', append=False)
    a = df.aggregate(variable='primary energy|gas',append=False)
    data = df.filter(variable='primary energy|coal|*')
    
    data.interpolate(2015)  # some values are missing
    
    # Emissions 
    emi = rep.full_key('emi')
    emi2 = emi.drop('h', 'hd', 'm', 'nd', 'nl')
    rep.get(emi2)
    
    def collapse_callback1(df):
        """Callback function to populate the IAMC 'variable' column."""
        df['variable'] = 'Emission|'+ df['e'] 
        return df.drop(['c','t'], axis=1)
    
    new_key1 = rep.convert_pyam(
        quantities=emi2,
        year_time_dim='ya',
        collapse=collapse_callback1)
    new_key1 = new_key1[0]  # Unwrap the single item in the list
    
    df1 = rep.get(new_key1) 
    df1 = df1.filter(year= plotyrs)
    
    
    fig, ax = plt.subplots(figsize=(10, 10))
    data.stack_plot(ax=ax, total=True)
    fig.subplots_adjust(right=0.55)
    plt.show()
    
    fig, ax = plt.subplots(figsize=(10, 10))
    data.bar_plot(ax=ax, stacked=True)
    fig.subplots_adjust(right=0.55)
    plt.show()
    


