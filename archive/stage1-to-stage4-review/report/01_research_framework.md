# Research Framework

**Transformer Loss Trade-off Optimisation**  
*A Parametric Study of Copper, Eddy Current and Hysteresis Losses*

## Research question and design scope

How can winding turns and effective core cross-sectional area minimise combined primary and secondary copper loss, classical core eddy current loss, and core hysteresis loss while satisfying fixed electrical requirements and practical constraints?

The main study is a steady-state, single-phase, sinusoidal 230 V RMS, 50 Hz design study for a 24 V RMS secondary target, 100 VA rated apparent power and unity load power factor. Vary positive integer primary turns \(N_p\) and effective steel area \(A_c\) in m². Assign positive integer secondary turns \(N_s\) using the voltage checks below. For a separated scenario, minimise \(P_{\mathrm{obj}}=P_{\mathrm{Cu}}+P_{\mathrm{cl}}+P_h\) in W over feasible candidates. A total-core-loss comparison has a separately named objective as described in the [source review](02_sources_and_material_selection.md).

## Electrical relationships

Faraday's law gives \(|e_i|=N_i|d\Phi/dt|\) for winding \(i\in\{p,s\}\) linking the common flux. With \(\Phi(t)=A_c B_{\mathrm{pk}}\sin(2\pi f t)\),

\[
E_i=\sqrt{2}\pi fN_iA_c B_{\mathrm{pk}},\qquad
E_s/E_p=N_s/N_p,\qquad
B_{\mathrm{pk}}\simeq V_p/(4.44fN_pA_c).
\]

