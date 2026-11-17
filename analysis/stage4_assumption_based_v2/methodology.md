# Stage 4, Version 2 · Assumption-Based Core Loss Optimisation

> Core-loss coefficients were selected as illustrative modelling assumptions and were not independently calibrated against measured transformer data. The optimisation results are therefore conditional on the selected coefficients, geometry, electrical assumptions and screening constraints.

## Model and coefficient selection

This version uses the tested Stage 2 copper, E–I core geometry and resistive circuit. The 230 V RMS source, 50 Hz frequency, 24 V target, 100 VA constant-output solution at unity power factor, wire sizes, copper resistivity, 60 °C winding assumption and winding layout are carried forward. The secondary turns are the nearest integer to \(N_p(24/230)\), and the corresponding ideal secondary voltage is recorded. The original numerical density of 7690 kg/m³ and 0.35 mm lamination thickness are retained as generic geometry assumptions to preserve the core-mass and sheet-gauge calculations. No manufacturer loss coefficients, total-loss anchors, steel conductivity or hysteresis coverage bounds enter the new objective.

The primary RMS induced voltage is \(E_p=230-I_pR_p\) in the existing resistive circuit, with \(V_{\mathrm{load}} I_s=100\) VA solved on the high-voltage branch. The loaded peak is \(B_{\mathrm{pk}}=E_p/(\sqrt{2}\pi fN_p A_c)\). The corresponding no-drop peak substitutes 230 V RMS for \(E_p\) and is used only for the flux screen and diagnostic comparison. For each candidate, the total is the unchanged two winding \(I^2R\) powers plus

\[
P_h=k_hm_cfB_{\mathrm{pk}}^n,\qquad
P_e=k_em_cf^2B_{\mathrm{pk}}^2t^2.
\]

Here \(m_c\) is steel mass in kg, \(t\) is the steel thickness in m, \(f\) is in Hz, and \(B_{\mathrm{pk}}\) is loaded peak induction in T. The positive, dimensionless \(n\) sets the slope of the assumed hysteresis energy per cycle versus induction. The product \(k_hB_{\mathrm{pk}}^n\) is the assumed specific hysteresis energy in J/kg per cycle. The eddy coefficient \(k_e\) is the classical thin-sheet scale factor per unit mass, with \(t^2\) explicit. The resulting powers are in watts.

All scenarios share the same illustrative reference conditions of **50 Hz, 1.20 T sinusoidal loaded peak and 0.35 mm laminations**. Set reference hysteresis and eddy specific powers first, then derive

\[
k_h=\frac{p_{h,\mathrm{ref}}}{f_{\mathrm{ref}}B_{\mathrm{ref}}^n},
\qquad
k_e=\frac{p_{e,\mathrm{ref}}}{f_{\mathrm{ref}}^2B_{\mathrm{ref}}^2t_{\mathrm{ref}}^2}.
\]

| Scenario | Reference \(p_h\) (W/kg) | Reference \(p_e\) (W/kg) | \(n\) | \(k_h\) (W·kg⁻¹·Hz⁻¹·T⁻ⁿ) | \(k_e\) (W·kg⁻¹·Hz⁻²·T⁻²·m⁻²) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Low | 0.45 | 0.15 | 1.6 | 0.006722836 | 340.1361 |
| Medium | 0.75 | 0.25 | 1.8 | 0.010803513 | 566.8934 |
| High | 1.05 | 0.35 | 2.0 | 0.014583333 | 793.6508 |

The medium reference assigns 1 W/kg of core loss, divided three to one between hysteresis and classical eddy current. At the existing 1.90 kg baseline core mass this would give about 1.9 W of core loss at the reference induction, a deliberately modest scale for a 100 VA educational case. The reference powers vary by −40% and +40%, while the exponent varies by −0.2 and +0.2. A classical plausibility check maps the selected \(k_e\) values to an implied positive electrical resistivity using \(\rho_{\mathrm{el}}=\pi^2/(6\rho_m k_e)\). The implied values range from \(2.70\times10^{-7}\) to \(6.29\times10^{-7}\) Ω·m, on the sub-micro-ohm-metre scale of resistive metallic sheet. The driver uses the medium implied value solely to reproduce and cross-check the Stage 2 classical equation. It is derived from the new assumption. The three reference splits and exponent choices were selected before running the grid, and they are sensitivity cases without a preferred empirical ranking. [Full-precision coefficient table](data/illustrative_coefficients.csv) · [Input manifest](data/model_inputs.csv)

## Screening and coverage

The requested grid contains 27 primary-turn values from 450 to 1100 in steps of 25 and 41 areas from 10 to 30 cm² in steps of 0.5 cm². Two inclusive tests determine eligibility: the nominal no-drop peak is at most **1.50 T** and the 100 VA terminal voltage is at least **22.0 V RMS**. Voltage deviation from 24 V, winding fill and build, current density, mass and ideal ratio are diagnostic. No upper terminal-voltage limit applies.

