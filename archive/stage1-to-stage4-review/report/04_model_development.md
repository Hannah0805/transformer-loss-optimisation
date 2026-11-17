# Mathematical and Geometric Model Development

## Model scope and evidence

The Python model evaluates a single-phase 230 V RMS, 50 Hz transformer with a 24 V RMS secondary target and 100 VA rated apparent power at unity load power factor. It evaluates a specified integer winding pair and an idealised E–I geometry. The separated loss sum includes primary and secondary copper loss, classical core eddy current loss and an explicitly supplied hysteresis scenario.

The [baseline register](../data/baseline_parameters.csv) distinguishes brief specifications, copper reference properties, manufacturer steel properties, provisional engineering parameters and illustrative hysteresis inputs. The selected steel is coated SIJ Acroni SIWATT M270-35A. Stage 1 sources and limits are in the [source review](02_sources_and_material_selection.md) and [source register](../data/source_register.csv). Material density and electrical resistivity are typical sheet properties. Dimensions, wire sizes, clearances, stacking factor and operating temperature are provisional because a finished core and winding drawing are unavailable.

## E–I geometry and scaling

The symmetric gross lamination has centre-limb width \(w\), stack depth \(d\), and two iron-to-iron windows of width \(u\) and height \(h\). Each return limb and each yoke have width or thickness \(w/2\). Under symmetric flux splitting, each return path carries approximately half the centre-limb flux through half its effective cross section. The steel occupies fraction \(k_s\) of gross stack depth. The model computes

\[
A_c=k_swd,\qquad
A_{\mathrm{footprint}}=(2w+2u)(h+w)-2uh,\qquad
V_{\mathrm{steel}}=k_s d A_{\mathrm{footprint}}
                 =2A_c(h+w+u),\qquad
m_c=\rho_m V_{\mathrm{steel}}.
\]

The one-loop magnetic centreline passes through the centre limb and one return limb. Its two vertical segments have length \(h+w/2\) between yoke centrelines, and its two horizontal segments have length \(u+3w/4\) between limb centrelines. The resulting path is \(2h+2u+2.5w\). This geometric path is reported for context. Loss uses the integral of the assumed uniform loss density over the calculated steel volume, and the model does not derive excitation current from path length or permeability. The stacking factor is applied once to gross geometry. The steel-loss formula uses actual nominal sheet gauge independently of the gross stack depth.

At the baseline, the 35 mm centre width and provisional \(k_s=0.95\) imply \(d=36.090\) mm for the specified 12 cm² net steel area. For area comparisons, the implemented geometry method multiplies all four linear dimensions by \(s=\sqrt{A_c/A_{c,0}}\), keeping the proportions and stack factor fixed. Magnetic path length scales as \(s\). Steel volume and mass scale as \(s^3=(A_c/A_{c,0})^{3/2}\). Fixed stamping dimensions with varying stack depth alone would produce different mass, path and window behaviour. The implemented scaling is a mathematical design family.

The layer layout assumes round wire, primary inside secondary, rectangular turns and a pitch equal to insulated wire diameter. Usable axial height excludes both end margins. Usable radial width excludes the inner former wall and outer clearance. At wire-centre offset \(r\), the turn length is approximated by \(2(w+d)+8r\). Each layer contributes its actual turn count, including partial layers. The secondary starts outside the primary radial build and interwinding barrier. As area increases, the base rectangular perimeter grows with \(s\). Offsets vary in steps as available height changes the number of layers. Fixed insulation dimensions and possible changes in wire size prevent a single power law for the full mean turn length.

## Voltage, load convention and winding loss

For linked sinusoidal flux, an RMS winding EMF is \(E_i=\sqrt{2}\pi fN_i A_cB_{\mathrm{pk}}\). The ideal turns ratio gives \(V_{s,0}=aV_p\) with \(a=N_s/N_p\), provided primary winding drop is neglected. The nearest positive integer to \(N_pV_{s,\mathrm{target}}/V_p\) is the default ideal-ratio suggestion with half-turn ties rounded up. The supplied 600:63 pair is retained for the baseline. Comparing the neighbouring integers gives 23.767 V at 62 turns and 24.150 V at 63 turns in the ideal model. The winding-pair evaluator accepts explicit integers so a later study can investigate compensation for resistive drop.

