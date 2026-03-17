"""
Reporting functions for MESSAGEix-Pakistan model output.

Uses the MESSAGEix Reporter and pyam for IAMC-formatted output and plots.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyam
from message_ix.reporting import Reporter


def get_report_df(scenario, output_csv=None, min_year=2015, max_year=2060):
    """Build the default MESSAGEix report and return a pyam.IamDataFrame.

    Parameters
    ----------
    scenario : message_ix.Scenario
    output_csv : str or Path, optional
        If provided, save the raw report DataFrame to this CSV path.
    min_year : int
    max_year : int

    Returns
    -------
    pyam.IamDataFrame
    """
    rep = Reporter.from_scenario(scenario)
    report = rep.get('message:default')

    report_df = report.timeseries()
    report_df.reset_index(inplace=True)
    report_df.columns = report_df.columns.astype(str)
    report_df.columns = report_df.columns.str.title()

    years = scenario.set('year').tolist()
    years = [str(x) for x in years if min_year <= x <= max_year]

    report_df.fillna(0, inplace=True)

    # Convert GWa → TWh
    c = report_df.select_dtypes(include=[np.number]) * 8.76
    report_df[c.columns] = c

    report_df.columns = report_df.columns.astype(str)
    report_df = report_df.drop(
        report_df.columns.to_series()['2020': str(min_year)], axis=1)

    if output_csv is not None:
        report_df.to_csv(output_csv, index=False)

    # Rename variables to IAMC conventions
    replacements = {
        'emis': 'Emissions',
        'out|final|': 'Final Energy|',
        'out|primary|': 'Primary Energy|',
        'in|renewable|': 'Primary Energy|renewable|',
        'out|renewable|': 'Primary Energy|renewable|',
        'total om cost|': 'Total Costs|',
        'out|useful|': 'Useful Energy|',
        'in|useful|': 'Useful Energy|',
    }
    for old, new in replacements.items():
        report_df['Variable'] = report_df['Variable'].str.replace(old, new, regex=False)

    return pyam.IamDataFrame(report_df)


def primary_energy_by_fuel_plot(pyam_df,
                                plotyrs=(2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060)):
    """Stacked area chart of primary energy by fuel type."""
    pdf = pyam_df.copy()
    plotyrs = list(plotyrs)

    biomass = ['Primary Energy|biomass|bio_istig_ccs|M1',
               'Primary Energy|biomass|bio_istig|M1']
    lng = ['Primary Energy|LNG|LNG_bal|M1']
    coal = ['Primary Energy|coal|coal_bal|M1', 'Primary Energy|coal|coal_exp|M1',
            'Primary Energy|coal|coal_extr_ch4|M1', 'Primary Energy|coal|coal_extr|M1',
            'Primary Energy|coal|lignite_extr|M1']
    gas = [f'Primary Energy|gas|gas_extr_{i}|M1' for i in range(1, 7)]
    oil = ['Primary Energy|crudeoil|oil_exp|M1'] + \
          [f'Primary Energy|crudeoil|oil_extr_{i}|M1' for i in range(1, 8)]
    hydro = ['Primary Energy|renewable|hydro|hydro_hc|M1',
             'Primary Energy|renewable|hydro|hydro_lc|M1']
    biomass_renew = [f'Primary Energy|renewable|biomass|bio_extr_{c}|M1'
                     for c in 'abcdefg']
    solar = ['Primary Energy|renewable|solar_pv|solar_pv_ppl|M1',
             'Primary Energy|renewable|solar_th|solar_th_ppl|M1']
    wind = ['Primary Energy|renewable|wind|wind_ppf|M1',
            'Primary Energy|renewable|wind|wind_ppl|M1']
    lh2 = ['Primary Energy|lh2|lh2_bal|M1', 'Primary Energy|lh2|lh2_exp|M1']
    ethanol = ['Primary Energy|methanol|meth_bal|M1', 'Primary Energy|methanol|meth_exp|M1']
    methanol = ['Primary Energy|ethanol|eth_bal|M1', 'Primary Energy|ethanol|eth_exp|M1']

    aggregations = {
        'Primary Energy|coal': coal,
        'Primary Energy|renewable|solar': solar,
        'Primary Energy|renewable|hydro': hydro,
        'Primary Energy|ethanol': ethanol,
        'Primary Energy|methanol': methanol,
        'Primary Energy|Liq. Hydrogen': lh2,
        'Primary Energy|renewable|wind': wind,
        'Primary Energy|renewable|biomass': biomass_renew,
        'Primary Energy|biomass': biomass,
        'Primary Energy|oil': oil,
        'Primary Energy|gas': gas,
        'Primary Energy|LNG': lng,
    }
    for name, components in aggregations.items():
        pdf.aggregate(name, components=components, append=True)

    data = pdf.filter(
        variable=['Primary Energy|renewable|solar', 'Primary Energy|gas',
                  'Primary Energy|oil', 'Primary Energy|biomass',
                  'Primary Energy|renewable|wind', 'Primary Energy|Liq. Hydrogen',
                  'Primary Energy|methanol', 'Primary Energy|ethanol',
                  'Primary Energy|renewable|hydro', 'Primary Energy|renewable|biomass',
                  'Primary Energy|coal'],
        year=plotyrs)

    data.plot.stack(title='Primary Energy by fuel - Baseline Scenario')
    plt.legend(loc=1)
    plt.ylabel('TWh')
    plt.tight_layout()
    plt.show()


def demand_by_sector_plot(pyam_df,
                          plotyrs=(2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060)):
    """Stacked area chart of useful energy demand by sector."""
    df_useful = pyam_df.copy()
    plotyrs = list(plotyrs)

    i_feed = ['Useful Energy|i_feed|ethanol_fs|M1', 'Useful Energy|i_feed|gas_fs|M1',
              'Useful Energy|i_feed|loil_fs|M1', 'Useful Energy|i_feed|methanol_fs|M1']
    transport = ['Useful Energy|transport|coal_trp|M1', 'Useful Energy|transport|elec_trp|M1',
                 'Useful Energy|transport|eth_fc_trp|M1', 'Useful Energy|transport|eth_ic_trp|M1',
                 'Useful Energy|transport|foil_trp|M1', 'Useful Energy|transport|gas_trp|M1',
                 'Useful Energy|transport|h2_fc_trp|M1', 'Useful Energy|transport|loil_trp|M1',
                 'Useful Energy|transport|meth_fc_trp|M1', 'Useful Energy|transport|meth_ic_trp|M1']
    i_spec = ['Useful Energy|i_spec|h2_fc_I|M1', 'Useful Energy|i_spec|sp_coal_I|M1',
              'Useful Energy|i_spec|sp_el_I|M1', 'Useful Energy|i_spec|sp_eth_I|M1',
              'Useful Energy|i_spec|sp_liq_I|M1', 'Useful Energy|i_spec|sp_meth_I|M1']
    i_therm = ['Useful Energy|i_therm|biomass_i|M1', 'Useful Energy|i_therm|coal_i|M1',
               'Useful Energy|i_therm|elec_i|M1', 'Useful Energy|i_therm|eth_i|M1',
               'Useful Energy|i_therm|foil_i|M1', 'Useful Energy|i_therm|gas_i|M1',
               'Useful Energy|i_therm|h2_fc_I|M1', 'Useful Energy|i_therm|h2_i|M1',
               'Useful Energy|i_therm|heat_i|M1', 'Useful Energy|i_therm|hp_el_i|M1',
               'Useful Energy|i_therm|hp_gas_i|M1', 'Useful Energy|i_therm|loil_i|M1',
               'Useful Energy|i_therm|meth_i|M1', 'Useful Energy|i_therm|solar_i|M1']
    rc_spec = ['Useful Energy|rc_spec|h2_fc_RC|M1', 'Useful Energy|rc_spec|sp_el_RC|M1']
    rc_therm = ['Useful Energy|rc_therm|biomass_rc|M1', 'Useful Energy|rc_therm|coal_rc|M1',
                'Useful Energy|rc_therm|eth_rc|M1', 'Useful Energy|rc_therm|foil_rc|M1',
                'Useful Energy|rc_therm|gas_rc|M1', 'Useful Energy|rc_therm|h2_fc_RC|M1',
                'Useful Energy|rc_therm|h2_rc|M1', 'Useful Energy|rc_therm|heat_rc|M1',
                'Useful Energy|rc_therm|hp_el_rc|M1', 'Useful Energy|rc_therm|hp_gas_rc|M1',
                'Useful Energy|rc_therm|loil_rc|M1', 'Useful Energy|rc_therm|meth_rc|M1',
                'Useful Energy|rc_therm|solar_rc|M1']

    df_useful.aggregate('Useful Energy|residential/commercial thermal',
                        components=rc_therm, append=True)
    df_useful.aggregate('Useful Energy|residential/commercial specific',
                        components=rc_spec, append=True)
    df_useful.aggregate('Useful Energy|industrial thermal',
                        components=i_therm, append=True)
    df_useful.aggregate('Useful Energy|industrial specific',
                        components=i_spec, append=True)
    df_useful.aggregate('Useful Energy|industrial feedstock',
                        components=i_feed, append=True)
    df_useful.aggregate('Useful Energy|transport',
                        components=transport, append=True)

    data = df_useful.filter(
        variable=['Useful Energy|residential/commercial thermal',
                  'Useful Energy|residential/commercial specific',
                  'Useful Energy|industrial thermal',
                  'Useful Energy|industrial specific',
                  'Useful Energy|industrial feedstock',
                  'Useful Energy|transport'],
        year=plotyrs)

    data.plot.stack(title='Demands by sector')
    plt.legend(loc=1)
    plt.ylabel('TWh')
    plt.tight_layout()
    plt.show()


def emission_plots(pyam_df,
                   plotyrs=(2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060)):
    """Stacked area chart of CO2 emissions by source."""
    df_emis = pyam_df.copy()
    plotyrs = list(plotyrs)

    cement = ['Emissions|CO2|cement_CO2|M1']
    coal = ['Emissions|CO2|coal_extr_ch4|M1', 'Emissions|CO2|coal_extr|M1',
            'Emissions|CO2|coal_imp|M1']
    gas = [f'Emissions|CO2|gas_extr_{i}|M1' for i in range(1, 7)]
    oil = ['Emissions|CO2|oil_extr_1_ch4|M1', 'Emissions|CO2|oil_extr_1|M1',
           'Emissions|CO2|oil_extr_2_ch4|M1', 'Emissions|CO2|oil_extr_2|M1',
           'Emissions|CO2|oil_extr_3_ch4|M1', 'Emissions|CO2|oil_extr_3|M1',
           'Emissions|CO2|oil_extr_4_ch4|M1', 'Emissions|CO2|oil_extr_4|M1',
           'Emissions|CO2|oil_extr_5|M1', 'Emissions|CO2|oil_extr_6|M1',
           'Emissions|CO2|oil_extr_7|M1']
    oil_trade = ['Emissions|CO2|foil_imp|M1', 'Emissions|CO2|loil_exp|M1',
                 'Emissions|CO2|loil_imp|M1', 'Emissions|CO2|oil_imp|M1']
    gas_trade = ['Emissions|CO2|LNG_exp|M1', 'Emissions|CO2|LNG_imp|M1',
                 'Emissions|CO2|gas_imp|M1']

    df_emis.aggregate('Emissions|CO2|gas', components=gas, append=True)
    df_emis.aggregate('Emissions|CO2|oil', components=oil, append=True)
    df_emis.aggregate('Emissions|CO2|coal', components=coal, append=True)
    df_emis.aggregate('Emissions|CO2|cement', components=cement, append=True)
    df_emis.aggregate('Emissions|CO2|oil trade', components=oil_trade, append=True)
    df_emis.aggregate('Emissions|CO2|gas trade', components=gas_trade, append=True)

    data = df_emis.filter(
        variable=['Emissions|CO2|gas', 'Emissions|CO2|oil', 'Emissions|CO2|coal',
                  'Emissions|CO2|cement', 'Emissions|CO2|oil trade',
                  'Emissions|CO2|gas trade'],
        year=plotyrs)

    data.plot.stack(title='CO2 Emissions - Baseline Scenario')
    plt.legend(loc=1)
    plt.ylabel('TWh')
    plt.tight_layout()
    plt.show()


def operation_investment_cost_plot(pyam_df,
                                   plotyrs=(2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060)):
    """Stacked area chart of total operation + investment costs."""
    df_cost = pyam_df.copy()
    plotyrs = list(plotyrs)

    coal = ['Total Costs|coal_adv', 'Total Costs|coal_adv_ccs', 'Total Costs|coal_bal',
            'Total Costs|coal_exp', 'Total Costs|coal_extr', 'Total Costs|coal_extr_ch4',
            'Total Costs|coal_gas', 'Total Costs|coal_hpl', 'Total Costs|coal_i',
            'Total Costs|coal_imp', 'Total Costs|coal_ppl', 'Total Costs|coal_ppl_u',
            'Total Costs|coal_rc', 'Total Costs|coal_t_d', 'Total Costs|syn_liq',
            'Total Costs|meth_coal', 'Total Costs|lignite_extr']
    biomass = ['bio_hpl', 'bio_ppl', 'Total Costs|liq_bio']
    elec = ['Total Costs|elec_exp', 'Total Costs|elec_i', 'Total Costs|elec_imp',
            'Total Costs|elec_t_d', 'Total Costs|elec_trp']
    oil = ['Total Costs|foil_i', 'Total Costs|foil_imp', 'Total Costs|foil_ppl',
           'Total Costs|oil_extr_1', 'Total Costs|oil_extr_1_ch4',
           'Total Costs|oil_extr_2', 'Total Costs|oil_extr_3', 'Total Costs|oil_extr_4',
           'Total Costs|oil_extr_5', 'Total Costs|oil_extr_6', 'Total Costs|oil_extr_7',
           'Total Costs|oil_extr_2_ch4', 'Total Costs|oil_extr_3_ch4',
           'Total Costs|loil_cc', 'Total Costs|loil_ppl']
    gas = ['Total Costs|gas_bal', 'Total Costs|gas_bio', 'Total Costs|gas_cc',
           'Total Costs|gas_cc_ccs', 'Total Costs|gas_ct',
           'Total Costs|gas_extr_1', 'Total Costs|gas_extr_2', 'Total Costs|gas_extr_3',
           'Total Costs|gas_extr_4', 'Total Costs|gas_extr_5', 'Total Costs|gas_extr_6',
           'Total Costs|gas_extr_mpen', 'Total Costs|gas_fs', 'Total Costs|gas_hpl',
           'Total Costs|gas_i', 'Total Costs|gas_imp', 'Total Costs|gas_ppl',
           'Total Costs|gas_rc', 'Total Costs|gas_t_d', 'Total Costs|gas_t_d_ch4',
           'Total Costs|gas_trp', 'Total Costs|igcc']
    geo_ppl = ['Total Costs|geo_hpl', 'Total Costs|geo_ppl']
    solar = ['Total Costs|solar_i', 'Total Costs|solar_pv_ppl',
             'Total Costs|solar_rc', 'Total Costs|solar_th_ppl']
    wind = ['Total Costs|wind_curtailment1', 'Total Costs|wind_curtailment2',
            'Total Costs|wind_curtailment3', 'Total Costs|wind_ppf', 'Total Costs|wind_ppl']
    hydro = ['Total Costs|hydro_hc', 'Total Costs|hydro_lc']
    nuclear = ['Total Costs|nuc_lc']

    df_cost.aggregate('Total Costs|coal', components=coal, append=True)
    df_cost.aggregate('Total Costs|biomass', components=biomass, append=True)
    df_cost.aggregate('Total Costs|electricity', components=elec, append=True)
    df_cost.aggregate('Total Costs|oil', components=oil, append=True)
    df_cost.aggregate('Total Costs|gas', components=gas, append=True)
    df_cost.aggregate('Total Costs|geothermal', components=geo_ppl, append=True)
    df_cost.aggregate('Total Costs|solar', components=solar, append=True)
    df_cost.aggregate('Total Costs|wind', components=wind, append=True)
    df_cost.aggregate('Total Costs|hydro', components=hydro, append=True)
    df_cost.aggregate('Total Costs|nuclear', components=nuclear, append=True)

    data = df_cost.filter(
        variable=['Total Costs|coal', 'Total Costs|biomass', 'Total Costs|electricity',
                  'Total Costs|oil', 'Total Costs|gas', 'Total Costs|geothermal',
                  'Total Costs|solar', 'Total Costs|wind', 'Total Costs|hydro',
                  'Total Costs|nuclear'],
        year=plotyrs)

    data.plot.stack(title='Total (Operational + Investment) Costs - Baseline')
    plt.legend(loc=1)
    plt.ylabel('TWh')
    plt.tight_layout()
    plt.show()
