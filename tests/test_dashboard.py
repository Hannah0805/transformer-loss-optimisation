"""Verify the in-browser calculator against the approved, recorded grid."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

from src.optimisation import DATA, build_model, load_parameters
from src.grid_support import read_csv


ROOT = Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = {
            (int(row["primary_turns"]), float(row["effective_area_cm2"])): row
            for row in read_csv(DATA / "all_1107_candidates.csv")
        }

    def open_page(self, page):
        app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=20).run()
        app.radio(key="navigation").set_value(page).run()
        self.assertFalse(app.exception)
        return app

    def verify_point(self, app, turns, area, scenario):
        row = self.grid[(turns, area)]
        metrics = {metric.label: metric.value for metric in app.metric}
        for label, key, unit in (
            ("No-drop peak flux density", "no_drop_peak_t", "T"),
            ("Loaded peak flux density", "loaded_peak_t", "T"),
            ("Load-terminal voltage", "load_terminal_v", "V RMS"),
            ("Primary copper", "primary_copper_w", "W"),
            ("Secondary copper", "secondary_copper_w", "W"),
            ("Classical eddy current", f"eddy_{scenario}_w", "W"),
            ("Illustrative hysteresis", f"hysteresis_{scenario}_w", "W"),
            ("Total modelled loss", f"total_{scenario}_w", "W"),
            ("Estimated core mass", "core_mass_kg", "kg"),
            ("Estimated bare copper mass", "copper_mass_kg", "kg"),
        ):
            self.assertEqual(metrics[label], f"{float(row[key]):.3f} {unit}", label)
        self.assertEqual(metrics["Primary turns"], f"{turns:,}")
        self.assertEqual(metrics["Secondary turns"], row["secondary_turns"])
        self.assertEqual(metrics["Effective core area"], f"{area:.1f} cm²")
        for label, key in (
            ("No-drop peak ≤ 1.50 T", "flux_pass"),
            ("Loaded voltage ≥ 22.0 V RMS", "voltage_pass"),
            ("Combined screening", "passes_both"),
        ):
            self.assertEqual(metrics[label], "Pass" if row[key] == "True" else "Fail")

    def test_overview_report_and_approved_metrics(self):
        app = self.open_page("Project overview")
        metrics = {m.label: m.value for m in app.metric}
        self.assertEqual(metrics["Baseline · medium scenario"], "9.567 W")
        self.assertEqual(metrics["Screened minimum · medium scenario"], "9.342 W")
        self.assertEqual(metrics["Reduction in modelled loss"], "2.35%")
        self.assertEqual(app.get("download_button")[0].label, "Download engineering report (PDF)")

    def test_baseline_optimum_scenario_and_reset(self):
        app = self.open_page("Interactive loss model")
        self.verify_point(app, 600, 12.0, "medium")
        app.slider(key="primary_turns").set_value(475).run()
        self.verify_point(app, 475, 12.0, "medium")
        app.slider(key="core_area").set_value(15.0).run()
        self.verify_point(app, 475, 15.0, "medium")
        app.selectbox(key="coefficient_scenario").select("High").run()
        self.verify_point(app, 475, 15.0, "high")
        app.selectbox(key="coefficient_scenario").select("Low").run()
        self.verify_point(app, 475, 15.0, "low")
        app.button(key="reset_baseline").click().run()
        self.verify_point(app, 600, 12.0, "medium")
        self.assertEqual(app.slider(key="primary_turns").value, 600)
        self.assertEqual(app.slider(key="core_area").value, 12.0)
        self.assertEqual(app.selectbox(key="coefficient_scenario").value, "Medium")

    def test_flux_only_voltage_only_and_low_flux_are_displayed(self):
        app = self.open_page("Interactive loss model")
        app.slider(key="primary_turns").set_value(450)
        app.slider(key="core_area").set_value(10.0)
        app.run()
        self.verify_point(app, 450, 10.0, "medium")
        app.slider(key="primary_turns").set_value(1100)
        app.slider(key="core_area").set_value(30.0)
        app.run()
        self.verify_point(app, 1100, 30.0, "medium")
        self.assertFalse(app.exception)

    def test_optimisation_charts_counts_and_downloads(self):
        app = self.open_page("Optimisation results")
        self.assertEqual(len(app.get("vega_lite_chart")), 4)
        self.assertEqual({m.label: m.value for m in app.metric}, {
            "Passes flux screen": "1,050", "Passes voltage screen": "308", "Passes both screens": "251",
        })
        self.assertEqual(len(app.get("download_button")), 2)
        app.selectbox(key="optimisation_scenario").select("Low").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("450:47 turns at 15.5 cm²" in note.value for note in app.caption))

    def test_live_evaluator_matches_each_approved_grid_row(self):
        model = build_model(load_parameters())
        self.assertEqual(len(self.grid), 1107)
        for (turns, area), archived in self.grid.items():
            actual = model.evaluate(turns, area)
            for name, value in actual.items():
                if isinstance(value, bool):
                    self.assertEqual(str(value), archived[name])
                else:
                    self.assertAlmostEqual(value, float(archived[name]), places=11)
