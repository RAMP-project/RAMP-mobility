<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/RAMP-mobility_logo_basic.png" width="300">

*RAMP-mobility: a RAMP application for generating bottom-up stochastic electric vehicles load profiles.*

---

## Overview
RAMP-mobility is an application of the **[RAMP main engine](https://github.com/RAMP-project/RAMP)**, tailored on the generation of European electric vehicles mobility and charging profiles.

This repository contains the complete RAMP-Mobility model. 

The source-code is currently released as v0.1-pre. This should be regarded as a pre-release: it is not yet accompained by a detailed documentation, but the Python code is fully commented in each line to allow a complete understanding of it. 
Further details about the conceptual and mathematical model formulation of the main engine can be found in the RAMP Journal publication (https://doi.org/10.1016/j.energy.2019.04.097). 

Please consider that a Journal publication dedicated only to RAMP-Mobility is under development. 
Also, a newer, fully commented and more user friendly version is under development and should be released soon. In the while, you can also join our **[Gitter chat](https://gitter.im/RAMP-project/community)** to discuss doubts and make questions about the code!

## Quick start

To get started, make sure that you have git and the [anaconda distribution](https://www.anaconda.com/distribution/) installed and type the following in the Anaconda Prompt:

```bash
git clone https://github.com/RAMP-project/RAMP-mobility.git
cd RAMP-mobility
conda env create  # Automatically creates environment based on environment.yml
conda activate ramp-mobility # Activate the environment
```

Then, simply run the "RAMP_run.py" script. The console will ask how many profiles (i.e. independent days) need to be simulated, and will provide the results for Italy, based on the default inputs defined in "IT.py". To change country, just select another country from the ones available in the "Input files/Europe" folder. 
Some guidance about the meaning of each input parameter is available in the "core.py" file, where the *User* and *Appliance* Python classes are defined and fully commented. 

## Model description

28 European countries are included: EU27 minus Cyprus and Malta, plus Norway, Switzerland and the UK.

Four charging strategies are implemented, to simulate different scenarios. 

1. *Uncontrolled*: The base case, where no control over the user behaviour is applied. If the charging point is available, the battery is charged immediately at the nominal power, until a user-defined value of SOC<sub>max</sub>.
2. *Perfect Foresight*: Strategy aiming at quantifying the possibility to implement a Vehicle-to-grid solution. If the charging point is available, the car is charged right before the end of the parking, at the nominal power, until the SOC satisfies the needs of the following
journey. This allows to compute the part of the vehicle's battery available to the system, without affecting the user driving range. 
3. *Night Charge*: First smart charging strategy. It aims at shifting the charging events to the night period. The car is charged only if the charging point is available and the parking happens during nighttime.
4. *RES Integration*: Second smart charging method. Has the goal of coupling the renewable power generation with the transport sector. The car is charged only if the charging point is available and the parking happens during periods when there is excess of renewable power production. As this condition is evaluated through the residual load curve, a file containing it should be provided in the folder "Input_data/Residual Load duration curve".

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

**Matija Pavičević** <br/>
KU Leuven, Belgium <br/>

**Emanuela Colombo** <br/>
Politecnico di Milano, Italy <br/>

## Citing

Please cite the original Journal publication if you use RAMP in your research:
*F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo, Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model, Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.*

Additionally, you may cite the master thesis where RAMP-Mobility was developed:
*A. Mangipinto, Development of electric vehicles load profiles for sector coupling in European energy system models, Master Thesis, Politecnico di Milano, 2020.*

## Contribute
This project is open-source. Interested users are therefore invited to test, comment or contribute to the tool. Submitting issues is the best way to get in touch with the development team, which will address your comment, question, or development request in the best possible way. We are also looking for contributors to the main code, willing to contibute to its capabilities, computational-efficiency, formulation, etc. 

## License

Copyright 2020 RAMP-Mobility, contributors listed in **Authors**

Licensed under the European Union Public Licence (EUPL), Version 1.1; you may not use this file except in compliance with the License. 

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License
