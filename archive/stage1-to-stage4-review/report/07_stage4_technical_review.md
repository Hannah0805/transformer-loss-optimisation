# Stage 4 Technical Review

## Decision and remaining coverage

Retain the Stage 2 illustrative hysteresis domain of **1.00–1.50 T loaded peak induction**. The reviewed sources do not establish a transferable low-induction hysteresis relation for the selected 0.35 mm SIJ Acroni SIWATT M270-35A in the proposed E–I assembly. Even within that interval, the three hysteresis scenarios lack independent calibration to the assembled core.

The archived grid contains 1,107 candidates. Of the 415 that pass both screens, 153 have a complete three-loss objective and 262 remain unresolved. The existing grid, loss equations and thresholds were retained. This review audited the archived results without running the optimisation driver.

## Evidence below 1.00 T

| Source | Evidence and applicability |
| --- | --- |
| **SIJ Acroni, SIWATT M270-35A (MAT-1)** | The typical 50 Hz total sheet-loss curve extends below 1.00 T and uses peak magnetic polarisation \(J\). The separate magnetisation curve can inform \(B=J+\mu_0H\). Even after converting the coordinate and subtracting the calculated classical eddy term, the remaining power includes hysteresis, excess loss and model discrepancy. The typical curve can support an aggregate sheet-loss comparison, but does not identify the hysteresis term or establish a guaranteed limit for the assembled core. [Manufacturer datasheet, pp. 1–2](https://cms.sij.si/storage/302/SIWATT-M270-35A.pdf) |
| **Bertotti (MAG-1)** | Separates quasi-static hysteresis, classical eddy and excess dynamic loss. The framework explains why a single-frequency total cannot identify hysteresis by subtraction. It supplies no SIWATT coefficient. [Primary paper](https://doi.org/10.1109/20.43994) |
| **Gmyrek et al. (MAG-3/4)** | The 0.35 mm M270-35A test campaign spans 0.1–1.5 T and 5–500 Hz. The authors estimate hysteresis by extrapolating energy per cycle to zero frequency and also examine fits to the 5 Hz data. Table II shows width- and cutting-dependent hysteresis at 0.6 T. Section IV-A and Appendix I distinguish induction ranges and specimen conditions. The coverage is sufficient for specimen-specific separation, but the source establishes no match to the selected SIWATT product or to the E–I assembly and its cutting or stress state. Applying those fits below 1 T and joining them to the Stage 2 law would assume transferability and continuity. [Publication record](https://iris.polito.it/handle/11583/3007680) · [Accepted author manuscript](https://www.researchgate.net/publication/395362841_Measurements_and_Modeling_of_Iron_Losses_in_Guillotine_and_Laser_Cut_Soft-Magnetic_Sheets) |
| **Jiles–Atherton validation (MAG-2)** | The study reports a DC loop for a 40 × 100 mm M270-35A sample. It supports the loop-area method, but does not provide a family of low-amplitude loop energies for the selected SIJ product. [Primary paper, §7 and Fig. 14](https://www.mdpi.com/1996-1073/15/18/6760) |
| **Steinert et al. (2015)** | Table III reports fitted M270-35A coefficients based on reference 13, which identifies Cogent Surahammars Bruk SURA M270-35A. The supplier and fitted loss formulation differ from the Stage 2 model. [Author-hosted paper, Table III and reference 13](https://www.ams-publications.ee.ethz.ch/uploads/tx_ethpublications/7_Loss_Investigation_of_Slotless_Bearingless_Disk_Drives_Steinert_ECCE_USA_2015_01.pdf) |
| **Daem et al. (2020)** | The 0.35 mm same-grade strips have resistivity 52 μΩ·cm, compared with SIJ's typical 42.2 μΩ·cm, and the study measured effects of orientation and deformation. This illustrates why a grade designation alone does not establish a coefficient match. [Primary paper, §§2.1 and 3.4](https://pmc.ncbi.nlm.nih.gov/articles/PMC7579121/) |

The current low, middle and high scenarios assign 25%, 50% and 75% of the unresolved 1.50 T, 50 Hz sheet-loss remainder to hysteresis. The allocations set a reference energy per unit mass per cycle, then assume \(w_h\propto B^2\). Both amplitude and exponent are illustrative.

A reliable extension would require quasi-static loop areas at several inductions for the selected SIWATT stock and relevant processing state, or matched frequency sweeps at fixed peak induction with enough low-frequency measurements to separate quasi-static energy and quantify residuals. The missing loaded induction range is **0.5362–0.9981 T**. Measurements should cover this range and overlap the current domain so the replacement can be applied consistently across the screened grid. Assembled-core validation would remain separate.

## Flux definitions and correction

In the retained resistive unity-power-factor circuit, \(a=N_s/N_p\), \(I_s=100\,\mathrm{VA}/V_{\mathrm{load}}\) and \(I_p=aI_s\). The internal induced RMS voltages satisfy

\[
E_p=V_p-I_pR_p,\qquad E_s=V_{\mathrm{load}}+I_sR_s=aE_p.
\]

With sinusoidal common flux and uniform effective steel area, Faraday's law gives

\[
B_{\mathrm{loaded}}=\frac{E_p}{\sqrt{2}\pi fN_pA_c},\qquad
B_{\mathrm{no\ drop}}=\frac{V_p}{\sqrt{2}\pi fN_pA_c}.
\]

Both quantities are peak flux densities calculated from RMS voltage. At nominal supply the in-phase primary resistive drop is positive under load, so the no-drop peak is the upper steady-state estimate over the modelled resistive load range and screens against 1.50 T. Classical eddy current loss and hysteresis use the loaded peak at 100 VA, since the internal induced voltage sets the modelled core flux. The nominal screen does not address overvoltage, waveform distortion, inrush or local flux concentration. [MIT OpenCourseWare, §3.2.4](https://live.ocw.mit.edu/courses/6-013-electromagnetics-and-applications-spring-2009/d3be4ea78b036a6362230fb41780cf54_MIT6_013S09_notes.pdf)

All **262** missing cases are below 1.00 T **under load**. Of those, **246** also fall below 1.00 T by the no-drop measure and **16** have a no-drop peak at or above 1.00 T. This corrects the description of the coverage gap. The saved voltage, flux and loss calculations require no numerical correction. At the middle-scenario minimum, the no-drop and loaded peaks are 1.45314 and 1.42251 T, respectively, and the loaded terminal voltage is 22.9043 V RMS.

## Restricted grid minimum

| Scenario | Primary : secondary turns | Effective area (cm²) | Primary copper (W) | Secondary copper (W) | Classical eddy current (W) | Scenario hysteresis (W) | Total (W) | Grid position |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Low | 450 : 47 | 15.5 | 2.125 | 3.337 | 0.916 | 1.503 | **7.881** | Lower primary-turn boundary |
| Middle | 475 : 50 | 15.0 | 2.228 | 3.475 | 0.835 | 2.737 | **9.274** | Interior |
| High | 550 : 57 | 13.0 | 2.491 | 4.030 | 0.665 | 3.273 | **10.460** | Interior |

Values were checked against the [archived scenario minima](../data/optimisation/best_by_hysteresis_scenario.csv). Displayed components are independently rounded. The middle-scenario result is **0.240 W (2.52%)** below the middle-scenario baseline of **9.514 W**. Under the high scenario, the same 475:50, 15.0 cm² point gives **10.642 W**, above its comparable baseline of **10.465 W**. The scenarios describe input sensitivity and carry no statistical confidence interpretation.

The optimum among all 415 screened candidates remains undetermined. The known copper-plus-classical subtotal is a lower bound on the three-loss model objective because hysteresis dissipation is nonnegative. **117** unresolved candidates have this subtotal below the middle-scenario restricted minimum. The lowest of those subtotals is **7.137 W** at **450:47 turns and 22.5 cm²**. That design would beat the restricted minimum only if its actual modelled hysteresis were below **2.137 W**. This difference is a break-even threshold and supplies no missing loss value. The corresponding counts of candidates with positive headroom under the low and high comparisons are 28 and 201. [Break-even audit of unresolved points](../data/stage4_technical_review/unresolved_candidate_break_even.csv)

## Verification and disclosure

The [audit script](../src/review_stage4.py) checks the archived results using both routes to the induced voltage, the 100 VA condition, both flux measures, all three scenario loss sums, blank entries outside the domain, the two filters and the saved minima and boundary flags. All 1,107 rows were checked. All 10 existing unit tests passed. The archived Stage 3 and Stage 4 artifacts matched their pre-review SHA-256 checksums. To reproduce from the project root:

~~~sh
python -m unittest discover -s tests -v
python -m src.review_stage4
~~~

Disclose the omitted excitation and core-loss current, leakage, excess magnetic loss, stray and dielectric losses, AC winding effects, nonuniform flux and temperature feedback. The winding temperature and E–I dimensions are provisional. Material processing and assembly uncertainty, thermal performance and manufacturability remain unverified. The restricted minimum is conditional on the discrete grid, educational screens and illustrative hysteresis assumptions. Stage 4 is at its technical review checkpoint.
