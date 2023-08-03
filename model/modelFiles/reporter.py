# Report Libraries
from message_ix.reporting import Reporter
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import pyam

# Get output dataframe
def get_report_df(scenario):

    rep = Reporter.from_scenario(scenario)
    report = rep.get('message:default')

    # In order to prepare model output
    from_excel = False
    min_year = 2015
    max_year = 2060

    if from_excel:
        # Read default report
         report_df = pd.read_csv('MESSAGE_NO_example_default_report.csv')
    else:
         # Or if trying another country model, execute the next 4:
        report_df = report.timeseries()
        report_df.reset_index(inplace=True)
        report_df.columns = report_df.columns.astype(str)
        report_df.columns = report_df.columns.str.title()

            # Plotted years
        years = scenario.set('year').tolist()
        years = [str(x) for x in years if x >= min_year and x <= max_year]

        # Create data for Sankey diagrams and plot it using plotly
        report_df.fillna(0, inplace = True)

        # Convert from GWa to TWh (*8.76)
        c = report_df.select_dtypes(include=[np.number]) * 8.76
        report_df[c.columns] = c

        # Drop not necessary years
        report_df.columns = report_df.columns.astype(str)
        report_df = report_df.drop(report_df.columns.to_series()['2020': str(min_year)],
                                axis=1)

        # Identify input and output variables and its flows (provided within the Reporter: in = input x ACT, out = output x ACT)
        in_flows = report_df[report_df['Variable'].str.startswith("in|")]
        out_flows = report_df[report_df['Variable'].str.startswith("out|")]
        all_flows = out_flows.append(in_flows)

        report_df.to_csv('output/MESSAGE_Pakistan_v1.csv')

        report_df["Variable"] = report_df["Variable"].str.replace('emis', 'Emissions', regex = False)
        #report_df["Variable"] = report_df["Variable"].str.replace('in|final|', 'Final Energy|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('out|final|', 'Final Energy|', regex = False)
        #report_df["Variable"] = report_df["Variable"].str.replace('in|primary|', 'Primary Energy|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('out|primary|', 'Primary Energy|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('in|renewable|', 'Primary Energy|renewable|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('out|renewable|', 'Primary Energy|renewable|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('total om cost|', 'Total Costs|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('out|useful|', 'Useful Energy|', regex = False)
        report_df["Variable"] = report_df["Variable"].str.replace('in|useful|', 'Useful Energy|', regex = False)

        pyam_df = pyam.IamDataFrame(report_df)

        return pyam_df


