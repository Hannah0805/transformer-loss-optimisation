# Revised Screening and Stage 4 Optimisation Preparation

## Screening change and material coverage

This version preserves the original Stage 3 notebook, report, CSVs and figures. It replays the revised criteria against the geometry-aware turns and area sweeps, then evaluates the requested joint grid at 230 V RMS, 50 Hz, 100 VA and unity power factor. The objective is the sum of primary and secondary copper loss, classical eddy current loss, and quasi-static hysteresis loss as represented by the Stage 2 illustrative scenarios.

| Screen | Original Stage 3 | Revised analysis |
| --- | --- | --- |
| Maximum flux density | No-drop peak ≤1.50 T at the separate 241.5 V, 50 Hz envelope | No-drop peak ≤1.50 T at the fixed 230 V, 50 Hz supply. The old high-supply peak remains a diagnostic in the joint grid. |
| Loaded terminal voltage | 24 V ±5%, or 22.8–25.2 V RMS | 24 V ±10%, or 21.6–26.4 V RMS, inclusive |
| Other engineering screens | Ideal secondary voltage error ≤1%, bare copper fill ≤35%, radial build within available width, and each winding current density ≤4 A/mm² | Diagnostic only. Mass is also diagnostic. There is no supported material cost calculation. |
| Physical and mathematical input requirements | Positive dimensions, valid winding and material inputs, and a solvable circuit | Retained. An undefined circuit or dimension would give no meaningful model result. All 1,107 points have valid circuit and geometry evaluations. |

The two revised screens isolate steady-state flux and loaded voltage for an educational design comparison. Window fill, winding fit, winding current density, mass and turns-ratio error have no effect on the combined screen flag. Passing the screens establishes eligibility under these two criteria. Manufacturing would require separate insulation, packing, thermal, magnetic and mechanical validation.

