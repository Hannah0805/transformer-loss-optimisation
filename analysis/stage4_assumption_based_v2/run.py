"""Generate the version 2 study using the Stage 2 circuit and generic loss assumptions."""

from dataclasses import dataclass, replace
from math import isfinite, pi, isclose
from pathlib import Path

from src.core_geometry import EICore, WindowClearances, require_positive
from src.material_models import Copper, LaminatedSteel
from src.grid_support import AREAS, TURNS, COPPER_DENSITY, read_csv, write_csv
from src.transformer_model import ElectricalSpec, Winding, evaluate_design, nearest_secondary_turns

VERSION = Path(__file__).resolve().parent
DATA = VERSION / "data"
FREQUENCY_REF = 50.0
INDUCTION_REF = 1.2
THICKNESS_REF = 0.00035
FLUX_LIMIT = 1.50
MINIMUM_VOLTAGE = 22.0


@dataclass(frozen=True)
class Scenario:
    name: str
    hysteresis_ref_w_kg: float
    eddy_ref_w_kg: float
    exponent: float

    def __post_init__(self):
        require_positive(hysteresis_ref_w_kg=self.hysteresis_ref_w_kg,
                         eddy_ref_w_kg=self.eddy_ref_w_kg, exponent=self.exponent)

    @property
    def kh(self):
        return self.hysteresis_ref_w_kg / (FREQUENCY_REF * INDUCTION_REF**self.exponent)

    @property
    def ke(self):
        return self.eddy_ref_w_kg / (FREQUENCY_REF**2 * INDUCTION_REF**2 * THICKNESS_REF**2)

    def core_losses(self, mass_kg, frequency_hz, loaded_peak_t, thickness_m):
        require_positive(mass_kg=mass_kg, frequency_hz=frequency_hz,
                         loaded_peak_t=loaded_peak_t, thickness_m=thickness_m)
        eddy = self.ke * mass_kg * frequency_hz**2 * loaded_peak_t**2 * thickness_m**2
        hysteresis = self.kh * mass_kg * frequency_hz * loaded_peak_t**self.exponent
        return eddy, hysteresis


# Reference specific powers were set before evaluating the grid.
SCENARIOS = (
    Scenario("low", 0.45, 0.15, 1.6),
    Scenario("medium", 0.75, 0.25, 1.8),
    Scenario("high", 1.05, 0.35, 2.0),
)


def screen(no_drop_peak_t, terminal_v):
    require_positive(no_drop_peak_t=no_drop_peak_t, terminal_v=terminal_v)
    flux_pass = no_drop_peak_t <= FLUX_LIMIT
    voltage_pass = terminal_v >= MINIMUM_VOLTAGE
    return flux_pass, voltage_pass, flux_pass and voltage_pass


def input_parameters():
    """Read only the fixed numerical inputs carried forward from Stage 2."""
    keys = """
        primary_rms_v secondary_target_rms_v frequency_hz rated_va load_power_factor
        primary_turns secondary_turns effective_area_m2 centre_width_m window_width_m
        window_height_m stacking_factor former_wall_m outer_clearance_m end_margin_m
        winding_barrier_m primary_bare_diameter_m primary_insulated_diameter_m
        secondary_bare_diameter_m secondary_insulated_diameter_m primary_lead_length_m
        secondary_lead_length_m winding_temperature_c copper_resistivity_20_ohm_m
        copper_temp_coefficient_per_k sheet_thickness_m steel_density_kg_m3
    """.split()
    rows = read_csv(VERSION.parents[1] / "data" / "baseline_parameters.csv")
    manifest = [{**row} for row in rows if row["parameter"] in keys]
    assert len(manifest) == len(keys)
    for row in manifest:
        if row["parameter"] in ("sheet_thickness_m", "steel_density_kg_m3"):
            row["evidence"] = "carried-forward illustrative geometry input"
            row["source_or_rationale"] = (
                "Prior numerical value retained to isolate the loss-model and screening changes"
            )
    return manifest, {row["parameter"]: float(row["value"]) for row in manifest}