# To get stack chart of primary_energy_by_fuel type
def primary_energy_by_fuel_plot(pyam_df):

    plotyrs = [2020,2025,2030,2035,2040,2045,2050,2055,2060]
    pdf = pyam_df.copy()

    biomass = ['Primary Energy|biomass|bio_istig_ccs|M1', 
    'Primary Energy|biomass|bio_istig|M1']
    #'Primary Energy|biomass|bio_ppl|M1',
    #'Primary Energy|biomass|biomass_nc|M1',
    #'Primary Energy|biomass|biomass_t_d|M1',
    #'Primary Energy|biomass|eth_bio_ccs|M1',
    #'Primary Energy|biomass|eth_bio|M1',
    #'Primary Energy|biomass|gas_bio|M1',
    #'Primary Energy|biomass|h2_bio_ccs|M1',
    #'Primary Energy|biomass|h2_bio|M1',
    #'Primary Energy|biomass|liq_bio_ccs|M1',
    #'Primary Energy|biomass|liq_bio|M1','Primary Energy|biomass|land_use_biomass|M1']

    lng = ['Primary Energy|LNG|LNG_bal|M1']

    coal = ['Primary Energy|coal|coal_bal|M1',
                        'Primary Energy|coal|coal_exp|M1',
                        'Primary Energy|coal|coal_exp|M1',
                        'Primary Energy|coal|coal_extr_ch4|M1',
                        'Primary Energy|coal|coal_extr|M1',
                        'Primary Energy|coal|lignite_extr|M1']

    gas = [#'Primary Energy|gas|gas_bal|M1',
        'Primary Energy|gas|gas_extr_1|M1',
        'Primary Energy|gas|gas_extr_2|M1',
        'Primary Energy|gas|gas_extr_3|M1',
        'Primary Energy|gas|gas_extr_4|M1',
        'Primary Energy|gas|gas_extr_5|M1',
        'Primary Energy|gas|gas_extr_6|M1']
        #'Primary Energy|gas|LNG_prod|M1']
        # 'Primary Energy|LNG|LNG_bal|M1']

    oil = [#'Primary Energy|crudeoil|oil_bal|M1',
        'Primary Energy|crudeoil|oil_exp|M1',
        # 'Primary Energy|crudeoil|oil_extr_1_ch4|M1',
            'Primary Energy|crudeoil|oil_extr_1|M1',
        # 'Primary Energy|crudeoil|oil_extr_2_ch4|M1',
            'Primary Energy|crudeoil|oil_extr_2|M1',
        #  'Primary Energy|crudeoil|oil_extr_3_ch4|M1',
            'Primary Energy|crudeoil|oil_extr_3|M1',
            #'Primary Energy|crudeoil|oil_extr_4_ch4|M1',
            'Primary Energy|crudeoil|oil_extr_4|M1',
            'Primary Energy|crudeoil|oil_extr_5|M1',
            'Primary Energy|crudeoil|oil_extr_6|M1',
            'Primary Energy|crudeoil|oil_extr_7|M1']

    hydro = ['Primary Energy|renewable|hydro|hydro_hc|M1',  'Primary Energy|renewable|hydro|hydro_lc|M1']

    biomass_renew = ['Primary Energy|renewable|biomass|bio_extr_a|M1',
                    'Primary Energy|renewable|biomass|bio_extr_b|M1',
                    'Primary Energy|renewable|biomass|bio_extr_c|M1',
                    'Primary Energy|renewable|biomass|bio_extr_d|M1',
                    'Primary Energy|renewable|biomass|bio_extr_e|M1',
                    'Primary Energy|renewable|biomass|bio_extr_f|M1',
                    'Primary Energy|renewable|biomass|bio_extr_g|M1']

    solar = ['Primary Energy|renewable|solar_pv|solar_pv_ppl|M1' , 
            'Primary Energy|renewable|solar_th|solar_th_ppl|M1']


    wind = ['Primary Energy|renewable|wind|wind_ppf|M1', 'Primary Energy|renewable|wind|wind_ppl|M1']

    lh2 = ['Primary Energy|lh2|lh2_bal|M1', 'Primary Energy|lh2|lh2_exp|M1']

    ethanol = ['Primary Energy|methanol|meth_bal|M1',  'Primary Energy|methanol|meth_exp|M1']

    methanol = ['Primary Energy|ethanol|eth_bal|M1', 'Primary Energy|ethanol|eth_exp|M1']

    pdf.aggregate(
    "Primary Energy|coal",
    components=coal,
    append=True
    )

    pdf.aggregate(
        "Primary Energy|renewable|solar",
        components=solar,
        append=True
    )

    pdf.aggregate(
        "Primary Energy|renewable|hydro",
        components=hydro,
        append=True
    )

    pdf.aggregate(
        "Primary Energy|ethanol",
        components=ethanol,
        append=True
    )
    pdf.aggregate(
        "Primary Energy|methanol",
        components=methanol,
        append=True
    )
    pdf.aggregate(
        "Primary Energy|Liq. Hydrogen",
        components=lh2,
        append=True
    )
    pdf.aggregate(
        "Primary Energy|renewable|wind",
        components=wind,
        append=True
    )

    pdf.aggregate(
        "Primary Energy|renewable|biomass",
        components= biomass_renew,
        append=True
    )


    pdf.aggregate(
        "Primary Energy|biomass",
        components= biomass,
        append=True
    )

    pdf.aggregate(
        "Primary Energy|oil",
        components=oil,
        append=True
    )

    pdf.aggregate(
        "Primary Energy|gas",
        components=gas,
        append=True
    )

    pdf.aggregate(
        "Primary Energy|LNG",
        components=lng,
        append=True
    )

    data = pdf.filter( variable=["Primary Energy|renewable|solar",
                                                #"Primary Energy|LNG",
                                                "Primary Energy|gas",
                                                "Primary Energy|oil",
                                                "Primary Energy|biomass",
                                                "Primary Energy|renewable|wind",
                                                "Primary Energy|Liq. Hydrogen",
                                                "Primary Energy|methanol",
                                                "Primary Energy|ethanol",
                                                "Primary Energy|renewable|hydro",
                                                "Primary Energy|renewable|biomass",
                                                "Primary Energy|methanol",
                                            "Primary Energy|coal"],
                year = plotyrs)

    data.plot.stack(title = 'Primary Energy by fuel - Baseline Scenario')
    plt.legend(loc=1)
    plt.tight_layout()
    plt.show()


