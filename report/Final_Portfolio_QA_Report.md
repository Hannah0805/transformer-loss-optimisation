# Final Portfolio QA Report

## Scope and disposition

Transformer Loss Explorer implements the approved Stage 4 v2 calculation and links to the Stage 5 report. The recruiter-facing project is prepared locally on a Git main branch. The earlier baseline notebook, sensitivity work and restricted-domain calculations are grouped under the legacy research archive in the publication copy. The owner approved GitHub publication after this local review. The licence decision and Streamlit Community Cloud deployment remain pending.

## Engineering checks

| Check | Verified local result |
| --- | --- |
| Dashboard and grid share the solver | Both use the same Stage 4 v2 candidate evaluator, including constant-power load, winding geometry, all losses and both screens. |
| Report and grid preserved | SHA-256 comparison confirmed the seven v2 numerical CSVs and approved PDF match their pre-dashboard copies. |
| Baseline and medium grid minimum | The dashboard displays 9.567 W for 600:63 turns at 12.0 cm² and 9.342 W for 475:50 at 15.0 cm². The latter predicts 22.904 V RMS and a 1.453 T no-drop peak. |
| Point-by-point parity | Live evaluation was compared with all 1,107 approved grid rows. The independent engineering audit confirmed the grid and the three minima. |
| Screen counts | 1,050 pass the no-drop flux test, 308 pass the loaded voltage test, and 251 pass both. The model includes the same low-induction cases and has no hard upper voltage criterion. |
| Interface and units | Automated tests exercised both sliders, secondary-turn calculation, all three scenarios, reset, separate and combined screening, and the displayed units for T, V RMS, W, cm² and kg. |
| Tests | 19 tests passed in the repository staging copy, including 5 dashboard tests and the 14 existing model tests. |
| Browser exercise | Chrome loaded all three pages on a local server. Tested the two live sliders, reset, four optimisation charts, matching PDF and CSV downloads, and a narrow viewport without horizontal page overflow. |
| Report and links | The browser PDF download matched the approved report bytes. Relative links and figure paths in the public-ready tree resolved locally. Public GitHub and hosted app checks remain pending. |
| Publication file hygiene | The publication tree was built from an allowlist. No local absolute personal paths or credential files were found in the staged content. Private CV drafts and working files remain outside the public package. |

The coefficients are illustrative and uncalibrated. The reported 2.35% reduction compares two predictions under the same medium coefficients. Thermal performance, practical build and measured efficiency remain unverified.

## Deployment handoff

The app entry point, Python version and dependency file are documented in [deployment instructions](../app/DEPLOYMENT.md). A future public dashboard deployment requires approval and may require an initial GitHub authorisation in the owner's session.

## Reviewer route

Start with the opening README result and optimisation figure. Open the dashboard and change a design or scenario. Use the report for modelling assumptions and the versioned CSVs and tests to inspect the calculations.
