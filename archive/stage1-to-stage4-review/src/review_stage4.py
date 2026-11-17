"""Audit saved Stage 4 results and tabulate unknown-loss break-even values."""

from csv import DictReader, DictWriter
from math import isclose, isfinite, pi, sqrt
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data"
SAVED = DATA / "optimisation"
REVIEW = DATA / "stage4_technical_review"
SCENARIOS = ("low", "mid", "high")


def read_csv(directory, name):
    with (directory / f"{name}.csv").open(encoding="utf-8", newline="") as handle:
        return list(DictReader(handle))


def close(value, expected):
    assert isclose(value, expected, rel_tol=1e-10, abs_tol=1e-12), (value, expected)


def verify_row(row, settings, inputs):
    """Check both flux definitions and the loss columns from saved circuit values."""
    def number(field):
        value = float(row[field])
        assert isfinite(value), field
        return value

    np = int(row["primary_turns"])
    ns = int(row["secondary_turns"])
    area = number("effective_area_cm2") * 1e-4
    ratio = ns / np
    vp = float(inputs["primary_rms_v"])
    frequency = float(inputs["frequency_hz"])
    target = float(inputs["secondary_target_rms_v"])
    assert ns == round(np * target / vp)
    ip, current = number("primary_rms_a"), number("secondary_rms_a")
    rp, rs = number("primary_ohm"), number("secondary_ohm")
    terminal = number("load_terminal_v")
    close(ip, ratio * current)
    close(terminal * current, float(inputs["rated_va"]))
    close(number("ideal_secondary_v"), ratio * vp)

    induced_primary = vp - ip * rp
    induced_secondary = terminal + current * rs
    close(induced_primary, induced_secondary / ratio)
    close(number("primary_induced_rms_v"), induced_primary)
    denominator = sqrt(2) * pi * frequency * np * area
    no_drop = vp / denominator
    loaded = induced_primary / denominator
    assert 0 < loaded < no_drop
    close(number("bmax_nominal_no_drop_t"), no_drop)
    close(number("loaded_peak_t"), loaded)

    bmax_pass = no_drop <= float(settings["applied_bmax_ceiling"])
    voltage_pass = float(settings["loaded_voltage_min"]) <= terminal <= float(settings["loaded_voltage_max"])
    covered = float(inputs["anchor_low_polarisation_t"]) <= loaded <= float(inputs["anchor_high_polarisation_t"])
    assert (row["bmax_pass"] == "True") == bmax_pass
    assert (row["vload_pass"] == "True") == voltage_pass
    assert (row["both_screens_pass"] == "True") == (bmax_pass and voltage_pass)
    assert (row["hysteresis_domain_covered"] == "True") == covered
    assert (row["rankable"] == "True") == (bmax_pass and voltage_pass and covered)

    for side, amps, resistance in (("primary", ip, rp), ("secondary", current, rs)):
        close(number(f"{side}_copper_loss_w"), amps**2 * resistance)
    copper = ip**2 * rp + current**2 * rs
    close(number("copper_loss_w"), copper)
    mass = number("core_mass_kg")
    eddy = mass * float(settings["classical_loss_coefficient"]) * (frequency * loaded)**2
    close(number("classical_eddy_loss_w"), eddy)
    for scenario in SCENARIOS:
        if covered:
            energy = float(settings[f"hysteresis_reference_energy_{scenario}"])
            anchor = float(inputs["anchor_high_polarisation_t"])
            exponent = float(inputs["hysteresis_exponent"])
            hysteresis = mass * frequency * energy * (loaded / anchor)**exponent
            close(number(f"hysteresis_{scenario}_w"), hysteresis)
            close(number(f"total_{scenario}_w"), copper + eddy + hysteresis)
        else:
            assert row[f"hysteresis_{scenario}_w"] == row[f"total_{scenario}_w"] == ""


