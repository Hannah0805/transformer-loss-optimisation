"""Interactive portfolio dashboard backed by the shared candidate evaluator."""

import csv
import io
import os
from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.optimisation import (
    DATA, FLUX_LIMIT, MINIMUM_VOLTAGE, SCENARIOS, build_model, load_parameters,
)
from src.grid_support import AREAS, TURNS


REPORT = ROOT / "report/Transformer_Loss_Optimisation_Report.pdf"
SCENARIO_NAMES = tuple(case.name.title() for case in SCENARIOS)
PAGES = ("Project overview", "Interactive loss model", "Optimisation results")
DISCLAIMER = (
    "Core-loss coefficients are illustrative and uncalibrated. Screening tests the two "
    "specified model limits. Manufacturing, thermal performance and actual efficiency remain unverified."
)
COLORS = ["#6887A9", "#17568F", "#8B6D47"]

st.set_page_config(page_title="Transformer Loss Explorer", layout="wide")


@st.cache_resource
def load_model():
    return build_model(load_parameters())


@st.cache_data
def saved_results():
    return tuple(pd.read_csv(DATA / name) for name in (
        "all_1107_candidates.csv", "scenario_summary.csv", "screening_summary.csv"))


def scalars(row, scenario):
    return {
        "Primary copper": row["primary_copper_w"],
        "Secondary copper": row["secondary_copper_w"],
        "Classical eddy current": row[f"eddy_{scenario}_w"],
        "Illustrative hysteresis": row[f"hysteresis_{scenario}_w"],
        "Total": row[f"total_{scenario}_w"],
    }


def comparison_frame(baseline, optimum, scenario):
    return pd.DataFrame([
        {"Loss component": component, "Design": label, "Loss (W)": value}
        for label, row in (("Baseline", baseline), ("Screened minimum", optimum))
        for component, value in scalars(row, scenario).items()
    ])


def comparison_chart(baseline, optimum, scenario):
    data = comparison_frame(baseline, optimum, scenario)
    return alt.Chart(data).mark_bar(cornerRadiusEnd=3).encode(
        y=alt.Y("Loss component:N", sort=list(scalars(baseline, scenario)), title=None,
                axis=alt.Axis(labelLimit=190)),
        yOffset=alt.YOffset("Design:N", sort=["Baseline", "Screened minimum"]),
        x=alt.X("Loss (W):Q", title="Modelled loss (W)"),
        color=alt.Color("Design:N", scale=alt.Scale(
            domain=["Baseline", "Screened minimum"], range=COLORS[:2]), legend=alt.Legend(orient="top")),
        tooltip=["Loss component", "Design", alt.Tooltip("Loss (W):Q", format=".3f")],
    ).properties(height=238)


def scenario_row(summary, name):
    return summary.loc[summary["scenario"] == name].iloc[0]


def grid_point(grid, row):
    return grid.loc[(grid["primary_turns"] == row["primary_turns"]) &
                    (grid["effective_area_cm2"] == row["effective_area_cm2"])].iloc[0]


def reset_to_baseline():
    model = load_model()
    st.session_state["primary_turns"] = model.primary.turns
    st.session_state["core_area"] = round(model.core.effective_area_m2 * 1e4, 8)
    st.session_state["coefficient_scenario"] = "Medium"