# To get stack chart of demand by sector
def demand_by_sector_plot(pyam_df):

    df_useful = pyam_df.copy()
    plotyrs = [2020,2025,2030,2035,2040,2045,2050,2055,2060]

    i_feed = ['Useful Energy|i_feed|ethanol_fs|M1', 'Useful Energy|i_feed|gas_fs|M1',
         'Useful Energy|i_feed|loil_fs|M1', 'Useful Energy|i_feed|methanol_fs|M1']

    transport = ['Useful Energy|transport|coal_trp|M1',
                'Useful Energy|transport|elec_trp|M1',
                'Useful Energy|transport|eth_fc_trp|M1',
                'Useful Energy|transport|eth_ic_trp|M1',
                'Useful Energy|transport|foil_trp|M1',
                'Useful Energy|transport|gas_trp|M1',
                'Useful Energy|transport|h2_fc_trp|M1',
                'Useful Energy|transport|loil_trp|M1',
                'Useful Energy|transport|meth_fc_trp|M1',
                'Useful Energy|transport|meth_ic_trp|M1']


    i_spec = ['Useful Energy|i_spec|h2_fc_I|M1',
            'Useful Energy|i_spec|sp_coal_I|M1',
            'Useful Energy|i_spec|sp_el_I|M1',
            'Useful Energy|i_spec|sp_eth_I|M1',
            'Useful Energy|i_spec|sp_liq_I|M1',
            'Useful Energy|i_spec|sp_meth_I|M1']

    i_therm =   ['Useful Energy|i_therm|biomass_i|M1',
                'Useful Energy|i_therm|coal_i|M1',
                'Useful Energy|i_therm|elec_i|M1',
                'Useful Energy|i_therm|eth_i|M1',
                'Useful Energy|i_therm|foil_i|M1',
                'Useful Energy|i_therm|gas_i|M1',
                'Useful Energy|i_therm|h2_fc_I|M1',
                'Useful Energy|i_therm|h2_i|M1',
                'Useful Energy|i_therm|heat_i|M1',
                'Useful Energy|i_therm|hp_el_i|M1',
                'Useful Energy|i_therm|hp_gas_i|M1',
                'Useful Energy|i_therm|loil_i|M1',
                'Useful Energy|i_therm|meth_i|M1',
                'Useful Energy|i_therm|solar_i|M1']
    rc_spec = ['Useful Energy|rc_spec|h2_fc_RC|M1',
            'Useful Energy|rc_spec|sp_el_RC|M1']

    rc_therm = ['Useful Energy|rc_therm|biomass_rc|M1',
                'Useful Energy|rc_therm|coal_rc|M1',
                'Useful Energy|rc_therm|eth_rc|M1',
                'Useful Energy|rc_therm|foil_rc|M1',
                'Useful Energy|rc_therm|gas_rc|M1',
                'Useful Energy|rc_therm|h2_fc_RC|M1',
                'Useful Energy|rc_therm|h2_rc|M1',
                'Useful Energy|rc_therm|heat_rc|M1',
                'Useful Energy|rc_therm|hp_el_rc|M1',
                'Useful Energy|rc_therm|hp_gas_rc|M1',
                'Useful Energy|rc_therm|loil_rc|M1',
                'Useful Energy|rc_therm|meth_rc|M1',
                'Useful Energy|rc_therm|solar_rc|M1']

    biom = ['Useful Energy|non-comm|biomass_nc|M1']