Electrical winding resistance and heat dissipation are computed in SI units:

\[
R_i=\rho_{\mathrm{Cu},20}\,[1+\alpha_{20}(T_i-20\,^\circ\mathrm C)]
 \frac{N_i\bar\ell_i+L_{\mathrm{lead},i}}{\pi d_{\mathrm{bare},i}^2/4},
\qquad P_{\mathrm{Cu},i}=I_{i,\mathrm{RMS}}^2R_i .
\]

\(\bar\ell_i\) includes the geometry and layer dependence. \(L_{\mathrm{lead},i}\) is the combined length of the included leads for that winding. Standard annealed copper supplies \(\rho_{\mathrm{Cu},20}\) and \(\alpha_{20}\). Both windings in the baseline are assigned 60 °C. The linear temperature approximation is intended for ordinary copper winding temperatures around the reference, with thermal expansion and self-heating omitted. The resistance units reduce to \((\Omega\cdot\mathrm m)\mathrm m/\mathrm m^2=\Omega\), and \(\mathrm A^2\Omega=\mathrm W\).

The rating-based ideal current estimates are 0.43478 A and 4.16667 A RMS. To predict the terminal voltage at load, the model uses a stiff primary supply, a unity-power-factor secondary, DC winding resistance, zero leakage reactance and zero excitation current. Therefore \(I_p=aI_s\), \(E_p=V_p-I_pR_p\) and \(V_{s,\mathrm{load}}=aV_p-I_s(R_s+a^2R_p)\). The baseline uses the rated secondary test current \(I_s=100/24\) A. The optional exact-output convention solves \(V_{s,\mathrm{load}}I_s=100\) VA using the positive high-voltage branch of the resistive load equation. It rejects requests with no real operating point. Primary current follows the actual ratio for both conventions. Core losses use the resulting loaded flux density based on \(E_p\). A separate no-drop flux calculation screens high voltage and low frequency. The resistive circuit power balance covers output and copper loss. The additional core-loss watts are estimates outside that circuit, and their effect on primary input current is omitted.

## Core-loss equations and sensitivity

Use the thin insulated lamination relation verified in Stage 1:

\[
p_{\mathrm{cl},v}=\frac{\pi^2(t f B_{\mathrm{pk}})^2}{6\rho_{\mathrm{el}}},
\qquad
P_{\mathrm{cl}}=V_{\mathrm{steel}}p_{\mathrm{cl},v}
              =m_c\,p_{\mathrm{cl},v}/\rho_m.
\]

The volumetric units are V²/(Ω·m³) = W/m³, since T = V·s/m². Through-thickness skin effect, nonuniform flux and currents across laminations are omitted. An explicitly labelled hysteresis scenario supplies a quasi-static reference energy \(w_{\mathrm{ref}}\) in J/kg per cycle:

\[
P_h=m_c f w_{\mathrm{ref}}
       \left(\frac{B_{\mathrm{pk}}}{B_{\mathrm{ref}}}\right)^\beta .
\]

With matched loop data, \(w_{\mathrm{ref}}\) could be estimated from the loop area divided by steel density. For this calculation, the illustrative low, middle and high cases allocate 25%, 50% and 75% of the unresolved sheet-loss remainder at 1.5 T and 50 Hz to hysteresis. That remainder is the published typical total of 2.64 W/kg minus the calculated 0.3493 W/kg classical term, using \(B\approx J\). Divide the allocated power by 50 Hz to obtain J/kg per cycle. The provisional common exponent \(\beta=2\) limits the calculation to a simple sensitivity over 1.0–1.5 T. These choices set scenarios and do not define statistical intervals or physical bounds. Outside the declared induction range, the model leaves hysteresis and the separated total unavailable.

The separate 50 Hz worksheet check linearly interpolates between the manufacturer tabulated typical totals at 1.0 and 1.5 T. It estimates 2.341 W/kg of **sheet total** at the baseline loaded induction, using \(B\approx J\). This comparison provides scale and range context and shares an anchor with the illustrative cases. It does not validate the decomposition or a finished core. The sheet total includes unresolved dynamic effects and is excluded from the separated loss sum.