\(E_i\) and the primary terminal supply \(V_p\) are RMS voltages in V, \(f\) is in Hz, flux \(\Phi\) is in Wb and \(B_{\mathrm{pk}}\) is peak flux density in T. The final expression is a first-pass approximation using \(E_p\simeq V_p\). Reassess it for candidates with appreciable winding voltage drop or excitation current. [MIT OpenCourseWare, §3.2.4 (MIT-1)](https://live.ocw.mit.edu/courses/6-013-electromagnetics-and-applications-spring-2009/d3be4ea78b036a6362230fb41780cf54_MIT6_013S09_notes.pdf).

Use \(I_{p,\mathrm{ref}}=100/230=0.4348\) A and \(I_{s,\mathrm{ref}}=100/24=4.1667\) A RMS for first-pass rated-current comparisons. These are ideal rating-based references. A loaded calculation should account for the current reflected by the actual integer ratio and state how excitation current is treated. For a unity-power-factor rated-point voltage screen, with the primary supply stiff and leakage reactance and excitation current neglected, refer the primary winding resistance to the secondary. With \(a=N_s/N_p\),

\[
V_{s,\mathrm{load}}\simeq a V_p-I_s(R_s+a^2R_p),\qquad I_p\simeq a I_s .
\]

Use this at \(I_{s,\mathrm{ref}}\) to screen the rated-current test point. Report the resulting apparent power \(V_{s,\mathrm{load}} I_{s,\mathrm{ref}}\) alongside the voltage error. If holding delivered apparent power exactly at 100 VA is required in the model, solve \(I_s=100/V_{s,\mathrm{load}}\) self-consistently on the normal high-voltage branch and reject candidates that fail the voltage or current constraints.

Start from \(N_s^\ast=N_p(24/230)\); evaluate neighbouring integers for the ideal ratio screen and search additional nearby integers when compensating for winding drop. Enumerate the allowable secondary turns if a local search could miss a feasible candidate. Record \(N_s^\ast\), the chosen integer, ideal and loaded voltage errors, and the selection rule. For the supplied baseline (600/63 turns, \(A_c=12\) cm²), \(N_s^\ast\approx62.61\), the ideal secondary EMF is 24.15 V and \(B_{\mathrm{pk}}\approx1.438\) T. These derived values leave rated-load voltage and saturation feasibility open.

## Loss mechanisms

### Winding copper loss

\[
R_i=\rho_{\mathrm{Cu},i}\frac{N_i\ell_{\mathrm{mt},i}+L_{\mathrm{lead},i}}{A_{\mathrm{wire},i}},
\qquad
P_{\mathrm{Cu}}=I_p^2R_p+I_s^2R_s.
\]

Electrical current dissipates heat in both finite-resistance copper windings. Independent inputs to this submodel are the RMS currents \(I_i\) (A), turns \(N_i\) (count), mean length per turn \(\ell_{\mathrm{mt},i}\) and total included lead length \(L_{\mathrm{lead},i}\) (m), bare conducting area \(A_{\mathrm{wire},i}\) (m²), and copper electrical resistivity \(\rho_{\mathrm{Cu},i}\) (Ω·m). Calculated quantities are winding resistances \(R_i\) (Ω), each winding's copper loss and their sum (W). In the design sweep the turns, geometry and current model determine several of these inputs. Magnetic reluctance \(\mathcal R_m=\ell_m/(\mu A_c)\), in A·turn/Wb for a simple uniform path of length \(\ell_m\) and permeability \(\mu\), relates magnetomotive force and flux in a linear magnetic circuit. It does not enter \(I^2R\).

Use the DC resistance approximation for conductors with small skin and proximity corrections at 50 Hz. Hold an explicit conductor temperature fixed in each scenario. A first-order temperature sensitivity can use \(R_i(T)\approx R_i(20\,^\circ\mathrm C)[1+\alpha_{20}(T-20\,^\circ\mathrm C)]\). Standard annealed copper has a reference resistivity of approximately \(1.7241\times10^{-8}\) Ω·m and resistance temperature coefficient \(0.00393\) K⁻¹ at 20 °C. Actual wire and operating temperature require separate inputs. The dimensional check is A²·Ω = W. [NBS Handbook 100 (CU-1)](https://nvlpubs.nist.gov/nistpubs/Legacy/hb/nbshandbook100.pdf).

More turns or a longer mean turn generally increase resistance at fixed wire area. Thicker wire lowers resistance and current density but consumes winding space. An increase in turns can also require thinner wire to fit. Keep the two winding lengths and conductor sizes distinct.

### Classical core eddy current loss

\[
p_{\mathrm{cl},v}=\frac{\pi^2t^2 f^2 B_{\mathrm{pk}}^2}{6\rho_{\mathrm{el}}},\qquad
p_{\mathrm{cl},m}=\frac{p_{\mathrm{cl},v}}{\rho_m},\qquad
P_{\mathrm{cl}}=m_c p_{\mathrm{cl},m}.
\]

A changing magnetic flux induces circulating currents within each conductive lamination, which dissipate heat. Interlaminar insulation limits current paths between sheets. Independent submodel inputs are steel thickness \(t\) (m), frequency \(f\) (Hz), peak in-plane flux density \(B_{\mathrm{pk}}\) (T), steel electrical resistivity \(\rho_{\mathrm{el}}\) (Ω·m), steel mass density \(\rho_m\) (kg/m³) and steel mass \(m_c\) (kg). Dependent quantities are volumetric loss \(p_{\mathrm{cl},v}\) (W/m³), mass-specific loss \(p_{\mathrm{cl},m}\) (W/kg) and core loss \(P_{\mathrm{cl}}\) (W). Since T = V·s/m², the volumetric expression has units V²/(Ω·m³) = W/m³.

Use insulated thin sheets, sinusoidal flux parallel to the sheets, approximately uniform induction through sheet thickness, weak skin effect and negligible edge, joint and interlaminar current effects. Thinner sheets, higher electrical resistivity and lower peak induction reduce classical loss per unit steel mass, all else equal. At fixed steel thickness and resistivity, increasing \(A_c\) also changes mass and winding geometry. The formula estimates the classical contribution only. [Bertotti, 1988, Eq. (2) (MAG-1)](https://doi.org/10.1109/20.43994).

### Core hysteresis loss

\[
w_{h,v}=\left|\oint H\,dB\right|,\qquad
P_h=fV_{\mathrm{steel}} w_{h,v},\qquad
P_h\simeq m_cf k_h B_{\mathrm{pk}}^\beta \quad\text{for an empirical fit}.
\]

Irreversible magnetisation reversal dissipates energy each cycle. A quasi-static \(B\)-\(H\) loop at the relevant excursion provides the energy per cycle per volume \(w_{h,v}\) (J/m³). Inputs are the loop \(H\) (A/m) versus \(B\) (T) or fitted parameters \(k_h\) (J·kg⁻¹·T\(^{-\beta}\)) and dimensionless \(\beta\), \(B_{\mathrm{pk}}\) (T), frequency \(f\) (Hz), and steel volume \(V_{\mathrm{steel}}\) (m³) or mass \(m_c\) (kg). The dependent quantities are loss per cycle, specific power \(p_{h,m}=P_h/m_c\) (W/kg), and total hysteresis power (W). The dimension check is (A/m)·T = J/m³. A 50 Hz dynamic loop includes dynamic losses.

The empirical form assumes a specified material condition and excursion range, approximately rate-independent hysteresis energy per cycle, symmetric cycling and negligible DC bias. Fit it only to isolated loop energies or use explicitly illustrative parameters. Lower peak induction generally decreases hysteresis loss density within a suitable fitted range. Increased core mass can offset that decrease, and added turns can increase winding resistance. Cutting stress and material condition can change loop area. [Bertotti, 1988 (MAG-1)](https://doi.org/10.1109/20.43994), [DC loop measurement on an M270-35A specimen, §7 (MAG-2)](https://www.mdpi.com/1996-1073/15/18/6760).

## Geometry and constraints

Use a proposed symmetric E–I lamination geometry with centre limb width \(w\), gross stack depth \(d\), and two identical windows each of clear iron-to-iron width \(u\) and height \(h\), all in m. For this approximation set the outer limb widths and yoke thicknesses to \(w/2\) so that each return path carries approximately half the centre-limb flux at comparable induction. With stack factor \(k_s\), the effective centre-limb area is \(A_c=k_swd\). Neglecting joint gaps, the lamination footprint is \((2w+2u)(h+w)-2uh=2w(h+w+u)\). Hence

\[
V_{\mathrm{steel}}=2k_swd(h+w+u),\qquad
m_c=2\rho_m A_c(h+w+u).
\]

For rectangular turns, a first approximation is \(\ell_{\mathrm{mt},i}\simeq2(w+d)+8r_i\), with mean normal offset \(r_i\) (m) from the centre-limb surface to the winding centreline. Derive each offset from the bobbin, insulation, winding order and mean layer build. Determine how area changes through \(w\), \(d\), or both, and how \(u\) and \(h\) scale. Different geometry families at the same \(A_c\) can have different mass, resistance and feasibility.

Check integer turns, the chosen voltage tolerance, rated operation, and \(B_{\mathrm{pk}}\le B_{\mathrm{lim}}\) using a justified margin based on the material magnetisation curve and the worst specified operating voltage and frequency. Check \(I_i/A_{\mathrm{wire},i}\le J_{\mathrm{lim},i}\), with current density in A/m². In each window, both windings require space. A screening condition is \(\sum_i N_i A_{\mathrm{wire},i}\le k_{\mathrm{fill}} A_{\mathrm{usable}}\), where \(A_{\mathrm{usable}}\) is the area of one window after fixed bobbin and clearance deductions and \(k_{\mathrm{fill}}\) is an effective bare-copper fraction. Confirm actual layer fit with insulated wire diameters, winding height, build, barriers and margins. Define the allocations to avoid counting the same insulation or clearance twice. See the [input and constraint register](03_assumptions_and_limitations.md).

## Hypotheses and tests

| Hypothesis | Controlled comparison | Outputs and test |
| --- | --- | --- |
| H1. More turns may lower core loss and raise winding copper loss. | Sweep feasible integer \(N_p\) at fixed \(A_c\), geometry, voltage, frequency and rating. Reassign \(N_s\) at each step. Start with fixed wire sizes, then check whether any winding redesign changes the trend. | Compare finite changes in \(B_{\mathrm{pk}}\), each winding's resistance and loss, both core terms (or the explicitly aggregate comparison), and total objective. Mark secondary-turn steps and rejected candidates. |
| H2. Larger \(A_c\) may lower \(B_{\mathrm{pk}}\) yet increase steel mass and winding length, creating competing effects. | Sweep \(A_c\) at fixed turns and wire sizes under one declared geometry rule, holding electrical requirements fixed. Repeat with a plausible alternative geometry rule if warranted. | Plot \(B_{\mathrm{pk}}\), \(m_c\), both mean turn lengths, specific and actual core losses, copper losses and objective. Separate the change in loss per kg from the change in kg. Identify where either effect dominates. |
| H3. Lower input voltage at fixed transferred VA may decrease flux density and increase copper loss. | Optional separate fixed-build experiment. Hold turns, geometry, frequency and 100 VA transfer fixed in a suitable operating range. Vary \(V_p\), allowing secondary voltage to track the fixed ratio and reassessing current and feasibility at each voltage. | Compare \(B_{\mathrm{pk}}\), both winding currents and losses, and the core-loss trend against the same build at 230 V. At ideal fixed ratio both currents scale inversely with voltage. Reject points outside current, voltage regulation or material model limits and report the changing secondary voltage. |

H3 intentionally varies a supply parameter outside the main optimisation. If 24 V must also be maintained at each optional supply level, define a separate re-ratioed design comparison and document which winding changes. Changing primary turns approximately in proportion to supply voltage can keep \(B_{\mathrm{pk}}\) approximately constant, so it tests a different mechanism.

## Later verification and reporting

Enumerate feasible pairs of primary turns and core area within declared bounds and resolve secondary-turn choices by the documented rule. Record infeasibility reasons and grid resolution. Inspect whether a minimum is interior or bound-limited and rerun at finer spacing and under plausible changes in temperature, geometry, winding capacity and loss model. Check unit conversions, monotonicity of individual equations under controlled inputs, equality of volume- and mass-based loss calculations, and voltage-ratio error at the baseline. Keep inputs, derivations, prediction tables and plotting code traceable by source ID. Publish a conditional optimum only where the evidence and sensitivity support it.