def main():
    settings = {row["parameter"]: row["value"] for row in read_csv(SAVED, "retained_parameters")}
    inputs = {row["parameter"]: row["value"] for row in read_csv(DATA, "baseline_parameters")}
    all_rows = read_csv(SAVED, "all_1107_candidates")
    screened = read_csv(SAVED, "candidates_passing_both_screens")
    winners = read_csv(SAVED, "best_by_hysteresis_scenario")
    baseline, middle = read_csv(SAVED, "baseline_vs_best_screened")
    rankable = [row for row in screened if row["rankable"] == "True"]
    unresolved = [row for row in screened if row["hysteresis_domain_covered"] == "False"]
    assert (len(all_rows), len(screened), len(rankable), len(unresolved)) == (1107, 415, 153, 262)
    assert screened == [row for row in all_rows if row["both_screens_pass"] == "True"]
    coordinates = {(row["primary_turns"], row["effective_area_cm2"]) for row in all_rows}
    assert len(coordinates) == len(all_rows)
    for row in all_rows:
        verify_row(row, settings, inputs)

    minima = {}
    for winner in winners:
        scenario = winner["scenario"]
        field = f"total_{scenario}_w"
        minima[scenario] = min(float(row[field]) for row in rankable)
        close(float(winner[field]), minima[scenario])
        assert any(all(row[key] == winner[key] for key in row) for row in rankable)
        boundary = (
            winner["primary_turns"] in (settings["primary_turns_min"], settings["primary_turns_max"])
            or winner["effective_area_cm2"] in (settings["area_min"], settings["area_max"])
        )
        assert (winner["on_search_grid_boundary"] == "True") == boundary
    for candidate in (baseline, middle):
        assert any(all(candidate[key] == row[key] for key in row) for row in rankable)
    close(float(middle["total_mid_w"]), minima["mid"])

    fields = ("primary_turns", "secondary_turns", "effective_area_cm2", "bmax_nominal_no_drop_t",
              "loaded_peak_t", "core_mass_kg", "copper_loss_w", "classical_eddy_loss_w")
    diagnostics = []
    for row in unresolved:
        assert float(row["loaded_peak_t"]) < float(inputs["anchor_low_polarisation_t"])
        subtotal = float(row["copper_loss_w"]) + float(row["classical_eddy_loss_w"])
        diagnostic = {key: row[key] for key in fields}
        diagnostic["copper_plus_classical_lower_bound_w"] = subtotal
        for scenario in SCENARIOS:
            # Positive headroom is necessary, but not sufficient, to beat this comparator.
            headroom = minima[scenario] - subtotal
            diagnostic[f"{scenario}_hysteresis_break_even_w"] = headroom
        diagnostics.append(diagnostic)

    REVIEW.mkdir(exist_ok=True)
    with (REVIEW / "unresolved_candidate_break_even.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = DictWriter(handle, fieldnames=list(diagnostics[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(diagnostics)

    low_field = "loaded_peak_t"
    peaks = [float(row[low_field]) for row in unresolved]
    no_drop_below_one = sum(float(row["bmax_nominal_no_drop_t"]) < 1 for row in unresolved)
    best_floor = min(diagnostics, key=lambda row: row["copper_plus_classical_lower_bound_w"])
    print(f"Verified {len(all_rows)} saved grid rows, {len(screened)} passes and {len(rankable)} complete objectives.")
    print(f"{len(unresolved)} unresolved: loaded flux {min(peaks):.6f}–{max(peaks):.6f} T, "
          f"{no_drop_below_one} also below 1 T at nominal no-drop.")
    print(f"Minimum unresolved copper-plus-classical subtotal: "
          f"{best_floor['copper_plus_classical_lower_bound_w']:.6f} W at "
          f"{best_floor['primary_turns']}:{best_floor['secondary_turns']} turns, "
          f"{best_floor['effective_area_cm2']} cm².")
    for scenario in SCENARIOS:
        possible = sum(row[f"{scenario}_hysteresis_break_even_w"] > 0 for row in diagnostics)
        print(f"{scenario}: {possible} unresolved points have positive break-even headroom against "
              f"the {minima[scenario]:.6f} W restricted minimum.")


if __name__ == "__main__":
    main()
