# PK/PD Model Description

## Study Objective

This project implements a mechanistic pharmacokinetic-pharmacodynamic (PK/PD) model to evaluate how antibiotic exposure, pharmacodynamic sensitivity, and biological system properties influence antibacterial efficacy under repeated dosing conditions.

The model is designed to identify key drivers of bacterial killing dynamics and to assess when simplified assumptions are sufficient versus when additional complexity may be required.

## Key Questions

This study focuses on three main components:

### 1. Drug Exposure
- How do dose, half-life, and dosing interval influence treatment response?
- Are there exposure thresholds or diminishing returns?

### 2. Pharmacodynamic Sensitivity
- How does EC50 shift exposure-response relationships?

### 3. Biological System Properties
- How do growth rate and initial bacterial burden affect treatment outcomes?

# Model Framework

### Pharmacokinetics (PK)

Drug concentration is modeled using a one-compartment system with first-order elimination:

$\frac{dC}{dt} = -k*C$

$k = \frac{\ln(2)}{t_{1/2}}$

Dosing is implemented as instantaneous bolus inputs at fixed intervals.

### Pharmacodynamics (PD)

Bacterial dynamics follow logistic growth with drug-mediated killing:

$Growth = r * B * (1-\frac{B}{B_{max}})$

$Kill(C) = \frac{E_{max} * C}{EC_{50} + C}$

$\frac{dB}{dt} = r * B * (1-\frac{B}{B_{max}}) - B*\frac{E_{max} * C}{EC_{50} + C}$

## Model Assumptions

- Homogeneous, well-mixed system
- No spatial structure
- No immune response
- No bacterial heterogeneity
- No biofilm-specific effects

This simplified framework is intended to isolate core PK/PD relationships and identify dominant drivers of system behavior.

## Key Parameters

### Pharmacokinetics
- Dose (mg)
- Dosing interval (hours)
- Half-life (hours)
- Volume of distribution (L)

### Pharmacodynamics
- Emax: maximum kill rate
- EC50: concentration for half-maximal effect

### Biological System
- r: bacterial growth rate
- Bmax: carrying capacity
- B0: initial bacterial burden

## Baseline Parameters

| Parameter       | Meaning                              | Baseline Value     | Basis for Choice                                   |
|----------------|--------------------------------------|--------------------|---------------------------------------------------|
| half_life      | Drug half-life                       | 6 hours            | Exploratory baseline                              |
| V              | Apparent volume of distribution      | 1 L                | Model simplification                              |
| r              | Bacterial growth rate                | 0.8 h⁻¹            | Chosen to produce plausible untreated growth      |
| Bmax           | Carrying capacity                    | 1 × 10⁹ CFU/mL     | Logistic growth upper bound                       |
| Emax           | Maximum kill rate                    | 1.0 h⁻¹            | Literature-informed baseline                      |
| EC50           | Half-maximal kill concentration      | 0.5 mg/L           | Literature-informed baseline                      |
| B0             | Initial bacterial burden             | 1 × 10⁶ CFU/mL     | Representative inoculum                           |
| dose_mg        | Dose per administration              | 10 mg              | Baseline exposure level                           |
| dose_interval  | Dosing interval                      | 12 hours           | Representative dosing schedule                    |
| n_doses        | Number of doses                      | 10                 | Consistent with total simulation duration         |
| t_end          | Total simulation duration            | 120 hours          | Defines treatment time window                     |

## Simulation Design

Parameter sweeps were performed to evaluate system sensitivity.

### Exposure Parameters
- Dose: 0.5–20 mg
- Half-life: 2–24 hours
- Dosing interval: 6–24 hours

### Pharmacodynamic Sensitivity
- EC50: 0.25–2 mg/L

### Biological Properties
- Growth rate (r): 0.2–1.2 hr⁻¹
- Initial burden: 1e4–1e8 CFU/mL

Each parameter was varied independently while holding others constant.
