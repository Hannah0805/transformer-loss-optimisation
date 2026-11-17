# Parametric Sensitivity Analysis

## Experimental controls

Experiments A–C use the tested [Stage 2 model](04_model_development.md), with 230 V RMS input, 50 Hz, unity load power factor and 100 VA delivered at each point. The resistive circuit solves for current on the high-voltage branch. This convention holds actual modelled VA fixed as the terminal voltage changes. Stage 2 used the nominal secondary current for its primary loss comparison and also reported the exact-100-VA operating point. The latter is the starting point here.

The SIWATT M270-35A material inputs, wire diameters, lead allowances, 60 °C winding temperature, provisional geometry dimensions and design limits come from the [baseline parameter register](../data/baseline_parameters.csv). Classical and hysteresis losses use the loaded peak flux density. The screening flux uses the no-drop estimate at the separate illustrative 241.5 V RMS and 50 Hz envelope. The screens use a 1.50 T flux ceiling, ±1% ideal voltage error, ±5% loaded voltage error, 35% maximum bare copper fill, 4 A/mm² maximum current density and the insulated radial build limit. Passing these screens would establish feasibility within this model.

The hysteresis values use the Stage 2 illustrative low, middle and high scenarios. Their shared quadratic dependence applies from 1.0 to 1.5 T loaded peak induction. Outside that domain the CSV leaves hysteresis and the three-loss total blank while retaining copper and classical loss predictions. The low–high band compares assumed scenarios. It does not estimate statistical uncertainty or bound physical hysteresis. Classical estimates at high induction or for rejected candidates are retained to show equation behaviour and require the thin-sheet and uniform-flux approximations.

## A · Primary and secondary winding turns

Primary turns varied from 480 to 900 in steps of five at 12 cm². At each primary count, the notebook screened integer secondary turns against the ±1% ideal voltage tolerance and chose the admissible integer giving the smallest absolute loaded voltage error. The tie-break was the smaller ideal error, then fewer turns. All selected ratios met the ideal tolerance. The [candidate table](../data/sensitivity_results/a_secondary_turn_candidates.csv) records the 124 evaluated options and the selected winding pair at each primary count.

| Primary:secondary turns | Loaded peak flux (T) | Copper (W) | Classical eddy current (W) | Illustrative hysteresis, middle (W) | Middle three-loss sum (W) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 600:63 | 1.402 | 7.031 | 0.580 | 1.902 | 9.514 |
| 750:79 | 1.113 | 9.552 | 0.365 | 1.198 | 11.115 |

Adding turns in this comparison lowered the flux density and both core loss components. Longer windings increased resistance, and the fixed-output circuit required higher secondary current as the terminal voltage fell. These changes increased copper loss by 2.520 W, more than the combined core loss reduction of 0.918 W in the middle hysteresis scenario. The small steps or reversals along the curves reflect integer secondary turns and winding layer changes. Hysteresis is available from 565 through 830 primary turns on this grid.

None of the 85 selected points passed all model screens. Only 485, 495 and 505 turns passed the loaded-voltage criterion, and each exceeded the flux limit. Among points that passed the flux screen, the highest loaded secondary voltage was 22.516 V RMS at 610 turns, short of the 22.8 V lower limit. The CSV records 82 loaded-voltage failures, 25 flux failures, 38 secondary current-density failures and three fill failures. Counts overlap.

## B · Effective core cross-sectional area

Effective steel area varied from 9 to 18 cm² at 0.125 cm² intervals with 600:63 turns. The proportional geometry scales all linear dimensions by the square root of the area ratio, giving a steel mass proportional to area to the power 1.5. The fixed-stamping case changes only stack depth at fixed centre-limb width and fixed window dimensions. Its modelled magnetic path is constant and mass is proportional to area. Both cases recalculate the winding mean turn lengths. Proportional windows can change the number of layers, while the fixed-stamping case adds directly to the turn perimeter without creating extra axial winding space.

| Case | Steel mass (kg) | Primary / secondary mean turn length (mm) | Loaded peak flux (T) | Copper (W) | Classical (W) | Hysteresis, middle (W) | Middle total (W) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Common baseline, 12 cm² | 1.901 | 163.9 / 196.3 | 1.402 | 7.031 | 0.580 | 1.902 | 9.514 |
| Proportional, 15 cm² | 2.657 | 179.1 / 212.3 | 1.119 | 7.728 | 0.516 | 1.693 | 9.937 |
| Fixed stamping, 15 cm² | 2.376 | 181.9 / 214.4 | 1.118 | 7.836 | 0.461 | 1.513 | 9.810 |

From 12 to 15 cm², both geometry rules lower the core loss density and increase core mass and winding length. The proportional geometry adds about 40% mass, while the fixed stamping adds 25%. Classical loss falls by about 11% and 20%, respectively. Despite the larger reduction of core watts in the fixed-stamping case, both rules produce a higher middle three-loss sum than at 12 cm². The magnitude of the change depends on the geometry rule and the assumed hysteresis magnitude. Hysteresis is available from 11.25 through 16.75 cm² for proportional geometry and from 11.25 through 16.625 cm² for fixed stamping on this grid.

All 73 area points in each geometry family failed the loaded voltage screen. The first flux-screen passes occurred at 12.125 cm², where loaded secondary voltage remained below 22.56 V in both cases. The sweeps evaluate fixed wire gauges and a fixed turns pair. The result leaves broader design feasibility unresolved.

## C · Frozen mass and mean turn length

The counterfactual fixes core mass and both mean turn lengths at their 12 cm², 600:63 baseline values. At the same turns and area as each matched geometry-aware point, it uses Stage 2 winding resistance, resistive load, flux and loss functions. The match is exact at the common baseline within floating-point precision. The counterfactual has no corresponding winding-window geometry to screen.

