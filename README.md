# NEST Pakistan

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![MESSAGEix version](https://img.shields.io/pypi/v/message_ix.svg)](https://pypi.python.org/pypi/message_ix/)
[![Anaconda version](https://img.shields.io/conda/vn/conda-forge/message-ix)](https://anaconda.org/conda-forge/message-ix)
[![Documentation build](https://readthedocs.com/projects/iiasa-energy-program-message-ix/badge/?version=stable)](https://docs.messageix.org/en/stable/)

Climate Policy Assessment and Mitigation Modeling to Integrate national and global TransiTion pathways for Environmental-friendly Development


## Objectives
The overall objective of this project is: to reinforce global climate change mitigation efforts by supporting the work of Asian researchers and experts on national and sectoral greenhouse gas emissions modeling. This is done by strengthening capacity building for GHG emissions modeling and exchanging best practices and know-how between leading EU and Asian modelers working closely with the government.

## Table of contents

- [Prerequisite](https://github.com/LUMS-WIT/NEST-Pakistan/blob/dev-pak/README.md#prerequisite)
- [Installation Steps](https://github.com/LUMS-WIT/NEST-Pakistan/blob/dev-pak/README.md#installation-steps)
- [Clone or Run Next-Pakistan model](https://github.com/LUMS-WIT/NEST-Pakistan/blob/dev-pak/README.md#next-step-clone-or-run-next-pakistan-model)
- [Copyright and license](https://github.com/LUMS-WIT/NEST-Pakistan/blob/dev-pak/README.md#license)

## Prerequisite

#### 1: Bash/CMD
Basic Understanding of <a href="https://www.tutorialspoint.com/unix/shell_scripting.htm">bash commands</a> or Windows command line interface.

#### 2: Git/GitHub
Make sure to have an account on <a href="https://github.com/"> GitHub </a> and <a href="https://git-scm.com/downloads"> GIT </a> is properly installed on your system. It will help to push/pull the latest code or contribute within the team.

#### 3: Python
Messageix framework is build on <a href= "https://www.python.org/downloads/">python programming langauge </a>. It is required to develop model and writing python scripts.

#### 4: Anaconda/Miniconda
Anaconda software provides different code editiors and help to create an environment for different versions of packages. <a href= "https://docs.anaconda.com/free/anaconda/install/windows/"> Anaconda CMD</a> is used to install, remove, and upgrade packages in your project environments.

#### 5: VS Code
There are so many code editors to run python code but here we suggest to utilize <a href= "https://www.python.org/downloads/">VS CODE</a> becasue it's help to manage your enviornments and version controlling using github.

## Installation Steps
<b>Step1: Open Ananconda/minconda command line prompt from the start manu and create a virtual environment</b>


```
conda create -n envname 
conda activate envname 
```

<b>Step2: Configure conda to install message_ix from the conda-forge channel and Install the ixmp package into the current environment </b>


```
conda config --prepend channels conda-forge
conda install -c conda-forge ixmp 
```

<b>Step3: Install all other required packages including MESSAGEix</b>
```
pip -r requirement.txt 
```

## Next Step: Clone or Run Next-Pakistan model
<b>Step1: clone repository from below command and change path to move into your project directory</b>


```
gh repo clone LUMS-WIT/NEST-Pakistan
cd committed
```

<b>Step2: Into the current environment type below command to Open Jupyter notbook</b>
```
jupyter notebook
```

<b><i>On the top nav-bar of the notebook you will find run all cell option, simply click on it and wait untill execuation complete and you will find your desire result in /output folder</i></b>


## License
Copyright 2023 WIT LUMS

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
