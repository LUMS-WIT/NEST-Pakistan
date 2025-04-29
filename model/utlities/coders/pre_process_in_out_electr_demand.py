import pandas as pd
import os

def pre_process_electr_demand(root, years, provinces):
    """
    Creates input/output table for electr consumption
    """
    print('Creating input/output sheets for electricity consumption')
    data = pd.read_csv('electr_demand.csv',index_col=0)

    data_input = {}
    data_output = {}
    for prov in provinces:
        for tech, r in data.iterrows():
            for year_vtg in years:
                act_years = [year for year in years if year >= year_vtg and year <= years[-1]]
                for year_act in act_years:
                    data_input[f'{prov}|{tech}|{year_vtg}|{year_act}|{r.inputs}'] = r.efficiency
                    data_output[f'{prov}|{tech}|{year_vtg}|{year_act}|{r.outputs}'] = 1
    
    # Creating inputs sheet
    inputs = pd.DataFrame.from_dict(data_input, orient='index',columns=['value']).reset_index()
    inputs[['node_loc', 'technology', 'year_vtg', 'year_act', 'commodity', 'level']] = inputs['index'].str.split('|', expand=True)
    inputs['node_origin'] = inputs['node_loc']
    inputs['mode'] = 'default'
    inputs['time'] = 'year'
    inputs['time_origin'] = 'year'
    inputs['unit'] = '%'
    inputs = inputs[['node_loc', 'technology', 'year_vtg', 'year_act', 'mode', 'node_origin', 'commodity', 'level', 'time', 'time_origin', 'value', 'unit']]
    inputs.to_csv(f'{root}\\data\\CODERS_data\\electr_gen_inputs.csv', index=False)

    # Creating outputs sheet
    outputs = pd.DataFrame.from_dict(data_output, orient='index',columns=['value']).reset_index()
    outputs[['node_loc', 'technology', 'year_vtg', 'year_act', 'commodity', 'level']] = outputs['index'].str.split('|', expand=True)
    outputs['node_dest'] = outputs['node_loc']
    outputs['mode'] = 'default'
    outputs['time'] = 'year'
    outputs['time_origin'] = 'year'
    outputs['unit'] = '%'
    outputs = outputs[['node_loc', 'technology', 'year_vtg', 'year_act', 'mode', 'node_dest', 'commodity', 'level', 'time', 'time_origin', 'value', 'unit']]
    outputs.to_csv(f'{root}\\data\\CODERS_data\\electr_gen_outputs.csv', index=False)

if __name__ == "__main__":
    provinces = ['Alberta']
    years = range(1960, 2060+1, 5)
    root = os.path.dirname(os.path.dirname(os.getcwd()))
    data = pre_process_electr_gen(root, years, provinces)