- **Turns sweep.** Mass is fixed in both versions. At 750:79 turns the frozen case gives 9.094 W copper and 10.660 W middle total. The geometry-aware layout requires longer mean turns as the layer build changes, giving 9.552 W copper and 11.115 W total. The difference in core losses between versions is small because their loaded flux predictions are close.
- **Area sweep.** At 15 cm² the frozen case gives 8.620 W middle total, down from 9.514 W at the baseline. The proportional geometry gives 9.937 W, up from the same baseline. The frozen case keeps resistance, currents and copper loss constant, while increasing area directly reduces loaded induction. It also omits the mass increase that offsets some of the reduction in specific core loss. Over this interval, freezing both quantities reverses the direction of the predicted total-loss change.

## D · Optional voltage-level sensitivity

This separate experiment holds the 600:63 build and 50 Hz fixed, delivering exactly 100 VA at each sampled input from 190 to 250 V RMS in 5 V steps. The fixed turns ratio is retained and the 24 V requirement is relaxed. No result from D enters A–C. The notebook flags nominal no-drop flux and current density at each input, using the same threshold values as the main model.

Reducing input from 230 V to 210 V lowers loaded peak induction from 1.402 to 1.273 T and raises copper loss from 7.031 to 8.700 W. Secondary voltage drops from 22.563 to 20.285 V RMS, and secondary current density exceeds the provisional limit at 210 V. These points illustrate the constant-power mechanism. A study that maintains 24 V by changing the winding ratio would test a different condition.

## Hypothesis conclusions

| Hypothesis | Finding | Evidence and limit |
| --- | --- | --- |
| H1. More turns can lower core loss and raise copper loss. | **Supported within the model.** | The 600-to-750-turn comparison lowers both core terms and raises copper loss. Integer turns and winding layers affect local steps. A feasible minimum is inconclusive under the screened fixed-core setup. |
| H2. Larger core area can lower induction while greater mass and mean turn length compete with that reduction. | **Supported within both tested geometry families.** | Both families show the competing effects from 12 to 15 cm². The prediction that larger area lowers the three-loss sum over this interval is contradicted by the geometry-aware middle scenario. Frozen geometry predicts the opposite. |
| H3. Lower input voltage at fixed VA may reduce peak induction and increase copper loss. | **Supported for the relaxed-output, fixed-build experiment.** | The 230-to-210 V comparison shows both trends. The result at a maintained 24 V output is inconclusive because the required winding change was outside this experiment. |

## Figures and numerical results

All figures have vector SVG and 360 dpi PNG versions. Hollow markers indicate that one or more main geometry-aware design screens failed. Lines break where the hysteresis scenario is outside its declared range.

1. [Peak flux density vs primary turns](../figures/sensitivity/a_peak_flux_density_vs_primary_turns.svg). Loaded, nominal no-drop and high-supply no-drop flux at 12 cm². The horizontal line denotes the provisional high-supply flux limit.
2. [Component losses vs primary turns](../figures/sensitivity/a_component_losses_vs_primary_turns.svg). Winding copper, classical eddy current and middle illustrative hysteresis at fixed input and delivered VA.
3. [Total modelled loss vs primary turns](../figures/sensitivity/a_total_modelled_loss_vs_primary_turns.svg). Middle scenario and low–high scenario band. Blank ends of the sweep are outside the declared hysteresis domain.
4. [Losses vs effective core area](../figures/sensitivity/b_losses_vs_effective_core_area.svg). Loss components and middle total for proportional dimensions and fixed stamping at the same 600:63 winding pair.
5. [Frozen vs geometry-aware model](../figures/sensitivity/c_frozen_vs_geometry_aware_total_loss.svg). Matched turns and proportional area sweeps. The line styles distinguish the two models, and the markers record screening failures of the geometry-aware cases.
6. [Optional input-voltage sensitivity](../figures/sensitivity/d_fixed_va_input_voltage_sensitivity.svg). Secondary output voltage, loaded peak induction and copper loss under separate fixed-build, constant-VA conditions.

| Data file | Contents |
| --- | --- |
| [A · Winding turns](../data/sensitivity_results/a_winding_turns.csv) | 85 selected winding pairs, electrical and geometry outputs, losses and constraint flags |
| [A · Secondary-turn candidates](../data/sensitivity_results/a_secondary_turn_candidates.csv) | All 124 evaluated pairs and selection flags |
| [B · Effective core area](../data/sensitivity_results/b_effective_core_area.csv) | 146 points across two geometry rules |
| [C · Frozen geometry](../data/sensitivity_results/c_frozen_geometry_comparison.csv) | 158 matched counterfactuals. Join turns or area coordinates to A or proportional B. |
| [D · Input voltage](../data/sensitivity_results/d_input_voltage_fixed_va.csv) | 13 fixed-build voltage cases |

## Reproduction and review

Run these commands from the project root inside the Python environment for this project:

~~~sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
jupyter execute --inplace --timeout=90 notebooks/02_sensitivity_analysis.ipynb
~~~

The [executed notebook](../notebooks/02_sensitivity_analysis.ipynb) generates the CSV files first, then loads them as the figure data source. It verifies that every plotted line has the saved coordinates, that reported totals add up, that unmodelled hysteresis is left blank and that every circuit solution delivers 100 VA. The geometry-aware and frozen cases also agree at their common baseline.

The priority for review is whether to retain the provisional gauges, 60 °C case, output tolerances and flux envelope for the next design stage. The one-variable sweeps leave the joint design space unresolved. The loss predictions also retain the Stage 2 limitations, including illustrative hysteresis, omitted excitation and leakage, uniform flux and fixed winding temperature.
