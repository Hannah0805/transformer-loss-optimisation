"""Reproduce the revised Stage 3 screening and the Stage 4 preparation grid."""

from collections import Counter
from csv import DictReader, DictWriter
from dataclasses import replace
from math import isclose, isfinite
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import numpy as np

from .core_geometry import EICore, WindowClearances
from .material_models import Copper, HysteresisScenario, LaminatedSteel
from .transformer_model import (
    ElectricalSpec, Winding, evaluate_design, nearest_secondary_turns, peak_flux_density,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = DATA / "optimisation"
FIGURES = ROOT / "figures" / "optimisation"
TURNS = range(450, 1101, 25)
AREAS = tuple(10 + index * 0.5 for index in range(41))
REQUESTED_FLUX_LIMIT = 1.70
VOLTAGE_LIMITS = (21.6, 26.4)
COPPER_DENSITY = 8890  # kg/m³, standard annealed copper, NBS Handbook 100 §1.3.
LEVELS = ("low", "mid", "high")


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as file:
        return list(DictReader(file))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def screening_columns(bmax, vload, flux_limit, covered):
    flux_pass = bmax <= flux_limit
    voltage_pass = VOLTAGE_LIMITS[0] <= vload <= VOLTAGE_LIMITS[1]
    both = flux_pass and voltage_pass
    return {
        "bmax_pass": flux_pass,
        "vload_pass": voltage_pass,
        "both_screens_pass": both,
        "rankable": both and covered,
    }


def design_row(result, steel, scenarios, inputs, flux_limit, area_cm2):
    spec, load, core = result.spec, result.load, result.core
    primary, secondary = result.primary, result.secondary
    p_mlt = result.primary_layout.mean_turn_length_m
    s_mlt = result.secondary_layout.mean_turn_length_m
    p_length = primary.turns * p_mlt + primary.lead_length_m
    s_length = secondary.turns * s_mlt + secondary.lead_length_m
    covered = scenarios["mid"].contains(result.loaded_peak_t)
    row = {
        "primary_turns": primary.turns, "secondary_turns": secondary.turns, "effective_area_cm2": area_cm2,
        "ideal_secondary_v": result.ideal_secondary_rms_v,
        "load_terminal_v": load.secondary_terminal_rms_v,
        "ideal_voltage_error_fraction": result.ideal_secondary_rms_v / spec.secondary_target_rms_v - 1,
        "rated_output_va": load.delivered_va, "primary_rms_a": load.primary_rms_a,
        "secondary_rms_a": load.secondary_rms_a, "primary_induced_rms_v": load.primary_induced_rms_v,
        "bmax_nominal_no_drop_t": result.no_drop_peak_t, "loaded_peak_t": result.loaded_peak_t,
        "old_high_supply_peak_t": peak_flux_density(inputs["maximum_supply_rms_v"], inputs["minimum_frequency_hz"],
                                                   primary.turns, core.effective_area_m2),
        "effective_bmax_limit_t": flux_limit, "requested_bmax_limit_t": REQUESTED_FLUX_LIMIT,
        "primary_ohm": result.primary_ohm, "secondary_ohm": result.secondary_ohm,
        "primary_copper_loss_w": result.primary_copper_w, "secondary_copper_loss_w": result.secondary_copper_w,
        "copper_loss_w": result.copper_w, "classical_eddy_loss_w": result.classical_w,
        "core_mass_kg": result.core_mass_kg,
        "primary_copper_mass_kg": COPPER_DENSITY * p_length * primary.conductor_area_m2,
        "secondary_copper_mass_kg": COPPER_DENSITY * s_length * secondary.conductor_area_m2,
        "copper_mass_kg": COPPER_DENSITY * (p_length * primary.conductor_area_m2 +
                                            s_length * secondary.conductor_area_m2),
        "centre_width_mm": core.centre_width_m * 1e3, "stack_depth_mm": core.stack_depth_m * 1e3,
        "window_width_mm": core.window_width_m * 1e3, "window_height_mm": core.window_height_m * 1e3,
        "path_length_mm": core.magnetic_path_m * 1e3, "steel_volume_cm3": core.steel_volume_m3 * 1e6,
        "primary_mean_turn_length_mm": p_mlt * 1e3, "secondary_mean_turn_length_mm": s_mlt * 1e3,
        "primary_layers": result.primary_layout.layers, "secondary_layers": result.secondary_layout.layers,
        "bare_copper_fill_fraction": result.bare_copper_fill,
        "usable_window_mm2": result.usable_window_m2 * 1e6,
        "required_build_mm": result.required_radial_build_m * 1e3,
        "available_build_mm": result.usable_width_m * 1e3,
        "radial_build_fits_diagnostic": result.required_radial_build_m <= result.usable_width_m,
        "primary_current_density_a_mm2": load.primary_rms_a / primary.conductor_area_m2 / 1e6,
        "secondary_current_density_a_mm2": load.secondary_rms_a / secondary.conductor_area_m2 / 1e6,
        "hysteresis_domain_covered": covered,
    }
    for level, scenario in scenarios.items():
        hysteresis = (result.core_mass_kg * scenario.specific_loss_w_kg(spec.frequency_hz, result.loaded_peak_t)
                      if covered else None)
        row[f"hysteresis_{level}_w"] = hysteresis
        row[f"total_{level}_w"] = result.copper_w + result.classical_w + hysteresis if covered else None
    row.update(screening_columns(result.no_drop_peak_t, load.secondary_terminal_rms_v, flux_limit, covered))
    assert isclose(load.delivered_va, spec.rated_va)
    assert isclose(result.classical_w, core.steel_volume_m3 * steel.classical_loss_w_m3(spec.frequency_hz, result.loaded_peak_t))
    if covered:
        assert isclose(row["total_mid_w"], result.separated_total_w)
    if any(not isfinite(value) for value in row.values() if isinstance(value, float)):
        raise ValueError("Nonfinite candidate result")
    return row


def rescreen_stage3(flux_limit):
    """Replay the two replacement screens against the preserved Stage 3 sweeps."""
    replay = []
    sources = {
        "A selected winding turns": "a_winding_turns.csv",
        "B area geometries": "b_effective_core_area.csv",
    }
    for sweep, filename in sources.items():
        for old in read_csv(DATA / "sensitivity_results" / filename):
            covered = old["hysteresis_covered"] == "True"
            bmax, vload = float(old["no_drop_peak_t"]), float(old["terminal_secondary_v"])
            replay.append({
                "stage3_sweep": sweep, "geometry": old["geometry"],
                "primary_turns": old["primary_turns"], "secondary_turns": old["secondary_turns"],
                "effective_area_cm2": old["effective_area_cm2"],
                "bmax_nominal_no_drop_t": bmax, "load_terminal_v": vload,
                "effective_bmax_limit_t": flux_limit, "stage3_original_screen_pass": old["design_feasible"],
                "stage3_original_failures": old["constraint_failures"],
                "hysteresis_domain_covered": covered, "total_mid_w": old["total_mid_w"],
                **screening_columns(bmax, vload, flux_limit, covered),
            })
    write_csv(RESULTS / "stage3_revised_screening.csv", replay)
    return replay


def save_figure(fig, name):
    for extension in ("png", "svg"):
        fig.savefig(FIGURES / f"{name}.{extension}", dpi=360, facecolor="white")
    plt.close(fig)


def make_figures(rows, comparison, flux_limit):
    """Use serialized results as the common source for all figures."""
    n_turns = len(TURNS)
    shape = (len(AREAS), n_turns)
    expected_coordinates = [(n, area) for area in AREAS for n in TURNS]
    actual_coordinates = [(int(row["primary_turns"]), float(row["effective_area_cm2"])) for row in rows]
    assert actual_coordinates == expected_coordinates
    extent = (TURNS[0] - 12.5, TURNS[-1] + 12.5, AREAS[0] - 0.25, AREAS[-1] + 0.25)
    origin = {"origin": "lower", "extent": extent, "aspect": "auto", "interpolation": "nearest"}
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5, "axes.labelsize": 11,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "svg.fonttype": "none",
    })

    loss = np.array([float(r["total_mid_w"]) if r["total_mid_w"] else np.nan for r in rows]).reshape(shape)
    cmap = plt.get_cmap("viridis").with_extremes(bad="#ECEFF3")
    fig, ax = plt.subplots(figsize=(8.2, 5.0), layout="constrained")
    image = ax.imshow(loss, **origin, cmap=cmap)
    assert np.allclose(image.get_array().filled(np.nan), loss, equal_nan=True)
    fig.colorbar(image, ax=ax, label="Middle scenario three-loss sum (W)")
    ax.set(xlabel="Primary turns", ylabel="Effective core area (cm²)")
    baseline = comparison[0]
    ax.scatter(int(baseline["primary_turns"]), float(baseline["effective_area_cm2"]), marker="o", s=54, facecolors="white", edgecolors="#252733", linewidths=1.1,
               label="Baseline")
    if len(comparison) > 1:
        ax.scatter(int(comparison[1]["primary_turns"]), float(comparison[1]["effective_area_cm2"]),
                   marker="*", s=126, c="#FFFFFF", edgecolors="#252733", linewidths=0.7,
                   label="Best rankable, middle scenario")
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor="#ECEFF3", edgecolor="#A5ADB7"))
    ax.legend(handles, [*labels, "Three-loss sum unavailable"], loc="upper right",
              facecolor="white", frameon=True)
    save_figure(fig, "total_modelled_loss_heatmap")

    classes = np.array([
        (r["bmax_pass"] == "False") + 2 * (r["vload_pass"] == "False") for r in rows
    ]).reshape(shape)
    palette = ["#C5DFD1", "#76538F", "#D99150", "#39333C"]
    labels = ["Passes both screens", f"Fails flux only (>{flux_limit:.2f} T)",
              "Fails voltage only", "Fails both"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8), sharey=True, layout="constrained")
    layers = (
        ("Flux screen", classes % 2, [palette[0], palette[1]], [labels[0].replace("both screens", "flux"), labels[1].replace(" only", "")]),
        ("Terminal-voltage screen", classes // 2, [palette[0], palette[2]], ["Passes voltage", "Fails voltage"]),
        ("Combined screens", classes, palette, labels),
    )
    for ax, (title, layer, colors, legend) in zip(axes, layers):
        image = ax.imshow(layer, **origin, cmap=ListedColormap(colors),
                          norm=BoundaryNorm(np.arange(len(colors) + 1) - 0.5, len(colors)))
        assert np.array_equal(image.get_array(), layer)
        ax.set(title=title, xlabel="Primary turns", xticks=[450, 600, 750, 900, 1100])
        ax.legend(handles=[Patch(facecolor=color, label=label) for color, label in zip(colors, legend)],
                  loc="upper left", fontsize=8, frameon=True, facecolor="white")
    axes[0].set_ylabel("Effective core area (cm²)")
    save_figure(fig, "flux_and_voltage_rejection_map")

    if len(comparison) > 1:
        fields = ("primary_copper_loss_w", "secondary_copper_loss_w", "classical_eddy_loss_w",
                  "hysteresis_mid_w", "total_mid_w")
        labels = ("Primary\ncopper", "Secondary\ncopper", "Classical\neddy", "Hysteresis\n(middle)", "Total\n(middle)")
        fig, ax = plt.subplots(figsize=(9.1, 4.5), layout="constrained")
        x = np.arange(len(fields))
        for offset, row, color in zip((-0.19, 0.19), comparison, ("#60788D", "#067266")):
            values = [float(row[field]) for field in fields]
            bars = ax.bar(x + offset, values, width=0.36, color=color, label=row["case"])
            assert [bar.get_height() for bar in bars] == values
            ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=8)
        ax.set(xticks=x, xticklabels=labels, ylabel="Modelled loss (W)", ylim=(0, ax.get_ylim()[1] * 1.11))
        ax.legend(loc="upper left")
        ax.grid(axis="y", alpha=0.21)
        ax.set_axisbelow(True)
        save_figure(fig, "baseline_vs_best_screened_losses")