def candidate_row(result, thickness_m, area_cm2):
    p, s, load = result.primary, result.secondary, result.load
    primary_length = p.turns * result.primary_layout.mean_turn_length_m + p.lead_length_m
    secondary_length = s.turns * result.secondary_layout.mean_turn_length_m + s.lead_length_m
    voltage_deviation = load.secondary_terminal_rms_v - result.spec.secondary_target_rms_v
    flux_ok, voltage_ok, passed = screen(result.no_drop_peak_t, load.secondary_terminal_rms_v)
    row = dict(
        primary_turns=p.turns, secondary_turns=s.turns, effective_area_cm2=area_cm2,
        ideal_secondary_v=result.ideal_secondary_rms_v, load_terminal_v=load.secondary_terminal_rms_v,
        target_voltage_deviation_v=voltage_deviation,
        target_voltage_deviation_percent=100 * voltage_deviation / result.spec.secondary_target_rms_v,
        delivered_va=load.delivered_va, primary_rms_a=load.primary_rms_a, secondary_rms_a=load.secondary_rms_a,
        primary_induced_rms_v=load.primary_induced_rms_v,
        no_drop_peak_t=result.no_drop_peak_t, loaded_peak_t=result.loaded_peak_t,
        primary_ohm=result.primary_ohm, secondary_ohm=result.secondary_ohm,
        primary_copper_w=result.primary_copper_w, secondary_copper_w=result.secondary_copper_w,
        copper_w=result.copper_w, core_mass_kg=result.core_mass_kg,
        copper_mass_kg=COPPER_DENSITY * (
            primary_length * p.conductor_area_m2 + secondary_length * s.conductor_area_m2),
        primary_mean_turn_length_mm=result.primary_layout.mean_turn_length_m * 1e3,
        secondary_mean_turn_length_mm=result.secondary_layout.mean_turn_length_m * 1e3,
        bare_copper_fill_fraction=result.bare_copper_fill,
        required_radial_build_mm=result.required_radial_build_m * 1e3,
        available_radial_build_mm=result.usable_width_m * 1e3,
        radial_build_fits_diagnostic=result.required_radial_build_m <= result.usable_width_m,
        primary_current_density_a_mm2=load.primary_rms_a / p.conductor_area_m2 / 1e6,
        secondary_current_density_a_mm2=load.secondary_rms_a / s.conductor_area_m2 / 1e6,
        loaded_below_previous_1t_domain=result.loaded_peak_t < 1,
        loaded_above_1_5t_diagnostic=result.loaded_peak_t > 1.5,
        flux_pass=flux_ok, voltage_pass=voltage_ok, passes_both=passed,
    )
    for scenario in SCENARIOS:
        eddy, hysteresis = scenario.core_losses(
            result.core_mass_kg, result.spec.frequency_hz, result.loaded_peak_t, thickness_m)
        row[f"eddy_{scenario.name}_w"] = eddy
        row[f"hysteresis_{scenario.name}_w"] = hysteresis
        row[f"total_{scenario.name}_w"] = result.copper_w + eddy + hysteresis
    assert isclose(row["eddy_medium_w"], result.classical_w, rel_tol=1e-12)
    assert isclose(load.delivered_va, result.spec.rated_va)
    if any(not isfinite(value) for value in row.values() if isinstance(value, float)):
        raise ValueError("Nonfinite grid result")
    return row


@dataclass(frozen=True)
class DesignModel:
    spec: ElectricalSpec
    core: EICore
    clearance: WindowClearances
    primary: Winding
    secondary: Winding
    copper: Copper
    steel: LaminatedSteel

    def evaluate(self, primary_turns: int, area_cm2: float):
        """Evaluate a candidate with the same methods used in the published grid."""
        scaled = self.core.with_effective_area(area_cm2 * 1e-4)
        secondary_turns = nearest_secondary_turns(
            self.spec.primary_rms_v, self.spec.secondary_target_rms_v, primary_turns)
        result = evaluate_design(
            self.spec, scaled, self.clearance, replace(self.primary, turns=primary_turns),
            replace(self.secondary, turns=secondary_turns), self.copper, self.steel, fixed_va=True,
        )
        return candidate_row(result, self.steel.sheet_thickness_m, area_cm2)


def build_model(p):
    spec = ElectricalSpec(p["primary_rms_v"], p["secondary_target_rms_v"], p["frequency_hz"], p["rated_va"])
    assert p["load_power_factor"] == 1
    depth = p["effective_area_m2"] / (p["stacking_factor"] * p["centre_width_m"])
    core = EICore(p["centre_width_m"], depth, p["window_width_m"], p["window_height_m"], p["stacking_factor"])
    clearance = WindowClearances(*(p[key] for key in (
        "former_wall_m", "outer_clearance_m", "end_margin_m", "winding_barrier_m")))
    primary, secondary = (
        Winding(int(p[f"{name}_turns"]), p[f"{name}_bare_diameter_m"],
                p[f"{name}_insulated_diameter_m"], p[f"{name}_lead_length_m"], p["winding_temperature_c"])
        for name in ("primary", "secondary")
    )
    copper = Copper(p["copper_resistivity_20_ohm_m"], p["copper_temp_coefficient_per_k"])
    thickness, density = p["sheet_thickness_m"], p["steel_density_kg_m3"]
    # This is the algebraic inverse of the Stage 2 classical coefficient, not a material input.
    implied_resistivity = pi**2 / (6 * density * SCENARIOS[1].ke)
    steel = LaminatedSteel(thickness, implied_resistivity, density)
    return DesignModel(spec, core, clearance, primary, secondary, copper, steel)