# df_useful.aggregate(
#     "Useful Energy|non-Commercial biomass",
#     components=biom,
#     append=True
# )

    df_useful.aggregate(
        "Useful Energy|residential/commercial thermal",
        components=rc_therm,
        append=True
    )

    df_useful.aggregate(
        "Useful Energy|residential/commercial specific",
        components=rc_spec,
        append=True
    )

    df_useful.aggregate(
        "Useful Energy|industrial thermal",
        components=i_therm,
        append=True
    )

    df_useful.aggregate(
        "Useful Energy|industrial specific",
        components=i_spec,
        append=True
    )

    df_useful.aggregate(
        "Useful Energy|industrial feedstock",
        components=i_feed,
        append=True
    )

    df_useful.aggregate(
        "Useful Energy|transport",
        components=i_therm,
        append=True
    )

    data = df_useful.filter(scenario = 'baseline_xlsx', variable=[
    "Useful Energy|non-Commercial biomass", # It's empty 
    "Useful Energy|residential/commercial thermal",
    "Useful Energy|residential/commercial specific",
    "Useful Energy|industrial thermal",
    "Useful Energy|industrial specific",
    "Useful Energy|industrial feedstock",
    "Useful Energy|transport"],
              year = plotyrs)


    data.plot.stack(title = 'Demands by sector')
    plt.legend(loc=1)
    plt.tight_layout()
    plt.show()


def emission_plots(pyam_df):

    df_emis = pyam_df.copy()
    plotyrs = [2020,2025,2030,2035,2040,2045,2050,2055,2060]

    cement = ['Emissions|CO2|cement_CO2|M1']
    coal = ['Emissions|CO2|coal_extr_ch4|M1',
            'Emissions|CO2|coal_extr|M1',
            'Emissions|CO2|coal_imp|M1']
    foil = ['Emissions|CO2|foil_imp|M1']
    gas = ['Emissions|CO2|gas_extr_1|M1',
            'Emissions|CO2|gas_extr_2|M1',
            'Emissions|CO2|gas_extr_3|M1',
            'Emissions|CO2|gas_extr_4|M1',
            'Emissions|CO2|gas_extr_5|M1',
            'Emissions|CO2|gas_extr_6|M1'
            ]
    lignite = ['Emissions|CO2|lignite_extr|M1']
    loil = ['Emissions|CO2|loil_imp|M1']
    meth_ccs = ['Emissions|CO2|meth_coal_ccs|M1']
    oil = ['Emissions|CO2|oil_extr_1_ch4|M1',
        'Emissions|CO2|oil_extr_1|M1',
        'Emissions|CO2|oil_extr_2_ch4|M1',
        'Emissions|CO2|oil_extr_2|M1',
        'Emissions|CO2|oil_extr_3_ch4|M1',
        'Emissions|CO2|oil_extr_3|M1',
        'Emissions|CO2|oil_extr_4_ch4|M1',
        'Emissions|CO2|oil_extr_4|M1',
        'Emissions|CO2|oil_extr_5|M1',
        'Emissions|CO2|oil_extr_6|M1',
        'Emissions|CO2|oil_extr_7|M1']

    oil_trade = ['Emissions|CO2|foil_imp|M1',
                'Emissions|CO2|loil_exp|M1',
                'Emissions|CO2|loil_imp|M1',
                'Emissions|CO2|oil_imp|M1']
        
    gas_trade = ['Emissions|CO2|LNG_exp|M1',
                'Emissions|CO2|LNG_imp|M1',
                'Emissions|CO2|gas_imp|M1']
                #'Emissions|CO2|LNG_exp|M1']


    df_emis.aggregate(
        "Emissions|CO2|gas",
        components=gas,
        append=True
    )

    df_emis.aggregate(
        "Emissions|CO2|oil",
        components=oil,
        append=True
    )

    df_emis.aggregate(
        "Emissions|CO2|coal",
        components=coal,
        append=True
    )

    df_emis.aggregate(
        "Emissions|CO2|cement",
        components=cement,
        append=True
    )

    df_emis.aggregate(
        "Emissions|CO2|oil trade",
        components=oil_trade,
        append=True
    )

    df_emis.aggregate(
        "Emissions|CO2|gas trade",
        components=gas_trade,
        append=True
    )

    data = df_emis.filter(scenario = 'baseline_xlsx', variable=
    ["Emissions|CO2|gas",
    "Emissions|CO2|oil",
    "Emissions|CO2|coal",
    "Emissions|CO2|cement",
    "Emissions|CO2|oil trade",
    "Emissions|CO2|gas trade"],
              year = plotyrs)

    data.plot.stack(title = 'CO2 Emissions - Baseline Scenario')
    plt.legend(loc=1)
    plt.tight_layout()
    plt.show()


