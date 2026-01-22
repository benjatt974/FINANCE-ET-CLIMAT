# FINANCE-ET-CLIMAT

# Climate Credit Stress Test – Prudential Banking Perspective

This project implements a simplified climate stress test from the perspective
of a European bank, inspired by the climate stress testing exercises conducted
by the European Central Bank (ECB) and the Autorité de contrôle prudentiel et de
résolution (ACPR).

## Objective

The objective is to assess how climate change can affect bank credit risk by
impacting the solvency of non-financial corporate borrowers. The analysis focuses
on projected credit losses under different climate scenarios.

## Scope

- European banking framework (ECB supervision)
- Credit risk only (PD, LGD, EAD)
- Corporate loan portfolio
- Climate scenarios inspired by the NGFS

## Methodology

1. Construction of a fictitious but realistic banking loan portfolio
2. Application of climate scenarios (orderly transition, disorderly transition,
   hot house world)
3. Stressing of credit risk parameters (PD and LGD) by sector
4. Computation of:
   - stressed probabilities of default,
   - projected credit losses,
   - Climate Value at Risk (Climate VaR)

## Data

All data used in this project are simulated for pedagogical purposes.
Key variables include:
- Exposure at Default (EAD)
- Probability of Default (PD)
- Loss Given Default (LGD)

## Repository structure
# Climate Credit Stress Test – Prudential Banking Perspective

This project implements a simplified climate stress test from the perspective
of a European bank, inspired by the climate stress testing exercises conducted
by the European Central Bank (ECB) and the Autorité de contrôle prudentiel et de
résolution (ACPR).

## Objective

The objective is to assess how climate change can affect bank credit risk by
impacting the solvency of non-financial corporate borrowers. The analysis focuses
on projected credit losses under different climate scenarios.

## Scope

- European banking framework (ECB supervision)
- Credit risk only (PD, LGD, EAD)
- Corporate loan portfolio
- Climate scenarios inspired by the NGFS

## Methodology

1. Construction of a fictitious but realistic banking loan portfolio
2. Application of climate scenarios (orderly transition, disorderly transition,
   hot house world)
3. Stressing of credit risk parameters (PD and LGD) by sector
4. Computation of:
   - stressed probabilities of default,
   - projected credit losses,
   - Climate Value at Risk (Climate VaR)

## Data

All data used in this project are simulated for pedagogical purposes.
Key variables include:
- Exposure at Default (EAD)
- Probability of Default (PD)
- Loss Given Default (LGD)

## Repository structure
climate-credit-stress-test/
│
├── data/
│ └── portfolio_climat.xlsx
│
├── src/
│ └── climate_stress_test.py
│
├── outputs/
│ └── (generated results)
│
├── README.md
├── requirements.txt
└── .gitignore

## How to run

bash
python src/climate_stress_test.py --input data/portfolio_climat.xlsx --alpha 0.95

Disclaimer
This project is for academic purposes only. The models and assumptions used are
simplified and do not reflect the full complexity of regulatory climate stress
testing frameworks.

