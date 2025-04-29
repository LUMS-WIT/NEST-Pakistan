import pandas as pd
import requests
import os
import math

class CODERS_pull:
    """
    Class containing the functions related to pulling CODERS data for use
    in the MESSAGE model. Requries an API key to be passed
    """
    def __init__(self, key, base_year, end_year, time_step, provincial=True):
        self.key = key
        self.url = 'http://206.12.95.102/'
        self.root = os.path.dirname(os.path.dirname(os.getcwd()))
        self.base_year = base_year
        self.end_year = end_year
        self.time_step = time_step
        self.years = range(base_year, end_year+1, time_step)
        self.provincial = provincial

        # Create gen_generic
        gen_generic = pd.DataFrame.from_dict(requests.get(f'{self.url}/generation_generic?key={self.key}').json())
        gen_generic = gen_generic.set_index(gen_generic['gen_type'], drop=True)
        gen_generic = gen_generic.join(pd.read_csv('CODERS-MESSAGE_technologies_temp.csv', index_col=1))
        gen_generic.index = gen_generic.index.str.lower()
        gen_generic['gen_type'] = gen_generic['gen_type'].str.lower()
        gen_generic['year'] = self.base_year
        self.gen_generic = gen_generic


        # Create generators file
        generators = pd.DataFrame.from_dict(requests.get(f'{self.url}/generators?key={self.key}').json())
        generators = generators.set_index(generators['generation_unit_name'],drop=True)
        generators['gen_type'] = generators['gen_type'].str.lower()
        # Fixing NaN closure years and generator types
        closure_year = {}
        updated_gen_type = {}
        for unit, data in generators.iterrows():
            # Fixing coders bugs
            if data.gen_type == 'wind_onshore':
                gentype = 'wind_ons'
            elif data.gen_type == 'solar_pv':
                gentype = 'solar_pv'
            elif data.gen_type == 'gas_ct':
                gentype = 'ng_sc'
            else:
                gentype = data.gen_type
            if math.isnan(data.closure_year):
                closure_year[unit] = data.start_year + self.gen_generic.at[gentype, 'service_life']
            else:
                closure_year[unit] = data.closure_year
            updated_gen_type[unit] = gentype
        generators['updated_closure_year'] = pd.Series(closure_year)
        generators['updated_gen_type'] = pd.Series(updated_gen_type)
        generators = pd.merge(generators, self.gen_generic['MESSAGE_tech'], left_on='updated_gen_type', right_index=True)
        self.generators = generators
        self.provinces = generators.operating_region.unique()


    def MESSAGE_inv_costs(self, method='coders'):
        """
        Pulls investment cost data from CODERS and creates inv_cost csv file in MESSAGE format
        """
        costs = self.gen_generic[['MESSAGE_tech', 'year']]
        costs['capital_cost_USD_per_kW'] = self.gen_generic['capital_cost_CAD_per_kW'].copy() / 1.3

        if method == 'coders':
            cost_evolution = self.CODERS_cost_evolution()

        cost_data = {}
        for year in self.years:
            for tech in cost_evolution.index:
                # Fixing coders bugs
                if tech == 'wind_onshore':
                    coders_tech = 'wind_ons'
                elif tech == 'wind_offshore':
                    coders_tech = 'wind_ofs'
                elif tech == 'solar_pv':
                    coders_tech = 'solar_pv'
                elif tech == 'gas_ct' or tech == 'ng_ct':
                    coders_tech = 'ng_sc'
                else:
                    coders_tech = tech
                cost_data[f'{tech}|{year}'] = cost_evolution.loc[f'{tech}', f'{year}'] * costs.loc[coders_tech, 'capital_cost_USD_per_kW']
        cost_data = pd.DataFrame.from_dict(cost_data,orient='index').reset_index()
        cost_data.columns = ['index', 'value']
        cost_data[['technology', 'year_vtg']] = cost_data['index'].str.split('|', expand=True)
        cost_data['node'] = 'Canada'
        cost_data['unit'] = 'USD/kW'
        cost_data = cost_data[['node', 'technology', 'year_vtg', 'value', 'unit']]

        if self.provincial:
            i = 0
            for prov in self.provinces:
                prov_cost = cost_data.copy()
                prov_cost['node'] = prov
                if i == 0:
                    result = pd.concat([cost_data, prov_cost])
                    i+=1
                else:
                    result = pd.concat([result, prov_cost])

        result.to_csv(f'{self.root}\\data\\CODERS_data\\generator_inv_costs.csv', index=False)


    def MESSAGE_fix_var_cost(self, om_type):
        """
        Pulls fixed or variable cost data from CODERS and creates csv file in MESSAGE format
        """
        costs = self.gen_generic[['MESSAGE_tech', 'year']]
        if om_type == 'fixed':
            unit = 'MWyear'
        elif om_type == 'variable':
            unit = 'MWh'

        costs[f'{om_type}_om_cost_USD_per_{unit}'] = self.gen_generic[f'{om_type}_om_cost_CAD_per_{unit}'].copy() / 1.3

        cost_data = {}
        for tech in costs.index:
            for year_vtg in self.years:
                act_years = [year for year in self.years if year >= year_vtg and year <= self.end_year and year <= year_vtg + self.gen_generic.loc[tech].service_life]
                for year_act in act_years:
                    cost_data[f'{tech}|{year_vtg}|{year_act}'] = costs.loc[tech, f'{om_type}_om_cost_USD_per_{unit}'].copy()
        cost_data = pd.DataFrame.from_dict(cost_data,orient='index').reset_index()
        cost_data.columns = ['index', 'value']
        cost_data[['technology', 'year_vtg', 'year_act']] = cost_data['index'].str.split('|', expand=True)
        cost_data['node'] = 'Canada'
        cost_data['unit'] = f'USD/{unit}'
        if om_type == 'variable':
            cost_data['mode'] = 'M1'
            cost_data = cost_data[['node', 'technology', 'year_vtg', 'year_act', 'mode', 'value', 'unit']]
        elif om_type == 'fixed':
            cost_data = cost_data[['node', 'technology', 'year_vtg', 'year_act', 'value', 'unit']]
        
        if self.provincial:
            i = 0
            for prov in self.provinces:
                prov_cost = cost_data.copy()
                prov_cost['node'] = prov
                if i == 0:
                    result = pd.concat([cost_data, prov_cost])
                    i+=1
                else:
                    result = pd.concat([result, prov_cost])

        if om_type == 'fixed':
            result.to_csv(f'{self.root}\\data\\CODERS_data\\generator_fix_costs.csv', index=False)
        elif om_type == 'variable':
            result.to_csv(f'{self.root}\\data\\CODERS_data\\generator_var_costs.csv', index=False)


    def CODERS_cost_evolution(self):
        """
        Pulls cost evolution data from CODERS, returns relative price change for each period
        """
        cost_evolution = pd.DataFrame.from_dict(requests.get(f'{self.url}/generation_cost_evolution?key={self.key}').json())
        cost_evolution = cost_evolution.set_index(cost_evolution['gen_type'])
        cost_evolution = cost_evolution.loc[:, cost_evolution.columns.str.contains('CAD_per_kW')]
        base_cost = cost_evolution[f'{self.base_year}_CAD_per_kW']
        cost_series = pd.DataFrame()
        for year in self.years:
            if year <= 2050:
                cost_series[f'{year}'] = cost_evolution[f'{year}_CAD_per_kW'] / base_cost
            else:
                cost_series[f'{year}'] = cost_evolution['2050_CAD_per_kW'] / base_cost
        cost_series.index = cost_series.index.str.lower()
        cost_series = cost_series.drop(['hydro_annual'])
        return cost_series


    def MESSAGE_create_generic_sheet(self, value):
        """
        Function for creating technical lifetime, construction time sheets in
        MESSAGE format
        """
        data = {}

        if value == 'technical_lifetime':
            value = 'service_life'
            unit = 'y'
        elif value == 'construction_time':
            unit = 'y'

        for year in self.years:
            for tech in self.gen_generic.index:
                data[f'{tech}|{year}'] = self.gen_generic.loc[tech][value].copy()
        data = pd.DataFrame.from_dict(data,orient='index').reset_index()
        data.columns = ['index', 'value']
        data[['technology', 'year_vtg']] = data['index'].str.split('|', expand=True)
        data['node'] = 'Canada'
        data['unit'] = unit
        data = data[['node', 'technology', 'year_vtg', 'value', 'unit']]
        
        if self.provincial:
            i = 0
            for prov in self.provinces:
                prov_data = data.copy()
                prov_data['node'] = prov
                if i == 0:
                    result = pd.concat([data, prov_data])
                    i+=1
                else:
                    result = pd.concat([result, prov_data])
        pd.DataFrame.from_dict(result).to_csv(f'{self.root}\\data\\CODERS_data\\{value}.csv', index=False)
    
    def MESSAGE_emission_factor(self):
        """
        Pulls emission factors from CODERS, creates csv in MESSAGE format
        """
        value = 'carbon_emissions'
        unit = 'tC'
        data = {}
        for tech in self.gen_generic.index:
            for year_vtg in self.years:
                act_years = [year for year in self.years if year >= year_vtg and year <= self.end_year and year <= year_vtg + self.gen_generic.loc[tech].service_life]
                for year_act in act_years:
                    data[f'{tech}|{year_vtg}|{year_act}'] = self.gen_generic.loc[tech][value].copy()
        data = pd.DataFrame.from_dict(data,orient='index').reset_index()
        data.columns = ['index', 'value']
        data[['technology', 'year_vtg', 'year_act']] = data['index'].str.split('|', expand=True)
        data['node'] = 'Canada'
        data['emission'] = 'TCE'
        data['unit'] = unit
        data['mode'] = 'M1'
        data = data[['node', 'technology', 'year_vtg', 'year_act', 'mode', 'emission', 'value', 'unit']]
        
        if self.provincial:
            i = 0
            for prov in self.provinces:
                prov_data= data.copy()
                prov_data['node'] = prov
                if i == 0:
                    result = pd.concat([data, prov_data])
                    i+=1
                else:
                    result = pd.concat([result, prov_data])

        result.to_csv(f'{self.root}\\data\\CODERS_data\\{value}.csv', index=False)


    def MESSAGE_historical_capacity_raw(self, years=[2015,2020]):
        """
        Calculates the generation capacity active at each year passed to the function,
        saves results in an excel file
        """
        generators = self.generators.copy()
        generators['region-technology'] = generators['operating_region'] + '-' + generators['MESSAGE_tech']
        i = 0
        for year in years:
            generators_year = generators[generators.start_year <= year]
            generators_year = generators_year[generators_year.updated_closure_year > year]
            gen_prov_tech = pd.DataFrame(generators_year.groupby(['region-technology']).sum().unit_effective_capacity)
            # Calculate national capacity
            for tech in generators['MESSAGE_tech']:
                name = f'Canada-{tech}'
                gen_prov_tech.loc[name] = generators.groupby(['MESSAGE_tech']).sum().unit_effective_capacity.loc[tech]
            gen_prov_tech = gen_prov_tech.reset_index()
            gen_prov_tech[['region', 'technology']] = gen_prov_tech['region-technology'].str.split('-',expand=True)

            gen_prov_tech = gen_prov_tech.set_index(gen_prov_tech['region'], drop=True)
            gen_prov_tech['year_vtg'] = year
            gen_prov_tech['unit'] = 'Gwa'
            gen_prov_tech['value'] = gen_prov_tech['unit_effective_capacity'] / 1000
            gen_prov_tech = gen_prov_tech[['technology', 'year_vtg', 'value', 'unit']]
            if i == 0:
                result = gen_prov_tech
                i+=1
            else:
                result = pd.concat([result, gen_prov_tech])

        if not self.provincial:
            result = result[result.index == 'Canada']
        pd.DataFrame.from_dict(result).to_excel(f'{self.root}\\data\\CODERS_data\\historical_capacity_raw_CODERS.xlsx')

    
    def MESSAGE_historical_activity_raw(self, years=[2015,2020]):
        """
        Calculates the historical capacity based on the active generators in each year and the 
        average annual energy column from CODERS, saves results in an excel file
        """
        generators = self.generators.copy()
        generators['region-technology'] = generators['operating_region'] + '-' + generators['MESSAGE_tech']
        i = 0
        for year in years:
            generators_year = generators[generators.start_year <= year]
            generators_year = generators_year[generators_year.updated_closure_year > year]
            gen_prov_tech = pd.DataFrame(generators_year.groupby(['region-technology']).sum().unit_average_annual_energy)
            # Calculate national capacity
            for tech in generators['MESSAGE_tech']:
                name = f'Canada-{tech}'
                gen_prov_tech.loc[name] = generators.groupby(['MESSAGE_tech']).sum().unit_average_annual_energy.loc[tech]
            gen_prov_tech = gen_prov_tech.reset_index()
            gen_prov_tech[['region', 'technology']] = gen_prov_tech['region-technology'].str.split('-',expand=True)

            # formatting
            gen_prov_tech = gen_prov_tech.set_index(gen_prov_tech['region'], drop=True)
            gen_prov_tech['year_act'] = year
            gen_prov_tech['unit'] = 'Gwa'
            gen_prov_tech['mode'] = 'M1'
            gen_prov_tech['time'] = 'year'
            gen_prov_tech['value'] = gen_prov_tech['unit_average_annual_energy'] / 1000
            gen_prov_tech = gen_prov_tech[['technology', 'year_act', 'mode', 'time', 'value', 'unit']]
            if i == 0:
                result = gen_prov_tech
                i+=1
            else:
                result = pd.concat([result, gen_prov_tech])
        
        if not self.provincial:
            result = result[result.index == 'Canada']
        # saving to excel
        pd.DataFrame.from_dict(result).to_excel(f'{self.root}\\data\\CODERS_data\\historical_activity_raw_CODERS.xlsx')
     

if __name__ == '__main__':
    pull = CODERS_pull("vBiOGBwJ3hwNLpqh", base_year=2020, end_year=2060, time_step=5, provincial=True)
    #pull.MESSAGE_inv_costs(method='coders')
    #pull.MESSAGE_fix_var_cost(om_type='variable')
    #pull.MESSAGE_fix_var_cost(om_type='fixed')
    #pull.MESSAGE_create_generic_sheet(value='technical_lifetime')
    #pull.MESSAGE_create_generic_sheet(value='construction_time')
    #pull.MESSAGE_emission_factor()
    #pull.MESSAGE_historical_capacity_raw([2015, 2020])
    #pull.MESSAGE_historical_activity_raw([2015, 2020])