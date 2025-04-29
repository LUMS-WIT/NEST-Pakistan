# Running the MESSAGEix-Canada Model

This section provides a structured guide for running **MESSAGEix-Canada** and reproducing the existing results without making modifications. The model can be executed using either **command-line execution** or **Jupyter Notebook**, depending on the preferred workflow.

## **1. Running the Model via Command Line**

The simplest way to run **MESSAGEix-Canada** is through the command line. This method ensures that predefined scenarios are executed as intended. Each scenario is stored in a dedicated folder containing input data and a `config.toml` file that specifies scenario parameters.

### **Steps to Run the Model Using Command Line**

1. **Ensure the correct environment is activated:**
   ```bash
   conda activate messageix-canada
   ```

2. **Navigate to the model directory:**
   ```bash
   cd message-ix
   ```

3. **Execute the model run script with the desired scenario:**
   ```bash
   python MESSAGE_CA.py --scenario baseline
   ```
   This will run the **baseline** scenario as defined in the yaml file. A sample of the yaml file with options is mentioned below:

```yaml
{% include "ModelSetup_CA.yaml" %}
```

4. **Monitor the process:**
   The script will load the necessary input files, execute the model, and generate output files in the `output/` directory.

## **2. Running the Model in a Jupyter Notebook**

For users who prefer interactive execution, the model can also be run using a Jupyter Notebook. This approach is ideal for adjusting parameters, visualizing data, and performing exploratory analysis.

### **Steps to Run the Model Using Jupyter Notebook**

1. **Ensure Jupyter Notebook is installed and launch it:**
   ```bash
   jupyter notebook
   ```

2. **Navigate to the development notebook:**
   Open `model/notebooks/development.ipynb` and execute the provided cells step by step.

3. **Initialize the scenario:**
   Within the notebook, the model can be configured using:
   ```python
   from message_ix import Scenario
   scenario = Scenario(platform, model, scenario_name)
   scenario.solve()
   ```

4. **Analyze results:**
   Once the model has run successfully, output files and processed results can be examined interactively.

## **3. Configuring Scenario Input Files**

Each scenario has a corresponding YAML configuration file specifying model parameters, input paths, and solver options. The **baseline scenario**, for instance, is configured in:

```
model/scenarios/baseline/model_setup_ca.yaml
```

Within this file, users can set key parameters such as:

```yaml
solve: true
legacy: true
```

To explore different scenario options, users can modify the YAML file accordingly before executing the model.

## **Summary**

- **For automated execution**, use the command-line interface to reproduce existing results efficiently.
- **For interactive exploration and customization**, use Jupyter Notebook.
- **Scenario configurations** can be modified via