All **1,107** rows have finite values for all three scenarios. **1,050** pass the flux test and **308** pass the voltage test separately. **251** pass both, including **129** with loaded peak induction below the previous 1.00 T cutoff. Compared with the prior 21.6–26.4 V interval, the new floor reduces the number passing both from 415 to 251 on the same electrical and geometry grid. Every one of the new passing points is included in the ranking.

The mathematical expressions evaluate at any positive loaded peak. Across the full grid the loaded peaks range from 0.2881 to 2.2624 T. Results below 1.00 T and above 1.50 T are flagged as diagnostics. A single hysteresis power law may fail to describe low-amplitude loops or high-induction behaviour. Large peaks also challenge the sinusoidal, uniformly linked flux and unsaturated equivalent-circuit assumptions. Rows beyond the flux screen keep their mathematical loss outputs for transparency. The boundary flags are not empirical validity certificates.

## Results

### Medium scenario, common assumptions for both designs

| Quantity | Recalculated baseline | Screened minimum |
| --- | ---: | ---: |
| Primary : secondary turns | 600 : 63 | **475 : 50** |
| Effective steel area (cm²) | 12.0 | **15.0** |
| Nominal no-drop peak (T) | 1.43801 | 1.45314 |
| Loaded peak (T) | 1.40205 | 1.42251 |
| Ideal secondary voltage (V RMS) | 24.150 | 24.211 |
| Loaded terminal voltage (V RMS) | 22.563 | **22.904** |
| Deviation from 24 V (V / %) | −1.437 / −5.99% | −1.096 / −4.57% |
| Primary copper loss (W) | 2.676 | **2.228** |
| Secondary copper loss (W) | 4.355 | **3.475** |
| Classical eddy current loss (W) | 0.649 | **0.933** |
| Illustrative hysteresis loss (W) | 1.887 | **2.706** |
| Total modelled loss (W) | **9.567** | **9.342** |
| Steel mass (kg) | 1.901 | 2.657 |
| Bare copper mass including leads (kg) | 0.266 | 0.223 |

The middle point is interior to the rectangular grid and reduces the modelled objective by **0.2244 W (2.35%)**, based on unrounded totals. Reduced copper loss outweighs the increase in core loss. The next-best passing point is only **0.014 W** higher, so a fine ranking would require more reliable material and winding inputs.

| Scenario | Best turns | Best area (cm²) | Recalculated baseline (W) | Minimum (W) | Reduction | Grid position |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Low | 450 : 47 | 15.5 | 8.518 | 7.785 | 8.60% | Lower primary-turn boundary |
| Medium | 475 : 50 | 15.0 | 9.567 | 9.342 | 2.35% | Interior |
| High | 600 : 63 | 12.0 | 10.664 | 10.664 | 0.00% | Interior, baseline itself |

The minimum varies over 150 primary turns and 3.5 cm² across the scenarios. The lower turns in the low scenario are consistent with the smaller weight on core losses, while the high scenario favours the baseline already present in the grid. The design coordinates and gains are sensitive to the choice of coefficients.

The three-loss objective excludes excitation and core-loss current in the voltage calculation, leakage, excess dynamic core loss, stray and dielectric losses, AC winding corrections and temperature feedback. It cannot establish real transformer efficiency or manufacturing feasibility. The low-scenario result at the grid boundary makes no claim about smaller turn counts.

## Outputs and verification

- [All 1,107 calculated candidates](data/all_1107_candidates.csv) and [251 passing candidates](data/passing_candidates.csv)
- [Screening counts](data/screening_summary.csv), [same-scenario baseline comparisons](data/baseline_vs_optimum.csv) and [scenario minima](data/scenario_summary.csv)
- [Total-loss heatmap](figures/medium_total_loss_heatmap.svg) · [PNG](figures/medium_total_loss_heatmap.png). The heatmap shows all mathematical results. The star identifies the minimum among passing points.
- [Two screening heatmaps and their intersection](figures/two_constraint_screening_heatmaps.svg) · [PNG](figures/two_constraint_screening_heatmaps.png)
- [Copper, eddy, hysteresis and total comparison](figures/medium_baseline_vs_optimum_losses.svg) · [PNG](figures/medium_baseline_vs_optimum_losses.png)
- [Coefficient scenarios and design coordinates](figures/coefficient_scenario_comparison.svg) · [PNG](figures/coefficient_scenario_comparison.png)

Reproduce from the repository root with the existing dependencies:

~~~sh
python -m pip install -r requirements.txt
python -m analysis.stage4_assumption_based_v2.run
python -m unittest discover -s tests -v
~~~

The driver reads the generated CSVs back to plot and validate the heatmap cells, bar heights and scenario coordinates. The regression tests recompute each scenario's loss sum from the saved coefficients, verify the exact screening rules and compare the circuit, copper and mass outputs point by point against the archived grid. **14 tests passed**, including the 10 existing tests. Original analyses and outputs were preserved.
