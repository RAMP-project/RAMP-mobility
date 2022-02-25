<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/RAMP-mobility_logo.png" width="300">

*RAMP-mobility: a RAMP application for generating bottom-up stochastic electric vehicles load profiles.*

---

## Overview
RAMP-mobility is an original application of the open-source **[RAMP software engine](https://github.com/RAMP-project/RAMP)**, tailored to the generation of European electric vehicles mobility and charging profiles at high temporal resolution (1-min).

This repository contains the complete RAMP-Mobility model, entirely developed in Python 3.7. The model is currently released as v0.3.1. It includes a minimum 'quick-start' documentation (see below), complemented by the code being fully commented in each line to allow a complete understanding of it. 

Further details about the conceptual and mathematical model formulation of the RAMP software engine can be found in the original [RAMP](https://doi.org/10.1016/j.energy.2019.04.097) and in the specific [RAMP-mobility](https://doi.org/10.1016/j.apenergy.2022.118676) publications. What is more, you are welcome to join our **[Gitter chat](https://gitter.im/RAMP-project/community)** to discuss doubts and make questions about the code!

<p align="center">
<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/example_profiles.jpg" width="1200">
</p>

## Quick start

Please refer to the complete **[getting started](https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/getting_started.md)** guide for instructions on how to run RAMP-Mobility. This includes information about installation and Python dependencies, as well as a minimum walkthrough of model structure and usage.

## Model description

RAMP-mobility covers 28 European countries, namely: EU27 minus Cyprus and Malta, plus Norway, Switzerland and the UK. 
The model consists of 2 main modules:

**Module 1:** bottom-up stochastic simulation of electric vehicle mobility profiles

<p align="center">
<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/module_1.png" width="600">
</p>

**Module 2:** simulation, for each electric vehicle, of a charging profile based on the previously obtained mobility pattern

Four pre-defined charging strategies are implemented, to simulate different plausible scenarios: 

1. *Uncontrolled*: The base case, where no control over the user behaviour is applied. If the charging point is available, the battery is charged immediately at the nominal power, until a user-defined value of SOC<sub>max</sub>.
2. *Perfect Foresight*: Strategy aiming at quantifying the possibility to implement a Vehicle-to-grid solution. If the charging point is available, the car is charged right before the end of the parking, at the nominal power, until the SOC satisfies the needs of the following
journey. This allows to compute the part of the vehicle's battery available to the system, without affecting the user driving range. 
3. *Night Charge*: First smart charging strategy. It aims at shifting the charging events to the night period. The car is charged only if the charging point is available and the parking happens during nighttime.
4. *RES Integration*: Second smart charging method. Has the goal of coupling the renewable power generation with the transport sector. The car is charged only if the charging point is available and the parking happens during periods when there is excess of renewable power production. As this condition is evaluated through the residual load curve, a file containing it should be provided in the folder "Input_data/Residual Load duration curve".

<p align="center">
<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/docs/module_2.png" width="600">
</p>

## Authors
The model has been developed by:

**Andrea Mangipinto** <br/>
Politecnico di Milano, Italy <br/>

**Francesco Lombardi** <br/>
TU Delft, Netherlands <br/>
<img src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2F1000logos.net%2Fwp-content%2Fuploads%2F2017%2F06%2FTwitter-Logo.png&f=1&nofb=1" width="20"/> [@FrLomb](https://twitter.com/FrLomb)
(Correspondence should be sent to: f.lombardi@tudelft.nl) <br/>

**Francesco Sanvito** <br/>
Politecnico di Milano, Italy <br/>
<img src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2F1000logos.net%2Fwp-content%2Fuploads%2F2017%2F06%2FTwitter-Logo.png&f=1&nofb=1" width="20"/> [@FrancescoSanvi2](https://twitter.com/FrancescoSanvi2)

**Sylvain Quoilin** <br/>
KU Leuven, Belgium <br/>

**Matija Pavičević** <br/>
KU Leuven, Belgium <br/>

**Emanuela Colombo** <br/>
Politecnico di Milano, Italy <br/>

## Citing

Please cite the related Journal publicaton if you use RAMP-mobility in your research:
*A. Mangipinto, F. Lombardi, F. Sanvito, M. Pavičević, S. Quoilin, E. Colombo, Impact of mass-scale deployment of electric vehicles and benefits of smart charging across all European countries, Applied Enery, 2022, https://doi.org/10.1016/j.apenergy.2022.118676. *

Additionally, you may cite the EMP-E presentation of RAMP-mobility:
*A. Mangipinto, F. Lombardi, F. Sanvito, S. Quoilin, M. Pavičević, E. Colombo, RAMP-mobility: time series of electric vehicle consumption and charging strategies for all European countries, EMP-E, 2020, https://doi.org/10.13140/RG.2.2.29560.26880*

Or the publication of the original RAMP software engine:
*F. Lombardi, S. Balderrama, S. Quoilin, E. Colombo, Generating high-resolution multi-energy load profiles for remote areas with an open-source stochastic model, Energy, 2019, https://doi.org/10.1016/j.energy.2019.04.097.*

## Contribute
This project is open-source. Interested users are therefore invited to test, comment or contribute to the tool. Submitting issues is the best way to get in touch with the development team, which will address your comment, question, or development request in the best possible way. We are also looking for contributors to the main code, willing to contibute to its capabilities, computational-efficiency, formulation, etc. 

## License

Copyright 2020 RAMP-Mobility, contributors listed in **Authors**

Licensed under the European Union Public Licence (EUPL), Version 1.2-or-later; you may not use this file except in compliance with the License. 

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License
