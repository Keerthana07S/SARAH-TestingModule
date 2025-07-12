# System Analysis and Reporting for Advanced Hardware (SARAH)

SARAH is an algorithm capable of detecting, classifying, and locating faults on 200 node systems within 11-40 seconds. What makes SARAH more effective than other reliability assessment options—particularly in the area of fault localization—is its non-heuristic nature. This characteristic allows it to solve optimization problems, which current reliability assessment methodologies can’t. S.A.R.A.H. also runs on pure mathematics, which allows for all outputs to be analyzed, traced, and corrected (if necessary). This sets SARAH apart from AI/ML models (e.g., PCANNs, which have been developed for fault localization), as the exact methodology for AI/ML models are more ambiguous. 

## FAQ
1. **Why is SARAH better than an AI/ML model for reliability assessment?**

SARAH is less ambiguous and does not have the same “black box” that AI/ML models have. This means that SARAH, while autonomous, is more trustworthy. After speaking to several electronics engineers about AI/ML solutions that have been on the market for decades, adopting these solutions is challenging due to the risk of ambiguity. Many in the electrical engineering space would prefer to do things manually than trust a hard-to-understand method with large volumes of data.

2. **Won’t SARAH consume a lot of energy, because quantum is involved?**

SARAH leverages Quantum Markov Chain Monte Carlo (QMCMC), which is very different compared to most quantum algorithms. QMCMC works by randomly sampling from a Boltzmann (AKA probability) distribution—in this case, the probability of a fault occurring on a specific node—to get a decent estimate of what the entire Boltzmann distribution looks like. The amount of energy used to traverse the Boltzmann distribution is defined by the temperature (T). If we use low temperatures, and only traverse the valleys of the distribution, it is feasible to reach convergence while spending the same amount of energy that we would classically. In fact, QMCMCs are one of the first quantum algorithms that are feasible to run on a quantum processor. Moreover, the bifurcation aspect of SARAH is the only part running continuously, while EKF and QMCMC are only in the picture once instability is detected. Thus, the QMCMC would only consume energy for 11-40 seconds whenever a fault occurs. 

## Repository Guide
The bifurcation and EKF components of SARAH are programmed in two languages: Python and Julia. For the QMCMC, it is recommended to use the Python version of this code, as it is derived from preexisting research from Dr. David Layden and has greater accruacy. 
Meanwhile, the C++ programs are used to construct a photovoltaic emulator, which is capable of simulating a photovoltaic module. There are a variety of ways to approach the photovoltaic emulator program, which is why multiple options are provided in this repository. Furthermore, a program for analyzing radiation levels using a Varadis RADFET is provided if the emulator is being tested at multiple altitudes. 
