import pandas as pd
import glob
import message_ix
import ixmp
from pre_process_coders import CODERS_pull
from pre_process_in_out_electr_gen import pre_process_electr_gen
from pre_process_renewables import pre_process_renewables

class provincial_model:
    def __init__(self, scenario, version):
        self.version = version
        self.scenario = scenario
        
        # Define dictionaries of sets
        self.sets = {}

        # Define dictionary of sheet data
        self.construction_time = pd.DataFrame()
        self.inputs = pd.DataFrame()
        self.outputs = pd.DataFrame()
        self.emission_factor = pd.DataFrame()
        self.fix_cost = pd.DataFrame()
        self.historical_activity = pd.DataFrame()
        self.historical_new_capacity = pd.DataFrame()
        self.inv_cost = pd.DataFrame()
        self.renewable_capacity_factor = pd.DataFrame()
        self.renewable_potential = pd.DataFrame()
        self.technical_lifetime = pd.DataFrame()
        self.var_cost = pd.DataFrame()

    
    def create_message_model(self, root):
        print('Creating message model')
        mp = ixmp.Platform()
        scenario = message_ix.Scenario(mp, model='Message_provincial', scenario=self.scenario, version=self.version)
        scenario.read_excel(f'{root}\\data\\model_{self.scenario}_v{self.version}.xlsx')
        return scenario, mp
        
    
    def pull_data(self, key):
        # Create input data files from CODERS
        pull = CODERS_pull(key, ref_year=1960, base_year=2020, end_year=2060, time_step=5, provincial=True)
        print(f'Pulling data from CODERS')
        #pull.run_all_electr_gen()
        #pull.interprovincial_lines()
        #pull.electricity_demand()
        return pull


    def create_sheet_data(self, root, years, provinces):
        pre_process_electr_gen(root, years, provinces)
        pre_process_renewables(root, years)

    
    def create_excel_model(self, root):
        print('Creating excel spreadsheet')
        with pd.ExcelWriter(f'{root}\\data\\model_{self.scenario}_v{self.version}.xlsx') as writer:
            for file in glob.glob(f'{root}\\data\\CODERS_data\\*.csv'):
                if '_construction_time' in file:
                    if self.construction_time.empty:
                        self.construction_time = pd.read_csv(file)
                    else:
                        self.construction_time = pd.concat([self.construction_time, pd.read_csv(file)], ignore_index=True)

                elif '_emission_factor' in file:
                    if self.emission_factor.empty:
                        self.emission_factor = pd.read_csv(file)
                    else:
                        self.emission_factor = pd.concat([self.emission_factor, pd.read_csv(file)], ignore_index=True)

                elif '_fix_cost' in file:
                    if self.fix_cost.empty:
                        self.fix_cost = pd.read_csv(file)
                    else:
                        self.fix_cost = pd.concat([self.fix_cost, pd.read_csv(file)], ignore_index=True)

                elif '_historical_activity' in file:
                    if self.historical_activity.empty:
                        self.historical_activity = pd.read_csv(file)
                    else:
                        self.historical_activity = pd.concat([self.historical_activity, pd.read_csv(file)], ignore_index=True)

                elif '_historical_new_capacity' in file:
                    if self.historical_new_capacity.empty:
                        self.historical_new_capacity = pd.read_csv(file)
                    else:
                        self.historical_new_capacity = pd.concat([self.historical_new_capacity, pd.read_csv(file)], ignore_index=True)

                elif '_inv_cost' in file:
                    if self.inv_cost.empty:
                        self.inv_cost = pd.read_csv(file)
                    else:
                        self.inv_cost = pd.concat([self.inv_cost, pd.read_csv(file)], ignore_index=True)

                elif 'renewable_capacity_factor' in file:
                    if self.renewable_capacity_factor.empty:
                        self.renewable_capacity_factor = pd.read_csv(file)
                    else:
                        self.renewable_capacity_factor = pd.concat([self.renewable_capacity_factor, pd.read_csv(file)], ignore_index=True)

                elif 'renewable_potential' in file:
                    if self.renewable_potential.empty:
                        self.renewable_potential = pd.read_csv(file)
                    else:
                        self.renewable_potential = pd.concat([self.renewable_potential, pd.read_csv(file)], ignore_index=True)

                elif '_technical_lifetime' in file:
                    if self.technical_lifetime.empty:
                        self.technical_lifetime = pd.read_csv(file)
                    else:
                        self.technical_lifetime = pd.concat([self.technical_lifetime, pd.read_csv(file)], ignore_index=True)

                elif '_var_cost' in file:
                    if self.var_cost.empty:
                        self.var_cost = pd.read_csv(file)
                    else:
                        self.var_cost = pd.concat([self.var_cost, pd.read_csv(file)], ignore_index=True)
                
                elif '_inputs' in file:
                    if self.inputs.empty:
                        self.inputs = pd.read_csv(file)
                    else:
                        self.inputs = pd.concat([self.inputs, pd.read_csv(file)], ignore_index=True)

                elif '_outputs' in file:
                    if self.inputs.empty:
                        self.outputs = pd.read_csv(file)
                    else:
                        self.outputs = pd.concat([self.outputs, pd.read_csv(file)], ignore_index=True)
           
            self.create_sets(writer)
            print('Saving parameter values')
            self.construction_time.to_excel(writer, sheet_name='construction_time', index=False)
            self.emission_factor.to_excel(writer, sheet_name='emission_factor', index=False)
            self.fix_cost.to_excel(writer, sheet_name='fix_cost', index=False)
            self.historical_activity.to_excel(writer, sheet_name='historical_activity', index=False)
            self.historical_new_capacity.to_excel(writer, sheet_name='historical_new_capacity', index=False)
            self.inputs.to_excel(writer, sheet_name='input', index=False)
            self.inv_cost.to_excel(writer, sheet_name='inv_cost', index=False)
            self.outputs.to_excel(writer, sheet_name='output', index=False)
            self.renewable_capacity_factor.to_excel(writer, sheet_name='renewable_capacity_factor', index=False)
            self.renewable_potential.to_excel(writer, sheet_name='renewable_potential', index=False)
            self.technical_lifetime.to_excel(writer, sheet_name='technical_lifetime', index=False)
            self.var_cost.to_excel(writer, sheet_name='var_cost', index=False)
            pd.read_csv(f'{root}\\model\\message_provincial\\ix_type_mapping.csv').to_excel(writer, sheet_name='ix_type_mapping', index=False)

            
    
    def create_sets(self, writer):
        print('Saving sets')
        self.sets['technology'] = set(self.outputs.technology.unique())
        self.sets['commodity'] = set(list(self.inputs.commodity.unique()) + list(self.outputs.commodity.unique()))
        self.sets['mode'] = set(self.inputs['mode'].unique())
        self.sets['node'] = set(list(self.construction_time.node.unique()) + list(self.inputs.node_loc.unique()))
        self.sets['emission'] = set(self.emission_factor.emission.unique())
        self.sets['level'] = set(list(self.inputs.level.unique()) + list(self.outputs.level.unique()))
        self.sets['grade'] = set(list(self.renewable_capacity_factor.grade))

        temp = pd.DataFrame.from_dict(self.sets['commodity'])
        temp.columns = ['commodity']
        temp.to_excel(writer, sheet_name='commodity', index=False)

        temp = pd.DataFrame.from_dict(self.sets['emission'])
        temp.columns = ['emission']
        temp.to_excel(writer, sheet_name='emission', index=False)

        temp = pd.DataFrame.from_dict(self.sets['grade'])
        temp.columns = ['grade']
        temp.to_excel(writer, sheet_name='grade', index=False)

        temp = pd.DataFrame.from_dict(self.sets['level'])
        temp.columns = ['level']
        temp.to_excel(writer, sheet_name='level', index=False)

        temp = pd.DataFrame.from_dict(self.sets['mode'])
        temp.columns = ['mode']
        temp.to_excel(writer, sheet_name='mode', index=False)

        temp = pd.DataFrame.from_dict(self.sets['node'])
        temp.columns = ['node']
        temp.to_excel(writer, sheet_name='node', index=False)

        temp = pd.DataFrame.from_dict(self.sets['technology'])
        temp.columns = ['technology']
        temp.to_excel(writer, sheet_name='technology', index=False)


if __name__ == '__main__':
    model = provincial_model('electricity_only', 'new')
    pull = model.pull_data('vBiOGBwJ3hwNLpqh')

    #model.create_sheet_data(pull.root, pull.years, pull.provinces)
    model.create_excel_model(pull.root)
    scenario, mp = model.create_message_model(pull.root)
    scenario.solve()
    print(scenario.var("OBJ"))
    mp.close_db()