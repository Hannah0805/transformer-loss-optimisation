import unittest
from dataclasses import replace
from math import isclose, pi, sqrt

from src.constraints import DesignLimits, check_design
from src.core_geometry import EICore, WindowClearances, winding_layout
from src.material_models import Copper, HysteresisScenario, LaminatedSteel
from src.transformer_model import (
    ElectricalSpec, Winding, evaluate_design, ideal_secondary_voltage,
    nearest_secondary_turns, peak_flux_density, resistive_load_point,
)


class TransformerModelTests(unittest.TestCase):
    def setUp(self):
        self.spec = ElectricalSpec(230, 24, 50, 100)
        self.core = EICore(0.035, 12e-4 / (0.95 * 0.035), 0.018, 0.050, 0.95)
        self.clearance = WindowClearances(0.001, 0.001, 0.003, 0.001)
        self.primary = Winding(600, 0.45e-3, 0.50e-3, 0.20, 60)
        self.secondary = Winding(63, 1.20e-3, 1.30e-3, 0.20, 60)
        self.copper = Copper(1.7241e-8, 0.00393)
        self.steel = LaminatedSteel(0.35e-3, 4.22e-7, 7690)
        self.scenario = HysteresisScenario("Illustrative test input", 0.02, 1.5, 2, 1, 1.5)
        self.limits = DesignLimits(1.5, 241.5, 50, 0.35, 0.01, 0.05, 4e6)

    def evaluate(self, scenario=None, **kwargs):
        return evaluate_design(
            self.spec, self.core, self.clearance, self.primary, self.secondary,
            self.copper, self.steel, scenario, **kwargs,
        )

    def test_integer_turns_and_voltage_ratio(self):
        self.assertEqual(nearest_secondary_turns(230, 24, 600), 63)
        self.assertEqual(nearest_secondary_turns(100, 25, 10), 3)
        self.assertEqual(nearest_secondary_turns(230, 24, 1), 1)
        self.assertAlmostEqual(ideal_secondary_voltage(230, 600, 63), 24.15)
        with self.assertRaises(ValueError):
            ideal_secondary_voltage(230, 600, 62.5)

    def test_faraday_rms_and_area_conversion(self):
        flux_density = peak_flux_density(230, 50, 600, 12 * (1e-2)**2)
        self.assertAlmostEqual(flux_density, 1.4380052272)
        peak_emf = 2 * pi * 50 * 600 * 12e-4 * flux_density
        self.assertAlmostEqual(peak_emf / sqrt(2), 230)
        self.assertAlmostEqual(peak_flux_density(230, 50, 1200, 12e-4), flux_density / 2)
        self.assertAlmostEqual(peak_flux_density(230, 100, 600, 12e-4), flux_density / 2)
        self.assertAlmostEqual(peak_flux_density(230, 50, 600, 24e-4), flux_density / 2)

    def test_geometry_volume_and_common_scale_law(self):
        core = self.core
        w, d, u, h, k = (core.centre_width_m, core.stack_depth_m, core.window_width_m,
                          core.window_height_m, core.stacking_factor)
        self.assertAlmostEqual(core.steel_volume_m3, ((2*w + 2*u)*(h + w) - 2*u*h)*k*d)
        self.assertAlmostEqual(core.steel_mass_kg(7690), core.steel_volume_m3 * 7690)
        self.assertAlmostEqual(core.magnetic_path_m, 2 * ((h + w/2) + (u + 3*w/4)))
        scaled = core.with_effective_area(core.effective_area_m2 * 4)
        self.assertAlmostEqual(scaled.effective_area_m2 / core.effective_area_m2, 4)
        self.assertAlmostEqual(scaled.magnetic_path_m / core.magnetic_path_m, 2)
        self.assertAlmostEqual(scaled.steel_volume_m3 / core.steel_volume_m3, 8)

    def test_layer_weight_and_mean_turn_length(self):
        layout = winding_layout(self.core, 3, 0.01, 0.02, 0)
        self.assertEqual((layout.turns_per_layer, layout.layers), (2, 2))
        base = 2*(self.core.centre_width_m + self.core.stack_depth_m)
        self.assertAlmostEqual(layout.mean_turn_length_m, base + (2*0.04 + 0.12)/3)
        self.assertAlmostEqual(layout.radial_build_m, 0.02)
        exact_fit = winding_layout(self.core, 3, 0.003, 0.009, 0)
        self.assertEqual((exact_fit.turns_per_layer, exact_fit.layers), (3, 1))
        result = self.evaluate()
        self.assertGreater(result.secondary_layout.mean_turn_length_m, result.primary_layout.mean_turn_length_m)

    def test_copper_units_and_temperature(self):
        winding = Winding(10, 2e-3, 2.1e-3, 0.5, 20)
        expected_area = pi * 1e-6
        expected_ohm = 1.7241e-8 * (10 * 0.25 + 0.5) / expected_area
        self.assertTrue(isclose(winding.conductor_area_m2, expected_area))
        self.assertTrue(isclose(winding.resistance_ohm(self.copper, 0.25), expected_ohm))
        hot = replace(winding, temperature_c=60)
        self.assertTrue(isclose(hot.resistance_ohm(self.copper, 0.25), expected_ohm * 1.1572))
        result = self.evaluate()
        self.assertAlmostEqual(result.copper_w, result.load.primary_rms_a**2 * result.primary_ohm
                               + result.load.secondary_rms_a**2 * result.secondary_ohm)

    def test_classical_loss_units_and_scaling(self):
        volumetric = self.steel.classical_loss_w_m3(50, 1.0)
        specific = self.steel.classical_loss_w_kg(50, 1.0)
        self.assertAlmostEqual(specific, 0.155233625861)
        self.assertAlmostEqual(volumetric / 7690, specific)
        self.assertAlmostEqual(volumetric * self.core.steel_volume_m3,
                               specific * self.core.steel_mass_kg(7690))
        self.assertAlmostEqual(self.steel.classical_loss_w_kg(100, 1), 4 * specific)
        self.assertAlmostEqual(self.steel.classical_loss_w_kg(50, 2), 4 * specific)
        thicker = replace(self.steel, sheet_thickness_m=self.steel.sheet_thickness_m * 2)
        self.assertAlmostEqual(thicker.classical_loss_w_kg(50, 1), 4 * specific)

    def test_hysteresis_energy_per_cycle_and_domain(self):
        self.assertAlmostEqual(self.scenario.specific_loss_w_kg(50, 1.5), 1.0)
        self.assertAlmostEqual(self.scenario.specific_loss_w_kg(100, 1.2), 2.0 * (1.2/1.5)**2)
        with self.assertRaises(ValueError):
            self.scenario.specific_loss_w_kg(50, 1.6)
        uncovered = self.evaluate(replace(self.scenario, min_flux_density_t=1.45))
        self.assertIsNone(uncovered.hysteresis_w)
        self.assertIsNone(self.evaluate().separated_total_w)
        result = self.evaluate(self.scenario)
        self.assertAlmostEqual(result.separated_total_w,
                               result.copper_w + result.classical_w + result.hysteresis_w)

    def test_load_conventions_and_power_balance(self):
        result = self.evaluate()
        self.assertAlmostEqual(self.spec.primary_reference_a, 100 / 230)
        self.assertAlmostEqual(result.load.secondary_rms_a, 100 / 24)
        self.assertAlmostEqual(result.load.primary_rms_a, result.load.secondary_rms_a * 63 / 600)
        self.assertAlmostEqual(result.load.primary_induced_rms_v - result.spec.primary_rms_v,
                               -result.load.primary_rms_a * result.primary_ohm)
        self.assertLess(result.loaded_peak_t, result.no_drop_peak_t)
        self.assertLess(result.load.delivered_va, 100)
        # The resistive circuit excludes excitation. Its balance covers output and copper only.
        self.assertAlmostEqual(self.spec.primary_rms_v * result.load.primary_rms_a,
                               result.load.delivered_va + result.copper_w)
        exact = self.evaluate(fixed_va=True)
        self.assertAlmostEqual(exact.load.delivered_va, 100)
        self.assertGreater(exact.load.secondary_rms_a, result.load.secondary_rms_a)
        self.assertAlmostEqual(resistive_load_point(self.spec, 24/230, 0, 0, fixed_va=True).delivered_va, 100)
        with self.assertRaisesRegex(ValueError, "No real"):
            resistive_load_point(self.spec, 0.1, 50, 100, fixed_va=True)
        with self.assertRaisesRegex(ValueError, "positive terminal"):
            resistive_load_point(self.spec, 0.1, 50, 100)

    def test_baseline_constraints_and_rejection_reasons(self):
        result = self.evaluate()
        checks = {check.name: check for check in check_design(result, self.limits)}
        self.assertTrue(checks["Ideal secondary voltage error"].passed)
        self.assertTrue(checks["Insulated radial build"].passed)
        self.assertTrue(checks["Bare-copper window fill"].passed)
        self.assertFalse(checks["Loaded secondary voltage error"].passed)
        self.assertFalse(checks["Peak flux at screening envelope"].passed)
        self.assertTrue(all(check.passed for check in checks.values() if "current density" in check.name))
        narrow = replace(self.core, window_width_m=0.008)
        squeezed = evaluate_design(self.spec, narrow, self.clearance, self.primary,
                                   self.secondary, self.copper, self.steel)
        checks = {check.name: check for check in check_design(squeezed, self.limits)}
        self.assertFalse(checks["Bare-copper window fill"].passed)
        self.assertFalse(checks["Insulated radial build"].passed)

    def test_invalid_physical_inputs(self):
        for overrides in ({"centre_width_m": 0}, {"stacking_factor": 1.1},
                          {"window_height_m": float("nan")}):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                replace(self.core, **overrides)
        with self.assertRaises(ValueError):
            replace(self.primary, insulated_diameter_m=0.1e-3)
        with self.assertRaises(ValueError):
            peak_flux_density(230, 0, 600, 12e-4)
        with self.assertRaises(ValueError):
            WindowClearances(0, 0, 0.030, 0).usable_dimensions(self.core)
        with self.assertRaises(ValueError):
            winding_layout(self.core, 1, 0.050, 0.040, 0)
        with self.assertRaises(ValueError):
            check_design(self.evaluate(), replace(self.limits, maximum_supply_rms_v=200))


if __name__ == "__main__":
    unittest.main()
