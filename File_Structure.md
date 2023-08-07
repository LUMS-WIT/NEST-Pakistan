MESSAGEix Pakistan Model
====================

Overview of the scripts or data files use to build *MESSAGEix-Pak* baseline model:

- Motivation to build a baseline model for Pakistan's energy sector.
- Scripts are used to update existing data or constraints in the model.

### A typical top-level directory layout

    .
    ├── modelData               # List of Excel files (alternatively `csv`, `xlsx` ) for model input data.
    ├── modelFiles              # Python Script (alternatively `.py`) to add data and apply constraints on the model.
    ├── Output                  # Output files (alternatively `pdf` or `xlsx`) include plots and output data.
    ├── .gitattributes          # add attributes of file extensions to compress while pushing or pulling the repository from GitHub.
    ├── .gitignore              # add name and extensions of files that are supposed to be not pushed or pulled from the GitHub repository.
    ├── File_Structure.md       # Detail of file structure in the model.
    ├── LICENSE  
    ├── Model_progress.md       # Activity/progress detail of model development.
    └── README.md
    └── github_help.txt         # Some useful commands which help to push or pull the latest code from GitHub 
    └── pakistan_model.ipynb    # Main model file which is supposed to run the model
    └── requirement.txt         # include packages name and their version which are used for the model
    └── test_utilities.py       # Use to test any script or function
    └── utility.py              # Include all test cases and macro functions  
    
### Model Files

There are some scripts that run spontaneously in the *pakistan_model.ipynb* file to load data and adjust the baseline model scenario. These files 
are placed in the modelfiles folder.
 
    .
    ├── ...
    ├── modelFiles                                    # Root file
    │   ├── adjust_electricity_generation.py          # Script to adjust the electricity generation profile in the model
    │   ├── adjust_renewable_potential.py             # Add renewable potential and capacity factor 
    │   └── demands.py                                # Script to adjust demands in the model
    │   └── downscale_demands.py                      # Downscale global demands to local region
    │   └── parameter_modifier.py                     # Script to modify parameters in the model
    │   └── plotter_pakistan.py                       # In order to get results from the model in CSV and plots
    │   └── postprocess.py                            # Script to aggregate data frame to plot results
    │   └── reporter.py                               # Scripts to plot (demands, primary energy, cost, and emissions) Areal charts.
    │   └── share_constraints.py                      # Add the percentage of renewable shares in the model 
    │   └── update_elec_share.py                      # Add percentage share of electric renewable technologies in the model
    │   └── Update_historical_activity.py             # Update historical activity data according to new demands.
    │   └── update_units_pakistan.py                  # Update Units for model parameters
    │   └── utilis.py                                 # Some useful additional functions
    └── ...

### Model Data

In this folder, we have multiple model input data files. These files are generally in the form of 'xlsx' and 'csv' which call in the model script to update and add data to the model. 
 
    .
    ├── ...
    ├── modelData                                                      # Root file
    │   ├── 25-07-2023-MESSAGEix_PK_ch_renewables_DEMAND.xlsx          # Updated and adjusted version of the primary model file to date (25-07-2023) - Backup
    │   ├── data_MESSAGE_PK.xlsx                                       # Primary model file to add default setting and run baseline model 
    │   └── global_demand.csv                                          # Given global demands divided into 11 regions from messageix_globium Model (IIASA)
    │   └── iso_reg.xlsx                                               # Countries name according to iso format
    │   └── messageix_pak_R11_SAS.csv                                  # Demand data for south asian region (SAS)
    │   └── ModelSetup_pak.xlsx                                        # Model setup file to add. remove and update model inputs
    │   └── OECD_SSP_GDP_PPP.xlsx                                      # GDP data for different countries from the OECD Env-Growth model
    │   └── OECD_SSP_POP.xlsx                                          # Population data for different countries from the OECD Env-Growth model
    │   └── pakistan_map.xlsx                                          # Get country wise setting to aggregate and update demand data 
    │   └── Parameters_messageix_pak.xlsx                              # To update and add different parameters in the model
    │   └── Parameters_pak.xlsx                                        # Backup and original file of *Parameters_messageix_pak*
    │   └── wbi_pop_gdp_2015.xlsx                                      # GPD and POP values of 2015 for all countries (Use to update GDP and POP values of OECD Env-Growth model)
    └── ...




