import pandas as pd
import requests
import os
import math

class CODERS_pull:
    """
    Class containing the functions related to pulling CODERS data for use
    in the MESSAGE model. Requries an API key to be passed
    """
    def __init__(self, key, ref_year, base_year, end_year, time_step, provincial=True):
        self.key = key
        self.url = 'http://206.12.95.102/'
        self.root = os.path.dirname(os.path.dirname(os.getcwd()))
        self.base_year = base_year
        self.ref_year = ref_year
        self.end_year = end_year
        self.time_step = time_step
        self.model_years = range(base_year, end_year+1, time_step)
        self.historic_years = range(ref_year, base_year, time_step)
        self.years = range(ref_year, end_year+1, time_step)
        self.provincial = provincial

        # Create gen_generic
        gen_generic = pd.DataFrame.from_dict(requests.get(f'{self.url}/generation_generic?key={self.key}').json())
        gen_generic = gen_generic.set_index(gen_generic['gen_type'], drop=True)
        gen_generic = gen_generic.join(pd.read_csv('CODERS-MESSAGE_technologies.csv', index_col=1))
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
        
        # create list of provinces from CODERS and add short forms
        self.provinces = generators.operating_region.unique()
        self.prov_short = {}
        for prov in self.provinces:
            self.prov_short[prov] = generators[generators.operating_region == prov]['province'].iloc[0]


    def run_all_electr_gen(self):
        self.electr_gen_inv_costs(method='coders')
        self.electr_gen_fix_var_cost(om_type='variable')
        self.electr_gen_fix_var_cost(om_type='fixed')
        self.electr_gen_create_generic_sheet(value='technical_lifetime')
        self.electr_gen_create_generic_sheet(value='construction_time')
        self.electr_gen_emission_factor()
        self.electr_gen_historical_new_capacity()
        self.electr_gen_historical_activity_raw()


    def electr_gen_inv_costs(self, method='coders'):
        """
        Pulls investment cost data from CODERS and creates inv_cost csv file in MESSAGE format
        """
        costs = self.gen_generic[['MESSAGE_tech', 'year']]
        costs['capital_cost_USD_per_MW'] = self.gen_generic['capital_cost_CAD_per_kW'] / 1.3 * 1000

        if method == 'coders':
            cost_evolution = self.CODERS_cost_evolution()

        cost_data = {}
        for year in self.model_years:
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
                mes_tech = costs.loc[coders_tech, 'MESSAGE_tech']
                cost_data[f'{mes_tech}|{year}'] = cost_evolution.loc[f'{tech}', f'{year}'] * costs.loc[coders_tech, 'capital_cost_USD_per_MW']
        cost_data = pd.DataFrame.from_dict(cost_data,orient='index').reset_index()
        cost_data.columns = ['index', 'value']
        cost_data[['technology', 'year_vtg']] = cost_data['index'].str.split('|', expand=True)
        cost_data['node'] = 'Canada'
        cost_data['unit'] = 'USD/MW'
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
            cost_data = cost_data[~(cost_data.node == 'Canada')]

        result.to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_inv_costs.csv', index=False)


    def electr_gen_fix_var_cost(self, om_type):
        """
        Pulls fixed or variable cost data from CODERS and creates csv file in MESSAGE format
        """
        costs = self.gen_generic[['MESSAGE_tech', 'year']]
        if om_type == 'fixed':
            unit = 'MWyear'
            msg_unit = 'MW'
        elif om_type == 'variable':
            unit = 'MWh'
            msg_unit = unit

        costs[f'{om_type}_om_cost_USD_per_{unit}'] = self.gen_generic[f'{om_type}_om_cost_CAD_per_{unit}'] / 1.3

        cost_data = {}
        for tech in costs.index:
            mes_tech = costs.loc[tech, 'MESSAGE_tech']
            for year_vtg in self.years:
                act_years = [year for year in self.years if year >= year_vtg and year <= self.end_year and year <= year_vtg + self.gen_generic.loc[tech].service_life]
                for year_act in act_years:
                    cost_data[f'{mes_tech}|{year_vtg}|{year_act}'] = costs.loc[tech, f'{om_type}_om_cost_USD_per_{unit}']
        cost_data = pd.DataFrame.from_dict(cost_data,orient='index').reset_index()
        cost_data.columns = ['index', 'value']
        cost_data[['technology', 'year_vtg', 'year_act']] = cost_data['index'].str.split('|', expand=True)
        cost_data['node'] = 'Canada'
        cost_data['unit'] = f'USD/{msg_unit}'
        if om_type == 'variable':
            cost_data['mode'] = 'default'
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
            result = result[~(result.node == 'Canada')]

        if om_type == 'fixed':
            result.to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_fix_costs.csv', index=False)
        elif om_type == 'variable':
            result.to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_var_costs.csv', index=False)


    def CODERS_cost_evolution(self):
        """
        Pulls cost evolution data from CODERS, returns relative price change for each period
        """
        cost_evolution = pd.DataFrame.from_dict(requests.get(f'{self.url}/generation_cost_evolution?key={self.key}').json())
        cost_evolution = cost_evolution.set_index(cost_evolution['gen_type'])
        cost_evolution = cost_evolution.loc[:, cost_evolution.columns.str.contains('CAD_per_kW')]
        base_cost = cost_evolution[f'{self.base_year}_CAD_per_kW']
        cost_series = pd.DataFrame()
        for year in self.model_years:
            if year <= 2050:
                cost_series[f'{year}'] = cost_evolution[f'{year}_CAD_per_kW'] / base_cost
            else:
                cost_series[f'{year}'] = cost_evolution['2050_CAD_per_kW'] / base_cost
        cost_series.index = cost_series.index.str.lower()
        cost_series = cost_series.drop(['hydro_annual'])
        return cost_series


    def electr_gen_create_generic_sheet(self, value):
        """
        Function for creating technical lifetime, construction time sheets in
        MESSAGE format
        """
        data = {}
        if value == 'technical_lifetime':
            name = value
            value = 'service_life'
            unit = 'y'
        elif value == 'construction_time':
            name = value
            unit = 'y'

        for year in self.years:
            for tech in self.gen_generic.index:
                mes_tech = self.gen_generic.loc[tech, 'MESSAGE_tech']
                data[f'{mes_tech}|{year}'] = self.gen_generic.loc[tech][value]
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
            result = result[~(result.node == 'Canada')]
        result.to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_{name}.csv', index=False)
    

    def electr_gen_emission_factor(self):
        """
        Pulls emission factors from CODERS, creates csv in MESSAGE format
        """
        value = 'carbon_emissions'
        unit = 'tC'
        data = {}
        for tech in self.gen_generic.index:
            mes_tech = self.gen_generic.loc[tech, 'MESSAGE_tech']
            for year_vtg in self.years:
                act_years = [year for year in self.years if year >= year_vtg and year <= self.end_year and year <= year_vtg + self.gen_generic.loc[tech].service_life]
                for year_act in act_years:
                    data[f'{mes_tech}|{year_vtg}|{year_act}'] = self.gen_generic.loc[tech][value]
        data = pd.DataFrame.from_dict(data,orient='index').reset_index()
        data.columns = ['index', 'value']
        data[['technology', 'year_vtg', 'year_act']] = data['index'].str.split('|', expand=True)
        data['node'] = 'Canada'
        data['emission'] = 'TCE'
        data['unit'] = unit
        data['mode'] = 'default'
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
            result = result[~(result.node == 'Canada')]

        result.to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_emission_factor.csv', index=False)


    def electr_gen_historical_new_capacity(self):
        """
        Calculates the generation capacity active at each year passed to the function,
        saves results in an excel file
        """
        generators = self.generators.copy()
        generators['region-technology'] = generators['operating_region'] + '-' + generators['MESSAGE_tech']
        i = 0
        for year in self.historic_years:
            generators_year = generators[generators.start_year < (year + self.time_step)]
            generators_year = generators_year[generators_year.start_year >= year]
            gen_prov_tech = pd.DataFrame(generators_year.groupby(['region-technology']).sum().unit_effective_capacity)
            # Calculate national capacity
            if not self.provincial:
                for tech in generators['MESSAGE_tech']:
                    name = f'Canada-{tech}'
                    gen_prov_tech.loc[name] = generators.groupby(['MESSAGE_tech']).sum().unit_effective_capacity.loc[tech]
            gen_prov_tech = gen_prov_tech.reset_index()
            gen_prov_tech[['region', 'technology']] = gen_prov_tech['region-technology'].str.split('-',expand=True)

            gen_prov_tech = gen_prov_tech.set_index(gen_prov_tech['region'], drop=True)
            gen_prov_tech['year_vtg'] = year
            gen_prov_tech['unit'] = 'MW'
            gen_prov_tech['value'] = gen_prov_tech['unit_effective_capacity']
            gen_prov_tech = gen_prov_tech[['technology', 'year_vtg', 'value', 'unit']]
            if i == 0:
                result = gen_prov_tech
                i+=1
            else:
                result = pd.concat([result, gen_prov_tech])

        if not self.provincial:
            result = result[result.index == 'Canada']
        pd.DataFrame.from_dict(result).to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_historical_new_capacity.csv')

    
    def electr_gen_historical_activity_raw(self):
        """
        Calculates the historical capacity based on the active generators in each year and the 
        average annual energy column from CODERS, saves results in an excel file
        """
        generators = self.generators.copy()
        generators['region-technology'] = generators['operating_region'] + '-' + generators['MESSAGE_tech']
        i = 0
        for year in self.years:
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
            gen_prov_tech['unit'] = 'MWa'
            gen_prov_tech['mode'] = 'default'
            gen_prov_tech['time'] = 'year'
            gen_prov_tech['value'] = gen_prov_tech['unit_average_annual_energy']
            gen_prov_tech = gen_prov_tech[['technology', 'year_act', 'mode', 'time', 'value', 'unit']]
            if i == 0:
                result = gen_prov_tech
                i+=1
            else:
                result = pd.concat([result, gen_prov_tech])
        
        if not self.provincial:
            result = result[result.index == 'Canada']
        # saving to excel
        pd.DataFrame.from_dict(result).to_csv(f'{self.root}\\data\\CODERS_data\\electr_gen_historical_activity.csv')


    def electricity_demand(self):
        """
        Gets annual provincial final electricity demand
        """
        demand = pd.DataFrame.from_dict(requests.get(f'{self.url}/forecasted_annual_demand?key={self.key}').json())
        # get rid of accent on quebec
        demand = demand.set_index(demand.province.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))
        demand = demand.rename(index={'Saskatachewan': 'Saskatchewan'})
        demand_dict = {}

        for year in self.model_years:
            for prov in self.provinces:
                if year <= 2050:
                    demand_dict[f'{prov}-{year}'] = demand.loc[prov][str(year)]
                else:
                    demand_dict[f'{prov}-{year}'] = demand.loc[prov]['2050']
        demand = pd.DataFrame.from_dict(demand_dict, orient='index',columns=['value']).reset_index()
        demand[['node', 'year']] = demand['index'].str.split('-',expand=True)
        demand['commodity'] = 'electr'
        demand['level'] = 'useful'
        demand['time'] = 'year'
        demand['unit'] = 'MWa'
        demand = demand.set_index(demand.node)
        demand = demand[['commodity', 'level', 'year', 'time', 'value', 'unit']]
        demand.to_csv(f'{self.root}\\data\\CODERS_data\\electr_demand.csv', index=True)


    def interprovincial_lines(self):
        """
        Creates the input and output data for interprovincial lines. Treats each line between two provinces as a technology,
        assigned to the Canada node. 2 modes of operation are used, from the first province (a) to the second province (b) and
        vice versa to allow bilateral trade of electricity.
        """     
        # Get line capacity data and name lines
        line_data = pd.DataFrame.from_dict(requests.get(f'{self.url}/transfer_capacities_copper?key={self.key}').json())
        efficiency = pd.DataFrame.from_dict(requests.get(f'{self.url}/CA_system_parameters?key={self.key}').json())
        
        # take average input efficiency for all provinces
        efficiency = round(1/(1-efficiency.system_line_losses_percent.mean()),2)

        line_data['avg_capacity'] = (line_data.ttc_summer + line_data.ttc_winter) / 2
        line_data[['prov_from', 'prov_a']] = line_data.balancing_area_from.str.split('.',n=1,expand=True)
        line_data[['prov_to', 'prov_b']] = line_data.balancing_area_to.str.split('.',n=1,expand=True)
        line_data = line_data.set_index('electr_trans_' + line_data.replace(self.prov_short).prov_from + '_' + line_data.replace(self.prov_short).prov_to)
        line_data = line_data[['prov_to', 'prov_from', 'avg_capacity']]
        line_data['efficiency'] = efficiency
        
        # create input sheet
        lines_input = {}
        for line in line_data.index:
            for year_vtg in self.model_years:
                act_years = [year for year in self.model_years if year >= year_vtg and year <= self.end_year]
                for year_act in act_years:
                    lines_input[f'{line}|{year_vtg}|{year_act}|a->b|{line_data.at[line,"prov_from"]}|{line_data.at[line,"prov_to"]}'] = line_data.at[line,'efficiency']
                    lines_input[f'{line}|{year_vtg}|{year_act}|b->a|{line_data.at[line,"prov_to"]}|{line_data.at[line,"prov_from"]}'] = line_data.at[line,'efficiency']
        lines_input = pd.DataFrame.from_dict(lines_input, orient='index',columns=['value']).reset_index()
        lines_input[['technology', 'year_vtg', 'year_act', 'mode', 'node_origin', 'node_dest']] = lines_input['index'].str.split('|', expand=True)
        lines_input = pd.merge(lines_input, line_data, left_on='technology', right_index=True)
        lines_input['node_loc'] = 'Canada'
        lines_input['commodity'] = 'electr'
        lines_input['level'] = 'secondary'
        lines_input['time'] = 'year'
        lines_input['time_origin'] = 'year'
        lines_input['unit'] = '%'
        temp = lines_input[['node_loc', 'technology', 'year_vtg', 'year_act', 'mode', 'node_origin', 'commodity', 'level', 'time', 'time_origin', 'value', 'unit']]
        temp.to_csv(f'{self.root}\\data\\CODERS_data\\electr_trans_inputs.csv',index=False)

        # create output sheet
        lines_input['value'] = 1
        temp = lines_input[['node_loc', 'technology', 'year_vtg', 'year_act', 'mode', 'node_dest', 'commodity', 'level', 'time', 'time_origin', 'value', 'unit']]
        temp.to_csv(f'{self.root}\\data\\CODERS_data\\electr_trans_outputs.csv',index=False)

        # create fixed costs
        lines_input['value'] = 25000/1.3 # TAKEN FROM COPPER INPUTS
        lines_input['unit'] = 'USD/MW'
        temp = lines_input[['node_loc', 'technology', 'year_vtg', 'year_act', 'value', 'unit']]
        temp.to_csv(f'{self.root}\\data\\CODERS_data\\electr_trans_fix_cost.csv',index=False)

        # create historical capacity
        temp = lines_input.copy()
        temp['value'] = temp['avg_capacity']
        temp['unit'] = 'MW'
        temp = temp[temp.year_act == str(self.base_year)]
        temp = temp[temp.year_vtg == str(self.base_year)]
        temp = temp[temp['mode'] == 'a->b']
        temp = temp[['node_loc', 'technology', 'year_vtg', 'value', 'unit']]
        temp.to_csv(f'{self.root}\\data\\CODERS_data\\electr_trans_historical_new_capacity.csv', index=False)
    

    def international_lines(self):
        line_data = pd.DataFrame.from_dict(requests.get(f'{self.url}/interty_capacity?key={self.key}').json())
        line_data = line_data.loc[~(line_data.country_from == line_data.country_to)]
        


if __name__ == '__main__':
    pull = CODERS_pull("vBiOGBwJ3hwNLpqh", ref_year=1960, base_year=2020, end_year=2060, time_step=5, provincial=True)
    pull.run_all_electr_gen()
    #pull.interprovincial_lines()
    #pull.international_lines()