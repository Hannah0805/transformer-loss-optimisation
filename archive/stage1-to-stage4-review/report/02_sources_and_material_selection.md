# Sources and Material Selection

## Recommended material for the initial model

Use coated, nominal 0.35 mm **SIJ Acroni SIWATT M270-35A**, a fully processed non-oriented electrical steel. Its manufacturer publishes 50 Hz specific total core loss and magnetisation curves as well as electrical resistivity and mass density. These support a same-supplier classical estimate, a check against measured material-level total loss and a basis for choosing a provisional flux-density limit. The non-oriented grade is a reasonable starting assumption for a punched E–I shape with flux along different in-plane directions. The grade can still be anisotropic, and coating, assembly, cutting method and availability of a suitable lamination remain open. [SIJ Acroni technical data sheet (MAT-1)](https://cms.sij.si/storage/302/SIWATT-M270-35A.pdf), [SIJ SIWATT catalogue (MAT-2)](https://cms.sij.si/storage/586/SIJ-Katalog-SIWATT-2022.pdf).

Grain-oriented steel is an established transformer material when the magnetic circuit makes effective use of the rolling direction. Manufacturer ratings for such grades use their own test orientations and induction levels. The recommendation here is based on the data available for a simple E–I model and does not establish the preferred material for a manufactured transformer. [thyssenkrupp powercore (MAT-3)](https://www.thyssenkrupp-steel.com/en/products/electrical-steel/electrical-steel-grain-oriented/powercore/powercore.html).

| Quantity | Published value | Interpretation |
| --- | --- | --- |
| Sheet thickness | 0.35 mm | Nominal gauge selected for the model. Use the steel thickness in the classical equation. |
| Density at 20 °C | 7.69 kg/dm³ | Typical. SI conversion gives \(7690\) kg/m³. |
| Electrical resistivity | \(42.2\times10^{-8}\) Ω·m | Typical. Use \(4.22\times10^{-7}\) Ω·m as the nominal model input. |
| Specific core loss at 50 Hz and 1.0 T | 1.08 W/kg | Typical total for the sheet. |
| Specific core loss at 50 Hz and 1.5 T | 2.64 W/kg typical and 2.70 W/kg guaranteed maximum | Keep the typical value and guarantee distinct. The maximum applies at the specified material test point. |
| Peak polarisation at 50 Hz | 1.60, 1.69 and 1.80 T typical at 2500, 5000 and 10000 A/m, respectively | Magnetisation evidence for setting a design limit. A point in this table is insufficient to define the limit on its own. |

The loss curve is plotted against magnetic polarisation \(J\). Use \(B=J+\mu_0H\) when a matched \(H\) is available from the magnetisation curve. A first-pass \(B\approx J\) comparison is acceptable only where the \(\mu_0 H\) correction is small relative to the design margin and data precision. Near high field, account for the distinction explicitly. The initial flux limit will be chosen separately from the extent of the published curve. [MAT-1, pp. 1–2](https://cms.sij.si/storage/302/SIWATT-M270-35A.pdf).

## What can be separated with published data?

Bertotti separates material core loss into quasi-static hysteresis, classical eddy current loss and excess dynamic loss associated with domain processes. The selected SIJ sheet data support calculation of the classical term and a 50 Hz total-loss comparison. They supply neither quasi-static loops at a range of peak inductions nor repeated-frequency loss measurements at fixed induction for this sheet. Subtracting the calculated classical term from the total leaves hysteresis plus excess, subject to the error in the classical approximation, test scatter and any \(J\)-to-\(B\) mismatch. A frequency sweep at fixed voltage would also change induction and would confound frequency scaling. [Bertotti, 1988, Eqs. (2)–(3) (MAG-1)](https://doi.org/10.1109/20.43994), [SIJ Acroni technical data sheet (MAT-1)](https://cms.sij.si/storage/302/SIWATT-M270-35A.pdf).

For an order-of-magnitude check, the mass-specific classical coefficient \(\pi^2 t^2/(6\rho_{\mathrm{el}}\rho_m)\) derived from the nominal material inputs is \(6.21\times10^{-5}\) W·kg⁻¹·Hz⁻²·T⁻². Applying it at 50 Hz and using \(B\approx J\) for this comparison gives:

| Nominal induction (T) | Manufacturer typical total (W/kg) | Calculated classical term (W/kg) | Unresolved remainder (W/kg) |
| --- | ---: | ---: | ---: |
| 1.0 | 1.08 | 0.155 | 0.925 |
| 1.5 | 2.64 | 0.349 | 2.291 |

This arithmetic check is an illustration at the two published points. It supplies neither a hysteresis fit nor a measurement of the proposed transformer.

### Evidence from same-grade specimens

- The 2022 Jiles–Atherton validation paper reports a DC hysteresis loop for a 40 × 100 mm M270-35A sample and compares it with a fitted model (Section 7, Fig. 14 and Table 13). It supports the use of a loop area to estimate hysteresis energy for a stated specimen and excursion. The single reported specimen loop does not establish an energy-versus-amplitude law for SIWATT. [Static hysteresis measurements (MAG-2)](https://www.mdpi.com/1996-1073/15/18/6760).
- Gmyrek et al. tested 0.35 mm M270-35A strips over 5–500 Hz at 0.1–1.5 T with controlled peak induction for different cut widths and methods. They estimate quasi-static energy per cycle by extrapolation towards zero frequency and analyse the classical and excess components. The results and published parameter tables support a meaningful **specimen-specific** separation and a possible literature-based sensitivity case. The test strip geometry, cutting conditions and rolling orientation limit transferability. A match to the selected SIWATT sheet and finished E–I assembly was not established. The institutional record verifies the citation and abstract. Method details were checked against the accepted author manuscript because automated access to the repository's version-of-record PDF returned HTTP 403. [Publication record (MAG-3)](https://iris.polito.it/handle/11583/3007680), [Accepted author manuscript (MAG-4)](https://www.researchgate.net/publication/395362841_Measurements_and_Modeling_of_Iron_Losses_in_Guillotine_and_Laser_Cut_Soft-Magnetic_Sheets).

An adequate matched separation would pair known sheet thickness, density and resistivity with either low-rate loop areas at several peak inductions or measured specific loss across several frequencies including low rates at each fixed induction. With \(p_{\mathrm{tot},m}\) in W/kg, extrapolate \(p_{\mathrm{tot},m}/f\) in J/kg towards zero frequency to estimate quasi-static energy per cycle. Use the predicted classical contribution \(p_{\mathrm{cl},m}/f\), check the fit's sensitivity to the frequency band and treatment of excess loss, and validate against held-out points when data permit. A fit that uses only \(f\) and \(f^2\) can absorb excess loss into both coefficients. The 50 Hz manufacturer curve varies induction at one frequency and cannot resolve this ambiguity.

## Model strategy for review

1. **Default under the three-loss scope.** Retain the physical classical equation and use a clearly labelled hysteresis sensitivity scenario. Same-grade literature can inform a provisional range after checking coefficient definitions, specimen condition and induction bounds. If transfer is too uncertain, use explicitly illustrative bounds on hysteresis energy, document how the bounds were chosen, and report whether candidate rankings persist across them. Keep \(k_h\) and \(\beta\) unset until that choice is reviewed. Treat the excess contribution as omitted from this objective.
2. **Independent 50 Hz check.** Digitise the typical SIJ total-loss curve with accepted \((J,p)\) coordinates, recording page, digitisation precision, applicable range and any \(J\)-to-\(B\) conversion. Cross-check against the two tabulated anchors and interpolate only within the supported range. Use \(P_{\mathrm{Cu}}+m_c p_{\mathrm{tot},m}\) as a separately labelled aggregate comparison if approved. Do not add a separate classical or hysteresis term to that total. Its diagnostic columns can show \(p_{\mathrm{cl},m}\) and the unresolved remainder. The aggregate includes unseparated dynamic effects and does not isolate the three-loss objective.
3. **If better matched evidence is obtained.** Replace the illustrative hysteresis input with a fit to matched loop energies or a defensible frequency-based separation. Check the predicted combined core terms against the measured total and state the expected excess and model discrepancy. Recompute sensitivity to the choice of model before claiming a conditional optimum.

No hysteresis coefficients were assigned in Stage 1. Full provenance and access dates are in the [source register](../data/source_register.csv).
