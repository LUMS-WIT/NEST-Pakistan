## Model Progress

- Overview of the activity that we have done to develop the MESSAGEix-Pakistan model. 
- During our model development phase we go through multiple reports, papers, and policies document to understand the current and future profile of Pakistan's energy sector.

<b>Initial Phase of the model development</b>
- Review Different papers and reports
- Remove infeasibility in the initial model file
- Start from a bottom-up approach to cross-check all technologies in the model output
- Figure out some limitations from the data side
- Move to a top-down approach and review all demands side model input data
<br>
<img src="https://raw.githubusercontent.com/UmerYasin1/Wind-Speed-forcasting/main/Model%20flow.PNG" alt="Model Flow chart" class="inline"/>
<br>
<b>Adjust parameters</b>

- Use IIASA Script to update model demands 
- Some new demands look fine and some are a bit off with the literature
- Model is not utilizing hydro because its potential was not added
- Add share constraint to define the percentage of renewables
- Moving to adjust the supply side of the model

<br>
<img src="https://raw.githubusercontent.com/UmerYasin1/Wind-Speed-forcasting/main/mf2.PNG" alt="Model Flow chart" class="inline"/>
<br>
<b>Move to Supply Side</b>

- Adjust the electricity generation values in the model
- Adjust constraints and add more capacity for hydro for future years
- Solve model and generate new results
  
<br>
<img src="https://raw.githubusercontent.com/UmerYasin1/Wind-Speed-forcasting/main/mf3.PNG" alt="Model Flow chart" class="inline"/>


### Adjustment of Electricity Generation values in model baseline scenario for the year 2020-2060

| Type Tec      | Intial_act_up | Intial_act_lo | growth_act_up | growth_act_lo | Intial_cap_up | Intial_cap_lo | growth_cap_up | growth_cap_lo |
| :---:         |     :---:     |         :---: | :---:         |     :---:     |         :---: | :---:         |     :---:     |         :---: |
| Bio           |      1.5%     |               | 5%            |               |               |               |               |               |  
| Coal          |               |               | 0.08%         |               |               |               |               |               |  
| Hydro         |      50%      |     remove    | 90%           | -0.1%         | 25%           | 0.05%         | 25%           | -0.05%        |  
| Wind          |     6.52%     |               |               |               |               |               |               |               |  
| Gas           |      5%       |               | 17%           |               |               |               |               |               |  
| Nuclear       |     50%       |               | 50%           | -0.001%       |               | 0.001%        |               | -0.005%       |  
| Solar         |    1.85%      |               |               |               |               |               |               |               |  