def calculate():
    DATA.mkdir(exist_ok=True)
    manifest, p = input_parameters()
    model = build_model(p)
    primary = model.primary
    secondary = model.secondary
    density = model.steel.density_kg_m3
    for name, value, unit, reason in (
        ("primary_conductor_area_m2", primary.conductor_area_m2, "m²", "Existing bare diameter"),
        ("secondary_conductor_area_m2", secondary.conductor_area_m2, "m²", "Existing bare diameter"),
        ("copper_density_kg_m3", COPPER_DENSITY, "kg/m³", "Retained Stage 4 diagnostic reference"),
        ("no_drop_flux_max", FLUX_LIMIT, "T", "Requested screening ceiling"),
        ("terminal_voltage_min", MINIMUM_VOLTAGE, "V RMS", "Requested screening floor"),
    ):
        manifest.append(dict(parameter=name, value=value, unit=unit, evidence="version 2 manifest",
                             source_or_rationale=reason))
    write_csv(DATA / "model_inputs.csv", manifest)
    write_csv(DATA / "illustrative_coefficients.csv", [
        dict(scenario=case.name, kh=case.kh, kh_unit=f"W kg^-1 Hz^-1 T^-{case.exponent:g}",
             ke=case.ke, ke_unit="W kg^-1 Hz^-2 T^-2 m^-2",
             n=case.exponent, n_unit="dimensionless", reference_f_hz=FREQUENCY_REF,
             reference_peak_t=INDUCTION_REF, reference_sheet_thickness_m=THICKNESS_REF,
             reference_hysteresis_w_kg=case.hysteresis_ref_w_kg, reference_eddy_w_kg=case.eddy_ref_w_kg,
             implied_classical_resistivity_ohm_m=pi**2 / (6 * density * case.ke),
             provenance="Illustrative assumption; no material fit")
        for case in SCENARIOS
    ])

    rows = [model.evaluate(turns, area) for area in AREAS for turns in TURNS]
    assert len(rows) == 1107
    passing = sorted((row for row in rows if row["passes_both"]), key=lambda row: row["total_medium_w"])
    baseline = next(row for row in rows if row["primary_turns"] == primary.turns
                    and row["secondary_turns"] == secondary.turns
                    and isclose(row["effective_area_cm2"], p["effective_area_m2"] * 1e4))
    comparisons, summary = [], []
    for case in SCENARIOS:
        total = f"total_{case.name}_w"
        ordered = sorted(passing, key=lambda row: (row[total], row["primary_turns"], row["effective_area_cm2"]))
        best = ordered[0]
        boundary = best["primary_turns"] in (TURNS[0], TURNS[-1]) or best["effective_area_cm2"] in (AREAS[0], AREAS[-1])
        for label, row in (("Baseline", baseline), ("Optimum", best)):
            comparisons.append(dict(scenario=case.name, case=label, **row))
        summary.append(dict(
            scenario=case.name, primary_turns=best["primary_turns"], secondary_turns=best["secondary_turns"],
            effective_area_cm2=best["effective_area_cm2"], no_drop_peak_t=best["no_drop_peak_t"],
            loaded_peak_t=best["loaded_peak_t"], load_terminal_v=best["load_terminal_v"],
            voltage_deviation_v=best["target_voltage_deviation_v"], primary_copper_w=best["primary_copper_w"],
            secondary_copper_w=best["secondary_copper_w"], copper_w=best["copper_w"],
            eddy_w=best[f"eddy_{case.name}_w"], hysteresis_w=best[f"hysteresis_{case.name}_w"],
            total_w=best[total], baseline_total_w=baseline[total],
            improvement_w=baseline[total] - best[total],
            improvement_percent=100 * (1 - best[total] / baseline[total]),
            second_best_gap_w=ordered[1][total] - best[total], on_grid_boundary=boundary,
            core_mass_kg=best["core_mass_kg"], copper_mass_kg=best["copper_mass_kg"],
        ))

    write_csv(DATA / "all_1107_candidates.csv", rows)
    write_csv(DATA / "passing_candidates.csv", passing)
    write_csv(DATA / "baseline_vs_optimum.csv", comparisons)
    write_csv(DATA / "scenario_summary.csv", summary)
    counts = {
        "total_candidates": len(rows), "flux_pass": sum(r["flux_pass"] for r in rows),
        "voltage_pass": sum(r["voltage_pass"] for r in rows), "passes_both": len(passing),
        "passing_below_1t_loaded": sum(r["loaded_below_previous_1t_domain"] for r in passing),
        "complete_objectives": sum(all(r[f"total_{c.name}_w"] > 0 for c in SCENARIOS) for r in rows),
    }
    write_csv(DATA / "screening_summary.csv", [dict(metric=key, count=value) for key, value in counts.items()])
    print(counts)
    for row in summary:
        print(row)


def main():
    from .figures import generate
    calculate()
    generate(DATA, VERSION / "figures")


if __name__ == "__main__":
    main()