def main():
    RESULTS.mkdir(exist_ok=True, parents=True)
    FIGURES.mkdir(exist_ok=True, parents=True)
    input_rows = read_csv(DATA / "baseline_parameters.csv")
    p = {row["parameter"]: float(row["value"]) for row in input_rows}
    assert p["load_power_factor"] == 1
    spec = ElectricalSpec(p["primary_rms_v"], p["secondary_target_rms_v"], p["frequency_hz"], p["rated_va"])
    depth = p["effective_area_m2"] / (p["stacking_factor"] * p["centre_width_m"])
    base = EICore(p["centre_width_m"], depth, p["window_width_m"], p["window_height_m"], p["stacking_factor"])
    clearances = WindowClearances(p["former_wall_m"], p["outer_clearance_m"],
                                  p["end_margin_m"], p["winding_barrier_m"])
    primary, secondary = (
        Winding(int(p[f"{name}_turns"]), p[f"{name}_bare_diameter_m"], p[f"{name}_insulated_diameter_m"],
                p[f"{name}_lead_length_m"], p["winding_temperature_c"])
        for name in ("primary", "secondary")
    )
    copper = Copper(p["copper_resistivity_20_ohm_m"], p["copper_temp_coefficient_per_k"])
    steel = LaminatedSteel(p["sheet_thickness_m"], p["steel_resistivity_ohm_m"], p["steel_density_kg_m3"])
    anchor_f, anchor_b = p["anchor_frequency_hz"], p["anchor_high_polarisation_t"]
    remainder = p["anchor_high_total_loss_w_kg"] - steel.classical_loss_w_kg(anchor_f, anchor_b)
    scenarios = {
        level: HysteresisScenario(level, p[f"hysteresis_{level}_fraction"] * remainder / anchor_f,
                                  anchor_b, p["hysteresis_exponent"], p["anchor_low_polarisation_t"], anchor_b)
        for level in LEVELS
    }
    flux_limit = min(REQUESTED_FLUX_LIMIT, scenarios["mid"].max_flux_density_t)

    removed_screens = {
        "maximum_supply_rms_v", "minimum_frequency_hz", "maximum_fill_fraction",
        "ideal_voltage_tolerance_fraction", "loaded_voltage_tolerance_fraction",
        "maximum_current_density_a_m2", "flux_limit_t",
    }
    manifest = [{**row, "usage": "prior screen or comparison only" if row["parameter"] in removed_screens
                 else "retained model input"} for row in input_rows]

    def record(name, value, unit, evidence, rationale):
        manifest.append(dict(parameter=name, value=value, unit=unit, evidence=evidence,
                             source_or_rationale=rationale, usage="revised analysis"))

    record("steel_grade", "SIJ Acroni SIWATT M270-35A", "designation", "Stage 2", "MAT-1 and MAT-2")
    record("baseline_stack_depth_m", depth, "m", "derived", "Effective area divided by stacking factor and centre width")
    record("primary_conductor_area_m2", primary.conductor_area_m2, "m²", "derived", "Stage 2 bare wire diameter")
    record("secondary_conductor_area_m2", secondary.conductor_area_m2, "m²", "derived", "Stage 2 bare wire diameter")
    record("copper_resistivity_at_winding_temperature", copper.resistivity_ohm_m(p["winding_temperature_c"]),
           "Ω·m", "derived", "Stage 2 linear copper temperature correction")
    record("copper_density_kg_m3", COPPER_DENSITY, "kg/m³", "reference", "CU-1 NBS Handbook 100 §1.3, copper mass diagnostic only")
    record("yoke_and_return_limb_width_ratio", 0.5, "fraction", "Stage 2", "Relative to centre width")
    record("turn_perimeter_width_depth_multiplier", 2, "dimensionless", "Stage 2", "Rectangular turn perimeter")
    record("turn_perimeter_offset_multiplier", 8, "dimensionless", "Stage 2", "Rectangular turn offset contribution")
    record("area_scaling_exponent", 0.5, "dimensionless", "Stage 2", "Rescale all linear dimensions at fixed proportions")
    record("classical_loss_coefficient", steel.classical_loss_w_kg(1, 1), "W·kg⁻¹·Hz⁻²·T⁻²",
           "derived", "Stage 2 thin-sheet equation with MAT-1 and MAT-2 inputs")
    for level, scenario in scenarios.items():
        record(f"hysteresis_reference_energy_{level}", scenario.reference_energy_j_kg, "J/kg per cycle",
               "illustrative", "Stage 2 allocation rule at the 1.5 T anchor")
    record("requested_bmax_ceiling", REQUESTED_FLUX_LIMIT, "T", "brief", "Conditional on model support")
    record("applied_bmax_ceiling", flux_limit, "T", "Stage 2 scenario coverage", "Nominal 230 V no-drop peak")
    record("loaded_voltage_min", VOLTAGE_LIMITS[0], "V RMS", "brief", "Relaxed 24 V target")
    record("loaded_voltage_max", VOLTAGE_LIMITS[1], "V RMS", "brief", "Relaxed 24 V target")
    for name, value, unit in (
        ("primary_turns_min", TURNS[0], "turn"), ("primary_turns_max", TURNS[-1], "turn"),
        ("primary_turns_step", TURNS.step, "turn"), ("area_min", AREAS[0], "cm²"),
        ("area_max", AREAS[-1], "cm²"), ("area_step", AREAS[1] - AREAS[0], "cm²"),
    ):
        record(name, value, unit, "brief", "Grid definition")
    record("load_model", "constant 100 VA, self-consistent high-voltage root", "description", "Stage 3",
           "No leakage or excitation")
    write_csv(RESULTS / "retained_parameters.csv", manifest)
    for row in manifest:
        print(f'{row["parameter"]} = {row["value"]} {row["unit"]} [{row["usage"]}]', flush=True)

    replay = rescreen_stage3(flux_limit)
    rows = []
    for area in AREAS:
        core = base.with_effective_area(area * 1e-4)
        for np_turns in TURNS:
            ns_turns = nearest_secondary_turns(spec.primary_rms_v, spec.secondary_target_rms_v, np_turns)
            assert ns_turns == round(np_turns * spec.secondary_target_rms_v / spec.primary_rms_v)
            result = evaluate_design(spec, core, clearances, replace(primary, turns=np_turns),
                                     replace(secondary, turns=ns_turns), copper, steel, scenarios["mid"], fixed_va=True)
            rows.append(design_row(result, steel, scenarios, p, flux_limit, area))
    assert len(rows) == 1107
    passes = [row for row in rows if row["both_screens_pass"]]
    ranked = [row for row in passes if row["rankable"]]
    baseline = next(row for row in rows if row["primary_turns"] == primary.turns and
                    row["secondary_turns"] == secondary.turns and isclose(row["effective_area_cm2"], p["effective_area_m2"] * 1e4))

    write_csv(RESULTS / "all_1107_candidates.csv", rows)
    if passes:
        write_csv(RESULTS / "candidates_passing_both_screens.csv", passes)
    else:
        with (RESULTS / "candidates_passing_both_screens.csv").open("w", encoding="utf-8", newline="") as file:
            DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n").writeheader()

    comparison = [{"case": "Baseline", **baseline}]
    if ranked:
        winners = []
        for level in LEVELS:
            chosen = min(ranked, key=lambda row: (row[f"total_{level}_w"], row["primary_turns"], row["effective_area_cm2"]))
            boundary = chosen["primary_turns"] in (TURNS[0], TURNS[-1]) or chosen["effective_area_cm2"] in (AREAS[0], AREAS[-1])
            winners.append({"scenario": level, "on_search_grid_boundary": boundary, **chosen})
        write_csv(RESULTS / "best_by_hysteresis_scenario.csv", winners)
        comparison.append({"case": "Best screened, middle", **{key: winners[1][key] for key in baseline}})
    write_csv(RESULTS / "baseline_vs_best_screened.csv", comparison)

    metrics = Counter(
        total_candidates=len(rows),
        bmax_pass=sum(row["bmax_pass"] for row in rows),
        vload_pass=sum(row["vload_pass"] for row in rows),
        both_screens_pass=len(passes),
        fails_bmax_only=sum(not row["bmax_pass"] and row["vload_pass"] for row in rows),
        fails_vload_only=sum(row["bmax_pass"] and not row["vload_pass"] for row in rows),
        fails_both=sum(not row["bmax_pass"] and not row["vload_pass"] for row in rows),
        rankable=len(ranked),
        pass_without_total=len(passes) - len(ranked),
        pass_below_hysteresis_domain=sum(row["loaded_peak_t"] < scenarios["mid"].min_flux_density_t for row in passes),
        pass_above_hysteresis_domain=sum(row["loaded_peak_t"] > scenarios["mid"].max_flux_density_t for row in passes),
        total_available_gridwide=sum(row["hysteresis_domain_covered"] for row in rows),
        stage3_replayed=len(replay),
        stage3_original_pass=sum(row["stage3_original_screen_pass"] == "True" for row in replay),
        stage3_revised_pass=sum(row["both_screens_pass"] for row in replay),
        stage3_revised_rankable=sum(row["rankable"] for row in replay),
    )
    write_csv(RESULTS / "screening_summary.csv", [{"metric": name, "count": count} for name, count in metrics.items()])
    for name, count in metrics.items():
        print(f"{name}: {count}")
    if ranked:
        best = comparison[-1]
        print(f'Middle scenario: {best["primary_turns"]}:{best["secondary_turns"]} turns, '
              f'{best["effective_area_cm2"]:.1f} cm², {best["total_mid_w"]:.6f} W')
    else:
        print("No screen-passing candidate with complete loss.")
    make_figures(read_csv(RESULTS / "all_1107_candidates.csv"), read_csv(RESULTS / "baseline_vs_best_screened.csv"), flux_limit)


if __name__ == "__main__":
    main()
