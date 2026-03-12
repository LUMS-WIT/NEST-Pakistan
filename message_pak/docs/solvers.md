# Solvers

There are a variety of available solvers to choose from when running the MESSAGE-ix model. Since MESSAGE-ix is a linear optimization problem, there is also a great number of algorithms that can be applied by each solver when tackling the problem. This page details some of the different options for running the model with different solvers.

# Solver Installation

Before we begin with the installation of our solver of choice, it is important to note that GAMS, the optimization engine behind MESSAGE-ix, requres a different license depending on the solver you ultimately decide to use to run the model. Read more on the available [license types for GAMS](https://www.gams.com/49/docs/UG_License.html?search=license#UG_License_license_types) before you proceed with your solver installation.

The recommended solver to run MESSAGE-ix is [CPLEX](https://www.ibm.com/products/ilog-cplex-optimization-studio/cplex-optimizer), however, this solver both requires a more expensive license to be used with GAMS, and is a paid sofyware of its own. There exist many open-source alternatives can can achieve comparable results in approximately the same time as CPLEX.

## Installing GAMSlinks and Solvers

To install open-source solvers via [GAMSlinks](https://github.com/coin-or/GAMSlinks/releases), follow these steps:

1. **Download the latest release**:

    - **Windows:** Download and unzip `GAMSlinks-windows.zip` to any folder of your choice.
    
    - **Linux:** Download `GAMSlinks-linux.tar.bz2` and extract it from within your terminal using:
      
      ```
      tar -xvjf GAMSlinks-linux.tar.bz2
      ```
    
    - **Mac OS:** Download `GAMSlinks-macos.tar.bz2` and extract it from within your terminal using:
      
      ```
      tar -xvjf GAMSlinks-macos.tar.bz2
      ```

2. **Update GAMS configuration:**
   Modify the `gamsconfig.yaml` file and add it to your **GAMS path**. Refer to the official [GAMS documentation](https://www.gams.com/latest/docs/UG_STANDARD_LOCATIONS.html) for details.


## Using CBC Solver

We recommend using the **CBC solver** out of the open-source alternatives, which can be installed via **Coin-OR**'s GitHub page, if not through GAMSlinks. Follow the installation guide in the [README](https://github.com/coin-or/Cbc/blob/master/README.md#download).

## Configuring Open-Source Solvers

MESSAGEix-Canada can be executed using open-source solvers such as **CBC** or **GLPK**. To enable these solvers, modify the **auxiliary settings file** located in:

```
anaconda3/envs/messageix-canada/lib/python3.12/site-packages/message_ix/model/MESSAGE/auxiliary_settings.gms
```

For further details, refer to the discussions [here](https://github.com/iiasa/message_ix/issues/576) and [here](https://github.com/iiasa/message_ix/discussions/794).

A collection of verified **open-source solvers** for **GAMS** is available via the **COIN-OR Foundation**. The latest release and installation instructions for GAMSlinks can be found [here](https://github.com/coin-or/GAMSlinks/releases).

# Solver Options

Each linear solver typically offers a few options which will dictate how the software will approach the optimization problem. In a GAMS system, these options are determined through the options file (`.opt`) which can be found inside the "model" folder for a MESSAGE-ix model. 

For CPLEX users, MESSAGE-ix conveiniantly provides direct access to these options withinb the [solve method](https://docs.messageix.org/en/latest/api.html#message_ix.Scenario.solve), where the options can be provided as an argument to the method as a Python dictionary. For other solvers, however, the user will need to provide GAMS with the `.opt` file by placing it inside their message-ix Python library path: `../miniconda3/envs/messageix/lib/python3.12/site-packages/message_ix/model/`

An example of such options file is provided below. A complete list of the solvers available to be used with GAMS and their possible options can be found in the references section of this page.

```
# Options for running a MESSAGE-ix model through GAMS using the HiGHS solver

solver = ipm # LP algorithm to run: "simplex", "choose", "ipm", or "pdlp"; ignored for MIP problems
ipm_optimality_tolerance = 1e-6 # Tolerance of IPM solver
run_crossover = off # Run IPM crossover
write_model_file = message_ix.lp # Name model LP file
write_model_to_file = 1 # Write model LP set to True
```

# References

1. [GAMS solver manuals](https://www.gams.com/49/docs/S_MAIN.html)
2. [GAMSlinks package](https://github.com/coin-or/GAMSlinks)
3. [GAMS Lincing](https://www.gams.com/49/docs/UG_License.html)
4. [Get GAMS](https://www.gams.com/latest/)