def operation_investment_cost_plot(pyam_df):

    df_cost = pyam_df.copy()
    plotyrs = [2020,2025,2030,2035,2040,2045,2050,2055,2060]

    coal = ['Total Costs|coal_adv',
            'Total Costs|coal_adv_ccs',
            'Total Costs|coal_bal',
            'Total Costs|coal_exp',
            'Total Costs|coal_extr',
            'Total Costs|coal_extr_ch4',
            'Total Costs|coal_gas',
            'Total Costs|coal_hpl',
            'Total Costs|coal_i',
            'Total Costs|coal_imp',
            'Total Costs|coal_ppl',
            'Total Costs|coal_ppl_u',
            'Total Costs|coal_rc',
            'Total Costs|coal_ppl',
            'Total Costs|coal_ppl_u',
        'Total Costs|coal_t_d',
        'Total Costs|syn_liq',
            'Total Costs|meth_coal',
        'Total Costs|lignite_extr']
    biomass = ['bio_hpl', 'bio_ppl',
            'Total Costs|liq_bio']


    elec = ['Total Costs|elec_exp',
            'Total Costs|elec_i',
            'Total Costs|elec_imp',
            'Total Costs|elec_t_d',
            'Total Costs|elec_trp']

    oil = ['Total Costs|foil_i',
        'Total Costs|foil_imp',
        'Total Costs|foil_ppl',
        'Total Costs|oil_extr_1'
        'Total Costs|oil_extr_1_ch4'
        'Total Costs|oil_extr_2',
        'Total Costs|oil_extr_3',
        'Total Costs|oil_extr_4',
        'Total Costs|oil_extr_5',
        'Total Costs|oil_extr_6',
        'Total Costs|oil_extr_7',
        'Total Costs|oil_extr_2_ch4',
        'Total Costs|oil_extr_3_ch4',
        'Total Costs|loil_cc',
        'Total Costs|loil_ppl']
    gas = ['Total Costs|gas_bal',
        'Total Costs|gas_bio',
        'Total Costs|gas_cc',
        'Total Costs|gas_cc_ccs',
        'Total Costs|gas_ct',
        'Total Costs|gas_extr_1',
        'Total Costs|gas_extr_2',
        'Total Costs|gas_extr_3',
        'Total Costs|gas_extr_4',
        'Total Costs|gas_extr_5',
        'Total Costs|gas_extr_6',
        'Total Costs|gas_extr_mpen',
        'Total Costs|gas_fs',
        'Total Costs|gas_hpl',
        'Total Costs|gas_i',
        'Total Costs|gas_imp',
        'Total Costs|gas_ppl',
        'Total Costs|gas_rc',
        'Total Costs|gas_t_d',
        'Total Costs|gas_t_d_ch4',
        'Total Costs|gas_trp',
        'Total Costs|igcc']

    geo_ppl = ['Total Costs|geo_hpl','Total Costs|geo_ppl']

    solar = ['Total Costs|solar_i',
            'Total Costs|solar_pv_ppl',
            'Total Costs|solar_rc',
            'Total Costs|solar_th_ppl']

    wind = ['Total Costs|wind_curtailment1',
    'Total Costs|wind_curtailment2',
    'Total Costs|wind_curtailment3',
    'Total Costs|wind_ppf',
    'Total Costs|wind_ppl']

    hydro = ['Total Costs|hydro_hc',
    'Total Costs|hydro_lc']

    nuclear = ['Total Costs|nuc_lc']


    df_cost.aggregate(
        "Total Costs|coal",
        components=coal,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|biomass",
        components=biomass,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|electricity",
        components=elec,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|oil",
        components=biomass,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|gas",
        components=gas,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|geothermal",
        components=geo_ppl,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|solar",
        components=solar,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|wind",
        components=wind,
        append=True
    )

    df_cost.aggregate(
        "Total Costs|hydro",
        components=hydro,
        append=True
    )
    df_cost.aggregate(
        "Total Costs|nuclear",
        components=nuclear,
        append=True
    )

    data = df_cost.filter(scenario = 'baseline_xlsx', variable=
    ["Total Costs|coal","Total Costs|biomass",
    "Total Costs|electricity",
    "Total Costs|oil",
    "Total Costs|gas",
    "Total Costs|geothermal",
    "Total Costs|solar",
    "Total Costs|wind",
    "Total Costs|hydro",
    "Total Costs|nuclear"],
              year = plotyrs)

    data.plot.stack(title = 'Total (Operational+ Investment) Costs - Baseline')
    plt.legend(loc=1)
    plt.tight_layout()
    plt.show()










