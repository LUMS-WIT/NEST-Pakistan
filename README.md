# NEST Pakistan

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://img.shields.io/pypi/v/message_ix.svg)](https://pypi.python.org/pypi/message_ix/)
[![Anaconda version](https://img.shields.io/conda/vn/conda-forge/message-ix)](https://anaconda.org/conda-forge/message-ix)
[![Documentation build](https://readthedocs.com/projects/iiasa-energy-program-message-ix/badge/?version=stable)](https://docs.messageix.org/en/stable/)

Climate Policy assessment and Mitigation Modeling to Integrate national and global TransiTion pathways for Environmental-friendly Development


## Objectives
The overall objective of this project is: to reinforce global climate change mitigation efforts by supporting the work of Asian researchers and experts on national and sectoral greenhouse gas emissions modelling. This is done by strengthening capacity building for GHG emissions modelling and exchanging best practices and know-how between leading EU and Asian modellers working closely with the government

## Documentation

<h2>Installation Steps</h2><br>
<b>Step1: Open Ananconda/minconda cmd and create a virtual environment</b>



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

<h2>Clone or Run Next-Pakistan model</h2><br>
<b>Step1: clone repository from below command and change path to move into your project directory</b>



```
git@github.com:LUMS-WIT/NEST-Pakistan.git
cd committed
```

<b>Step2: Into the current environment type below command to Open Jupyter notbook</b>
```
jupyter notebook
```

<b><i>On the top nav-bar of the notebook you will find run all cell option, simply click on it and wait untill execuation complete and you will find your desire result in /output folder</i></b>

## License
Copyright 2023 WIT Lums

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
