# Verification and Reproducibility

## Decision

The independent audit covers the assumption-based transformer loss model used in the report and dashboard. The audit reproduced the complete grid, screening and three scenario minima. No significant numerical or physical-consistency error was found within the assumed equivalent circuit. The model is internally reproducible and ready for an educational portfolio. Experimental and compliance validation remain outside the project.

## Numerical verification

| Medium scenario | Baseline | Minimum among screened candidates |
| --- | ---: | ---: |
| Primary / secondary turns | 600 / 63 | 475 / 50 |
| Effective area (cm²) | 12.0 | 15.0 |
| Primary copper (W) | 2.676278 | 2.228205 |
| Secondary copper (W) | 4.355187 | 3.474614 |
| Classical eddy (W) | 0.648752 | 0.933315 |
| Illustrative hysteresis (W) | 1.886615 | 2.706291 |
| Modelled total (W) | 9.566831 | 9.342424 |
| Terminal voltage (V RMS) | 22.563458 | 22.904334 |
| No-drop peak (T) | 1.438005 | 1.453142 |
| Loaded peak (T) | 1.402048 | 1.422510 |
| Steel mass (kg) | 1.900968 | 2.656684 |
| Bare copper mass with modelled leads (kg) | 0.265664 | 0.222795 |
| Passes both screens | Yes | Yes |

Independent recomputation uses the saved inputs and coefficient table. Full precision gives a reduction of 0.2244069 W (2.345676%). The low-scenario minimum is 7.785331 W at 450:47 turns and 15.5 cm², on the primary-turn lower boundary. The high-scenario minimum is 10.664473 W at the baseline, on an interior point. The medium point is also interior, and its next-ranked passing point is about 0.01396 W higher. All three results are discrete. [Independent audit](../src/validate_final_report.py) · [Scenario summary](../data/scenario_summary.csv)

## Review of the calculation

| Review item | Finding |
| --- | --- |
| A. Constant apparent power and voltage drop | The positive high-voltage root satisfies $V_s I_s=100$ VA and $V_s=230a-I_s(R_s+a^2R_p)$ at unity load power factor. The reflected current is $I_p=aI_s$. At the medium minimum the currents are 0.45958 A and 4.36599 A RMS. Both loaded winding drops are in phase in the adopted model. |
| B. Flux definitions | The no-drop screening peak uses 230 V RMS. Both core losses use the peak from the internal induced voltage under load. Independent checks used both $230-I_pR_p$ and $(V_s+I_sR_s)/a$. |
| C. Dimensions | Copper uses A²Ω. Hysteresis uses W·kg⁻¹·Hz⁻¹·T⁻ⁿ with dimensionless $n$. The eddy coefficient uses W·kg⁻¹·Hz⁻²·T⁻²·m⁻². These units cancel with the corresponding factors to watts. |
| D. Geometry and resistance | A core footprint calculation independent of the production volume expression matched the saved mass. The audit sums weighted winding layers analytically and reproduces both mean lengths and both resistances. Conductor area uses the bare diameter. Layer pitch uses the insulated diameter. |
| E. RMS and peak convention | Winding voltages and currents are RMS. The $\sqrt2\pi fN A_c$ conversion yields peak induction. No extra sine-wave factor is applied to the copper terms. |
| F. Shared operating point | Each row uses the same core, winding geometry and solved 100 VA condition for both windings and both core terms. The medium eddy calculation from the new coefficient is cross-checked by the equivalent laminated-steel expression, then included once in the sum. |
| G. Baseline screening | 1.438005 T ≤ 1.50 T and 22.563458 V RMS ≥ 22.0 V RMS. Only these two tests apply. |
| H. Search extent | The medium point is interior, with 25-turn and 0.5 cm² spacing. The grid minimum can shift under refinement. The low scenario reaches the lower turns boundary. |
| I. Coefficient influence | All three coefficient sets select different grid points. The high scenario selects the original baseline, demonstrating sensitivity to loss weighting. |
| J. Target voltage and ranking | The medium point happens to be closest to 24 V among the passing rows, at 22.904334 V RMS. The high-scenario minimum has 22.563458 V RMS and a larger target deviation. The objective ranks loss and the voltage screen sets a floor. |
| K. Circuit and loss accounting | Within the resistive circuit $230 I_p=100+P_{\mathrm{Cu,p}}+P_{\mathrm{Cu,s}}$. The electrical operating point does not feed core current back into the voltage drop. The objective adds the two separately estimated magnetic terms once. This approximation does not predict a measured input-power balance or efficiency. |

All 1,107 rows have complete loss estimates. Of these, 1,050 pass the flux test, 308 pass the voltage test and 251 pass both. Among the passing rows, 129 have loaded induction below 1.00 T and all remain eligible. The code case above 26.4 V confirms there is no upper voltage criterion. [Screening summary](../data/screening_summary.csv) · [Model assumptions and limitations](Methodology.md)


## Run the checks

From the project root with Python 3.13:

~~~sh
python -m pip install -r requirements.txt
python -m src.optimisation
python -m src.validate_final_report
python -m unittest discover -s tests -v
~~~

- [Model inputs](../data/model_inputs.csv) supply the dimensions, electrical inputs and material assumptions.
- [Illustrative coefficients](../data/illustrative_coefficients.csv) record the exact values for each loss scenario.
- [Complete grid](../data/all_1107_candidates.csv), [passing designs](../data/passing_candidates.csv) and [baseline comparisons](../data/baseline_vs_optimum.csv) contain the numerical results.
- The independent audit uses its own footprint calculation, winding-layer sum and load quadratic. It verifies all 1,107 designs and recomputes the scenario minima.
- The test suite checks model equations, the two screens, dashboard controls, displayed units and agreement between the live calculator and the saved grid.
- The [PDF report](Transformer_Loss_Optimisation_Report.pdf) presents the same model and findings as the dashboard.