def overview():
    model = load_model()
    grid, summary, _ = saved_results()
    reference = model.evaluate(model.primary.turns, round(model.core.effective_area_m2 * 1e4, 8))
    medium = scenario_row(summary, "medium")
    best = grid_point(grid, medium)
    st.title("Transformer Loss Explorer")
    st.markdown("**Transformer Loss Trade-off Optimisation**  \nA Parametric Study of Copper, Eddy Current and Hysteresis Losses")
    st.write("How can winding turns and effective core area minimise combined copper, classical eddy current and hysteresis losses under simplified electrical constraints?")
    metrics = st.columns(3)
    metrics[0].metric("Baseline · medium scenario", f"{reference['total_medium_w']:.3f} W", border=True)
    metrics[1].metric("Screened minimum · medium scenario", f"{medium['total_w']:.3f} W", border=True)
    metrics[2].metric("Reduction in modelled loss", f"{medium['improvement_percent']:.2f}%", border=True)
    main, links = st.columns([3, 2], gap="large")
    with main:
        st.subheader("Where losses change")
        st.write(
            "Copper loss follows winding current and resistance. Classical eddy current loss "
            "comes from currents induced in the steel. Hysteresis represents energy dissipated "
            "when the magnetic field cycles."
        )
        st.write(
            "More turns can lower flux density while raising winding resistance. Increasing "
            "core area lowers induction at fixed turns but can increase steel mass and mean turn length."
        )
        st.caption(DISCLAIMER)
    with links:
        st.subheader("Project files")
        st.download_button("Download engineering report (PDF)", REPORT.read_bytes(), REPORT.name,
                           mime="application/pdf", icon=":material/download:")
        github = os.environ.get("PORTFOLIO_GITHUB_URL")
        if not github:
            try:
                github = st.secrets.get("PORTFOLIO_GITHUB_URL")
            except StreamlitSecretNotFoundError:
                github = None
        repository = github or "https://github.com/Hannah0805/transformer-loss-optimisation"
        st.link_button("GitHub repository", repository, icon=":material/open_in_new:")
    st.subheader("Baseline and screened minimum")
    st.altair_chart(comparison_chart(reference, best, "medium"), width="stretch")
    st.caption(
        f"The medium scenario selects {int(best['primary_turns'])}:"
        f"{int(best['secondary_turns'])} turns and {best['effective_area_cm2']:.1f} cm². "
        f"Both designs deliver {model.spec.rated_va:g} VA in the model."
    )


def status(condition):
    return "Pass" if condition else "Fail"


def one_row_csv(row):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=list(row), lineterminator="\n")
    writer.writeheader()
    writer.writerow(row)
    return handle.getvalue()


def explorer():
    model = load_model()
    st.title("Interactive Loss Model")
    st.write("Choose a grid point to solve the constant-power circuit and calculate each loss component.")
    st.button("Reset to Baseline", on_click=reset_to_baseline, key="reset_baseline")
    n_col, area_col, scenario_col = st.columns(3)
    turns = n_col.slider("Primary turns", TURNS.start, TURNS[-1], model.primary.turns,
                         step=TURNS.step, key="primary_turns")
    area = area_col.slider("Effective core area (cm²)", AREAS[0], AREAS[-1],
                           round(model.core.effective_area_m2 * 1e4, 8),
                           step=AREAS[1] - AREAS[0], format="%.1f", key="core_area")
    scenario = scenario_col.selectbox("Core-loss coefficient scenario", SCENARIO_NAMES,
                                      index=1, key="coefficient_scenario").lower()
    row = model.evaluate(turns, area)
    label = st.columns(3)
    label[0].metric("Primary turns", f"{turns:,}", border=True)
    label[1].metric("Secondary turns", str(row["secondary_turns"]), border=True)
    label[2].metric("Effective core area", f"{area:.1f} cm²", border=True)
    peaks = st.columns(3)
    peaks[0].metric("No-drop peak flux density", f"{row['no_drop_peak_t']:.3f} T", border=True)
    peaks[1].metric("Loaded peak flux density", f"{row['loaded_peak_t']:.3f} T", border=True)
    peaks[2].metric("Load-terminal voltage", f"{row['load_terminal_v']:.3f} V RMS", border=True)
    st.caption(f"Deviation from the {model.spec.secondary_target_rms_v:g} V target is "
               f"{row['target_voltage_deviation_v']:+.3f} V.")
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Modelled losses")
        losses = scalars(row, scenario)
        for column, (name, value) in zip(st.columns(2), list(losses.items())[:2]):
            column.metric(name, f"{value:.3f} W")
        for column, (name, value) in zip(st.columns(2), list(losses.items())[2:4]):
            column.metric(name, f"{value:.3f} W")
        st.metric("Total modelled loss", f"{losses['Total']:.3f} W", border=True)
    with right:
        st.subheader("Design screening")
        st.metric(f"No-drop peak ≤ {FLUX_LIMIT:.2f} T", status(row["flux_pass"]))
        st.metric(f"Loaded voltage ≥ {MINIMUM_VOLTAGE:.1f} V RMS", status(row["voltage_pass"]))
        st.metric("Combined screening", status(row["passes_both"]), border=True)
        st.caption("No upper voltage criterion. Geometry, estimated masses and winding fit are diagnostics.")
    mass = st.columns(2)
    mass[0].metric("Estimated core mass", f"{row['core_mass_kg']:.3f} kg")
    mass[1].metric("Estimated bare copper mass", f"{row['copper_mass_kg']:.3f} kg")
    st.caption(DISCLAIMER)
    st.download_button("Download selected design (CSV)",
                       one_row_csv({"selected_scenario": scenario, **row}),
                       "selected_transformer_design.csv", mime="text/csv")


