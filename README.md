# PK/PD Antibiotic Modeling Project

A mechanistic modeling framework to explore how drug exposure, pharmacodynamic sensitivity, and biological system properties influence antibacterial efficacy under repeated dosing conditions.

---

## Overview

This project implements a mechanistic pharmacokinetic-pharmacodynamic (PK/PD) model to study antibiotic treatment dynamics.

The model is used to systematically evaluate how:
- drug exposure (dose, half-life, dosing interval)
- pharmacodynamic sensitivity (EC50)
- biological system properties (growth rate, initial burden)

influence bacterial response and treatment outcomes.

For a full description of the model framework, equations, assumptions, and simulation design, see:

➡️ [Full Model Description](docs/model_description.md)

---

## What This Project Explores

This project is structured around three key questions:

1. **How does drug exposure influence treatment efficacy?**
   - Dose-response relationships  
   - Exposure thresholds and diminishing returns  

2. **How does pharmacodynamic potency affect response?**
   - Role of EC50 in shaping exposure-response relationships  

3. **How do biological factors influence outcomes?**
   - Growth rate effects  
   - Initial bacterial burden and time to control  

---

## Model Summary

The model combines:

- One-compartment pharmacokinetics with first-order elimination  
- Logistic bacterial growth  
- Emax concentration-dependent killing  

This simplified framework is designed to isolate key drivers of treatment response while maintaining biological interpretability.

---

## Example Outputs

The model generates:

- Concentration-time profiles (PK)
- Bacterial burden trajectories (PD)
- Log₁₀ reduction curves
- Final treatment outcome metrics
- Time-to-threshold metrics

---

## Repository Structure

```text
PKPD-Antibiotic-Model/
├── README.md
├── docs/
│   └── model_description.md
├── src/
├── figures/
└── outputs/
