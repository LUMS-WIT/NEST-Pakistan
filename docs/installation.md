# Installation Instructions

This section provides a detailed guide to installing and setting up **MESSAGEix-Canada** on your local machine. The setup process involves configuring a **Python environment**, installing necessary dependencies, and ensuring that all required external tools are properly installed.

## **Prerequisites**

Before proceeding with the installation, ensure you have the following dependencies installed on your system:

- **[Miniconda or Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)** – Required for managing Python environments.
- **[Git](https://git-scm.com/downloads)** – Needed to clone the MESSAGEix-Canada repository.
- **[GAMS](https://www.gams.com/download/)** – Required for running MESSAGEix models.

> Note: if your GAMS license [does not include CPLEX](https://www.gams.com/49/docs/UG_License.html?search=licenses#No_License_for_a_particular_Solver_found) you will need to use an open-source solver instead. Refer to the [solvers section](docs/solvers.md) of this documentation to understand how to update your solver of choice.

## **Setting Up MESSAGEix-Canada**

### **1. Clone the Repository**

Start by cloning the MESSAGEix-Canada repository from GitLab and navigating to the project directory:

```bash
git clone https://gitlab.com/sesit/message-ix
cd message-ix
```

### **2. Configure the Conda Environment**

Create a new isolated **Anaconda** environment to ensure all dependencies work correctly:

```bash
conda create -n messageix-canada python=3.12
```

### **3. Activate the Environment**

Once created, activate the environment:

```bash
conda activate messageix-canada
```

### **4. Install Required Packages**

Install the necessary Python dependencies:

```bash
pip install -e .
```

### **5. Verify the Installation**

To confirm that MESSAGEix-Canada is correctly installed, execute the following command:

```bash
message-ix show-versions
```

If the command runs successfully, your setup is complete.

For further troubleshooting or known installation issues, refer to the **official installation guide** in the [MESSAGEix documentation](https://docs.messageix.org/en/latest/install.html).