## Executed baseline results

| Quantity | Result | Basis |
| --- | ---: | --- |
| Effective core area | 12.000 cm² | Brief |
| Magnetic path through one return | 223.500 mm | Provisional geometry |
| Steel volume and mass | 247.200 cm³ and 1.9010 kg | Provisional geometry and typical sheet density |
| Primary and secondary mean turn length | 163.860 mm and 196.333 mm | Layer-weighted estimates |
| Primary and secondary resistance | 12.3585 Ω and 0.22173 Ω | Both at assumed 60 °C |
| Ideal secondary voltage and nominal no-drop flux | 24.150 V RMS and 1.43801 T peak | Sinusoidal ideal equations |
| At rated secondary current | 22.6584 V RMS, 94.4101 VA, 1.40420 T peak | Primary 0.43750 A RMS, secondary 4.16667 A RMS |
| At exactly 100 VA | 22.5635 V RMS, 1.40205 T peak | Primary 0.46535 A RMS, secondary 4.43194 A RMS |
| Primary and secondary copper loss | 2.3655 W and 3.8494 W | Rated secondary current |
| Classical eddy current loss | 0.5819 W | Loaded induction, rated secondary current |
| Copper and classical subtotal | 6.7968 W | Before hysteresis |
| Illustrative hysteresis, low / middle / high | 0.9540 / 1.9081 / 2.8621 W | Rated secondary current, three assumed allocations |
| Separated loss sum, low / middle / high | 7.7508 / 8.7048 / 9.6589 W | Scenario outputs |

The provisional one-window fill is 23.676% against 35%, and the 7.100 mm insulated radial build fits within 16.000 mm. The ideal secondary voltage error is 0.625% against 1%. The primary and secondary current densities at the rated-current test point are 2.751 and 3.684 A/mm² against 4 A/mm². Two screens fail under the stated assumptions:

- The loaded secondary voltage error is 5.590%, above the provisional ±5% limit.
- The no-drop flux at the illustrative 241.5 V RMS and 50 Hz envelope is 1.5099 T, above the provisional 1.50 T cap. The cap is a conservative model criterion, not a measured saturation threshold.

Constructors reject nonpositive physical dimensions, nonfinite values where applicable, invalid gauges and invalid stacking factors. Layout evaluation rejects a window with no usable space or which cannot fit a single wire diameter axially. Cases reaching the numerical screens report individual failure reasons. Fill uses bare conductor area in one usable window. The separate radial check includes actual layer pitch and the interwinding barrier. These screens do not verify creepage, clearance for a particular insulation system, thermal rise or manufacturability.

## Reproduction and verification

Run the following from the project root with Python 3.10 or later. The model and unit tests use the Python standard library. The notebook packages are listed in [requirements.txt](../requirements.txt). The saved notebook includes outputs from a fresh Python 3.13 kernel.

~~~sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
jupyter execute --inplace --timeout=60 notebooks/01_baseline_calculation.ipynb
~~~

The tests check the ideal ratio, RMS-to-peak conversion, cm²-to-m² conversion, geometric volume by two routes, area scaling, partial winding layers, copper temperature and unit consistency, classical volume-to-mass conversion and scaling, hysteresis scaling and domain, both electrical load conventions, and explicit constraint failures. The executed [baseline notebook](../notebooks/01_baseline_calculation.ipynb) reads the parameter register and cross-checks the two classical-loss unit routes.

## Review decisions and unresolved validation

Confirm the E–I dimensions, winding geometry, candidate wire sizes and 60 °C reference before interpreting the losses as representative. Review the two output operating-point conventions, tolerances, current-density limit and the conservative flux screen. Choose whether to retain the illustrative hysteresis cases or use matched measurements or explicitly transferred same-grade literature in a later stage. The model omits excess core loss in the separated objective, stray and dielectric losses, leakage-flux effects, excitation current, AC winding resistance, flux nonuniformity, joint and cutting effects, and temperature feedback. This stage evaluates the specified baseline and does not carry out a design sweep or optimisation.
