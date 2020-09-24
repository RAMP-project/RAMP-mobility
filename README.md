<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/RAMP-mobility_logo.png" width="300">

*RAMP-mobility: a RAMP application for generating bottom-up stochastic electric vehicles load profiles.*

---

## Overview
RAMP-mobility is an application of the **[RAMP main engine](https://github.com/RAMP-project/RAMP)**, tailored on the generation of European electric vehicles mobility and charging profiles.

This repository contains the complete RAMP-Mobility model, entirely developed in Python 3.6. The model is currently released as v0.2-pre, which should be regarded as a pre-release. As such, it includes a minimum 'quick-start' documentation (see below), complemented by the code being fully commented in each line to allow a complete understanding of it. A more thorougly documented version of the repository is under development and should be released soon, alongside a Journal publication.

In the while, further details about the conceptual and mathematical model formulation of the RAMP software engine can be found in the original RAMP Journal publication (https://doi.org/10.1016/j.energy.2019.04.097). What is more, you are welcome to join our **[Gitter chat](https://gitter.im/RAMP-project/community)** to discuss doubts and make questions about the code!

<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/example_profiles.jpg" width="1200">


## Quick start

Please refer to the complete **[getting started](https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/getting_started.md)** guide for instructions on how to run RAMP-Mobility. This includes information about installation and Python dependencies, as well as a minimum walkthrough of model structure and usage.

## Model description

RAMP-mobility consits of 2 main modules:

**Module 1:** bottom-up stochastic simulation of electric vehicle mobility profiles

<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/module_1.png" width="600">


**Module 2:** simulation, for each electric vehicle, of a charging profile based on the previously obtained mobility pattern

<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/module_2.png" width="600">

28 European countries are included: EU27 minus Cyprus and Malta, plus Norway, Switzerland and the UK.

Four pre-defined charging strategies are implemented, to simulate different plausible scenarios: 

1. *Uncontrolled*: The base case, where no control over the user behaviour is applied. If the charging point is available, the battery is charged immediately at the nominal power, until a user-defined value of SOC<sub>max</sub>.
2. *Perfect Foresight*: Strategy aiming at quantifying the possibility to implement a Vehicle-to-grid solution. If the charging point is available, the car is charged right before the end of the parking, at the nominal power, until the SOC satisfies the needs of the following
journey. This allows to compute the part of the vehicle's battery available to the system, without affecting the user driving range. 
3. *Night Charge*: First smart charging strategy. It aims at shifting the charging events to the night period. The car is charged only if the charging point is available and the parking happens during nighttime.
4. *RES Integration*: Second smart charging method. Has the goal of coupling the renewable power generation with the transport sector. The car is charged only if the charging point is available and the parking happens during periods when there is excess of renewable power production. As this condition is evaluated through the residual load curve, a file containing it should be provided in the folder "Input_data/Residual Load duration curve".

## Authors
The model has been developed by:

**Andrea Mangipinto** <br/>
Politecnico di Milano, Italy <br/>

**Francesco Lombardi** <br/>
Politecnico di Milano, Italy <br/>
(Correspondence should be sent to: francesco.lombardi@polimi.it <br/>)

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

Additionally, you may cite the EMP-E presentation of RAMP-mobility:
*A. Mangipinto, F. Lombardi, F. Sanvito, S. Quoilin, M. Pavičević, E. Colombo, RAMP-mobility: time series of electric vehicle consumption and charging strategies for all European countries, Master Thesis, EMP-E, 2020.*

## Contribute
This project is open-source. Interested users are therefore invited to test, comment or contribute to the tool. Submitting issues is the best way to get in touch with the development team, which will address your comment, question, or development request in the best possible way. We are also looking for contributors to the main code, willing to contibute to its capabilities, computational-efficiency, formulation, etc. 

## License

Copyright 2020 RAMP-Mobility, contributors listed in **Authors**

Licensed under the European Union Public Licence (EUPL), Version 1.1; you may not use this file except in compliance with the License. 

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License