def heatmap(grid, scenario):
    order = "descending"
    return alt.Chart(grid).mark_rect().encode(
        x=alt.X("primary_turns:O", axis=alt.Axis(values=[450, 550, 650, 750, 850, 950, 1050],
                                                labelAngle=0), title="Primary turns"),
        y=alt.Y("effective_area_cm2:O", sort=order, axis=alt.Axis(values=[10, 15, 20, 25, 30]),
                title="Effective core area (cm²)"),
        color=alt.Color(f"total_{scenario}_w:Q", title="Loss (W)", scale=alt.Scale(scheme="tealblues")),
        tooltip=[alt.Tooltip("primary_turns:Q", title="Primary turns"),
                 alt.Tooltip("effective_area_cm2:Q", title="Core area (cm²)", format=".1f"),
                 alt.Tooltip(f"total_{scenario}_w:Q", title="Total loss (W)", format=".3f"),
                 alt.Tooltip("passes_both:N", title="Passes both")],
    ).properties(height=320)


def tradeoff_chart(grid, scenario):
    chart_data = grid.assign(core_loss_w=grid[f"eddy_{scenario}_w"] + grid[f"hysteresis_{scenario}_w"],
                             Screening=grid["passes_both"].map({True: "Passes", False: "Fails"}))
    return alt.Chart(chart_data).mark_circle(size=34, opacity=.63).encode(
        x=alt.X("copper_w:Q", title="Winding copper loss (W)", scale=alt.Scale(zero=False)),
        y=alt.Y("core_loss_w:Q", title="Core loss (W)", scale=alt.Scale(zero=False)),
        color=alt.Color("Screening:N", scale=alt.Scale(
            domain=["Fails", "Passes"], range=["#ADBACA", "#17568F"]), legend=alt.Legend(orient="top")),
        tooltip=[alt.Tooltip("primary_turns:Q", title="Primary turns"),
                 alt.Tooltip("effective_area_cm2:Q", title="Core area (cm²)", format=".1f"),
                 alt.Tooltip("copper_w:Q", title="Copper (W)", format=".3f"),
                 alt.Tooltip("core_loss_w:Q", title="Core (W)", format=".3f"), "Screening"],
    ).properties(height=310)


def scenario_chart(summary):
    frame = summary.melt(id_vars=["scenario"], value_vars=["baseline_total_w", "total_w"],
                         var_name="Design", value_name="Loss (W)")
    frame["Design"] = frame["Design"].map({"baseline_total_w": "Baseline", "total_w": "Screened minimum"})
    frame["scenario"] = frame["scenario"].str.title()
    return alt.Chart(frame).mark_bar(cornerRadiusEnd=3).encode(
        x=alt.X("scenario:N", sort=list(SCENARIO_NAMES), title="Coefficient scenario", axis=alt.Axis(labelAngle=0)),
        xOffset="Design:N", y=alt.Y("Loss (W):Q", title="Modelled total loss (W)"),
        color=alt.Color("Design:N", scale=alt.Scale(domain=["Baseline", "Screened minimum"], range=COLORS[:2]),
                        legend=alt.Legend(orient="top")),
        tooltip=["scenario", "Design", alt.Tooltip("Loss (W):Q", format=".3f")],
    ).properties(height=250)


