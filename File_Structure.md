MESSAGEix Pakistan Model
====================

Overview of the scripts or data files use to build *MESSAGEix-Pak* baseline model:

- Motivation to build a baseline model for Pakistan's energy sector.
- Scripts are used to update existing data or constraints in the model.

### A typical top-level directory layout

    .
    ├── modelData               # List of Excel files (alternatively `csv`, `xlsx` ) for model input data.
    ├── modelFiles              # Python Script (alternatively `.py`) to add data and apply constraints on the model.
    ├── Output                  # Output files (alternatively `pdf` or `xlsx`) include plots and data.
    ├── .gitattributes          # add attributes of file extensions to compress while pushing or pulling the repository from GitHub.
    ├── .gitignore              # add name and extensions of files that are supposed to be not pushed or pulled from the GitHub repository.
    ├── LICENSE                  
    └── README.md
    └── github_help.txt         # Some useful commands which help to push or pull the latest code from GitHub 
    └── pakistan_model.ipynb    # Main model file which is supposed to run the model
    └── requirement.txt         # include packages name and their version which are used for the model
    └── test_utilities.py       # Use to test any script or function
    └── utility.py              # Include all test cases and macro functions  
    
There are some scripts that run spontaneously in the *pakistan_model.ipynb* file to load data and adjust the baseline model scenario. These files 
are placed in the modelfiles folder.
 
    .
    ├── ...
    ├── modelFiles                                    # Test files (alternatively `spec` or `tests`)
    │   ├── adjust_electricity_generation.py          # Load and stress tests
    │   ├── adjust_renewable_potential.py                               # End-to-end, integration tests (alternatively `e2e`)
    │   └── demands.py
    │   └── downscale_demands.py
    │   └── parameter_modifier.py
    │   └── plotter_pakistan.py    
    │   └── postprocess.py  
    │   └── reporter.py   
    │   └── share_constraints.py   
    │   └── update_elec_share.py   
    │   └── Update_historical_activity.py   
    │   └── update_units_pakistan.py   
    │   └── utilis.py   
    └── ...



