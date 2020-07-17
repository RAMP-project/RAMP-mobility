*RAMP-mobility: An open-source bottom-up stochastic model for generating electric vehicles load profiles.*

---

## Overview
RAMP-mobility is a new version of the RAMP model for the generation of European electric vehicles mobility and charging profiles.

[TO DO: IMPROVE RELEASE STATUS AND REFER TO THESIS FOR FULL DOCUMENTATION.]

The source-code is currently released as v.0.2.1-pre. This should be regarded as a pre-release: it is not yeat accompained by a detailed documentation, but the Python code is fully commented in each line to allow a complete understanding of it. Further details about the conceptual and mathematical model formulation are provided in the related Journal publication (https://doi.org/10.1016/j.energy.2019.04.097). 

Please consider that a newer, fully commented and more user friendly version is under development and should be released soon.

## Quick start

[TO DO: CHECK THAT THE ENVIRONMENT CREATION WORKS]

If you want to download the latest version from github for use or development purposes, make sure that you have git and the [anaconda distribution](https://www.anaconda.com/distribution/) installed and type the following:

```bash
git clone https://github.com/RAMP-project/RAMP-mobility.git
cd RAMP-mobility
conda env create  # Automatically creates environment based on environment.yml
conda activate ramp-mobility # Activate the environment
```
[TO DO: SET DEFAULT INPUT FILES]

To get started, simply run the "RAMP_run.py" script. The console will ask how many profiles (i.e. independent days) need to be simulated, and will provide the results based on the default inputs defined in "input_file_1.py" and "input_file_2". To change the inputs, just modify the latter files. Some guidance about the meaning of each input parameter is available in the "core.py" file, where the *User* and *Appliance* Python classes are defined and fully commented. 

## Authors
The model has been developed by:

**Andrea Mangipinto** <br/>
Politecnico di Milano, Italy <br/>
E-mail: andrea.mangipinto@gmail.com<br/>

**Francesco Lombardi** <br/>
Politecnico di Milano, Italy <br/>
E-mail: francesco.lombardi@polimi.it <br/>

**Francesco Sanvito** <br/>
Politecnico di Milano, Italy <br/>

**Sylvain Quoilin** <br/>
KU Leuven, Belgium <br/>

**Emanuela Colombo** <br/>
Politecnico di Milano, Italy <br/>

## Citing
[TO DO: Insert thesis as starting reference. Then when available the paper.]

Please cite the original Journal publication if you use RAMP in your research:
*F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo, Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model, Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.*

## Contribute
This project is open-source. Interested users are therefore invited to test, comment or contribute to the tool. Submitting issues is the best way to get in touch with the development team, which will address your comment, question, or development request in the best possible way. We are also looking for contributors to the main code, willing to contibute to its capabilities, computational-efficiency, formulation, etc. 

## License
[TO DO: Fix licence]

Copyright 2019 RAMP, contributors listed in **Authors**

Licensed under the European Union Public Licence (EUPL), Version 1.1; you may not use this file except in compliance with the License. 

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License