def optimisation():
    model = load_model()
    grid, summary, screening = saved_results()
    st.title("Optimisation Results")
    counts = screening.set_index("metric")["count"]
    st.write(f"The grid contains {counts['total_candidates']:,} configurations. "
             f"{counts['passes_both']:,} pass both screens and enter the loss ranking.")
    scenario = st.selectbox("Scenario for grid charts", SCENARIO_NAMES, index=1, key="optimisation_scenario").lower()
    result = scenario_row(summary, scenario)
    best = grid_point(grid, result)
    baseline = model.evaluate(model.primary.turns, round(model.core.effective_area_m2 * 1e4, 8))
    charts = st.columns(2, gap="large")
    with charts[0]:
        st.subheader("Total-loss heatmap")
        st.altair_chart(heatmap(grid, scenario), width="stretch")
        st.caption("Every cell has a complete modelled loss. Hover to see the two-screen outcome.")
    with charts[1]:
        st.subheader("Copper and core loss")
        st.altair_chart(tradeoff_chart(grid, scenario), width="stretch")
        st.caption("Core loss is the sum of classical eddy current and illustrative hysteresis. Blue points pass both screens.")
    comparisons = st.columns(2, gap="large")
    with comparisons[0]:
        st.subheader("Baseline and screened minimum")
        st.altair_chart(comparison_chart(baseline, best, scenario), width="stretch")
        boundary = "on the grid boundary" if result["on_grid_boundary"] else "inside the grid"
        st.caption(f"{int(result['primary_turns'])}:{int(result['secondary_turns'])} turns at "
                   f"{result['effective_area_cm2']:.1f} cm², {boundary}. "
                   f"Change relative to the same-scenario baseline {result['improvement_percent']:.2f}% lower.")
    with comparisons[1]:
        st.subheader("Sensitivity to coefficients")
        st.altair_chart(scenario_chart(summary), width="stretch")
        st.caption("Each scenario has its own recalculated baseline. The low, medium and high assumptions select different turns and areas.")
    st.dataframe(summary.assign(scenario=summary["scenario"].str.title()).rename(columns={
        "scenario": "Scenario", "primary_turns": "Primary turns", "secondary_turns": "Secondary turns",
        "effective_area_cm2": "Core area (cm²)", "total_w": "Minimum loss (W)",
    })[["Scenario", "Primary turns", "Secondary turns", "Core area (cm²)", "Minimum loss (W)"]],
        hide_index=True, width="stretch",
        column_config={"Core area (cm²)": st.column_config.NumberColumn(format="%.1f"),
                       "Minimum loss (W)": st.column_config.NumberColumn(format="%.3f")})
    cols = st.columns(3)
    for column, label, key in zip(cols, ("Passes flux screen", "Passes voltage screen", "Passes both screens"),
                                  ("flux_pass", "voltage_pass", "passes_both")):
        column.metric(label, f"{counts[key]:,}", border=True)
    st.caption(DISCLAIMER)
    for column, label, filename in zip(st.columns(2),
                                      ("Download complete grid (CSV)", "Download passing grid (CSV)"),
                                      ("all_1107_candidates.csv", "passing_candidates.csv")):
        column.download_button(label, (DATA / filename).read_bytes(), filename, mime="text/csv")


with st.sidebar:
    st.markdown("### Transformer Loss Explorer")
    page = st.radio("Navigation", PAGES, key="navigation")
    st.divider()
    st.caption("100 VA · 230 V RMS · 50 Hz")
    st.caption("Illustrative engineering model")

{PAGES[0]: overview, PAGES[1]: explorer, PAGES[2]: optimisation}[page]()
