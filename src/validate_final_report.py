"""Independently audit the design grid from its input and coefficient tables."""

from csv import DictReader
from math import ceil, floor, inf, isclose, nextafter, pi, sqrt
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data"


def table(name):
    with (DATA / f"{name}.csv").open(encoding="utf-8", newline="") as handle:
        return list(DictReader(handle))


def independent_design(p, n, area_cm2):
    """Calculate geometry with a closed-form layer sum and solve the load quadratic."""
    rated, source, target, f = (p[k] for k in ("rated_va", "primary_rms_v", "secondary_target_rms_v", "frequency_hz"))
    ns = round(n * target / source)
    area = area_cm2 / 10000
    w0 = p["centre_width_m"]
    scale = sqrt(area / p["effective_area_m2"])
    w = w0 * scale
    d = p["effective_area_m2"] / (w0 * p["stacking_factor"]) * scale
    u = p["window_width_m"] * scale
    h = p["window_height_m"] * scale
    # Outer rectangular footprint less two open windows.
    mass = ((2*w + 2*u) * (h + w) - 2*u*h) * d * p["stacking_factor"] * p["steel_density_kg_m3"]
    copper_rho = p["copper_resistivity_20_ohm_m"] * (
        1 + p["copper_temp_coefficient_per_k"] * (p["winding_temperature_c"] - 20))
    inner = p["former_wall_m"]
    mean_lengths, resistances, conductor_masses, builds = [], [], [], []
    usable_height = h - 2 * p["end_margin_m"]
    for side, turns in (("primary", n), ("secondary", ns)):
        pitch = p[f"{side}_insulated_diameter_m"]
        layer_capacity = floor(nextafter(usable_height / pitch, inf))
        assert layer_capacity > 0
        full, remainder = divmod(turns, layer_capacity)
        layer_index_sum = layer_capacity * full*(full - 1)/2 + remainder*full
        mean = 2*(w + d) + 8*(inner + pitch*(.5 + layer_index_sum/turns))
        length = turns*mean + p[f"{side}_lead_length_m"]
        conductor_area = pi/4 * p[f"{side}_bare_diameter_m"]**2
        assert isclose(conductor_area, p[f"{side}_conductor_area_m2"], rel_tol=1e-12)
        mean_lengths.append(mean)
        resistances.append(copper_rho * length / conductor_area)
        conductor_masses.append(length * conductor_area * p["copper_density_kg_m3"])
        build = ceil(turns/layer_capacity) * pitch
        builds.append(build)
        inner += build + p["winding_barrier_m"]

    rp, rs = resistances
    a = ns/n
    req = rs + a*a*rp
    v0 = source*a
    v = v0/2 + sqrt((v0/2)**2 - rated*req)
    current = rated/v
    primary_current = a*current
    induced = (v + current*rs)/a
    assert isclose(induced, source - primary_current*rp, rel_tol=1e-12)
    pp, ps = primary_current**2 * rp, current**2 * rs
    assert isclose(source*primary_current, rated + pp + ps, rel_tol=1e-12)
    flux_denominator = sqrt(2)*pi*f*n*area
    b0, b = source/flux_denominator, induced/flux_denominator
    assert 0 < b < b0
    assert isclose(v*current, rated, rel_tol=1e-12)
    return dict(
        primary_turns=n, secondary_turns=ns, effective_area_cm2=area_cm2,
        load_terminal_v=v, ideal_secondary_v=v0, primary_induced_rms_v=induced,
        no_drop_peak_t=b0, loaded_peak_t=b, primary_rms_a=primary_current, secondary_rms_a=current,
        delivered_va=v*current, copper_w=pp+ps, primary_copper_w=pp, secondary_copper_w=ps,
        primary_ohm=rp, secondary_ohm=rs, primary_mean_turn_length_mm=1000*mean_lengths[0],
        secondary_mean_turn_length_mm=1000*mean_lengths[1], core_mass_kg=mass,
        copper_mass_kg=sum(conductor_masses), flux_pass=b0 <= p["no_drop_flux_max"],
        voltage_pass=v >= p["terminal_voltage_min"],
        required_radial_build_mm=1000*(sum(builds) + p["winding_barrier_m"]),
    )


def verify():
    p = {r["parameter"]: float(r["value"]) for r in table("model_inputs")}
    assert p["load_power_factor"] == 1
    coefficients = table("illustrative_coefficients")
    ranked = {c["scenario"]: [] for c in coefficients}
    rows = table("all_1107_candidates")
    coordinates = [(int(r["primary_turns"]), float(r["effective_area_cm2"])) for r in rows]
    assert coordinates == [(turns, area/2) for area in range(20, 61) for turns in range(450, 1101, 25)]
    for row, (turns, area) in zip(rows, coordinates):
        calc = independent_design(p, turns, area)
        calc["passes_both"] = calc["flux_pass"] and calc["voltage_pass"]
        for c in coefficients:
            level = c["scenario"]
            f, t, mass, b = p["frequency_hz"], p["sheet_thickness_m"], calc["core_mass_kg"], calc["loaded_peak_t"]
            eddy = float(c["ke"])*mass*(f*b*t)**2
            hysteresis = float(c["kh"])*mass*f*b**float(c["n"])
            total = sum((calc["primary_copper_w"], calc["secondary_copper_w"], eddy, hysteresis))
            calc.update({f"eddy_{level}_w": eddy, f"hysteresis_{level}_w": hysteresis, f"total_{level}_w": total})
            if calc["passes_both"]:
                ranked[level].append((total, turns, area))
        for key, value in calc.items():
            if isinstance(value, bool):
                assert row[key] == str(value), (turns, area, key)
            else:
                assert isclose(float(row[key]), value, rel_tol=1e-11, abs_tol=1e-12), (turns, area, key)
    assert len(rows) == 1107 and all(len(items) == 251 for items in ranked.values())
    for row in table("scenario_summary"):
        level = row["scenario"]
        total, turns, area = min(ranked[level])
        assert isclose(total, float(row["total_w"]), rel_tol=1e-12)
        assert (turns, area) == (int(row["primary_turns"]), float(row["effective_area_cm2"]))
        print(f"{level}: {turns}:{round(turns*24/230)} turns at {area:.1f} cm², {total:.9f} W")
    for row in table("baseline_vs_optimum"):
        if row["scenario"] == "medium":
            print(row["case"], ", ".join(f"{key}={float(row[key]):.6f}" for key in (
                "primary_copper_w", "secondary_copper_w", "eddy_medium_w", "hysteresis_medium_w",
                "total_medium_w", "load_terminal_v", "no_drop_peak_t", "loaded_peak_t",
                "core_mass_kg", "copper_mass_kg",
            )))
    print("Independent circuit, geometry, losses and ranking agree for all 1,107 saved rows.")


if __name__ == "__main__":
    verify()
