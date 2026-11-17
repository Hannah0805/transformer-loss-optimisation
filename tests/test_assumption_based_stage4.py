"""Regression checks for the separate, assumption-based Stage 4 version."""

import unittest
from math import isfinite
from pathlib import Path

from analysis.stage4_assumption_based_v2.run import (
    DATA, SCENARIOS, FLUX_LIMIT, MINIMUM_VOLTAGE, screen,
)
from src.grid_support import AREAS, TURNS, read_csv


class IllustrativeLossTests(unittest.TestCase):
    def test_reference_powers_and_scaling(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario.name):
                eddy, hysteresis = scenario.core_losses(2, 50, 1.2, .00035)
                self.assertAlmostEqual(eddy, 2 * scenario.eddy_ref_w_kg)
                self.assertAlmostEqual(hysteresis, 2 * scenario.hysteresis_ref_w_kg)
                scaled = scenario.core_losses(2, 100, 2.4, .00070)
                self.assertAlmostEqual(scaled[0], eddy * 64)
                self.assertAlmostEqual(scaled[1], hysteresis * 2 * 2**scenario.exponent)
                self.assertTrue(all(value > 0 for value in scenario.core_losses(2, 50, .35, .00035)))
                with self.assertRaises(ValueError):
                    scenario.core_losses(2, 50, 0, .00035)

    def test_screen_limits_and_no_voltage_maximum(self):
        self.assertEqual(screen(1.50, 22.0), (True, True, True))
        self.assertEqual(screen(.7, 28.0), (True, True, True))
        self.assertEqual(screen(1.50001, 22.0), (False, True, False))
        self.assertEqual(screen(1.0, 21.9999), (True, False, False))
        with self.assertRaises(ValueError):
            screen(float("nan"), 24)


class SavedOptimisationTests(unittest.TestCase):
    def test_all_grid_outputs_and_archived_circuit_agreement(self):
        rows = read_csv(DATA / "all_1107_candidates.csv")
        root = DATA.parents[2]
        archived_csv = Path("data/optimisation/all_1107_candidates.csv")
        original_location = root / archived_csv
        if not original_location.is_file():
            original_location = root / "archive/stage1-to-stage4-review" / archived_csv
        old = read_csv(original_location)
        def coordinate(row):
            return int(row["primary_turns"]), float(row["effective_area_cm2"])

        self.assertEqual([coordinate(r) for r in rows], [(n, a) for a in AREAS for n in TURNS])
        previous = {coordinate(row): row for row in old}
        coefficients = {row["scenario"]: row for row in read_csv(DATA / "illustrative_coefficients.csv")}
        passing = read_csv(DATA / "passing_candidates.csv")
        calculated_passes = []
        for row in rows:
            n, _ = coordinate(row)
            self.assertEqual(int(row["secondary_turns"]), round(n * 24 / 230))
            archived = previous[coordinate(row)]
            for current, historical in (
                ("load_terminal_v", "load_terminal_v"), ("no_drop_peak_t", "bmax_nominal_no_drop_t"),
                ("loaded_peak_t", "loaded_peak_t"), ("primary_ohm", "primary_ohm"),
                ("secondary_ohm", "secondary_ohm"), ("copper_w", "copper_loss_w"),
                ("core_mass_kg", "core_mass_kg"), ("copper_mass_kg", "copper_mass_kg"),
            ):
                self.assertAlmostEqual(float(row[current]), float(archived[historical]), places=10)
            terminal = float(row["load_terminal_v"])
            self.assertAlmostEqual(terminal * float(row["secondary_rms_a"]), 100)
            flux_ok = float(row["no_drop_peak_t"]) <= FLUX_LIMIT
            voltage_ok = terminal >= MINIMUM_VOLTAGE
            self.assertEqual(row["flux_pass"], str(flux_ok))
            self.assertEqual(row["voltage_pass"], str(voltage_ok))
            self.assertEqual(row["passes_both"], str(flux_ok and voltage_ok))
            if flux_ok and voltage_ok:
                calculated_passes.append(row)
            for scenario, coeff in coefficients.items():
                b, m = float(row["loaded_peak_t"]), float(row["core_mass_kg"])
                eddy = float(coeff["ke"]) * m * (50 * b * .00035)**2
                hysteresis = float(coeff["kh"]) * m * 50 * b**float(coeff["n"])
                total = float(row[f"total_{scenario}_w"])
                self.assertTrue(isfinite(total) and total > 0)
                self.assertAlmostEqual(float(row[f"eddy_{scenario}_w"]), eddy)
                self.assertAlmostEqual(float(row[f"hysteresis_{scenario}_w"]), hysteresis)
                self.assertAlmostEqual(total, float(row["copper_w"]) + eddy + hysteresis)
        self.assertEqual(passing, sorted(calculated_passes, key=lambda row: float(row["total_medium_w"])))
        self.assertTrue(any(float(row["loaded_peak_t"]) < 1 for row in passing))

    def test_each_saved_optimum_and_baseline_use_matching_scenario(self):
        passing = read_csv(DATA / "passing_candidates.csv")
        summary = read_csv(DATA / "scenario_summary.csv")
        comparison = read_csv(DATA / "baseline_vs_optimum.csv")
        self.assertEqual(len(summary), 3)
        for row in summary:
            scenario = row["scenario"]
            total = f"total_{scenario}_w"
            baseline, optimum = [r for r in comparison if r["scenario"] == scenario]
            self.assertEqual((baseline["primary_turns"], baseline["secondary_turns"], baseline["effective_area_cm2"]),
                             ("600", "63", "12.0"))
            self.assertEqual(float(row["total_w"]), min(float(r[total]) for r in passing))
            self.assertEqual(row["total_w"], optimum[total])
            self.assertEqual(row["baseline_total_w"], baseline[total])
            self.assertAlmostEqual(float(row["improvement_w"]), float(baseline[total]) - float(optimum[total]))
            boundary = (int(optimum["primary_turns"]) in (TURNS[0], TURNS[-1])
                        or float(optimum["effective_area_cm2"]) in (AREAS[0], AREAS[-1]))
            self.assertEqual(row["on_grid_boundary"], str(boundary))