The requested **1.70 T** flux ceiling was conditional on loss-model coverage. SIJ Acroni publishes magnetic polarisation and total sheet-loss information. It does not supply a matched separated hysteresis coefficient for the selected assembly, and the existing Stage 2 illustrative hysteresis law has a declared loaded-induction domain of **1.00–1.50 T**. The revised screen therefore uses **1.50 T at nominal supply** as the conservative upper bound for the no-drop estimate. This is a model-domain choice and is not a measured saturation threshold. Classical eddy and copper results remain visible even where the three-loss objective is unavailable. No hysteresis extrapolation was performed. [Stage 1 source review](02_sources_and_material_selection.md) · [SIJ Acroni technical data sheet](https://cms.sij.si/storage/302/SIWATT-M270-35A.pdf)

The maximum-flux screen uses \(B_{\max}=V_p/(\sqrt{2}\pi fN_pA_c)\) as the maximum normal steady-state peak in this nominal-supply resistive model, because primary winding drop lowers the modelled internal voltage under load. The core-loss terms use the smaller *loaded* peak based on the internal primary voltage. The loaded lower domain limit of 1.00 T affects the availability of hysteresis and the total. It does not change whether a point passes the two research screens.

## Retained inputs, load model and search grid

The program writes and prints the [exact numeric values, units and provenance](../data/optimisation/retained_parameters.csv) before evaluating the grid. It reads the original [baseline parameter table](../data/baseline_parameters.csv) and calls the existing [Stage 2 Python model](../src/transformer_model.py). The nominal steel lamination is 0.00035 m thick, with typical electrical resistivity \(4.22\times10^{-7}\) Ω·m and density 7690 kg/m³. The annealed copper reference is \(1.7241\times10^{-8}\) Ω·m at 20 °C, corrected to the same fixed 60 °C with \(0.00393\ \mathrm{K}^{-1}\). The bare conductor areas are approximately 0.1590 mm² and 1.1310 mm². The stacking factor is 0.95. Baseline centre width, window width and window height are 35, 18 and 50 mm, respectively. The baseline stack depth is derived from effective area. All linear core dimensions scale by \(\sqrt{A_c/A_{c,0}}\) at unchanged proportions. Wire gauges, insulation and clearance coefficients, winding order and lead lengths remain as in Stage 2. Diagnostic copper mass uses bare wire cross-section times modelled length including leads, multiplied by the standard annealed copper density of 8890 kg/m³ from [NBS Handbook 100, §1.3](https://nvlpubs.nist.gov/nistpubs/Legacy/hb/nbshandbook100.pdf).

Stages 3 and 4 use the same **self-consistent constant-output-VA circuit**, with unity power factor. Neither a fixed secondary current nor a fixed load resistance is imposed. At each winding pair \(a=N_s/N_p\), \(V_0=aV_p\) and \(R_{\mathrm{eq}}=R_s+a^2R_p\). The model solves \(V_{\mathrm{load}}=V_0-R_{\mathrm{eq}}(100/V_{\mathrm{load}})\) on the high-voltage branch:

\[
V_{\mathrm{load}}=\frac{V_0+\sqrt{V_0^2-4R_{\mathrm{eq}}(100\,\mathrm{VA})}}{2},\qquad
I_s=100\,\mathrm{VA}/V_{\mathrm{load}},\qquad I_p=aI_s .
\]

The secondary power factor is unity throughout, so 100 VA corresponds to 100 W at the modelled load. The primary induced voltage \(E_p=V_p-I_pR_p\) sets the loaded flux used for core-loss calculations. Excitation current, core-loss current and leakage reactance are omitted from the voltage calculation, as in Stage 2. The resistive operating point is internally consistent with its stated assumptions. Core loss is estimated separately from the power balance used to solve that operating point.

The grid is the Cartesian product of 27 primary-turn values (450–1100 in steps of 25) and 41 effective areas (10–30 cm² in steps of 0.5 cm²). For every point the model uses \(N_s=\mathrm{round}(N_p\,24/230)\), a positive integer, and records \(230N_s/N_p\) as the actual ideal secondary voltage. This replaces the Stage 3 loaded-voltage tie-break among secondary turn counts **for the new joint grid**. The Stage 3 replay holds its original chosen turns and geometry fixed so that the effect of the screening change can be isolated. Counterfactual geometry and variable-input-voltage runs from Stage 3 are outside the replay.

## Replayed Stage 3 screening

| Preserved geometry-aware sweep | Points | Original passes | Revised passes | Revised passes with complete objective |
| --- | ---: | ---: | ---: | ---: |
| A · Chosen secondary turns at fixed area | 85 | 0 | 57 | 50 |
| B · Proportional geometry at fixed turns | 73 | 0 | 52 | 42 |
| B · Fixed stamping at fixed turns | 73 | 0 | 52 | 41 |
| Total | 231 | 0 | 161 | 133 |

The replay makes the effect of the replacement criteria explicit on the same computed voltages and nominal fluxes. The resulting [replay CSV](../data/optimisation/stage3_revised_screening.csv) records old and new flags for each row.

## Joint-grid results

| Result | Candidates |
| --- | ---: |
| Grid points | 1,107 |
| Passes flux screen, regardless of voltage | 1,050 |
| Passes terminal-voltage screen, regardless of flux | 472 |
| Passes both | **415** |
| Fails flux only | 57 |
| Fails voltage only | 635 |
| Fails both | 0 |
| Passes both with complete three-loss objective | **153** |
| Passes both but total unavailable | **262** |

All 262 passing points without a total have loaded induction below 1.00 T, outside the Stage 2 hysteresis scenario domain. They remain in the passing CSV with blank hysteresis and total columns. The grid provides no established loss ranking for those 262 points. The minimum reported below therefore applies only to grid points that pass both screens and have a complete modelled objective.

### Baseline vs best rankable candidate, middle hysteresis scenario

| Model output | Baseline | Best rankable, middle |
| --- | ---: | ---: |
| Primary : secondary turns | 600 : 63 | **475 : 50** |
| Effective area (cm²) | 12.0 | **15.0** |
| Ideal secondary voltage (V RMS) | 24.150 | 24.211 |
| Loaded secondary voltage at 100 VA (V RMS) | 22.563 | 22.904 |
| Nominal no-drop peak used for screening (T) | 1.4380 | 1.4531 |
| Loaded peak used for losses (T) | 1.4020 | 1.4225 |
| Peak from old 241.5 V screen (T), diagnostic | 1.5099 | 1.5258 |
| Primary resistance (Ω) | 12.3584 | 10.5496 |
| Secondary resistance (Ω) | 0.22173 | 0.18228 |
| Primary copper loss (W) | 2.6763 | 2.2282 |
| Secondary copper loss (W) | 4.3552 | 3.4746 |
| Copper subtotal (W) | 7.0315 | 5.7028 |
| Classical eddy current loss (W) | 0.5801 | 0.8345 |
| Illustrative hysteresis loss, middle (W) | 1.9022 | 2.7366 |
| Three-loss total, middle (W) | **9.5138** | **9.2739** |
| Core mass (kg), diagnostic | 1.9010 | 2.6567 |
| Bare copper mass including modelled leads (kg), diagnostic | 0.2657 | 0.2228 |
| Bare copper fill, diagnostic | 23.68% | 14.60% |

The middle-scenario minimum is **inside the requested rectangular grid**. The 0.240 W decrease from the baseline is about 2.52%. The candidate has higher core mass and higher modelled core loss, offset by lower winding loss. This reduction depends on the hysteresis assumption.

| Hysteresis scenario used for ranking | Primary : secondary turns | Area (cm²) | Scenario minimum (W) | Grid position |
| --- | ---: | ---: | ---: | --- |
| Low | 450 : 47 | 15.5 | 7.8812 | Lower primary-turn boundary |
| Middle | 475 : 50 | 15.0 | 9.2739 | Interior |
| High | 550 : 57 | 13.0 | 10.4601 | Interior |

The ranking changes across scenarios. Under the high hysteresis assumptions, the middle-scenario candidate gives 10.6422 W versus the baseline's 10.4649 W. Without matched hysteresis data over a wider range, the best design in the full passing set remains unresolved. These results do not establish a real transformer optimum or manufacturing feasibility.

## Output files and verification

- [Complete grid](../data/optimisation/all_1107_candidates.csv), [two-screen passing candidates](../data/optimisation/candidates_passing_both_screens.csv) and [screening counts](../data/optimisation/screening_summary.csv).
- [Baseline and best rankable candidate](../data/optimisation/baseline_vs_best_screened.csv) and [minimum for each hysteresis scenario](../data/optimisation/best_by_hysteresis_scenario.csv).
- [Total loss heatmap](../figures/optimisation/total_modelled_loss_heatmap.svg) · [PNG](../figures/optimisation/total_modelled_loss_heatmap.png). Grey denotes unavailable hysteresis and total. Coloured cells include modelled points that can fail a research screen.
- [Flux and terminal-voltage rejection maps](../figures/optimisation/flux_and_voltage_rejection_map.svg) · [PNG](../figures/optimisation/flux_and_voltage_rejection_map.png). The first two panels show the individual screens and the third shows the combined status.
- [Loss component and total comparison](../figures/optimisation/baseline_vs_best_screened_losses.svg) · [PNG](../figures/optimisation/baseline_vs_best_screened_losses.png). Each bar shows the saved baseline or middle-scenario winner value.

From the project root, install the packages in [requirements.txt](../requirements.txt) and run:

~~~sh
python -m unittest discover -s tests -v
python -m src.optimisation
~~~

The driver saves the input manifest before the calculations and regenerates the versioned outputs without editing the prior Stage 3 results. Figures are constructed from the saved candidate and comparison data. The checks verify integer turns, the 100 VA operating point, the loss sum, the correspondence between each plotted grid cell or bar and its CSV value, and the preservation of the original Stage 3 outputs.
